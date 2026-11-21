"""Melody + chart -> N Polyffusion accompaniments (runs in envs/polyffusion).  UNTESTED end to end.

    envs/polyffusion/bin/python steps/accomp_polyffusion.py MELODY.mid CHART.json OUTDIR
        [--samples 8] [--seed 0] [--device cpu]

Calls upstream polyffusion/inference_sdf.py once per sample, as its README shows for
"accompaniment generation given melody, conditioned on chord progressions of another midi":
    --inpaint_from_midi=<melody> --inpaint_type=below --from_midi=<melody + block chords> --seed=<k>
(the build plan said --inpaint_type=above; upstream code and README define 'below' as
"inpaint accompaniment for melody", so 'below' is used). Upstream re-detects chords from the
block-chord MIDI with its own chord extractor. Polyffusion works on 4/4 8-bar segments at a fixed
120 bpm grid; 2/4 and 3/4 melodies are re-barred into 4-beat bars, and the output is rescaled
from upstream's 1/8 s per 16th to the melody's tempo and trimmed to the chart's end.

Needs the trained chord-conditioned checkpoint (sdf_chd8bar) under
models/polyffusion/result/**/chkpts/weights*.pt (+ params.yaml two levels up) and the pretrained
chord encoder at models/polyffusion/polyffusion/pretrained/chd8bar/weights.pt -- both only on the
authors' SharePoint, which refused access when this prototype was built (see README).
POLYFFUSION_CKPT=/path/to/weights.pt overrides the checkpoint search.
Writes OUTDIR/cand-<k>.mid (accompaniment only).
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "polyffusion"
PKG = REPO / "polyffusion"
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402


def find_checkpoint():
    env = os.environ.get("POLYFFUSION_CKPT")
    if env:
        return Path(env) if Path(env).exists() else None
    hits = sorted(glob.glob(str(REPO / "result" / "**" / "chkpts" / "weights*.pt"), recursive=True))
    chd = [h for h in hits if "chd" in h] or hits
    return Path(chd[0]) if chd else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("chart")
    ap.add_argument("outdir")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu", help="upstream picks cuda if available, else cpu")
    ap.add_argument("--max-bars", type=int, default=None)
    args = ap.parse_args()
    out = Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    ckpt = find_checkpoint()
    enc = PKG / "pretrained" / "chd8bar" / "weights.pt"
    missing = []
    if ckpt is None:
        missing.append("trained checkpoint (models/polyffusion/result/**/chkpts/weights*.pt)")
    if not enc.exists():
        missing.append(f"pretrained chord encoder ({enc.relative_to(ROOT)})")
    if missing:
        sys.exit("Polyffusion weights not available: " + "; ".join(missing)
                 + ". Upstream hosts them on SharePoint only, and the links refused access "
                   "('Sorry, you cannot access this document') when this prototype was built.")

    import pretty_midi
    chart = C.load(args.chart)
    meta = C.melody_meta(args.melody)
    beat = meta["beat_sec"]
    n_beats = len(C.per_beat(chart))
    n44 = -(-n_beats // 4)
    if args.max_bars:
        n44 = min(n44, args.max_bars)
    end_sec = min(n_beats, n44 * 4) * beat

    # 4/4 re-barred inputs at the melody's own tempo (upstream reads downbeats from the MIDI)
    work = out / "_inputs"
    work.mkdir(exist_ok=True)
    mel = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
    mel.time_signature_changes.append(pretty_midi.TimeSignature(4, 4, 0))
    mt = pretty_midi.Instrument(program=0, name="melody")
    mt.notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, n.end) for n in meta["notes"] if n.start < end_sec]
    mel.instruments.append(mt)
    mel_path = work / "melody_4-4.mid"
    mel.write(str(mel_path))
    cond = pretty_midi.PrettyMIDI(str(mel_path))
    ch = pretty_midi.Instrument(program=0, name="chords")
    ch.notes = [pretty_midi.Note(v, p, s, min(e, end_sec)) for s, e, p, v in C.block_notes(chart, beat) if s < end_sec]
    cond.instruments.append(ch)
    cond_path = work / "melody_chords_4-4.mid"
    cond.write(str(cond_path))

    (PKG / "exp").mkdir(exist_ok=True)
    scale = (beat / 4) / (1 / 8)  # upstream writes 1/8 s per 16th step
    info = {"checkpoint": str(ckpt), "inpaint_type": "below", "samples": []}
    for k in range(args.samples):
        seed = args.seed + k
        sdir = work / f"raw-{k}"
        sdir.mkdir(exist_ok=True)
        for old in sdir.glob("*.mid"):
            old.unlink()
        t0 = time.time()
        cmd = [sys.executable, "inference_sdf.py", f"--chkpt_path={ckpt}", f"--seed={seed}",
               f"--inpaint_from_midi={mel_path}", "--inpaint_type=below", f"--from_midi={cond_path}",
               f"--output_dir={sdir}"]
        r = subprocess.run(cmd, cwd=PKG, capture_output=True, text=True)
        sec = time.time() - t0
        mids = sorted(sdir.glob("*.mid"), key=lambda p: p.stat().st_mtime)
        if r.returncode != 0 or not mids:
            sys.exit(f"inference_sdf.py failed for sample {k} (exit {r.returncode}):\n"
                     + "\n".join((r.stdout + r.stderr).splitlines()[-15:]))
        raw = pretty_midi.PrettyMIDI(str(mids[-1]))
        gen = raw.instruments[1] if len(raw.instruments) > 1 else raw.instruments[0]  # [origin, inpainted]
        acc = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
        piano = pretty_midi.Instrument(program=0, name="Polyffusion")
        for n in gen.notes:
            s, e = n.start * scale, n.end * scale
            if s < end_sec - 1e-6:
                piano.notes.append(pretty_midi.Note(n.velocity, n.pitch, s, min(e, end_sec)))
        acc.instruments.append(piano)
        path = out / f"cand-{k}.mid"
        acc.write(str(path))
        info["samples"].append({"k": k, "seed": seed, "file": path.name, "notes": len(piano.notes),
                                "generate_sec": round(sec, 1)})
        print(f"sample {k}: {len(piano.notes)} notes in {sec:.1f} s", flush=True)
    if meta["beats_per_bar"] != 4:
        print(f"WARNING: {meta['beats_per_bar']}/4 melody re-barred into 4-beat bars for Polyffusion",
              file=sys.stderr)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
