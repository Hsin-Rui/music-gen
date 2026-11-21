"""Merge melody + AMT accompaniment into one quantized piano track (plain.mid).

    uv run steps/merge_piano.py MELODY.mid ACCOMP.mid OUT.mid

- every accompaniment instrument is remapped to piano (program 0); drum notes are dropped
- accompaniment onsets/offsets are snapped to the melody's 16th-note grid
  (AMT works in 10 ms real time; the renderers expect a quantized score)
- same-pitch overlaps are trimmed so each key is struck cleanly
- output keeps the melody's tempo, time and key signature
Prints a RESULT json line with counts.
"""
import json
import sys
from pathlib import Path

import pretty_midi

sys.path.insert(0, str(Path(__file__).parent))
from midi_utils import first_melody_track  # noqa: E402


def main(melody_path, accomp_path, out_path):
    mel_pm = pretty_midi.PrettyMIDI(melody_path)
    melody, warnings = first_melody_track(mel_pm)
    acc_pm = pretty_midi.PrettyMIDI(accomp_path)

    _, tempi = mel_pm.get_tempo_changes()
    bpm = float(tempi[0]) if len(tempi) else 120.0
    ts = mel_pm.time_signature_changes[0] if mel_pm.time_signature_changes else None
    grid = 60.0 / bpm / 4  # 16th note
    q = lambda t: round(t / grid) * grid

    stats = {"melody_notes": len(melody.notes), "accomp_programs": {}, "drums_dropped": 0,
             "dup_dropped": 0}
    mel_keys = {(round(n.start, 3), n.pitch) for n in melody.notes}
    acc_notes = []
    for inst in acc_pm.instruments:
        key = "drums" if inst.is_drum else str(inst.program)
        stats["accomp_programs"][key] = stats["accomp_programs"].get(key, 0) + len(inst.notes)
        if inst.is_drum:
            stats["drums_dropped"] += len(inst.notes)
            continue
        for n in inst.notes:
            s = q(n.start)
            e = max(q(n.end), s + grid)
            if (round(s, 3), n.pitch) in mel_keys:
                stats["dup_dropped"] += 1
                continue
            acc_notes.append(pretty_midi.Note(n.velocity, n.pitch, s, e))
    # drop exact duplicates from the accompaniment itself
    seen, uniq = set(), []
    for n in acc_notes:
        k = (round(n.start, 3), n.pitch)
        if k in seen:
            stats["dup_dropped"] += 1
            continue
        seen.add(k)
        uniq.append(n)

    notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, n.end) for n in melody.notes] + uniq
    notes.sort(key=lambda n: (n.start, n.pitch))
    # trim same-pitch overlaps
    last = {}
    for n in notes:
        prev = last.get(n.pitch)
        if prev is not None and prev.end > n.start:
            prev.end = max(n.start, prev.start + 1e-3)
        last[n.pitch] = n

    out = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    if ts:
        out.time_signature_changes.append(pretty_midi.TimeSignature(ts.numerator, ts.denominator, 0))
    out.key_signature_changes.extend(mel_pm.key_signature_changes[:1])
    piano = pretty_midi.Instrument(program=0, name="piano")
    piano.notes = notes
    out.instruments.append(piano)
    out.write(out_path)
    stats["accomp_notes_kept"] = len(uniq)
    stats["total_notes"] = len(notes)
    stats["warnings"] = warnings
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    print("RESULT " + json.dumps(stats), flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
