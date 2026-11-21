"""Smoke test: each model on a short clip, CPU then MPS. Writes output/smoke-test.md (+ .json).

    uv run smoke_test.py [--clip examples/ode_to_joy.mid] [--seconds 8]

Records per model x device: works/fails, wall time (incl. model load), peak RSS
of the step's process tree, note fidelity (renderers) and an error excerpt on failure.
MPS runs with PYTORCH_ENABLE_MPS_FALLBACK=1.
"""
import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import pretty_midi

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "steps"))
from fidelity import compare  # noqa: E402
from midi_utils import first_melody_track  # noqa: E402
from runner import PY, STEPS, excerpt, run  # noqa: E402

DEVICES = ["cpu", "mps"]


def make_clip(src, dst, seconds):
    pm = pretty_midi.PrettyMIDI(str(src))
    mel, _ = first_melody_track(pm)
    _, tempi = pm.get_tempo_changes()
    out = pretty_midi.PrettyMIDI(initial_tempo=float(tempi[0]) if len(tempi) else 120.0)
    out.time_signature_changes = pm.time_signature_changes[:1]
    out.key_signature_changes = pm.key_signature_changes[:1]
    inst = pretty_midi.Instrument(program=0, name="melody")
    inst.notes = [n for n in mel.notes if n.start < seconds]
    out.instruments.append(inst)
    out.write(str(dst))
    return len(inst.notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", default=str(ROOT / "examples" / "ode_to_joy.mid"))
    ap.add_argument("--seconds", type=float, default=8.0)
    args = ap.parse_args()

    work = ROOT / "output" / "smoke"
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "clip.mid"
    n_clip = make_clip(args.clip, clip, args.seconds)
    rows = []

    # AMT: accompany the clip (prompt none)
    score_for_renderers = clip
    score_device = None
    for dev in DEVICES:
        acc = work / f"amt-{dev}.mid"
        print(f"AMT on {dev} ...", flush=True)
        r = run([PY["amt"], STEPS / "amt_accompany.py", clip, acc, "--prompt", "none", "--device", dev],
                work / f"amt-{dev}.log")
        res = r["result"] or {}
        rows.append({"model": "AMT (music-medium-800k)", "device": dev, **r,
                     "detail": (f"{res.get('accompaniment_notes')} accompaniment notes for "
                                f"{res.get('end_time', 0):.1f} s of melody; generate {res.get('generate_sec')} s "
                                f"({res.get('generate_sec', 0) / max(1, res.get('accompaniment_notes') or 1):.2f} s/note)"
                                if r["ok"] else "")})
        if r["ok"] and score_for_renderers == clip:
            plain = work / "plain.mid"
            m = run([sys.executable, STEPS / "merge_piano.py", clip, acc, plain], work / "merge.log")
            if m["ok"]:
                score_for_renderers, score_device = plain, dev

    for key, script, label in [("pianoflow", "render_pianoflow.py", "SyMuPe/PianoFlow-base"),
                               ("pianist", "render_pianist.py", "Pianist Transformer")]:
        for dev in DEVICES:
            mid = work / f"{key}-{dev}.mid"
            mid.unlink(missing_ok=True)
            print(f"{label} on {dev} ...", flush=True)
            r = run([PY[key], STEPS / script, score_for_renderers, mid, "--device", dev],
                    work / f"{key}-{dev}.log")
            detail = ""
            if r["ok"] and mid.exists():
                f = compare(score_for_renderers, mid)
                r["fidelity"] = f
                res = r["result"] or {}
                detail = (f"generate {res.get('generate_sec')} s; fidelity: kept {f['kept']}/{f['score_notes']}, "
                          f"changed {f['changed']}, dropped {f['dropped']}, added {f['added']}"
                          f"{' (same pitches, only order differs)' if f['pitch_multiset_equal'] and f['kept'] < f['score_notes'] else ''}")
            elif r["ok"]:
                r["ok"], r["error"] = False, "exit 0 but no MIDI written"
            rows.append({"model": label, "device": dev, **r, "detail": detail})

    L = ["# Smoke test", "",
         f"- date: {dt.datetime.now():%Y-%m-%d %H:%M}; machine: {platform.machine()} {platform.mac_ver()[0]}",
         f"- clip: first {args.seconds:.0f} s of `{Path(args.clip).name}` ({n_clip} melody notes)",
         f"- renderer input: `{score_for_renderers.relative_to(ROOT)}` "
         f"({f'AMT-{score_device} accompaniment merged with the clip' if score_for_renderers != clip else 'melody clip only (AMT failed)'})",
         "- time = wall clock of the whole step incl. Python start-up and model load; "
         "peak RSS = step process tree; MPS runs use PYTORCH_ENABLE_MPS_FALLBACK=1",
         "- AMT samples a different number of notes on each run, so compare its s/note, not total time", "",
         "| model | device | result | time (s) | peak RSS (MB) | detail |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['model']} | {r['device']} | {'works' if r['ok'] else 'FAILS'} | {r['sec']} | "
                 f"{r['peak_rss_mb']} | {r['detail']} |")
    fails = [r for r in rows if not r["ok"]]
    if fails:
        L += ["", "## Errors", ""]
        for r in fails:
            L += [f"**{r['model']} / {r['device']}**", "", "```", excerpt(r["error"], 10), "```", ""]
    warns = [(r["model"], r["device"], w) for r in rows for w in r.get("warnings", [])]
    if warns:
        L += ["", "## Warnings", ""] + [f"- {m} / {d}: {w}" for m, d, w in warns]
    L.append("")
    (ROOT / "output" / "smoke-test.md").write_text("\n".join(L))
    (ROOT / "output" / "smoke-test.json").write_text(json.dumps(rows, indent=1, default=str))
    print("\n".join(L))


if __name__ == "__main__":
    main()
