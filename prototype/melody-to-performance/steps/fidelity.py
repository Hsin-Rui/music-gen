"""Note fidelity: does a rendered performance keep the score's notes?

    uv run steps/fidelity.py SCORE.mid RENDERED.mid

Both files are reduced to an onset-ordered pitch sequence. Notes whose onsets
lie within CHORD_WINDOW seconds are treated as one chord and sorted by pitch,
so expressive chord spreading does not count as a change. The two sequences
are aligned with difflib:
  kept    = aligned identical pitches
  changed = substituted pitches (a score note replaced by a different pitch)
  dropped = score notes with no counterpart
  added   = rendered notes with no counterpart
Percentages are relative to the score's note count. An order-free count
(per-pitch multiset) is reported too: if it is identical, the sequence
differences are only re-orderings from expressive timing, not note changes.
"""
import difflib
import json
import sys
from collections import Counter
from pathlib import Path

import pretty_midi

sys.path.insert(0, str(Path(__file__).parent))
from midi_utils import all_notes  # noqa: E402

CHORD_WINDOW = 0.05  # seconds


def pitch_sequence(path):
    notes = all_notes(pretty_midi.PrettyMIDI(str(path)))
    seq, group, t0 = [], [], None
    for n in notes:
        if t0 is None or n.start - t0 > CHORD_WINDOW:
            seq.extend(sorted(group))
            group, t0 = [], n.start
        group.append(n.pitch)
    seq.extend(sorted(group))
    return seq


def compare(score_path, rendered_path):
    a, b = pitch_sequence(score_path), pitch_sequence(rendered_path)
    kept = changed = dropped = added = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        la, lb = i2 - i1, j2 - j1
        if op == "equal":
            kept += la
        elif op == "delete":
            dropped += la
        elif op == "insert":
            added += lb
        else:  # replace
            changed += min(la, lb)
            dropped += max(0, la - lb)
            added += max(0, lb - la)
    ca, cb = Counter(a), Counter(b)
    n = len(a) or 1
    return {
        "score_notes": len(a), "rendered_notes": len(b),
        "kept": kept, "changed": changed, "dropped": dropped, "added": added,
        "kept_pct": round(100 * kept / n, 1), "changed_pct": round(100 * changed / n, 1),
        "dropped_pct": round(100 * dropped / n, 1), "added_pct": round(100 * added / n, 1),
        # order-free cross-check: counts per pitch, ignoring timing/order
        "pitch_multiset_equal": ca == cb,
        "multiset_kept": sum((ca & cb).values()),
        "multiset_dropped": sum((ca - cb).values()),
        "multiset_added": sum((cb - ca).values()),
    }


def summary(r):
    return (f"{r['score_notes']} score notes → {r['rendered_notes']} rendered: "
            f"kept {r['kept']} ({r['kept_pct']}%), changed {r['changed']} ({r['changed_pct']}%), "
            f"dropped {r['dropped']} ({r['dropped_pct']}%), added {r['added']} ({r['added_pct']}%); "
            f"order-free: kept {r['multiset_kept']}, dropped {r['multiset_dropped']}, "
            f"added {r['multiset_added']}"
            f"{' (same pitches, only order differs)' if r['pitch_multiset_equal'] and r['kept'] < r['score_notes'] else ''}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    r = compare(sys.argv[1], sys.argv[2])
    print(summary(r))
    print("RESULT " + json.dumps(r))
