"""Melody MIDI -> AMT accompaniment (2 prompt variants) -> plain / PianoFlow / Pianist MIDI + WAV.

    uv run run.py examples/<name>.mid [--device cpu|mps] [--soundfont PATH] [--seed N]

Output: output/<name>/{noprompt,chords}/{plain,pianoflow,pianist}.{mid,wav}
        output/<name>/run-notes.md   (timings, failures, fidelity)
        output/<name>/logs/*.log     (full output of every step)
Each model runs in its own env (envs/amt, envs/pianoflow, envs/pianist) via subprocess.
Exit code is non-zero only if no version at all could be produced.
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import pretty_midi

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "steps"))
from fidelity import compare  # noqa: E402
from midi_utils import first_melody_track  # noqa: E402
from runner import DEFAULT_SOUNDFONT, PY, STEPS, excerpt, run, wav_stats  # noqa: E402

VARIANTS = {"noprompt": "none", "chords": "chords"}
RENDERERS = {
    "pianoflow": ("pianoflow", "render_pianoflow.py", "SyMuPe/PianoFlow-base"),
    "pianist": ("pianist", "render_pianist.py", "Pianist Transformer"),
}
VERSIONS = ["plain", "pianoflow", "pianist"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--device", default="cpu", help="torch device for all models (cpu|mps)")
    ap.add_argument("--soundfont", default=os.environ.get("SOUNDFONT", DEFAULT_SOUNDFONT))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="output dir (default output/<name>)")
    args = ap.parse_args()

    inp = Path(args.input).resolve()
    name = inp.stem
    out = Path(args.out).resolve() if args.out else ROOT / "output" / name
    logs = out / "logs"
    out.mkdir(parents=True, exist_ok=True)

    _, input_warnings = first_melody_track(pretty_midi.PrettyMIDI(str(inp)))
    started = dt.datetime.now()
    records = {}  # variant -> version -> dict
    amt_info = {}

    def note_step(variant, version, **kw):
        records.setdefault(variant, {}).setdefault(version, {}).update(kw)

    for variant, prompt in VARIANTS.items():
        vdir = out / variant
        vdir.mkdir(parents=True, exist_ok=True)
        for old in vdir.glob("*"):  # never report a stale file from an earlier run
            old.unlink()
        print(f"[{name}/{variant}] AMT accompaniment (prompt={prompt}, device={args.device}) ...", flush=True)
        acc = vdir / "accompaniment.mid"
        r = run([PY["amt"], STEPS / "amt_accompany.py", inp, acc, "--prompt", prompt,
                 "--device", args.device, "--seed", args.seed], logs / f"{variant}-amt.log")
        amt_info[variant] = r
        if not r["ok"]:
            for v in VERSIONS:
                note_step(variant, v, ok=False, reason="AMT accompaniment failed", error=r["error"])
            print(f"  AMT failed: {excerpt(r['error'], 3)}", flush=True)
            continue

        plain = vdir / "plain.mid"
        m = run([sys.executable, STEPS / "merge_piano.py", inp, acc, plain],
                logs / f"{variant}-merge.log")
        amt_info[variant]["merge"] = m
        if not m["ok"]:
            for v in VERSIONS:
                note_step(variant, v, ok=False, reason="merge failed", error=m["error"])
            continue
        note_step(variant, "plain", ok=True, sec=r["sec"] + m["sec"], peak_rss_mb=r["peak_rss_mb"],
                  model="AMT + merge")

        for version, (env, script, label) in RENDERERS.items():
            print(f"[{name}/{variant}] {label} ...", flush=True)
            mid = vdir / f"{version}.mid"
            rr = run([PY[env], STEPS / script, plain, mid, "--device", args.device, "--seed", args.seed],
                     logs / f"{variant}-{version}.log")
            if rr["ok"] and mid.exists():
                note_step(variant, version, ok=True, sec=rr["sec"], peak_rss_mb=rr["peak_rss_mb"],
                          model=label, result=rr["result"], warnings=rr["warnings"])
                try:
                    note_step(variant, version, fidelity=compare(plain, mid))
                except Exception as e:  # fidelity is a report, never fatal
                    note_step(variant, version, fidelity_error=str(e))
            else:
                note_step(variant, version, ok=False, reason=f"{label} failed",
                          error=rr["error"] or "no MIDI written")
                print(f"  failed: {excerpt(rr['error'], 3)}", flush=True)

        for version in VERSIONS:
            rec = records[variant][version]
            if not rec.get("ok"):
                continue
            wav = vdir / f"{version}.wav"
            w = run([STEPS / "to_wav.sh", vdir / f"{version}.mid", wav, args.soundfont],
                    logs / f"{variant}-{version}-wav.log")
            if w["ok"] and wav.exists():
                rec["wav"] = wav_stats(wav)
            else:
                rec["wav_error"] = w["error"]

    n_ok, n_wav = write_notes(out, name, inp, args, started, input_warnings, amt_info, records)
    print(f"\n{n_ok}/6 versions (MIDI) written to {out}, {n_wav}/{n_ok} with WAV"
          f"{'' if n_wav == n_ok else ' (FluidSynth failed for the rest, see run-notes)'}"
          f"\nrun notes: {out / 'run-notes.md'}")
    sys.exit(0 if n_ok > 0 else 1)


def write_notes(out, name, inp, args, started, input_warnings, amt_info, records):
    L = [f"# Run notes: {name}", "",
         f"- input: `{inp.relative_to(ROOT) if inp.is_relative_to(ROOT) else inp}`",
         f"- started: {started:%Y-%m-%d %H:%M}, finished: {dt.datetime.now():%H:%M}",
         f"- device: `{args.device}`, seed: {args.seed}, soundfont: `{args.soundfont}`",
         "- model parameters: library defaults (AMT top_p=0.98 as in its README; "
         "PianoFlow 1 sample; Pianist temperature 1.0, top_p 0.95)", ""]
    if input_warnings:
        L += ["## Warnings", ""] + [f"- {w}" for w in input_warnings] + [""]

    L += ["## Versions", "",
          "| prompt | version | MIDI | WAV (s / RMS dBFS) | time (s) | peak RSS (MB) | note fidelity vs plain |",
          "|---|---|---|---|---|---|---|"]
    missing, n_ok, n_wav = [], 0, 0
    for variant in VARIANTS:
        for version in VERSIONS:
            rec = records.get(variant, {}).get(version, {"ok": False, "reason": "not run"})
            if not rec.get("ok"):
                L.append(f"| {variant} | {version} | missing | – | – | – | – |")
                missing.append((variant, version, rec))
                continue
            n_ok += 1  # MIDI written
            wav = rec.get("wav")
            if wav:
                n_wav += 1
                wtxt = f"{wav['duration_sec']} / {wav['rms_dbfs']}" + ("" if wav["audible"] else " (SILENT?)")
            else:
                wtxt = "missing"
                missing.append((variant, f"{version}.wav", {"reason": "FluidSynth failed",
                                                             "error": rec.get("wav_error")}))
            fid = rec.get("fidelity")
            ftxt = ("(score itself)" if version == "plain" else
                    (f"kept {fid['kept']}/{fid['score_notes']}, changed {fid['changed']}, "
                     f"dropped {fid['dropped']}, added {fid['added']}"
                     f"{'; same pitches, only order differs' if fid['pitch_multiset_equal'] and fid['kept'] < fid['score_notes'] else ''}")
                    if fid else rec.get("fidelity_error", "–"))
            L.append(f"| {variant} | {version} | `{variant}/{version}.mid` | {wtxt} | {rec['sec']} | "
                     f"{rec['peak_rss_mb']} | {ftxt} |")
    L.append("")
    L.append("Time for `plain` = AMT generation (incl. model load) + merge. "
             "Fidelity: onset-ordered pitch sequence of the rendered MIDI aligned to `plain.mid` "
             "(`steps/fidelity.py`).")
    L.append("")

    L += ["## Missing versions", ""]
    if missing:
        for variant, version, rec in missing:
            L.append(f"- **{variant}/{version}**: {rec.get('reason', 'failed')}")
            if rec.get("error"):
                L += ["  ```", *["  " + ln for ln in excerpt(rec["error"]).splitlines()], "  ```"]
    else:
        L.append("None — all 6 MIDI + 6 WAV written.")
    L.append("")

    L += ["## AMT accompaniment", ""]
    for variant, r in amt_info.items():
        res = r.get("result") or {}
        L.append(f"- **{variant}**: {'ok' if r['ok'] else 'FAILED'}, {r['sec']} s, peak {r['peak_rss_mb']} MB")
        if res:
            L.append(f"  - generated {res.get('accompaniment_notes')} accompaniment notes over "
                     f"{res.get('end_time', 0):.1f} s; AMT instruments (programs): {res.get('instruments')}")
            if res.get("chords"):
                L.append(f"  - chord prompt: {res['key']} ({res['key_source']}), {res['bars']} bars "
                         f"({res['history_sec']:.1f} s): {' '.join(res['chords'])}")
        mres = (r.get("merge") or {}).get("result")
        if mres:
            L.append(f"  - merge: accompaniment programs {mres['accomp_programs']} → all piano (program 0); "
                     f"drums dropped {mres['drums_dropped']}; duplicates dropped {mres['dup_dropped']}; "
                     f"plain.mid has {mres['total_notes']} notes ({mres['melody_notes']} melody)")
        for w in r.get("warnings", []):
            L.append(f"  - warning: {w}")
    L.append("")
    (out / "run-notes.md").write_text("\n".join(L))
    (out / "run-notes.json").write_text(json.dumps({"amt": amt_info, "versions": records}, indent=1, default=str))
    return n_ok, n_wav


if __name__ == "__main__":
    main()
