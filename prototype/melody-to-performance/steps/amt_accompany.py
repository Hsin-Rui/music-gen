"""Melody MIDI -> AMT accompaniment MIDI (runs in envs/amt, Python 3.10).

    envs/amt/bin/python steps/amt_accompany.py IN.mid OUT.mid --prompt none|chords [--device cpu|mps]

The melody is put on its own MIDI program (MELODY_PROGRAM) and passed to AMT as
`controls`; AMT generates the other instruments. With --prompt chords, a few bars
of block chords (I-IV-V-I in the melody's key, program CHORD_PROGRAM) are given
as `inputs` history and generation starts where the chords end.
Output contains only the accompaniment (history chords + generated events).
"""
import argparse
import json
import math
import sys
import time

import numpy as np
import pretty_midi
import torch

from anticipation import ops
from anticipation.config import MAX_DUR, MAX_TIME, TIME_RESOLUTION
from anticipation.convert import events_to_midi
import anticipation.sample as amt_sample
from anticipation.sample import generate
from anticipation.vocab import CONTROL_OFFSET, DUR_OFFSET, MAX_NOTE, MAX_PITCH, NOTE_OFFSET, TIME_OFFSET

MODEL = "stanford-crfm/music-medium-800k"
MELODY_PROGRAM = 1   # bright acoustic piano: piano-like but distinct from the chord program
CHORD_PROGRAM = 0    # acoustic grand piano
MIN_HISTORY_SEC = 4.0

# Krumhansl-Kessler key profiles
KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def warn(msg):
    print(f"WARNING: {msg}", file=sys.stderr, flush=True)


def load_melody(path):
    pm = pretty_midi.PrettyMIDI(path)
    tracks = [i for i in pm.instruments if not i.is_drum and i.notes]
    if not tracks:
        sys.exit("no non-drum notes in input")
    if len(tracks) > 1:
        warn(f"input has {len(tracks)} non-drum tracks; using the first ({tracks[0].name!r}) as melody")
    notes = sorted(tracks[0].notes, key=lambda n: (n.start, n.pitch))
    return pm, notes


def detect_key(pm, notes):
    if pm.key_signature_changes:
        k = pm.key_signature_changes[0].key_number  # 0-11 major, 12-23 minor
        return k % 12, k >= 12, "key signature"
    hist = np.zeros(12)
    for n in notes:
        hist[n.pitch % 12] += n.end - n.start
    best = max(((np.corrcoef(hist, np.roll(prof, t))[0, 1], t, minor)
                for t in range(12) for minor, prof in ((False, KK_MAJOR), (True, KK_MINOR))))
    return best[1], best[2], "Krumhansl-Kessler estimate"


def meter(pm):
    _, tempi = pm.get_tempo_changes()
    bpm = float(tempi[0]) if len(tempi) else 120.0
    ts = pm.time_signature_changes[0] if pm.time_signature_changes else pretty_midi.TimeSignature(4, 4, 0)
    beat = 60.0 / bpm * 4.0 / ts.denominator
    return bpm, ts.numerator, beat


def chord_history(pm, notes):
    tonic, minor, how = detect_key(pm, notes)
    bpm, num, beat = meter(pm)
    bar = num * beat
    n_bars = 2 if 2 * bar >= MIN_HISTORY_SEC else math.ceil(MIN_HISTORY_SEC / bar)
    # harmonic rhythm: half bar in even meters, whole bar otherwise
    step = bar / 2 if num % 2 == 0 else bar
    n_chords = int(round(n_bars * bar / step))
    third = 3 if minor else 4
    degrees = {  # root offset, chord intervals
        "I": (0, [0, third, 7]),
        "IV": (5, [0, 3 if minor else 4, 7]),
        "V": (7, [0, 4, 7]),  # major V in minor too (raised leading tone)
    }
    prog = ["I", "IV", "V", "I"]
    events, out = [], []
    for c in range(n_chords):
        name = prog[c * len(prog) // n_chords]  # stretch I-IV-V-I over the history
        root_off, ivs = degrees[name]
        root = 48 + (tonic + root_off) % 12  # triad root in C3..B3
        pitches = [root - 12] + [root + i for i in ivs]  # bass + close triad
        t0, t1 = c * step, (c + 1) * step * 0.98
        for p in pitches:
            events.append((t0, t1, p, CHORD_PROGRAM))
        out.append(name)
    keyname = pretty_midi.key_number_to_key_name(tonic + (12 if minor else 0))
    info = {"key": keyname, "key_source": how, "bpm": bpm, "bars": n_bars,
            "chords": out, "history_sec": n_bars * bar}
    return events, n_bars * bar, info


def restrict_to_piano():
    """Only let AMT write notes for program 0 (acoustic grand piano).

    Upstream add_token() applies instr_logits() when sampling the note token (the 3rd
    token of each event); wrap it so every other instrument, drums included, gets
    -inf. Rests (NOTE_OFFSET + MAX_NOTE) stay allowed.
    """
    original = amt_sample.instr_logits

    def piano_only(logits, full_history):
        logits = original(logits, full_history)
        logits[NOTE_OFFSET + MAX_PITCH:NOTE_OFFSET + MAX_NOTE] = -float("inf")
        return logits

    amt_sample.instr_logits = piano_only


def to_tokens(notes):
    """(start, end, pitch, program) -> AMT event tokens (time, dur, note)."""
    toks = []
    for start, end, pitch, prog in notes:
        t = int(round(TIME_RESOLUTION * start))
        d = max(1, min(MAX_DUR - 1, int(round(TIME_RESOLUTION * (end - start)))))
        if t >= MAX_TIME:
            continue
        toks.extend([TIME_OFFSET + t, DUR_OFFSET + d, NOTE_OFFSET + prog * 128 + pitch])
    return ops.sort(toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--prompt", choices=["none", "chords"], default="none")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--all-instruments", action="store_true",
                    help="let AMT pick any instrument (default: piano only, program 0)")
    ap.add_argument("--max-seconds", type=float, default=None,
                    help="only accompany the first N seconds (smoke test)")
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM

    torch.manual_seed(args.seed)
    pm, notes = load_melody(args.input)
    if args.max_seconds:
        notes = [n for n in notes if n.start < args.max_seconds]
    mel = [(n.start, n.end, n.pitch, MELODY_PROGRAM) for n in notes]
    end_time = max(n.end for n in notes)
    if end_time > MAX_TIME / TIME_RESOLUTION - 1:
        warn(f"melody is {end_time:.0f}s; AMT handles at most ~{MAX_TIME // TIME_RESOLUTION}s, clipping")
        end_time = MAX_TIME / TIME_RESOLUTION - 1
    controls = [CONTROL_OFFSET + tok for tok in to_tokens(mel)]

    info = {"prompt": args.prompt, "melody_program": MELODY_PROGRAM, "end_time": end_time,
            "piano_only": not args.all_instruments}
    if not args.all_instruments:
        restrict_to_piano()
    if args.prompt == "chords":
        chords, start_time, cinfo = chord_history(pm, notes)
        history = to_tokens(chords)
        info.update(cinfo)
    else:
        history, start_time = [], 0

    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(MODEL).to(args.device).eval()
    info["load_sec"] = round(time.time() - t0, 1)

    t0 = time.time()
    accompaniment = generate(model, start_time, end_time, inputs=history,
                             controls=controls, top_p=.98)
    info["generate_sec"] = round(time.time() - t0, 1)
    info["accompaniment_notes"] = len(accompaniment) // 3
    info["instruments"] = sorted(ops.get_instruments(accompaniment).keys())

    events_to_midi(accompaniment).save(args.output)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
