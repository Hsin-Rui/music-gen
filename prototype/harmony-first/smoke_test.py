"""Smoke test: each new model on a short clip. Writes output/smoke-test.md (+ .json).

    uv run smoke_test.py [--clip ../melody-to-performance/examples/ode_to_joy.mid] [--bars 8] [--mps]

Clip = first N bars of the melody (default 8: two 4-bar phrases; upstream AccoMontage's
dp_search crashes on a single phrase, AccoMontage2 needs 4- or 8-bar phrases) and the
matching first N bars of its LLM chart. Rows: MelodyT5 and AccoMontage2 (harmonize the clip),
AccoMontage, Polyffusion and AMT + chord controls (1 accompaniment sample each from the clip chart).
Records works/fails, wall time (incl. Python start-up and model load), peak RSS of the step's
process tree, a detail line and an error excerpt on failure. CPU only unless --mps (adds MPS rows
for the models whose wrappers take a device).
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
import chart as C  # noqa: E402
from paths import EXAMPLES, LLM_CHARTS, PY, STEPS, excerpt, run  # noqa: E402


def make_clip(src, dst, bars):
    meta = C.melody_meta(src)
    end = bars * meta["bar_sec"]
    pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
    pm.time_signature_changes.append(pretty_midi.TimeSignature(meta["numerator"], meta["denominator"], 0))
    pm.key_signature_changes = pretty_midi.PrettyMIDI(str(src)).key_signature_changes[:1]
    inst = pretty_midi.Instrument(program=0, name="melody")
    inst.notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, min(n.end, end)) for n in meta["notes"] if n.start < end]
    pm.instruments.append(inst)
    pm.write(str(dst))
    return len(inst.notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", default=str(EXAMPLES / "ode_to_joy.mid"))
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--mps", action="store_true")
    args = ap.parse_args()

    work = ROOT / "output" / "smoke"
    work.mkdir(parents=True, exist_ok=True)
    src = Path(args.clip).resolve()
    clip = work / "clip.mid"
    n_clip = make_clip(src, clip, args.bars)
    chart = C.load(LLM_CHARTS / f"{src.stem}.json")
    chart["bars"] = chart["bars"][:args.bars]
    chart_path = work / "clip-chart.json"
    C.save(chart, chart_path)
    devices = ["cpu", "mps"] if args.mps else ["cpu"]
    rows = []

    for key, script, label in [("melodyt5", "harmonize_melodyt5.py", "MelodyT5"),
                               ("accomontage2", "harmonize_accomontage2.py", "AccoMontage2")]:
        out = work / f"{key}.json"
        out.unlink(missing_ok=True)
        print(f"{label} ...", flush=True)
        r = run([PY[key], STEPS / script, clip, out], work / f"{key}.log")
        res = r["result"] or {}
        detail = f"chart: {res.get('chart', '').replace('|', chr(92) + '|')}" if r["ok"] and res.get("chart") else ""
        rows.append({"model": label, "role": "harmonizer", "device": "cpu", **r, "detail": detail})

    for key, env, script, label, devs in [
            ("accomontage", "accomontage", "accomp_accomontage.py", "AccoMontage", ["cpu"]),
            ("polyffusion", "polyffusion", "accomp_polyffusion.py", "Polyffusion", ["cpu"]),
            ("amt", "amt", "accomp_amt.py", "AMT + chord controls (prototype-01 env)", devices)]:
        for dev in devs:
            cdir = work / f"{key}-{dev}"
            for old in cdir.glob("cand-*.mid") if cdir.exists() else []:
                old.unlink()
            print(f"{label} on {dev} ...", flush=True)
            r = run([PY[env], STEPS / script, clip, chart_path, cdir, "--samples", "1", "--device", dev],
                    work / f"{key}-{dev}.log")
            res = r["result"] or {}
            s = (res.get("samples") or [{}])[0]
            if r["ok"] and not (cdir / "cand-0.mid").exists():
                r["ok"], r["error"] = False, "exit 0 but no MIDI written"
            detail = (f"{s.get('notes')} accompaniment notes for {args.bars} bars; generate {s.get('generate_sec')} s"
                      f"{'; load ' + str(res.get('load_sec')) + ' s' if res.get('load_sec') is not None else ''}"
                      if r["ok"] else "")
            rows.append({"model": label, "role": "accompaniment", "device": dev, **r, "detail": detail})

    L = ["# Smoke test (prototype 02)", "",
         f"- date: {dt.datetime.now():%Y-%m-%d %H:%M}; machine: {platform.machine()} {platform.mac_ver()[0]}",
         f"- clip: first {args.bars} bars of `{src.name}` ({n_clip} melody notes) and the first {args.bars} bars "
         f"of its LLM chart ({C.compact(chart)})",
         "- time = wall clock of the whole step incl. Python start-up and model load; peak RSS = step process tree",
         "- harmonizers produce a chart for the clip; accompaniment models produce 1 sample", "",
         "| model | role | device | result | time (s) | peak RSS (MB) | detail |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['model']} | {r['role']} | {r['device']} | {'works' if r['ok'] else 'FAILS'} | {r['sec']} | "
                 f"{r['peak_rss_mb']} | {r['detail']} |")
    fails = [r for r in rows if not r["ok"]]
    if fails:
        L += ["", "## Errors", ""]
        for r in fails:
            L += [f"**{r['model']} / {r['device']}**", "", "```", excerpt(r["error"], 10), "```", ""]
    warns = [(r["model"], w) for r in rows for w in r.get("warnings", [])]
    if warns:
        L += ["", "## Warnings", ""] + [f"- {m}: {w}" for m, w in warns]
    L.append("")
    (ROOT / "output" / "smoke-test.md").write_text("\n".join(L))
    (ROOT / "output" / "smoke-test.json").write_text(json.dumps(rows, indent=1, default=str))
    print("\n".join(L))


if __name__ == "__main__":
    main()
