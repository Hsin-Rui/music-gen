"""Round 3: re-score the saved round-2 candidates with the gate-then-rank selector; plain playback only.

    uv run round3.py [--melodies ode_to_joy,greensleeves] [--soundfont PATH]

Scope (docs/plan-harmony-first-round3.md): melodies ode_to_joy, greensleeves x chart sources llm (Claude),
gemini x models amt, accomontage, claude, gemini = 16 cells. Nothing is generated: AMT and AccoMontage
select among their saved output/<m>/<s>/<model>/candidates/cand-*.mid; Claude and Gemini cells have one
candidate, which is scored and shown but not "selected". Round-2 files are only read.

Output (output/round3/):
  <m>/<s>/<model>/{accompaniment.mid, plain.mid, plain.wav, scores.json}
  summary.json  (also copied to reports/round3-scores.json), logs/*.log
Each cell prints `new k / old k / passers n/N`. Exit code is non-zero only if no cell was produced.
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
from paths import DEFAULT_SOUNDFONT, MODELS, OUTPUT, P01_STEPS, SOURCES, run, wav_stats  # noqa: E402

MELODIES = ["ode_to_joy", "greensleeves"]
R3_SOURCES = ["llm", "gemini"]
R3_MODELS = ["amt", "accomontage", "claude", "gemini"]
SELECTABLE = {"amt", "accomontage"}
REPORT_COPY = ROOT / "reports" / "round3-scores.json"


def to_wav(mid, wav, soundfont, log):
    w = run([P01_STEPS / "to_wav.sh", mid, wav, soundfont], log)
    if w["ok"] and Path(wav).exists():
        return wav_stats(wav), None
    return None, w["error"] or "no WAV written"


def old_pick(cand_dir):
    """Round-2 pick: scores.json `best` is an index into its `candidates` list -> that entry's k."""
    p = cand_dir / "scores.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    best = d.get("best")
    if best is None:
        return None
    return d["candidates"][best]["k"]


def score_candidates(melody_path, chart, files, n_bars):
    cands = []
    for p in files:
        k = int(p.stem.split("-")[1])
        try:
            rec = {"k": k, "file": p.name, **M.compute_r3(melody_path, chart, p)}
        except Exception as e:  # a broken sample is recorded, never fatal
            rec = {"k": k, "file": p.name, "notes": 0, "error": f"{type(e).__name__}: {e}"}
        rec["gates"] = M.gates_r3(rec, n_bars)
        cands.append(rec)
    return cands


