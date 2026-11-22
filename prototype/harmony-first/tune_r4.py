"""Round 4: parameter grids for AMT, AccoMontage and Compose & Embellish on Ode to Joy x Gemini chart.

    uv run tune_r4.py [--models accomontage,compose_embellish,amt] [--only-render]

Design (docs/prototype-plan-harmony-first/tuning-design-r4.html, approved 2026-11-22):
- AMT: prompt style {sustain, short, beat} x top_p {0.95, 0.98, 1.0}
- AccoMontage: PREFILTER rhythmic density {2,3,4} x voice number {1,2,3}, plus no prefilter;
  segmentation A4A4B4A4, randomness 0.1
- Compose & Embellish: temperature {1.0, 1.2, 1.4} x top_p {0.90, 0.97, 0.99}
3 samples per setting, seeds 0..2. Settings run ONE PROCESS AT A TIME (memory: AccoMontage
peaked 3.9 GB, AMT 3.2 GB, C&E 1.9 GB in this round); a setting whose candidates already exist is skipped (resume).

Then every candidate is: dropped if blank (0 notes); merged with the melody; cut to the first
8 bars (16 s at the melody tempo) with a 1 s fade; scored with both selectors' metrics; and
de-duplicated (identical accompaniments become one clip listing every setting that made it).
Output: output/round4/<model>/<setting>/cand-k.mid, output/round4/clips/<clip>.wav,
output/round4/manifest.json (also copied to reports/round4-manifest.json, no audio).
"""
import argparse
import array
import hashlib
import json
import os
import shutil
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "steps"))
import chart as C  # noqa: E402
import metrics as M  # noqa: E402
from paths import DEFAULT_SOUNDFONT, OUTPUT, P01_STEPS, PY, STEPS, run  # noqa: E402

MELODY = "ode_to_joy"
SOURCE = "gemini"
SEEDS = 3
CLIP_BARS = 8
FADE_SEC = 1.0
OUT = OUTPUT / "round4"
REPORT_COPY = ROOT / "reports" / "round4-manifest.json"


def settings():
    s = []
    for style in ["sustain", "short", "beat"]:
        for tp in [0.95, 0.98, 1.0]:
            s.append(("amt", f"amt-{style}-p{tp}", {"prompt_style": style, "top_p": tp},
                      ["--prompt-style", style, "--top-p", tp, "--device", "mps"]))
    for d in [2, 3, 4]:
        for v in [1, 2, 3]:
            s.append(("accomontage", f"acco-d{d}-v{v}", {"density": d, "voices": v},
                      ["--prefilter", f"{d},{v}", "--segmentation", "A4A4B4A4", "--randomness", 0.1]))
    s.append(("accomontage", "acco-none", {"density": None, "voices": None},
              ["--segmentation", "A4A4B4A4", "--randomness", 0.1]))
    for t in [1.0, 1.2, 1.4]:
        for tp in [0.90, 0.97, 0.99]:
            s.append(("compose_embellish", f"ce-t{t}-p{tp}", {"temp": t, "top_p": tp},
                      ["--temp", t, "--top-p", tp, "--device", "mps"]))
    return s


SCRIPTS = {"amt": "accomp_amt.py", "accomontage": "accomp_accomontage.py",
           "compose_embellish": "accomp_compose_embellish.py"}


def notes_hash(path):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(str(path))
    ns = sorted((round(n.start, 3), round(n.end, 3), n.pitch) for i in pm.instruments for n in i.notes)
    return len(ns), hashlib.sha1(json.dumps(ns).encode()).hexdigest()[:12]


def cut_midi(src, dst, end_sec):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(str(src))
    for inst in pm.instruments:
        inst.notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, min(n.end, end_sec))
                      for n in inst.notes if n.start < end_sec - 1e-3]
        inst.control_changes = [c for c in inst.control_changes if c.time < end_sec]
    pm.write(str(dst))


