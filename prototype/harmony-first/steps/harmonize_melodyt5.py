"""Melody MIDI -> MelodyT5 harmonization -> normalised chart JSON (runs in envs/melodyt5).

    envs/melodyt5/bin/python steps/harmonize_melodyt5.py MELODY.mid OUT.json [--seed 0] [--device cpu|mps]

1. MIDI -> MusicXML (music21) -> ABC with the repo's xml2abc.py, filtered like
   upstream batch_xml2abc.py (header lines stripped, L/Q/M/K kept).
2. Prompt "%%harmonization" + ABC; sampling exactly as upstream inference.py with its
   defaults (top_p 0.8, top_k 8, temperature 2.6, max_patch 128). In harmonization
   mode upstream copies the melody bar by bar and only samples the quoted chord symbols.
3. The output ABC is parsed with music21; chord symbols are snapped to the nearest
   beat and turned into the chart shape (a bar without a symbol keeps the previous chord).
If the output does not have the melody's bar count, the next seed is tried (max 3 tries).
Also writes OUT.abc (the raw model output) next to OUT.json.
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "melodyt5"
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

TOP_P, TOP_K, TEMPERATURE, MAX_PATCH = 0.8, 8, 2.6, 128  # upstream inference.py defaults
MAX_TRIES = 3


def warn(msg):
    print(f"WARNING: {msg}", file=sys.stderr, flush=True)


def midi_to_abc(midi_path, workdir):
    from music21 import converter
    s = converter.parse(str(midi_path), quantizePost=True)
    xml = Path(workdir) / "melody.musicxml"
    s.write("musicxml", str(xml))
    subprocess.run([sys.executable, str(REPO / "xml2abc" / "xml2abc.py"), "-d", "8", "-x", "-o",
                    str(workdir), str(xml)], check=True, capture_output=True)
    raw = (Path(workdir) / "melody.abc").read_text()
    # upstream batch_xml2abc.run_filter: drop metadata/voice lines and comments
    keep = []
    for line in raw.replace("\r", "").split("\n"):
        if line[:2] in ["A:", "B:", "C:", "D:", "F:", "G", "H:", "N:", "O:", "R:", "r:", "S:", "T:",
                        "V:", "W:", "X:", "Z:"] or line.startswith("%") or not line.strip():
            continue
        if "%" in line:
            line = line.split("%")[0]
        keep.append(line)
    abc = "\n".join(keep).strip()
    if abc.endswith(" |"):
        abc += "]"
    return abc


def load_model(device):
    os.chdir(REPO)  # upstream code loads 'random_model' and 'weights.pth' relative to cwd
    sys.path.insert(0, str(REPO))
    import torch
    from transformers import GPT2Config
    from config import CHAR_NUM_LAYERS, PATCH_LENGTH, PATCH_NUM_LAYERS, PATCH_SIZE
    from utils import MelodyT5, Patchilizer
    patch_config = GPT2Config(num_hidden_layers=PATCH_NUM_LAYERS, max_length=PATCH_LENGTH,
                              max_position_embeddings=PATCH_LENGTH, vocab_size=1)
    char_config = GPT2Config(num_hidden_layers=CHAR_NUM_LAYERS, max_length=PATCH_SIZE,
                             max_position_embeddings=PATCH_SIZE, vocab_size=128)
    model = MelodyT5(patch_config, char_config)
    state = torch.load(REPO / "weights.pth", map_location="cpu")["model"]
    # local shim: newer transformers no longer stores GPT-2's causal-mask buffers
    state = {k: v for k, v in state.items() if not re.search(r"\.(attn|crossattention)\.(bias|masked_bias)$", k)}
    missing, unexpected = model.load_state_dict(state, strict=False)
    real_missing = [k for k in missing if not re.search(r"\.(bias|masked_bias)$", k) or "attn" not in k]
    if real_missing or unexpected:
        raise SystemExit(f"weights mismatch: missing {real_missing[:5]}, unexpected {unexpected[:5]}")
    return model.to(device).eval(), Patchilizer()


def generate(model, patchilizer, input_abc, seed, device):
    """Mirror of upstream inference.generate_abc for one tune, no decoder prompt."""
    import torch
    task = input_abc.split("\n")[0][2:]
    patches = torch.tensor([patchilizer.encode(input_abc, add_special_patches=True)], device=device)
    decoder_patches = torch.tensor([patchilizer.encode("", add_special_patches=True)[:-1]], device=device)
    tune = ""
    with torch.no_grad():
        while decoder_patches.shape[1] < MAX_PATCH:
            predicted_patch, seed = model.generate(patches, decoder_patches, None, task=task,
                                                   top_p=TOP_P, top_k=TOP_K, temperature=TEMPERATURE,
                                                   seed=seed)
            if predicted_patch[0] == patchilizer.eos_token_id:
                break
            next_bar = patchilizer.decode([predicted_patch])
            if next_bar == "":
                break
            tune += next_bar
            predicted_patch = torch.tensor(patchilizer.bar2patch(next_bar), device=device).unsqueeze(0)
            decoder_patches = torch.cat([decoder_patches, predicted_patch.unsqueeze(0)], dim=1)
    return tune


def abc_to_chart(abc, meta):
    """Parse quoted chord symbols per measure -> chart bars (beats snapped to integers)."""
    from music21 import converter, harmony, stream
    # strip control-code lines (E:, S:, B:) that music21 does not know
    body = "\n".join(ln for ln in abc.split("\n") if ln[:2] not in ("E:", "S:", "B:"))
    s = converter.parse("X:1\n" + body, format="abc")
    part = s.parts[0] if s.parts else s
    measures = list(part.getElementsByClass(stream.Measure))
    q_per_beat = 4.0 / meta["denominator"]
    bpb = meta["beats_per_bar"]
    events = []  # (bar index, beat, symbol)
    for bi, m in enumerate(measures):
        pad = float(m.paddingLeft or 0)
        for cs in m.getElementsByClass(harmony.ChordSymbol):
            fig = cs.figure if hasattr(cs, "figure") else str(cs)
            beat = int(round((float(cs.offset) + pad) / q_per_beat))
            events.append((bi, min(beat, bpb - 1), fig))
    return measures, events


def events_to_bars(events, n_bars, bpb):
    if not events:
        return None
    bars, current = [], events[0][2]
    by_bar = {}
    for bi, beat, sym in events:
        by_bar.setdefault(bi, {})[beat] = sym  # last symbol on a beat wins
    for bi in range(n_bars):
        changes = by_bar.get(bi, {})
        seq = []
        for beat in range(bpb):
            if beat in changes:
                current = changes[beat]
            if seq and seq[-1][0] == current:
                seq[-1][1] += 1
            else:
                seq.append([current, 1])
        bars.append(seq)
    return bars


def normalise_symbol(sym):
    """music21 figures use '-' for flats ('B-'); charts use 'b'."""
    m = re.match(r"^([A-G])(-*)(.*)$", sym)
    if m:
        sym = m.group(1) + "b" * len(m.group(2)) + m.group(3)
    sym = sym.replace("/B-", "/Bb").replace("/E-", "/Eb").replace("/A-", "/Ab").replace("/D-", "/Db").replace("/G-", "/Gb")
    return sym


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("output")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    melody = Path(args.melody).resolve()
    out = Path(args.output).resolve()
    meta = C.melody_meta(melody)

    with tempfile.TemporaryDirectory() as td:
        abc = midi_to_abc(melody, td)
    input_abc = "%%harmonization\n" + abc + "\n"

    t0 = time.time()
    model, patchilizer = load_model(args.device)
    load_sec = time.time() - t0

    tries = []
    chosen = None
    t0 = time.time()
    for k in range(MAX_TRIES):
        seed = args.seed + k
        random.seed(seed)
        tune = generate(model, patchilizer, input_abc, seed, args.device)
        try:
            measures, events = abc_to_chart(tune, meta)
            n_meas = len(measures)
        except Exception as e:  # unparsable output
            tries.append({"seed": seed, "ok": False, "why": f"music21 parse failed: {e}"})
            warn(f"seed {seed}: output not parseable ({e})")
            continue
        if n_meas != meta["n_bars"]:
            tries.append({"seed": seed, "ok": False, "why": f"{n_meas} bars, melody has {meta['n_bars']}"})
            warn(f"seed {seed}: {n_meas} bars in output, melody has {meta['n_bars']}; retrying")
            continue
        events = [(b, beat, normalise_symbol(sym)) for b, beat, sym in events]
        bars = events_to_bars(events, meta["n_bars"], meta["beats_per_bar"])
        if bars is None:
            tries.append({"seed": seed, "ok": False, "why": "no chord symbols in output"})
            continue
        tries.append({"seed": seed, "ok": True, "n_symbols": len(events)})
        chosen = (seed, tune, bars, events)
        break
    gen_sec = time.time() - t0

    if chosen is None:
        out.with_suffix(".abc").write_text(tune if tries else "")
        print("RESULT " + json.dumps({"ok": False, "tries": tries}), flush=True)
        sys.exit(f"MelodyT5 gave no usable harmonization in {MAX_TRIES} tries: {tries}")
    seed, tune, bars, events = chosen
    out.with_suffix(".abc").write_text(input_abc + "\n%%output\n" + tune)
    key = C.key_name(*meta["key"]) if meta["key"] else "unknown"
    chart = {"key": key, "meter": f"{meta['numerator']}/{meta['denominator']}",
             "beats_per_bar": meta["beats_per_bar"], "bars": bars, "melody": melody.stem,
             "source": "melodyt5", "model": "sander-wood/melodyt5 weights.pth",
             "params": {"top_p": TOP_P, "top_k": TOP_K, "temperature": TEMPERATURE, "seed": seed},
             "note": "chord symbols snapped to the nearest beat; a bar without a symbol keeps the previous chord",
             "format": "bars: list of [chord_symbol, beats] per bar; bar 1 = first bar of the MIDI"}
    problems = C.validate(chart, meta["n_bars"])
    C.save(chart, out)
    for w in C.warnings_of(chart) if not problems else []:
        warn(w)
    print("RESULT " + json.dumps({"ok": not problems, "problems": problems, "tries": tries,
                                  "load_sec": round(load_sec, 1), "generate_sec": round(gen_sec, 1),
                                  "raw_symbols": [e[2] for e in events], "chart": C.compact(chart)}),
          flush=True)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