def process_cell(melody, source, model, src_root, out_root, soundfont=None, logs=None, render=True):
    """Score + select one cell. Returns its record (also written to <out>/scores.json when not missing)."""
    rec = {"melody": melody, "source": source, "model": model, "selectable": model in SELECTABLE}
    mdir = src_root / melody
    cand_dir = mdir / source / model / "candidates"
    melody_path = mdir / "input.mid"
    chart_path = mdir / "harmony" / f"{source}.json"
    files = sorted(cand_dir.glob("cand-*.mid"), key=lambda p: int(p.stem.split("-")[1])) if cand_dir.is_dir() else []
    if not files:
        return {**rec, "missing": True, "reason": f"沒有第二輪候選（{cand_dir.relative_to(src_root)} 不存在或是空的）"}
    if not melody_path.exists() or not chart_path.exists():
        return {**rec, "missing": True, "reason": "缺少旋律或和弦檔"}
    chart = C.load(chart_path)
    n_bars = C.melody_meta(melody_path)["n_bars"]
    cands = score_candidates(melody_path, chart, files, n_bars)
    sel = M.select_r3(cands, selectable=rec["selectable"])
    old = old_pick(cand_dir)
    rec.update(missing=False, n=len(cands), n_bars=n_bars, chosen=sel["chosen"], old_chosen=old,
               same_as_old=(sel["chosen"] == old) if rec["selectable"] else None,
               fallback=sel["fallback"], passers=sel["passers"], selected=sel["selected"], candidates=cands)
    if sel["chosen"] is None:
        return {**rec, "missing": True, "reason": "每一份候選都是空的"}
    cdir = out_root / melody / source / model
    cdir.mkdir(parents=True, exist_ok=True)
    pick = next(c for c in cands if c["k"] == sel["chosen"])
    shutil.copy(cand_dir / pick["file"], cdir / "accompaniment.mid")
    if render:
        tag = f"{melody}-{source}-{model}"
        m = run([sys.executable, P01_STEPS / "merge_piano.py", melody_path, cdir / "accompaniment.mid",
                 cdir / "plain.mid"], logs / f"{tag}-merge.log")
        if not m["ok"]:
            rec.update(wav=None, wav_error="merge failed: " + (m["error"] or ""))
        else:
            rec["wav"], rec["wav_error"] = to_wav(cdir / "plain.mid", cdir / "plain.wav", soundfont,
                                                  logs / f"{tag}-wav.log")
    (cdir / "scores.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    return rec


def run_cells(melodies, src_root, out_root, soundfont=None, render=True):
    logs = out_root / "logs"
    cells = []
    for melody in melodies:
        for source in R3_SOURCES:
            for model in R3_MODELS:
                rec = process_cell(melody, source, model, src_root, out_root, soundfont, logs, render)
                cells.append(rec)
                tag = f"[{melody}/{source}/{model}]"
                if rec["missing"]:
                    print(f"{tag} missing: {rec['reason']}", flush=True)
                    continue
                old = "–" if rec["old_chosen"] is None else rec["old_chosen"]
                extra = (" (fallback)" if rec["fallback"] else "") + ("" if rec["selectable"] else " (not selected)")
                w = rec.get("wav")
                wtxt = "" if not render else (f" wav {w['duration_sec']}s" + ("" if w["audible"] else " SILENT?")
                                              if w else f" WAV FAILED: {rec.get('wav_error')}")
                print(f"{tag} new {rec['chosen']} / old {old} / passers {rec['passers']}/{rec['n']}{extra}{wtxt}",
                      flush=True)
    return cells


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--soundfont", default=os.environ.get("SOUNDFONT", DEFAULT_SOUNDFONT))
    ap.add_argument("--melodies", default=",".join(MELODIES))
    args = ap.parse_args()
    melodies = [m for m in args.melodies.split(",") if m]
    out_root = OUTPUT / "round3"
    out_root.mkdir(parents=True, exist_ok=True)
    cells = run_cells(melodies, OUTPUT, out_root, args.soundfont)
    summary = {"created": f"{dt.datetime.now():%Y-%m-%d %H:%M}", "plan": "docs/plan-harmony-first-round3.md",
               "melodies": melodies, "sources": {s: SOURCES[s] for s in R3_SOURCES},
               "models": {m: MODELS[m][2] for m in R3_MODELS}, "gates": M.R3_GATES, "axes": M.R3_AXES,
               "thresholds": {"empty_beat_max": M.EMPTY_BEAT_MAX, "copy_max": M.COPY_MAX, "doc_max": M.DOC_MAX,
                              "chord_match_min": M.CHORD_MATCH_MIN, "ook_max": M.OOK_MAX,
                              "hand_notes": M.HAND_NOTES, "hand_span": M.HAND_SPAN, "onset_tol": M.ONSET_TOL},
               "cells": cells}
    text = json.dumps(summary, indent=1, ensure_ascii=False)
    (out_root / "summary.json").write_text(text)
    REPORT_COPY.parent.mkdir(parents=True, exist_ok=True)
    REPORT_COPY.write_text(text)
    produced = sum(1 for c in cells if not c["missing"])
    print(f"\n{produced}/{len(cells)} cells produced; {out_root / 'summary.json'} -> {REPORT_COPY.relative_to(ROOT)}")
    sys.exit(0 if produced else 1)


if __name__ == "__main__":
    main()