def cut_fade_wav(path, end_sec, fade=FADE_SEC):
    with wave.open(str(path), "rb") as w:
        params = w.getparams()
        frames = w.readframes(min(w.getnframes(), int(end_sec * w.getframerate())))
    assert params.sampwidth == 2, "expected 16-bit WAV"
    a = array.array("h", frames)
    ch, sr = params.nchannels, params.framerate
    n = len(a) // ch
    f0 = max(0, n - int(fade * sr))
    for i in range(f0, n):
        g = (n - i) / (n - f0)
        for c in range(ch):
            a[i * ch + c] = int(a[i * ch + c] * g)
    with wave.open(str(path), "wb") as w:
        w.setparams(params)
        w.writeframes(a.tobytes())
    return round(n / sr, 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default="accomontage,compose_embellish,amt")
    ap.add_argument("--only-render", action="store_true", help="skip generation, rebuild clips + manifest")
    ap.add_argument("--soundfont", default=os.environ.get("SOUNDFONT", DEFAULT_SOUNDFONT))
    args = ap.parse_args()
    models = args.models.split(",")
    mdir = OUTPUT / MELODY
    melody = mdir / "input.mid"
    chart_path = mdir / "harmony" / f"{SOURCE}.json"
    chart = C.load(chart_path)
    meta = C.melody_meta(melody)
    end_sec = CLIP_BARS * meta["bar_sec"]
    logs = OUT / "logs"
    OUT.mkdir(parents=True, exist_ok=True)

    gen = {}
    for model, sid, params, extra in settings():
        if model not in models:
            continue
        sdir = OUT / model / sid
        have = sorted(sdir.glob("cand-*.mid")) if sdir.is_dir() else []
        if len(have) == SEEDS or args.only_render:
            print(f"[{sid}] have {len(have)} candidates, skipped", flush=True)
            continue
        if sdir.exists():
            shutil.rmtree(sdir)
        print(f"[{sid}] generating {SEEDS} ...", flush=True)
        r = run([PY[model], STEPS / SCRIPTS[model], melody, chart_path, sdir, "--samples", SEEDS, "--seed", 0, *extra],
                logs / f"{sid}.log")
        gen[sid] = {"ok": r["ok"], "sec": r["sec"], "peak_rss_mb": r["peak_rss_mb"]}
        print(f"  -> ok={r['ok']} {r['sec']} s, peak {r['peak_rss_mb']} MB", flush=True)
        if not r["ok"]:
            print("  " + (r["error"] or "")[-600:], flush=True)

    prev = json.loads((OUT / "manifest.json").read_text()) if (OUT / "manifest.json").exists() else {}
    gen_all = {**prev.get("generation", {}), **gen}
    clips, by_hash, blanks, failed = [], {}, [], []
    cdir = OUT / "clips"
    cdir.mkdir(exist_ok=True)
    n_bars = meta["n_bars"]
    for model, sid, params, _ in settings():
        sdir = OUT / model / sid
        for k in range(SEEDS):
            cand = sdir / f"cand-{k}.mid"
            src = {"model": model, "setting": sid, "params": params, "seed": k}
            if not cand.exists():
                if (sdir.is_dir() or sid in gen_all) and model in models:
                    failed.append(src)
                continue
            n, h = notes_hash(cand)
            if n == 0:
                blanks.append(src)
                continue
            key = f"{model}:{h}"
            if key in by_hash:
                by_hash[key]["also"].append(src)
                continue
            cid = f"{sid}-s{k}"
            plain = cdir / f"{cid}.full.mid"
            m = run([sys.executable, P01_STEPS / "merge_piano.py", melody, cand, plain], logs / f"{cid}-merge.log")
            if not m["ok"]:
                failed.append({**src, "error": "merge failed"})
                continue
            clip_mid = cdir / f"{cid}.mid"
            cut_midi(plain, clip_mid, end_sec)
            wav = cdir / f"{cid}.wav"
            w = run([P01_STEPS / "to_wav.sh", clip_mid, wav, args.soundfont], logs / f"{cid}-wav.log")
            if not w["ok"] or not wav.exists():
                failed.append({**src, "error": "wav failed"})
                continue
            dur = cut_fade_wav(wav, end_sec)
            old = M.compute(melody, chart, cand)
            new = M.compute_r3(melody, chart, cand)
            new["gates"] = M.gates_r3(new, n_bars)
            new["failed"] = [g for g in M.R3_GATES if new["gates"].get(g) is False]
            clip = {"id": cid, **src, "wav": f"clips/{cid}.wav", "dur": dur, "notes": n, "also": [],
                    "old_metrics": {k2: old.get(k2) for k2 in ["ctnctr", "ook", "dissonant_overlap", "copy"]},
                    "new_metrics": {k2: new.get(k2) for k2 in ["prompt_doc", "chord_match", "ook", "copy", "empty_beat_rate",
                                                                "playable", "prompt_sim", "rules", "bass_ok", "failed"]}}
            by_hash[key] = clip
            clips.append(clip)
    # within-model scores of both selectors, for comparing with the battle afterwards
    for model in {c["model"] for c in clips}:
        mc = [c for c in clips if c["model"] == model]
        olds = [{"k": i, "notes": c["notes"], **c["old_metrics"]} for i, c in enumerate(mc)]
        M.rank(olds, min_notes=n_bars)
        news = [{"k": i, "notes": c["notes"], **c["new_metrics"],
                 "gates": {g: (g not in c["new_metrics"]["failed"]) for g in M.R3_GATES}} for i, c in enumerate(mc)]
        M.select_r3(news)
        for c, o, nw in zip(mc, olds, news):
            c["old_score"] = o.get("score")
            c["new_borda"] = nw.get("borda")
            c["new_pool"] = nw.get("pool")
    man = {"melody": MELODY, "source": SOURCE, "clip_bars": CLIP_BARS, "clip_sec": round(end_sec, 2),
           "seeds": list(range(SEEDS)), "settings": [{"model": m, "setting": s, "params": p} for m, s, p, _ in settings()],
           "generation": gen_all, "clips": clips, "blank": blanks, "failed": failed}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    REPORT_COPY.parent.mkdir(exist_ok=True)
    REPORT_COPY.write_text(json.dumps(man, indent=1, ensure_ascii=False))
    per = {m: sum(1 for c in clips if c["model"] == m) for m in ["amt", "accomontage", "compose_embellish"]}
    print(f"\nclips {len(clips)} {per}; blank {len(blanks)}; duplicates "
          f"{sum(len(c['also']) for c in clips)}; failed {len(failed)}")


if __name__ == "__main__":
    main()
