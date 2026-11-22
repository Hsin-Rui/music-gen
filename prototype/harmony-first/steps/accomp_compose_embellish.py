"""Melody + chart -> N Compose & Embellish piano accompaniments (runs in envs/compose-embellish).

    envs/compose-embellish/bin/python steps/accomp_compose_embellish.py MELODY.mid CHART.json OUTDIR
        [--samples 8] [--seed 0] [--device cpu|mps] [--max-bars N] [--temp 1.2] [--top-p 0.97]

Compose & Embellish (Wu & Yang, ICASSP 2023, MIT; models/compose-embellish, weights
slseanwu/compose-and-embellish-pop1k7). Only stage 2 ("Embellish", GPT-2 backbone) is used:
it turns a lead sheet (melody + chord per position, REMI events) into a full piano
performance, bar by bar. Stage 1 (writing the lead sheet) is replaced by our melody + chart.
Local shims:
- the lead sheet is written from the melody and chart directly, in the event order of the
  training data (Bar, Beat_k, Chord_<root>_<quality>, Note_Pitch, Note_Duration; 16 positions
  per 4/4 bar, 120 ticks per 16th). Chords are mapped to the model's 11 qualities (nearest;
  slash bass dropped).
- 2/4 and 3/4 melodies are re-barred into 4-beat bars on the same beat grid (as for AccoMontage).
- the sampling loop is upstream generate_conditional() (stage02_embellish/inference.py),
  copied because that script runs CUDA setup at import; temp 1.2 / top_p 0.97 = upstream GPT-2
  defaults. Runs on CPU or MPS.
- the model plays the melody inside its performance; notes with the melody's exact pitch at
  the melody's position are removed so only the accompaniment remains (count reported).
Writes OUTDIR/cand-<k>.mid (accompaniment only, seconds on the melody's tempo).
"""
import argparse
import json
import pickle
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "compose-embellish"
S2 = REPO / "stage02_embellish"
WEIGHTS = REPO / "compose-and-embellish-pop1k7" / "embellish_model_gpt2_pop1k7_loss0.398.bin"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(S2))
import chart as C  # noqa: E402

QUALITY_SETS = {
    "M": {0, 4, 7}, "m": {0, 3, 7}, "o": {0, 3, 6}, "+": {0, 4, 8}, "7": {0, 4, 7, 10},
    "M7": {0, 4, 7, 11}, "m7": {0, 3, 7, 10}, "o7": {0, 3, 6, 9}, "/o7": {0, 3, 6, 10},
    "sus2": {0, 2, 7}, "sus4": {0, 5, 7},
}
MAX_DEC_INP_LEN = 2048


def quality(c):
    rel = {i % 12 for i in c["intervals"]}
    for q, s in QUALITY_SETS.items():
        if rel == s:
            return q
    if 3 in rel and 4 not in rel:
        return "m7" if 10 in rel else "o" if 6 in rel and 7 not in rel else "m"
    if 4 in rel:
        return "7" if 10 in rel else "M7" if 11 in rel else "+" if 8 in rel and 7 not in rel else "M"
    if 5 in rel:
        return "sus4"
    if 2 in rel:
        return "sus2"
    return "M"


def lead_sheet(meta, chart, tempo_tok):
    """-> (list of bars, each a list of event strings incl. leading Bar_None), n 4/4 bars, step sec."""
    beat = meta["beat_sec"]
    step = beat / 4
    labels = C.per_beat(chart)
    n_beats = len(labels)
    n44 = (n_beats + 3) // 4
    bars = [["Bar_None"] for _ in range(n44)]
    by_pos = {}
    for n in meta["notes"]:
        p = int(round(n.start / step))
        if p < n44 * 16:
            by_pos.setdefault(p, []).append(n)
    prev = None
    for b in range(n44):
        for pos in range(16):
            gp = b * 16 + pos
            evs = []
            if pos % 4 == 0:
                bi = gp // 4
                c = labels[bi] if bi < n_beats else None
                tok = "Chord_None_None" if c is None else f"Chord_{c['root']}_{quality(c)}"
                if pos == 0 or tok != prev:
                    evs.append(tok)
                prev = tok
            for n in sorted(by_pos.get(gp, []), key=lambda n: -n.pitch)[:1]:  # skyline = top note
                d = max(1, min(16, int(round((n.end - n.start) / step))))
                evs += [f"Note_Pitch_{n.pitch}", f"Note_Duration_{d * 120}"]
            if evs:
                bars[b] += [f"Beat_{pos}"] + evs
    return bars, n44, step


def temperature(logits, t):
    import numpy as np
    z = logits / t
    z = z - z.max()
    p = np.exp(z)
    return p / p.sum()


def nucleus(probs, p):
    import numpy as np
    probs = probs / probs.sum()
    idx = np.argsort(probs)[::-1]
    cs = np.cumsum(probs[idx])
    after = cs > p
    last = np.where(after)[0][1] if after.sum() > 1 else len(idx)
    cand = idx[:max(1, last)]
    cp = probs[cand] / probs[cand].sum()
    return int(np.random.choice(cand, p=cp))


