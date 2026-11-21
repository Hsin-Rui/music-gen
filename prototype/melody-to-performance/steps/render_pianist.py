"""Score MIDI -> expressive performance MIDI with Pianist Transformer (runs in envs/pianist).

    envs/pianist/bin/python steps/render_pianist.py SCORE.mid OUT.mid [--device cpu|mps]

Mirrors upstream src/inference/inference.py (which hard-codes
data/midis/testset/score/0.mid as input): same model dir (models/sft),
dtype bfloat16, temperature=1.0, top_p=0.95, then map_midi() -> the
"editable" tempo-mapped MIDI that script/inference.sh writes. If map_midi
fails (it asserts equal note counts) the raw absolute-time performance is
written instead.
"""
import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent / "models" / "PianistTransformer"
sys.path.insert(0, str(REPO))

import torch  # noqa: E402
from miditoolkit import MidiFile  # noqa: E402

from src.model.generate import batch_performance_render, map_midi  # noqa: E402
from src.model.pianoformer import PianoT5Gemma  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("score")
    ap.add_argument("output")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    t0 = time.time()
    model = PianoT5Gemma.from_pretrained(str(REPO / "models" / "sft"), torch_dtype=torch.bfloat16)
    model = model.to(args.device).eval()
    load = time.time() - t0

    score = MidiFile(args.score)
    t0 = time.time()
    res, _ = batch_performance_render(model, [score], temperature=1.0, top_p=0.95,
                                      device=args.device)
    gen = time.time() - t0
    info = {"load_sec": round(load, 1), "generate_sec": round(gen, 1), "tempo_mapped": True}
    try:
        out = map_midi(score, res[0])
    except Exception as e:  # upstream assert on note counts
        print(f"WARNING: map_midi failed ({type(e).__name__}: {e}); writing raw performance",
              file=sys.stderr)
        out, info["tempo_mapped"] = res[0], False
    out.dump(args.output)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
