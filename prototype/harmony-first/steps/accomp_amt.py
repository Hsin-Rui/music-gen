"""Melody + chart -> N AMT accompaniment samples, chord-conditioned (runs in prototype 01's envs/amt).

    ../melody-to-performance/envs/amt/bin/python steps/accomp_amt.py MELODY.mid CHART.json OUTDIR
        [--samples 8] [--seed 0] [--device cpu|mps]

Reuses prototype 01's steps/amt_accompany.py (melody on MELODY_PROGRAM as `controls`,
piano-only logit mask, token conversion, AMT top_p=0.98). New here: the chart's block
chords (steps/chart.py voicing) are added as extra `controls` on CHORD_PROGRAM, so AMT
"sees" the harmony ahead of time; only AMT's own events (piano, program 0) are written.
Sample k uses torch seed SEED+k; the model is loaded once.
Writes OUTDIR/cand-<k>.mid (accompaniment only).
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P01_STEPS = ROOT.parent / "melody-to-performance" / "steps"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P01_STEPS))
import chart as C  # noqa: E402
import amt_accompany as P01  # noqa: E402  (prototype 01 wrapper: to_tokens, restrict_to_piano, ...)

CHORD_PROGRAM = 48  # String Ensemble 1: a sustained-harmony instrument, distinct from melody (1) and output (0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("chart")
    ap.add_argument("outdir")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--max-seconds", type=float, default=None, help="only the first N seconds (smoke test)")
    args = ap.parse_args()

    import torch
    from anticipation import ops
    from anticipation.config import MAX_TIME, TIME_RESOLUTION
    from anticipation.convert import events_to_midi
    from anticipation.sample import generate
    from anticipation.vocab import CONTROL_OFFSET
    from transformers import AutoModelForCausalLM

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    chart = C.load(args.chart)
    meta = C.melody_meta(args.melody)
    _, notes = P01.load_melody(args.melody)
    chords = C.block_notes(chart, meta["beat_sec"])
    if args.max_seconds:
        notes = [n for n in notes if n.start < args.max_seconds]
        chords = [c for c in chords if c[0] < args.max_seconds]
    end_time = min(max(n.end for n in notes), MAX_TIME / TIME_RESOLUTION - 1)
    mel = [(n.start, n.end, n.pitch, P01.MELODY_PROGRAM) for n in notes]
    chd = [(s, min(e, end_time), p, CHORD_PROGRAM) for s, e, p, _ in chords]
    controls = [CONTROL_OFFSET + tok for tok in ops.sort(P01.to_tokens(mel) + P01.to_tokens(chd))]
    P01.restrict_to_piano()

    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(P01.MODEL).to(args.device).eval()
    info = {"load_sec": round(time.time() - t0, 1), "chord_program": CHORD_PROGRAM,
            "melody_program": P01.MELODY_PROGRAM, "end_time": end_time, "top_p": 0.98,
            "n_chord_control_notes": len(chd), "samples": []}
    for k in range(args.samples):
        seed = args.seed + k
        torch.manual_seed(seed)
        t0 = time.time()
        events = generate(model, 0, end_time, inputs=[], controls=controls, top_p=.98)
        sec = time.time() - t0
        path = out / f"cand-{k}.mid"
        import pretty_midi
        if len(events) >= 3:
            events_to_midi(events).save(str(path))
            # keep only piano (program 0) notes; chord/melody controls are never in `events`, but be safe
            pm = pretty_midi.PrettyMIDI(str(path))
            pm.instruments = [i for i in pm.instruments if not i.is_drum and i.program == 0]
        else:  # AMT wrote nothing (upstream events_to_midi() crashes on an empty list)
            pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
            print(f"WARNING: sample {k} (seed {seed}) has no notes", file=sys.stderr)
        pm.write(str(path))
        n = sum(len(i.notes) for i in pm.instruments)
        info["samples"].append({"k": k, "seed": seed, "file": path.name, "notes": n,
                                "generate_sec": round(sec, 1)})
        print(f"sample {k}: {n} notes in {sec:.1f} s", flush=True)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
