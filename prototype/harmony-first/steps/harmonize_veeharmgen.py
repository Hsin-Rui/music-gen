"""Melody MIDI -> VeeHarmGen (rule/statistical lookup) -> normalised chart JSON (runs in envs/veeharmgen).

    envs/veeharmgen/bin/python steps/harmonize_veeharmgen.py MELODY.mid OUT.json [--style folk_1]
        [--rhythm BAR1] [--rank 100] [--seed 0]

VeeHarmGen (LGPL-3.0, github.com/RedFerret61/VeeHarmGen, v3.1.0) maps the pitch-class set of each
melody slice to the chord a style file says is most common for it. Two steps, as its run_BAR2_folk.sh:
1. melody .mxl -> placeholder files for each harmonic rhythm (BEAT1, BEAT2, BAR1, BAR2, BAR4);
2. the chosen placeholder file + a style filter -> chords (chord_choice rank, 100 = most frequent).
The melody is transposed to C major / A minor for the lookup and the chords transposed back.\nPrototype choice: one chord per bar (BAR1, like the Claude/Gemini charts), style folk_1, rank 100.
Local shim in the clone: upstream's default `offsets` [0.0] made every harmonic-rhythm step zero
(ZeroDivisionError); it is set to None so the time signature decides the step.
--seed is accepted for the runner and ignored (rank 100 is deterministic).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT / "models" / "veeharmgen"
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402


def norm(sym):
    m = re.match(r"^([A-G])(-*)(.*)$", sym)
    if m:
        sym = m.group(1) + "b" * len(m.group(2)) + m.group(3)
    return re.sub(r"/([A-G])-", r"/\1b", sym)


def back(fig, semis):
    """Transpose a chord symbol figure by semis, keeping flats/sharps sensible for the target key."""
    from music21 import harmony
    if not semis:
        return fig
    cs = harmony.ChordSymbol(fig).transpose(semis)
    return cs.figure


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("melody")
    ap.add_argument("output")
    ap.add_argument("--style", default="folk_1")
    ap.add_argument("--rhythm", default="BAR1")
    ap.add_argument("--rank", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    from music21 import converter, harmony, stream

    melody = Path(args.melody).resolve()
    out = Path(args.output).resolve()
    meta = C.melody_meta(melody)
    name = f"hf-{melody.stem}"
    (REPO / "output").mkdir(exist_ok=True)
    for old in (REPO / "output").glob(f"{name}*"):
        old.unlink()
    work = REPO / "output" / f"{name}.mxl"
    # VeeHarmGen's style maps are pitch-class tables built in C major / A minor and it does not
    # transpose by default, so the melody is moved to C/Am here and the chords moved back after.
    tonic, minor = meta["key"] if meta["key"] else (0, False)
    shift = ((9 if minor else 0) - tonic + 6) % 12 - 6
    converter.parse(str(melody), quantizePost=True).transpose(shift).write("mxl", str(work))
    py = sys.executable
    log = []
    for cmd in ([py, "VeeHarmGen.py", "-m", f"output/{name}.mxl", "-f", "mxl"],
                [py, "VeeHarmGen.py", "-m", f"output/{name}-{args.rhythm}.mxl", "-s", args.style,
                 "-c", "rank", "-n", str(args.rank), "-f", "mxl"]):
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        log.append(r.stdout[-2000:] + r.stderr[-2000:])
        if r.returncode:
            sys.exit(f"VeeHarmGen failed: {' '.join(cmd)}\n{log[-1]}")
    res = sorted((REPO / "output").glob(f"{name}-{args.rhythm}-{args.style}-*.mxl"))
    if not res:
        sys.exit(f"VeeHarmGen wrote no output for style {args.style}\n{log[-1]}")
    s = converter.parse(str(res[0]))
    measures = list(s.parts[0].getElementsByClass(stream.Measure))
    if len(measures) != meta["n_bars"]:
        sys.exit(f"{len(measures)} bars in VeeHarmGen output, melody has {meta['n_bars']}")
    q_per_beat = 4.0 / meta["denominator"]
    bpb = meta["beats_per_bar"]
    bars, current = [], None
    for m in measures:
        changes = {}
        for cs in m.getElementsByClass(harmony.ChordSymbol):
            if isinstance(cs, harmony.NoChord):
                continue
            beat = min(int(round(float(cs.offset) / q_per_beat)), bpb - 1)
            changes[beat] = norm(back(cs.figure, -shift))
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
        sys.exit("VeeHarmGen output has no chord symbols")
    bars = [[[c or first, b] for c, b in bar] for bar in bars]
    key = C.key_name(*meta["key"]) if meta["key"] else "unknown"
    ch = {"key": key, "meter": f"{meta['numerator']}/{meta['denominator']}", "beats_per_bar": bpb,
          "bars": bars, "melody": melody.stem, "source": "veeharmgen",
          "model": f"VeeHarmGen v3.1.0, rhythm {args.rhythm}, style {args.style}, rank {args.rank}",
          "file": res[0].name, "transposed_for_lookup": shift}
    problems = C.validate(ch, meta["n_bars"])
    C.save(ch, out)
    print("RESULT " + json.dumps({"ok": not problems, "problems": problems, "chart": C.compact(ch),
                                  "params": {"rhythm": args.rhythm, "style": args.style, "rank": args.rank}}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