def generate(model, e2i, i2e, skyline, tempo_id, temp, top_p, device):
    """Upstream generate_conditional() (GPT-2 path, no chord embedding), condensed."""
    import torch
    gen = [tempo_id, e2i["Track_Skyline"]] + skyline[0] + [e2i["Track_Midi"]]
    seg = [0] * len(gen)
    seg[-1] = 1
    target, done, cur_pos, failed = len(skyline), 0, 0, 0
    while done < target:
        x = torch.tensor([gen[-MAX_DEC_INP_LEN:]], device=device)
        s = torch.tensor([seg[-MAX_DEC_INP_LEN:]], device=device)
        with torch.no_grad():
            logits = model(x, seg_inp=s, keep_last_only=True)[0].float().cpu().numpy()
        w = nucleus(temperature(logits, temp), top_p)
        ev = i2e.get(w, "PAD_None")  # index len(vocab) = dataset PAD
        if ev.startswith("Beat"):
            pos = int(ev.split("_")[-1])
            if pos < cur_pos:
                failed += 1
                if failed >= 256:
                    break
                continue
            cur_pos, failed = pos, 0
        if ev == "Track_Skyline":
            gen.append(w)
            seg.append(0)
            done += 1
            if done < target:
                gen += skyline[done] + [e2i["Track_Midi"]]
                seg += [0] * len(skyline[done]) + [1]
                cur_pos = 0
            continue
        if ev == "PAD_None" or (ev == "EOS_None" and done < target - 1):
            continue
        if ev == "EOS_None":
            break
        gen.append(w)
        seg.append(1)
        if len(gen) > 20000:
            break
    return [i2e.get(i, "PAD_None") for i in gen]


def performance_notes(events):
    """Notes of the Track_Midi segments -> [(bar, pos, pitch, dur_ticks, vel)]."""
    out, in_midi, bar, pos = [], False, -1, 0
    for i, ev in enumerate(events):
        if ev == "Track_Midi":
            in_midi = True
            continue
        if ev == "Track_Skyline":
            in_midi = False
            continue
        if not in_midi:
            continue
        if ev == "Bar_None":
            bar += 1
            pos = 0
        elif ev.startswith("Beat_"):
            pos = int(ev.split("_")[-1])
        elif ev.startswith("Note_Pitch_") and i + 2 < len(events) and events[i + 1].startswith("Note_Duration_") \
                and events[i + 2].startswith("Note_Velocity_"):
            out.append((bar, pos, int(ev.split("_")[-1]), int(events[i + 1].split("_")[-1]),
                        int(events[i + 2].split("_")[-1])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("chart")
    ap.add_argument("outdir")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--max-bars", type=int, default=None, help="only the first N 4/4 bars (smoke test)")
    ap.add_argument("--temp", type=float, default=1.2)
    ap.add_argument("--top-p", type=float, default=0.97)
    args = ap.parse_args()

    import numpy as np
    import pretty_midi
    import random
    import torch
    import yaml
    from model.music_gpt2 import MusicGPT2

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    chart = C.load(args.chart)
    meta = C.melody_meta(args.melody)
    e2i, i2e = pickle.load(open(S2 / "vocab" / "skyline2midi_vocab.pkl", "rb"))
    tempos = [int(k.split("_")[1]) for k in e2i if k.startswith("Tempo_") and "Conti" not in k]
    tempo_val = min(tempos, key=lambda t: abs(t - meta["bpm"]))
    bars, n44, step = lead_sheet(meta, chart, f"Tempo_{tempo_val}")
    if args.max_bars:
        bars = bars[:args.max_bars]
    skyline = [[e2i[e] for e in b] for b in bars]
    end_sec = min(len(C.per_beat(chart)), len(bars) * 4) * meta["beat_sec"]

    conf = yaml.safe_load(open(S2 / "config" / "pop1k7_gpt2.yaml"))["model"]
    t0 = time.time()
    model = MusicGPT2(len(e2i) + 1, conf["n_layer"], conf["n_head"], conf["d_model"], conf["d_ff"], conf["d_embed"],
                      use_segment_emb=conf["use_segemb"], n_segment_types=2)
    sd = torch.load(WEIGHTS, map_location="cpu", weights_only=True)
    state = model.state_dict()
    state.update({k: v for k, v in sd.items() if "feature_map.omega" not in k
                  and not k.endswith((".attn.bias", ".attn.masked_bias"))})  # old-transformers mask buffers
    model.load_state_dict(state)
    model.to(args.device).eval()
    info = {"load_sec": round(time.time() - t0, 1), "temp": args.temp, "top_p": args.top_p,
            "tempo_token": tempo_val, "rebarred": meta["beats_per_bar"] != 4, "bars_4_4": len(bars),
            "samples": []}

    mel_keys = {(int(round(n.start / step)), n.pitch) for n in meta["notes"]}
    for k in range(args.samples):
        seed = args.seed + k
        np.random.seed(seed)
        random.seed(seed)
        torch.manual_seed(seed)
        t0 = time.time()
        events = generate(model, e2i, i2e, skyline, e2i[f"Tempo_{tempo_val}"], args.temp, args.top_p, args.device)
        sec = time.time() - t0
        notes = performance_notes(events)
        pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
        piano = pretty_midi.Instrument(program=0, name="Compose & Embellish")
        stripped = 0
        for bar, pos, pitch, dur, vel in notes:
            gp = bar * 16 + pos
            if (gp, pitch) in mel_keys:
                stripped += 1
                continue
            s = gp * step
            if s >= end_sec - 1e-6:
                continue
            e = min(s + dur / 120 * step, end_sec)
            piano.notes.append(pretty_midi.Note(vel, pitch, s, e))
        pm.instruments.append(piano)
        path = out / f"cand-{k}.mid"
        pm.write(str(path))
        info["samples"].append({"k": k, "seed": seed, "file": path.name, "notes": len(piano.notes),
                                "melody_notes_removed": stripped, "events": len(events),
                                "generate_sec": round(sec, 1)})
        print(f"sample {k}: {len(piano.notes)} notes ({stripped} melody notes removed) in {sec:.1f} s", flush=True)
    if info["rebarred"]:
        print(f"WARNING: {meta['beats_per_bar']}/4 melody re-barred into 4-beat bars for Compose & Embellish "
              f"(trained on 4/4 pop piano)", file=sys.stderr)
    print("RESULT " + json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
