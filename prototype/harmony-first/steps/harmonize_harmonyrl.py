"""Melody MIDI -> HarmonyRL -> normalised chart JSON (runs in envs/harmonyrl, Python 3.12).

    envs/harmonyrl/bin/python steps/harmonize_harmonyrl.py MELODY.mid OUT.json [--variant base]
        [--seed 0] [--temperature 1.0] [--device cpu]

HarmonyRL (github.com/HarmonyRL/HarmonyRL, code MIT, weights CC BY-NC-SA 3.0, gated on Hugging Face:
log in and accept the terms once) harmonizes a lead-sheet melody with a HookTheory-trained,
RL-fine-tuned chord policy. Variants: base, smooth, chromatic. Library defaults except seed.
The result is written as MusicXML (OUT.musicxml) and its chord symbols are read into the chart
shape (chords snapped to beats; a beat without a new symbol keeps the previous chord).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

os.environ.setdefault("HF_HOME", str(ROOT.parent / "melody-to-performance" / "models" / "hf-cache"))


def norm(sym):
    m = re.match(r"^([A-G])(-*)(.*)$", sym)
    if m:
        sym = m.group(1) + "b" * len(m.group(2)) + m.group(3)
    return re.sub(r"/([A-G])-", r"/\1b", sym)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("output")
    ap.add_argument("--variant", default="base", choices=["base", "smooth", "chromatic"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    from harmonyrl import HarmonyRL
    from harmonyrl.ingest.sheet import read_lead_sheet
    from harmonyrl.render.sheet import write_lead_sheet
    from music21 import converter, harmony, stream

    melody = Path(args.melody).resolve()
    out = Path(args.output).resolve()
    meta = C.melody_meta(melody)
    model = HarmonyRL.from_pretrained(f"CloudHolic/harmonyrl-{args.variant}", device=args.device)
    imp = read_lead_sheet(melody)
    overrides = {} if args.temperature is None else {"temperature": args.temperature}
    sheets = model.harmonize_sheet(imp.sheet, candidates=1, seed=args.seed, **overrides)
    xml = out.with_suffix(".musicxml")
    write_lead_sheet(sheets[0], xml)

    s = converter.parse(str(xml))
    measures = list(s.parts[0].getElementsByClass(stream.Measure))
    if len(measures) != meta["n_bars"]:
        sys.exit(f"{len(measures)} bars in HarmonyRL output, melody has {meta['n_bars']}")
    q_per_beat = 4.0 / meta["denominator"]
    bpb = meta["beats_per_bar"]
    bars, current = [], None
    for m in measures:
        changes = {}
        pad = float(m.paddingLeft or 0)
        for cs in m.getElementsByClass(harmony.ChordSymbol):
            if isinstance(cs, harmony.NoChord):
                continue
            beat = min(int(round((float(cs.offset) + pad) / q_per_beat)), bpb - 1)
            changes[beat] = norm(cs.figure)
        seq = []
        for beat in range(bpb):
            current = changes.get(beat, current)
            if seq and seq[-1][0] == current:
                seq[-1][1] += 1
            else:
                seq.append([current, 1])
        bars.append(seq)
    first = next((c for bar in bars for c, _ in bar if c), None)
    if first is None:
        sys.exit("HarmonyRL output has no chord symbols")
    bars = [[[c or first, b] for c, b in bar] for bar in bars]
    key = C.key_name(*meta["key"]) if meta["key"] else "unknown"
    ch = {"key": key, "meter": f"{meta['numerator']}/{meta['denominator']}", "beats_per_bar": bpb,
          "bars": bars, "melody": melody.stem, "source": "harmonyrl",
          "model": f"CloudHolic/harmonyrl-{args.variant}", "params": {"seed": args.seed, **overrides},
          "import_warnings": list(imp.warnings)}
    problems = C.validate(ch, meta["n_bars"])
    C.save(ch, out)
    print("RESULT " + json.dumps({"ok": not problems, "problems": problems, "chart": C.compact(ch),
                                  "warnings": list(imp.warnings)}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
