"""Score MIDI -> expressive performance MIDI with SyMuPe/PianoFlow-base (runs in envs/pianoflow).

    envs/pianoflow/bin/python steps/render_pianoflow.py SCORE.mid OUT.mid [--device cpu|mps]

Uses library defaults except num_samples=1 (we keep one rendering) and a fixed seed.
Writes the sustain-applied version (perf_midi_sus) when present, else perf_midi.
"""
import argparse
import json
import time

import torch
from symupe import AutoGenerator

MODEL = "SyMuPe/PianoFlow-base"


def mps_float64_shim():
    """Local shim: TokSequence.torch() moves float64 arrays to the device before
    casting to float32, which MPS rejects. Cast float64 numpy arrays first."""
    from dataclasses import replace

    import numpy as np
    from symupe.data.tokenizers.classes import TokSequence

    orig = TokSequence.torch

    def torch_(self, device=None):
        seq = replace(self)
        for attr in ("ids", "values", "interpolated"):
            data = getattr(seq, attr)
            if isinstance(data, np.ndarray) and data.dtype == np.float64:
                setattr(seq, attr, data.astype(np.float32))
            elif isinstance(data, torch.Tensor) and data.dtype == torch.float64:
                setattr(seq, attr, data.float())
        return orig(seq, device=device)

    TokSequence.torch = torch_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("score")
    ap.add_argument("output")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.device.startswith("mps"):
        mps_float64_shim()
    t0 = time.time()
    generator =AutoGenerator.from_pretrained(MODEL, device=torch.device(args.device))
    load = time.time() - t0

    t0 = time.time()
    results = generator.perform_score(args.score, num_samples=1, seed=args.seed, show_progress=False)
    gen = time.time() - t0
    r = results[0]
    midi = r.perf_midi_sus if r.perf_midi_sus is not None else r.perf_midi
    midi.dump_midi(args.output)
    print("RESULT " + json.dumps({"load_sec": round(load, 1), "generate_sec": round(gen, 1),
                                  "sustain_applied": r.perf_midi_sus is not None}), flush=True)


if __name__ == "__main__":
    main()
