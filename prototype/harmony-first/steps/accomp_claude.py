"""Melody + chart -> accompaniment from Claude's per-bar texture plan (runs in this prototype's .venv).

    .venv/bin/python steps/accomp_claude.py MELODY.mid CHART.json OUTDIR [--samples N] [--seed S] [--device X]

Claude wrote accompaniments/claude/<melody>.json in conversation: one texture per bar
(halves, broken8, alberti, oompah, open8, sustain, bass, final, rest) with reasons. This script
realises it deterministically on any chart: for each chord span in a bar it voices the chord
below the melody (top voice at least a minor 3rd under the lowest melody note of the span,
never above G4; bass in E2..D#3) and lays out the texture. Not a model: the musical choices are
Claude's plan, the notes follow from the chart. Writes OUTDIR/cand-0.mid only (deterministic;
--samples/--seed/--device are accepted for the runner and ignored).
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

TOP_CAP, BASS_LO = 67, 40
TEXTURES = {"halves", "broken8", "alberti", "oompah", "open8", "sustain", "bass", "final", "rest"}


def voice(c, ceiling):
    pcs = {(c["root"] + i) % 12 for i in c["intervals"]}
    bass_pc = c["bass"]
    bass = next(p for p in range(BASS_LO, BASS_LO + 12) if p % 12 == bass_pc)
    top = min(ceiling, TOP_CAP)
    upper = [p for p in range(bass + 3, top + 1) if p % 12 in pcs][-3:]
    return bass, upper


def realise(texture, start, beats, beat, bass, upper):
    """-> [(start_sec, dur_sec, pitch, velocity)]"""
    out = []
    end = start + beats * beat
    def add(t, d, p, v):
        if t < end - 1e-6:
            out.append((t, min(d, end - t) * 0.95, p, v))
    if texture == "rest":
        return out
    if texture in ("sustain", "bass"):
        add(start, beats * beat, bass, 60)
        if texture == "sustain":
            for p in upper:
                add(start, beats * beat, p, 48)
    elif texture == "final":
        add(start, beats * beat, bass, 60)
        for i, p in enumerate(upper):
            add(start + 0.06 * (i + 1), beats * beat, p, 50)
    elif texture == "halves":
        t = 0
        while t < beats:
            d = min(2, beats - t)
            add(start + t * beat, d * beat, bass, 60)
            for p in upper:
                add(start + t * beat, d * beat, p, 48)
            t += 2
    elif texture == "oompah":
        for b in range(int(beats)):
            if b == 0:
                add(start, beat, bass, 62)
            else:
                for p in upper:
                    add(start + b * beat, beat * 0.8, p, 46)
    else:  # eighth-note figures
        if texture == "broken8":
            u = upper or [bass + 12]
            cycle = [bass] + u + u[-2:0:-1] if len(u) > 1 else [bass, u[0]]
        elif texture == "alberti":
            u = (upper + upper)[:3] if upper else [bass + 12] * 3
            cycle = [u[0], u[2], u[1], u[2]]
        else:  # open8: root - fifth - octave - fifth, no third
            cycle = [bass, bass + 7, bass + 12, bass + 7]
        if texture != "open8":
            add(start, beats * beat, bass, 58)  # held bass under the figure
        for i in range(int(round(beats * 2))):
            p = cycle[i % len(cycle)]
            if texture != "open8" and i % len(cycle) == 0 and p == bass:
                continue
            add(start + i * beat / 2, beat / 2, p, 50)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("chart")
    ap.add_argument("outdir")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    import pretty_midi

    melody = Path(args.melody)
    plan_path = ROOT / "accompaniments" / "claude" / f"{melody.stem}.json"
    if not plan_path.exists():
        sys.exit(f"no Claude accompaniment plan at {plan_path}")
    plan = json.loads(plan_path.read_text())
    chart = C.load(args.chart)
    meta = C.melody_meta(melody)
    if len(plan["bars"]) != meta["n_bars"] or len(chart["bars"]) != meta["n_bars"]:
        sys.exit(f"bar count mismatch: plan {len(plan['bars'])}, chart {len(chart['bars'])}, melody {meta['n_bars']}")
    bad = sorted(set(plan["bars"]) - TEXTURES)
    if bad:
        sys.exit(f"unknown textures in plan: {bad}")

    beat, bpb = meta["beat_sec"], meta["beats_per_bar"]
    notes = []
    for bi, (texture, bar) in enumerate(zip(plan["bars"], chart["bars"])):
        t = bi * bpb * beat
        for sym, beats in bar:
            c = C.parse_symbol(sym)
            span_end = t + beats * beat
            mel = [n.pitch for n in meta["notes"] if n.start < span_end - 1e-6 and n.end > t + 1e-6]
            ceiling = (min(mel) - 3) if mel else TOP_CAP
            bass, upper = voice(c, ceiling)
            notes += realise(texture, t, beats, beat, bass, upper)
            t = span_end

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
    inst = pretty_midi.Instrument(program=0, name="claude accompaniment")
    inst.notes = [pretty_midi.Note(v, p, s, s + d) for s, d, p, v in notes]
    pm.instruments.append(inst)
    pm.write(str(out / "cand-0.mid"))
    print(f"cand-0: {len(notes)} notes", flush=True)
    print("RESULT " + json.dumps({"samples": [{"k": 0, "file": "cand-0.mid", "notes": len(notes)}],
                                  "plan": str(plan_path.relative_to(ROOT)), "deterministic": True}), flush=True)


if __name__ == "__main__":
    main()
