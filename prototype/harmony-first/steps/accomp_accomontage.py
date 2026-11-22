"""Melody + chart -> N AccoMontage piano accompaniments (runs in envs/accomontage).

    envs/accomontage/bin/python steps/accomp_accomontage.py MELODY.mid CHART.json OUTDIR
        [--samples 8] [--seed 0]

Follows upstream AccoMontage_inference.ipynb (set_premises -> phrase_selection ->
re_harmonization) with these local shims:
- CPU: the model is built on CPU and checkpoints are loaded with map_location='cpu';
  torch.Tensor.cuda is made a no-op so upstream re_harmonization() runs unchanged.
- the lead sheet is built from the chart directly (upstream would re-detect chords
  from a chord track with its chord recogniser): per 16th step [root, 12-d chroma,
  bass relative to root], the same 14-d format as upstream leadsheet2matrix().
- AccoMontage's phrase pool is 4/4 (16 sixteenths per bar). 2/4 and 3/4 melodies are
  re-barred into 4-beat bars on the same beat grid (harmony stays beat-aligned, but the
  texture's metre does not match a 3/4 tune); the tail is padded to whole bars.
- segmentation: consecutive 4-bar phrases A, B, C, ... (a 2-3 bar remainder becomes its own phrase; a 1-bar remainder joins the last phrase).
- 8 different samples need randomness > 0 in phrase selection: we use RANDOMENESS=0.1, the
  value of the upstream demo notebook, and numpy seed SEED+k per sample. Other parameters
  are notebook defaults (no PREFILTER, no SPOTLIGHT).
Writes OUTDIR/cand-<k>.mid (accompaniment only, trimmed to the chart's end).
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "AccoMontage"
CKPT = REPO / "checkpoints"
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

RANDOMNESS = 0.1  # upstream notebook demo value


def segmentation_for(n_bars):
    lens = [4] * (n_bars // 4)
    r = n_bars % 4
    if r >= 2 or not lens:
        lens.append(r)
    elif r:
        lens[-1] += r
    lens = [x for x in lens if x > 0]
    return "".join(f"{chr(65 + i)}{x}" for i, x in enumerate(lens)), lens


def chord_row(c):
    import numpy as np
    chroma = np.zeros(12)
    chroma[c["pcs"]] = 1
    return np.concatenate([[c["root"]], chroma, [(c["bass"] - c["root"]) % 12]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("chart")
    ap.add_argument("outdir")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu", help="ignored (CPU only)")
    ap.add_argument("--max-bars", type=int, default=None, help="only the first N 4/4 bars (smoke test)")
    ap.add_argument("--segmentation", default=None, help="phrase labels, e.g. A4A4B4A4 (default: A4B4C4...)")
    ap.add_argument("--prefilter", default=None, help="'density,voices' degrees 0-4 (upstream PREFILTER); default off")
    ap.add_argument("--randomness", type=float, default=RANDOMNESS)
    args = ap.parse_args()
    args.melody, args.chart = str(Path(args.melody).resolve()), str(Path(args.chart).resolve())
    out = Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    import numpy as np
    import pandas as pd
    import pretty_midi
    import torch
    torch.Tensor.cuda = lambda self, *a, **k: self  # local shim: CPU only

    os.chdir(REPO)  # upstream format_converter appends 'AccoMontage/chord_recognition' to sys.path
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "AccoMontage" / "chord_recognition"))
    from AccoMontage import phrase_selection, re_harmonization
    from AccoMontage import AccoMontage as AM
    from AccoMontage import format_converter as cvt
    from AccoMontage.acc_utils import split_phrases
    from AccoMontage.models import DisentangleVAE

    chart = C.load(args.chart)
    meta = C.melody_meta(args.melody)
    bpb, beat = meta["beats_per_bar"], meta["beat_sec"]
    if meta["denominator"] != 4:
        sys.exit(f"AccoMontage wrapper expects a quarter-note beat, melody is {meta['numerator']}/{meta['denominator']}")
    labels = C.per_beat(chart)  # one chord per beat
    n_beats = len(labels)
    n44 = -(-n_beats // 4)
    if args.max_bars:
        n44 = min(n44, args.max_bars)
    segmentation, _ = segmentation_for(n44)
    if args.segmentation:
        segmentation = args.segmentation
    prefilter = tuple(int(x) for x in args.prefilter.split(",")) if args.prefilter else None
    T = n44 * 16
    notes_info = {"rebarred": bpb != 4, "bars_4_4": n44, "segmentation": segmentation,
                  "pad_beats": n44 * 4 - n_beats if not args.max_bars else 0}

    # ---- lead sheet straight from melody + chart (upstream 142-d format)
    quaver = np.arange(T) * beat / 4
    mel_track = pretty_midi.Instrument(program=0)
    mel_track.notes = [n for n in meta["notes"] if n.start < T * beat / 4 - 1e-6]
    melody_roll = cvt.ec2vae_mel_format(cvt.midi2matrix(mel_track, quaver))
    chord_roll = np.zeros((T, 14))
    for step in range(T):
        b = step // 4
        if b < n_beats:
            chord_roll[step] = chord_row(labels[b])
        else:  # padding: 'no chord', as upstream load_lead_sheet pads
            chord_roll[step, 0] = -1
            chord_roll[step, -1] = -1
    chord_table = np.stack([cvt.expand_chord(ch) for ch in chord_roll[::4]], axis=0)
    lead_sheet = np.concatenate((melody_roll, chord_roll[:, 1:-1]), axis=-1)
    query_phrases = split_phrases(segmentation)

    # ---- premises (upstream set_premises, on CPU)
    t0 = time.time()
    data = np.load(CKPT / "phrase_data.npz", allow_pickle=True)
    acc_pool = {}
    for length in range(1, 17):
        acc_pool[length] = AM.find_by_length(data["melody"], data["acc"], data["chord"],
                                             data["velocity"], data["cc"], length)
    del data
    texture_filter = AM.get_texture_filter(acc_pool)
    edge_weights = np.load(CKPT / "edge_weights.npz", allow_pickle=True)
    model = DisentangleVAE.init_model(torch.device("cpu"))
    model.load_state_dict(torch.load(CKPT / "model_master_final.pt", map_location="cpu"))
    model.eval()
    reference_check = pd.read_excel(CKPT / "pop909_quadraple_meters_index.xlsx")
    load_sec = time.time() - t0

    end_sec = n_beats * beat if not args.max_bars else T * beat / 4
    info = {"load_sec": round(load_sec, 1), "randomness": args.randomness, "prefilter": prefilter, **notes_info, "samples": []}
    for k in range(args.samples):
        seed = args.seed + k
        np.random.seed(seed)
        random.seed(seed)
        torch.manual_seed(seed)
        t0 = time.time()
        with torch.no_grad():
            selection = phrase_selection(lead_sheet, query_phrases, reference_check, acc_pool,
                                         edge_weights, texture_filter, prefilter, None, args.randomness)
            midi = re_harmonization(lead_sheet, chord_table, query_phrases, *selection, model,
                                    acc_pool, meta["bpm"])
        sec = time.time() - t0
        acc = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
        piano = pretty_midi.Instrument(program=0, name="AccoMontage")
        for inst in midi.instruments[1:]:  # [0] is upstream's melody track
            for n in inst.notes:
                if n.start < end_sec - 1e-6:
                    piano.notes.append(pretty_midi.Note(n.velocity, n.pitch, n.start, min(n.end, end_sec)))
            piano.control_changes += [cc for cc in inst.control_changes if cc.time < end_sec]
        acc.instruments.append(piano)
        path = out / f"cand-{k}.mid"
        acc.write(str(path))
        info["samples"].append({"k": k, "seed": seed, "file": path.name, "notes": len(piano.notes),
                                "generate_sec": round(sec, 1),
                                "donor_phrases": [list(map(int, p)) for p in selection[0]]})
        print(f"sample {k}: {len(piano.notes)} notes in {sec:.1f} s", flush=True)
    if notes_info["rebarred"]:
        print(f"WARNING: {bpb}/4 melody re-barred into 4-beat bars for AccoMontage's 4/4 phrase pool "
              f"(harmony stays beat-aligned; texture metre is 4/4)", file=sys.stderr)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
