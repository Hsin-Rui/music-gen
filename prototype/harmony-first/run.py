"""Melody MIDI -> 3 harmonizers -> chart -> 3 accompaniment models x 8 samples -> rank -> plain / PianoFlow / Pianist.

    uv run run.py ../melody-to-performance/examples/<name>.mid [--samples 8] [--seed 0]
        [--device cpu|mps] [--amt-device cpu|mps] [--soundfont PATH]
        [--sources llm,melodyt5,accomontage2] [--models amt,accomontage,polyffusion] [--resume]

Output (output/<name>/):
  harmony/<source>.{json,mid,wav}       chart + melody with block chords
  <source>/<model>/candidates/cand-<k>.mid + scores.json   8 scored accompaniment samples
  <source>/<model>/accompaniment.mid    the chosen sample
  <source>/<model>/{plain,pianoflow,pianist}.{mid,wav}
  run-notes.md / run-notes.json, logs/*.log, input.{mid,wav}
Every model runs in its own env via subprocess (prototype 01's runner). A failing harmonizer or
model marks its cells missing with the reason; the exit code is non-zero only if nothing was produced.
--resume reuses charts and complete candidate sets already on disk.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "steps"))
import chart as C  # noqa: E402
import metrics as M  # noqa: E402
from paths import (DEFAULT_SOUNDFONT, LLM_CHARTS, MODELS, P01_STEPS, PY, RENDERERS, SOURCES, STEPS,  # noqa: E402
                   VERSIONS, compare, excerpt, run, wav_stats)

SKIPPED = 3  # harmonizer exit code for "not applicable to this melody"


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


def to_wav(mid, wav, soundfont, log):
    w = run([P01_STEPS / "to_wav.sh", mid, wav, soundfont], log)
    if w["ok"] and Path(wav).exists():
        return wav_stats(wav), None
    return None, w["error"] or "no WAV written"


def harmonize(source, inp, meta, hdir, logs, args):
    """-> record dict; writes hdir/<source>.json on success."""
    out = hdir / f"{source}.json"
    rec = {"source": source}
    if args.resume and out.exists() and not C.validate(C.load(out), meta["n_bars"]):
        rec.update(ok=True, reused=True, sec=0)
    elif source == "llm":
        src = LLM_CHARTS / f"{inp.stem}.json"
        if not src.exists():
            return {**rec, "ok": False, "reason": f"no LLM chart at {rel(src)}"}
        shutil.copy(src, out)  # used as given, never edited
        rec.update(ok=True, sec=0, given=rel(src))
    else:
        script = {"melodyt5": "harmonize_melodyt5.py", "accomontage2": "harmonize_accomontage2.py"}[source]
        out.unlink(missing_ok=True)
        r = run([PY[source], STEPS / script, inp, out, "--seed", args.seed], logs / f"harmony-{source}.log")
        rec.update(sec=r["sec"], peak_rss_mb=r["peak_rss_mb"], result=r["result"], warnings=r["warnings"])
        if r["result"] and r["result"].get("skipped"):
            return {**rec, "ok": False, "skipped": True, "reason": r["result"]["why"]}
        if not r["ok"] or not out.exists():
            return {**rec, "ok": False, "reason": f"{SOURCES[source]} failed", "error": r["error"]}
        rec["ok"] = True
    chart = C.load(out)
    problems = C.validate(chart, meta["n_bars"])
    if problems:  # CHART_FORMAT: invalid chart -> source failed
        return {**rec, "ok": False, "reason": "invalid chart: " + "; ".join(problems[:4])}
    rec["chart"] = C.compact(chart)
    rec["chart_warnings"] = C.warnings_of(chart)
    mid = hdir / f"{source}.mid"
    C.write_blocks(chart, inp, mid)
    rec["wav"], rec["wav_error"] = to_wav(mid, hdir / f"{source}.wav", args.soundfont, logs / f"harmony-{source}-wav.log")
    return rec


def accompany(source, model, inp, chart_path, cdir, logs, args, prev=None):
    env, script, label = MODELS[model]
    cand_dir = cdir / "candidates"
    rec = {"source": source, "model": model}
    have = sorted(cand_dir.glob("cand-*.mid")) if cand_dir.exists() else []
    if args.resume and len(have) == args.samples:
        rec.update(gen_ok=True, reused=True, sec=0, peak_rss_mb=0)
        # keep the generation record (time, RSS, sample info, warnings) of the run that made the samples
        for k in ("sec", "peak_rss_mb", "result", "warnings"):
            if prev and prev.get(k) is not None:
                rec[k] = prev[k]
    else:
        if cand_dir.exists():
            shutil.rmtree(cand_dir)
        device = args.amt_device if model == "amt" else args.device
        print(f"  [{source}/{model}] {label}: {args.samples} samples on {device} ...", flush=True)
        r = run([PY[env], STEPS / script, inp, chart_path, cand_dir, "--samples", args.samples,
                 "--seed", args.seed, "--device", device], logs / f"{source}-{model}.log")
        rec.update(sec=r["sec"], peak_rss_mb=r["peak_rss_mb"], result=r["result"], warnings=r["warnings"])
        have = sorted(cand_dir.glob("cand-*.mid")) if cand_dir.exists() else []
        if not r["ok"] or not have:
            rec.update(gen_ok=False, reason=f"{label} failed", error=r["error"])
            return rec
        rec["gen_ok"] = True
    chart = C.load(chart_path)
    cands = []
    for p in sorted(have, key=lambda p: int(p.stem.split("-")[1])):
        try:
            cands.append({"k": int(p.stem.split("-")[1]), "file": p.name, **M.compute(inp, chart, p)})
        except Exception as e:  # a broken sample is reported, not fatal
            cands.append({"k": int(p.stem.split("-")[1]), "file": p.name, "notes": 0, "error": str(e)})
    best = M.rank(cands, min_notes=C.melody_meta(inp)["n_bars"])
    rec["candidates"] = cands
    (cand_dir / "scores.json").write_text(json.dumps({"best": best, "candidates": cands}, indent=1))
    if best is None:
        rec.update(ok=False, reason="all samples empty")
        return rec
    rec["chosen"] = cands[best]["k"]
    acc = cdir / "accompaniment.mid"
    shutil.copy(cand_dir / cands[best]["file"], acc)

    versions = {}
    plain = cdir / "plain.mid"
    m = run([sys.executable, P01_STEPS / "merge_piano.py", inp, acc, plain], logs / f"{source}-{model}-merge.log")
    rec["merge"] = m["result"]
    if not m["ok"]:
        rec.update(ok=False, reason="merge failed", error=m["error"])
        return rec
    rec["ok"] = True
    versions["plain"] = {"ok": True}
    for version, (renv, rscript, rlabel) in RENDERERS.items():
        print(f"  [{source}/{model}] {rlabel} ...", flush=True)
        mid = cdir / f"{version}.mid"
        rr = run([PY[renv], P01_STEPS / rscript, plain, mid, "--device", args.device, "--seed", args.seed],
                 logs / f"{source}-{model}-{version}.log")
        if rr["ok"] and mid.exists():
            v = {"ok": True, "sec": rr["sec"], "peak_rss_mb": rr["peak_rss_mb"], "warnings": rr["warnings"]}
            try:
                v["fidelity"] = compare(plain, mid)
            except Exception as e:
                v["fidelity_error"] = str(e)
            versions[version] = v
        else:
            versions[version] = {"ok": False, "reason": f"{rlabel} failed", "error": rr["error"] or "no MIDI"}
    for version, v in versions.items():
        if v.get("ok"):
            v["wav"], v["wav_error"] = to_wav(cdir / f"{version}.mid", cdir / f"{version}.wav", args.soundfont,
                                              logs / f"{source}-{model}-{version}-wav.log")
    rec["versions"] = versions
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu", help="torch device for the models (cpu|mps)")
    ap.add_argument("--amt-device", default=None, help="device for AMT only (default: --device)")
    ap.add_argument("--soundfont", default=os.environ.get("SOUNDFONT", DEFAULT_SOUNDFONT))
    ap.add_argument("--sources", default=",".join(SOURCES))
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    args.amt_device = args.amt_device or args.device

    inp = Path(args.input).resolve()
    name = inp.stem
    out = Path(args.out).resolve() if args.out else ROOT / "output" / name
    logs, hdir = out / "logs", out / "harmony"
    hdir.mkdir(parents=True, exist_ok=True)
    meta = C.melody_meta(inp)
    started = dt.datetime.now()
    shutil.copy(inp, out / "input.mid")
    if not (out / "input.wav").exists():
        to_wav(out / "input.mid", out / "input.wav", args.soundfont, logs / "input-wav.log")

    prev_notes = {}
    if args.resume and (out / "run-notes.json").exists():
        try:
            prev_notes = json.loads((out / "run-notes.json").read_text()).get("cells", {})
        except json.JSONDecodeError:
            pass
    sources = [s for s in args.sources.split(",") if s]
    models = [m for m in args.models.split(",") if m]
    notes = {"melody": name, "input": rel(inp), "started": f"{started:%Y-%m-%d %H:%M}",
             "args": {k: v for k, v in vars(args).items() if k != "input"},
             "meta": {k: v for k, v in meta.items() if k != "notes"}, "harmony": {}, "cells": {}}

    for source in sources:
        print(f"[{name}] harmony: {SOURCES[source]} ...", flush=True)
        h = harmonize(source, inp, meta, hdir, logs, args)
        notes["harmony"][source] = h
        print(f"  -> {'ok: ' + h['chart'] if h['ok'] else 'missing: ' + h['reason']}", flush=True)

    for source in sources:
        h = notes["harmony"][source]
        for model in models:
            cdir = out / source / model
            if not h["ok"]:
                notes["cells"].setdefault(source, {})[model] = {
                    "ok": False, "reason": f"no chart from {SOURCES[source]} ({h['reason']})"}
                continue
            cdir.mkdir(parents=True, exist_ok=True)
            for old in cdir.glob("*.*"):  # never report a stale result
                old.unlink()
            rec = accompany(source, model, inp, hdir / f"{source}.json", cdir, logs, args,
                            prev=prev_notes.get(source, {}).get(model))
            notes["cells"].setdefault(source, {})[model] = rec
            if not rec.get("ok"):
                print(f"  -> missing: {rec.get('reason')}: {excerpt(rec.get('error'), 3)}", flush=True)
            # write notes after every cell so a long run can be inspected midway
            write_notes(out, notes, args)

    notes["finished"] = f"{dt.datetime.now():%Y-%m-%d %H:%M}"
    n_cells, n_wav = write_notes(out, notes, args)
    print(f"\n{n_cells} cells produced, {n_wav} WAVs; run notes: {out / 'run-notes.md'}")
    sys.exit(0 if n_cells > 0 or any(h["ok"] for h in notes["harmony"].values()) else 1)


def fmt(v, nd=3):
    return "–" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def write_notes(out, notes, args):
    name = notes["melody"]
    meta = notes["meta"]
    L = [f"# Run notes: {name}", "",
         f"- input: `{notes['input']}` ({meta['numerator']}/{meta['denominator']}, {meta['n_bars']} bars, "
         f"{meta['bpm']:.0f} bpm)",
         f"- started: {notes['started']}, finished: {notes.get('finished', '(running)')}",
         f"- samples per cell: {args.samples}, seeds {args.seed}..{args.seed + args.samples - 1}; device: "
         f"`{args.device}` (AMT: `{args.amt_device}`); soundfont: `{args.soundfont}`",
         "- parameters: library defaults except sample count and seeds (AccoMontage: phrase-selection "
         "randomness 0.1 from its demo notebook, needed for 8 different samples)", "",
         "## Harmony", "", "| source | status | chart (bars separated by \\|) | time (s) | WAV (s / dBFS) |",
         "|---|---|---|---|---|"]
    for s, h in notes["harmony"].items():
        if h["ok"]:
            w = h.get("wav")
            wtxt = f"{w['duration_sec']} / {w['rms_dbfs']}" + ("" if w["audible"] else " SILENT?") if w else "missing"
            L.append(f"| {SOURCES[s]} | ok{' (chart reused)' if h.get('reused') else ''} | {h['chart'].replace('|', chr(92) + '|')} | "
                     f"{h.get('sec', 0)} | {wtxt} |")
        else:
            L.append(f"| {SOURCES[s]} | {'skipped' if h.get('skipped') else 'missing'} | {h['reason']} | "
                     f"{h.get('sec', '–')} | – |")
    for s, h in notes["harmony"].items():
        for w in (h.get("chart_warnings") or []) + (h.get("warnings") or []):
            L.append(f"- {SOURCES[s]}: {w}")
        if h.get("error"):
            L += [f"- {SOURCES[s]} error:", "  ```", *["  " + x for x in excerpt(h["error"]).splitlines()], "  ```"]
    L.append("")

    L += ["## Cells", "",
          "| harmony | model | status | chosen | score | plain / PianoFlow / Pianist WAV (s) | gen time (s) | peak RSS (MB) |",
          "|---|---|---|---|---|---|---|---|"]
    n_cells = n_wav = 0
    missing = []
    for s, row in notes["cells"].items():
        for m, c in row.items():
            label = MODELS[m][2]
            if not c.get("ok"):
                L.append(f"| {SOURCES[s]} | {label} | missing | – | – | – | {c.get('sec', '–')} | {c.get('peak_rss_mb', '–')} |")
                missing.append((s, m, c))
                continue
            n_cells += 1
            best = next(x for x in c["candidates"] if x["k"] == c["chosen"])
            wavs = []
            for v in VERSIONS:
                vv = c["versions"].get(v, {})
                w = vv.get("wav")
                if w:
                    n_wav += 1
                    wavs.append(f"{w['duration_sec']}" + ("" if w["audible"] else " SILENT?"))
                else:
                    wavs.append("missing")
                    missing.append((s, f"{m}/{v}", vv if not vv.get("ok") else
                                    {"reason": "FluidSynth failed", "error": vv.get("wav_error")}))
            L.append(f"| {SOURCES[s]} | {label} | ok{' (samples reused)' if c.get('reused') else ''} | "
                     f"cand-{c['chosen']} | {fmt(best['score'])} | {' / '.join(wavs)} | {c.get('sec', 0)} | "
                     f"{c.get('peak_rss_mb', 0)} |")
    L.append("")
    L += ["## Missing", ""]
    if missing:
        for s, m, c in missing:
            L.append(f"- **{SOURCES[s]} / {m}**: {c.get('reason', 'failed')}")
            if c.get("error"):
                L += ["  ```", *["  " + x for x in excerpt(c["error"]).splitlines()], "  ```"]
    else:
        L.append("None.")
    L.append("")

    L += ["## Candidates and ranking", "",
          "Metrics (`steps/metrics.py`): CTnCTR (accompaniment vs chart, higher better), PCS (melody vs "
          "accompaniment consonance, higher better), OOK (out-of-key share, lower better), dissonant overlap "
          "(m2/tritone/M7 share of melody–accompaniment overlap time, lower better). "
          "copy (share of accompaniment notes shadowing the melody at a near-constant interval, lower better). "
          "score = z(CTnCTR) − z(OOK) − z(dissonant overlap) − z(copy), z within the cell's ranked samples; "
          "PCS is reported, not scored. Samples with fewer notes than bars, or copy ≥ 0.5, are not ranked "
          "(score –) unless none pass. ★ = chosen.", ""]
    for s, row in notes["cells"].items():
        for m, c in row.items():
            if not c.get("candidates"):
                continue
            L += [f"### {SOURCES[s]} × {MODELS[m][2]}", "",
                  "| sample | seed | notes | CTnCTR | PCS (not scored) | OOK | dissonant overlap | copy | score |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for x in c["candidates"]:
                seed = args.seed + x["k"]
                star = " ★" if x["k"] == c.get("chosen") else ""
                L.append(f"| cand-{x['k']}{star} | {seed} | {x.get('notes')} | {fmt(x.get('ctnctr'))} | "
                         f"{fmt(x.get('pcs'))} | {fmt(x.get('ook'))} | {fmt(x.get('dissonant_overlap'))} | {fmt(x.get('copy'))} | "
                         f"{fmt(x.get('score'))} |")
            for w in c.get("warnings") or []:
                L.append(f"\n- warning: {w}")
            for v, vv in (c.get("versions") or {}).items():
                f = vv.get("fidelity")
                if f:
                    L.append(f"\n- {v}: kept {f['kept']}/{f['score_notes']} notes, changed {f['changed']}, "
                             f"dropped {f['dropped']}, added {f['added']}"
                             f"{' (same pitches, only order differs)' if f['pitch_multiset_equal'] and f['kept'] < f['score_notes'] else ''}")
            L.append("")
    (out / "run-notes.md").write_text("\n".join(L))
    (out / "run-notes.json").write_text(json.dumps(notes, indent=1, default=str, ensure_ascii=False))
    return n_cells, n_wav


if __name__ == "__main__":
    main()
