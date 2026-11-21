"""Melody MIDI -> AccoMontage2 harmonization (chord module only) -> chart JSON (runs in envs/accomontage2).

    envs/accomontage2/bin/python steps/harmonize_accomontage2.py MELODY.mid OUT.json [--seed 0]

AccoMontage2 only supports 4/4 with 4- or 8-bar phrases:
- 4/4 melodies are used as is; 2/4 melodies are re-barred to 4/4 (two 2/4 bars = one 4/4 bar)
  and the chords are mapped back afterwards. Any other meter exits with code 3 ("skipped").
- the melody is padded to a multiple of 4 bars by holding its last note; chords of
  padded bars are dropped.
- segmentation: consecutive 4-bar phrases labelled A, B, C, ... (no phrase analysis).
- tonic/mode from the MIDI key signature; output style left at the library default ('*').
Chords are read from chord_gen_log.json ('progression_full': 8 eighth-note labels per bar,
"<root> <type>"), taking the label at each beat. Upstream's chord-only task path
crashes (Pipeline.__add_textures() missing 'log'); a local shim gives that argument a default.
Raw outputs (chord_gen.mid, chord_gen_log.json) go to OUT_DIR/<OUT stem>-accomontage2/.
"""
import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "AccoMontage2"
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

# chorderator/utils/constants.py chord types
TYPE_SUFFIX = {0: "", 1: "m", 2: "aug", 3: "dim", 4: "maj7", 5: "m7", 6: "7", 7: "m7b5", 8: "dim7",
               9: "sus4", 10: ""}
SKIPPED = 3


SHARP_TO_FLAT = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}
FLAT_KEYS = {(5, False), (10, False), (3, False), (8, False), (1, False),  # F Bb Eb Ab Db major
             (2, True), (7, True), (0, True), (5, True), (10, True)}       # d g c f bb minor


def label_to_symbol(label, flats=False):
    """'E 1' / 'A#0' -> 'Em' / 'A#' (or 'Bb' in flat keys)."""
    m = re.match(r"\s*([A-G][#b]?)\s*(-?\d+)?", label)
    if not m:
        raise ValueError(f"unexpected AccoMontage2 chord label {label!r}")
    root = m.group(1)
    if flats:
        root = SHARP_TO_FLAT.get(root, root)
    return root + TYPE_SUFFIX.get(int(m.group(2)) if m.group(2) else 0, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("output")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    melody = Path(args.melody).resolve()
    out = Path(args.output).resolve()
    meta = C.melody_meta(melody)

    num, den = meta["numerator"], meta["denominator"]
    if den != 4 or num not in (2, 4):
        print("RESULT " + json.dumps({"ok": False, "skipped": True,
                                      "why": f"AccoMontage2 supports 4/4 only; melody is {num}/{den}"}))
        sys.exit(SKIPPED)
    group = 4 // num  # source bars per 4/4 bar
    n44 = -(-meta["n_bars"] // group)  # ceil
    n44_padded = -(-n44 // 4) * 4
    segmentation = "".join(f"{chr(65 + i)}4" for i in range(n44_padded // 4))

    import numpy as np
    import pretty_midi
    import torch
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    raw_dir = out.parent / f"{out.stem}-accomontage2"
    raw_dir.mkdir(parents=True, exist_ok=True)
    # 4/4 copy of the melody, last note held to the end of the padded phrase
    pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
    pm.time_signature_changes.append(pretty_midi.TimeSignature(4, 4, 0))
    inst = pretty_midi.Instrument(program=0, name="melody")
    notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, n.end) for n in meta["notes"]]
    notes[-1].end = n44_padded * 4 * meta["beat_sec"]
    inst.notes = notes
    pm.instruments.append(inst)
    mel44 = raw_dir / "melody_4-4.mid"
    pm.write(str(mel44))

    if meta["key"] is None:
        sys.exit("no key signature in melody MIDI; AccoMontage2 needs a tonic")
    tonic, minor = meta["key"]
    tonic_name = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"][tonic]

    sys.path.insert(0, str(REPO))
    os.chdir(REPO)
    t0 = time.time()
    import chorderator as cdt
    from chorderator.utils.pipeline import Pipeline

    orig = Pipeline._Pipeline__add_textures

    def add_textures(self, output, log=None, melo=None, do_add_textures=True, **kw):  # local shim
        return orig(self, output, log, melo, do_add_textures, **kw)

    Pipeline._Pipeline__add_textures = add_textures
    cdt.set_melody(str(mel44))
    cdt.set_meta(tonic=tonic_name, mode="min" if minor else "maj", meter="4/4")
    cdt.set_segmentation(segmentation)
    cdt.generate_save(str(raw_dir), task="chord", log=True)
    sec = time.time() - t0

    log = json.loads((raw_dir / "chord_gen_log.json").read_text())
    seg_lens = [int(x) for x in re.findall(r"\d+", segmentation)]
    if len(log) != len(seg_lens):
        sys.exit(f"AccoMontage2 returned {len(log)} phrases, segmentation {segmentation} has {len(seg_lens)}")
    bars44 = []
    for i, (phrase, n) in enumerate(zip(log, seg_lens)):
        prog = phrase["progression_full"]
        if len(prog) < n:
            sys.exit(f"AccoMontage2 phrase {i + 1} has {len(prog)} bars, its segment needs {n}")
        bars44 += prog[:n]  # a phrase may come back longer than its segment; keep later phrases aligned
    # beat-level symbols in 4/4, then regroup into source bars
    flats = (tonic, minor) in FLAT_KEYS
    beats = [label_to_symbol(bar[2 * b], flats) for bar in bars44[:n44] for b in range(4)]
    bpb = meta["beats_per_bar"]
    bars = []
    for bi in range(meta["n_bars"]):
        seq = []
        for sym in beats[bi * bpb:(bi + 1) * bpb]:
            if seq and seq[-1][0] == sym:
                seq[-1][1] += 1
            else:
                seq.append([sym, 1])
        bars.append(seq)
    chart = {"key": C.key_name(tonic, minor), "meter": f"{num}/{den}", "beats_per_bar": bpb,
             "bars": bars, "melody": melody.stem, "source": "accomontage2",
             "model": "AccoMontage2 chorderator (chord module)",
             "params": {"segmentation": segmentation, "tonic": tonic_name, "mode": "min" if minor else "maj",
                        "style": "* (default)", "seed": args.seed,
                        "rebarred": f"{num}/4 -> 4/4 ({group} bars per 4/4 bar)" if group > 1 else None,
                        "padded_bars_4_4": n44_padded - n44},
             "phrases": [{"style": p.get("style"), "progression_style": p.get("progression_style"),
                          "progression": p.get("progression")} for p in log],
             "format": "bars: list of [chord_symbol, beats] per bar; bar 1 = first bar of the MIDI"}
    problems = C.validate(chart, meta["n_bars"])
    C.save(chart, out)
    for w in C.warnings_of(chart) if not problems else []:
        print(f"WARNING: {w}", file=sys.stderr)
    print("RESULT " + json.dumps({"ok": not problems, "problems": problems, "sec": round(sec, 1),
                                  "segmentation": segmentation, "chart": C.compact(chart)}), flush=True)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
