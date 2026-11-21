"""Chord charts: the one shared format every harmonizer is normalised to.

Chart JSON (same shape as harmonizations/llm/*.json):
    {"key": "D major", "meter": "4/4", "beats_per_bar": 4,
     "bars": [[["D", 4]], [["A7", 2], ["D", 2]], ...],   # bar 1 = first MIDI bar
     "melody": "ode_to_joy", "source": "llm", ...}

This module only needs the standard library (+ pretty_midi for the MIDI helpers,
imported lazily), so every env can import it.

    uv run steps/chart.py validate CHART.json MELODY.mid
    uv run steps/chart.py blocks CHART.json MELODY.mid OUT.mid   # melody + block chords
"""
import json
import math
import re
import sys

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
PC_NAME = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# quality suffix -> intervals above the root (root position)
QUALITIES = {
    "": [0, 4, 7], "maj": [0, 4, 7], "M": [0, 4, 7],
    "m": [0, 3, 7], "min": [0, 3, 7], "-": [0, 3, 7],
    "dim": [0, 3, 6], "o": [0, 3, 6],
    "aug": [0, 4, 8], "+": [0, 4, 8],
    "5": [0, 7],
    "sus": [0, 5, 7], "sus4": [0, 5, 7], "sus2": [0, 2, 7],
    "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9],
    "7": [0, 4, 7, 10], "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11], "M7": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10], "min7": [0, 3, 7, 10],
    "mmaj7": [0, 3, 7, 11], "mM7": [0, 3, 7, 11],
    "m7b5": [0, 3, 6, 10], "ø": [0, 3, 6, 10], "hdim7": [0, 3, 6, 10],
    "dim7": [0, 3, 6, 9], "o7": [0, 3, 6, 9],
    "aug7": [0, 4, 8, 10], "7#5": [0, 4, 8, 10], "+7": [0, 4, 8, 10],
    "7sus4": [0, 5, 7, 10], "7sus": [0, 5, 7, 10],
    "9": [0, 4, 7, 10, 14], "maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14],
    "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14],
    "7b9": [0, 4, 7, 10, 13], "11": [0, 4, 7, 10, 14, 17], "13": [0, 4, 7, 10, 14, 21],
}
SYMBOL_RE = re.compile(r"^([A-G])([#b]*)([^/]*)(?:/([A-G])([#b]*))?$")


def _pc(letter, acc):
    return (NOTE_PC[letter] + acc.count("#") - acc.count("b")) % 12


def parse_symbol(sym):
    """'F#m7/C#' -> {symbol, root, bass, intervals, pcs, warning}. Raises ValueError if unparseable."""
    s = sym.strip()
    m = SYMBOL_RE.match(s)
    if not m:
        raise ValueError(f"cannot parse chord symbol {sym!r}")
    root = _pc(m.group(1), m.group(2))
    qual = m.group(3)
    warning = None
    if qual in QUALITIES:
        ivs = QUALITIES[qual]
    else:  # unknown extension: fall back to its triad
        ivs = [0, 3, 7] if (qual.startswith("m") and not qual.startswith("maj")) else [0, 4, 7]
        warning = f"unknown chord quality {qual!r} in {sym!r}; using {'minor' if ivs[1] == 3 else 'major'} triad"
    bass = _pc(m.group(4), m.group(5)) if m.group(4) else root
    pcs = sorted({(root + i) % 12 for i in ivs} | {bass})
    return {"symbol": s, "root": root, "bass": bass, "intervals": ivs, "pcs": pcs, "warning": warning}


# ------------------------------------------------------------------ melody facts

def melody_meta(path):
    """bpm, meter, beat length, bar count of a (constant-tempo, quantized) melody MIDI."""
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(str(path))
    notes = sorted((n for i in pm.instruments if not i.is_drum for n in i.notes), key=lambda n: n.start)
    _, tempi = pm.get_tempo_changes()
    bpm = float(tempi[0]) if len(tempi) else 120.0
    ts = pm.time_signature_changes[0] if pm.time_signature_changes else pretty_midi.TimeSignature(4, 4, 0)
    beat_sec = 60.0 / bpm * 4.0 / ts.denominator
    bpb = ts.numerator
    last_onset_beat = notes[-1].start / beat_sec
    n_bars = int(math.floor(last_onset_beat / bpb + 1e-6)) + 1
    key = None
    if pm.key_signature_changes:
        k = pm.key_signature_changes[0].key_number
        key = (k % 12, k >= 12)
    return {"bpm": bpm, "numerator": ts.numerator, "denominator": ts.denominator,
            "beats_per_bar": bpb, "beat_sec": beat_sec, "bar_sec": bpb * beat_sec,
            "n_bars": n_bars, "key": key, "notes": notes}


# ------------------------------------------------------------------ validation

def validate(chart, n_bars=None):
    """Return a list of problems (empty = valid). Checks shape, parseable symbols,
    each bar summing to the meter, and (if given) the bar count."""
    problems = []
    bpb = chart.get("beats_per_bar")
    bars = chart.get("bars")
    if not isinstance(bpb, (int, float)) or bpb <= 0:
        return ["beats_per_bar missing or invalid"]
    if not isinstance(bars, list) or not bars:
        return ["bars missing or empty"]
    for i, bar in enumerate(bars, 1):
        if not isinstance(bar, list) or not bar:
            problems.append(f"bar {i}: empty")
            continue
        total = 0
        for item in bar:
            if not (isinstance(item, (list, tuple)) and len(item) == 2):
                problems.append(f"bar {i}: item {item!r} is not [chord, beats]")
                continue
            sym, beats = item
            try:
                parse_symbol(sym)
            except (ValueError, AttributeError, TypeError) as e:
                problems.append(f"bar {i}: {e}")
            if not isinstance(beats, (int, float)) or beats <= 0 or float(beats) != int(beats):
                problems.append(f"bar {i}: bad beat count {beats!r} (must be a positive whole number)")
            else:
                total += beats
        if abs(total - bpb) > 1e-6:
            problems.append(f"bar {i}: beats sum to {total}, meter needs {bpb}")
    if n_bars is not None and len(bars) != n_bars:
        problems.append(f"chart has {len(bars)} bars, melody has {n_bars}")
    return problems


def warnings_of(chart):
    out = []
    for bar in chart["bars"]:
        for sym, _ in bar:
            w = parse_symbol(sym)["warning"]
            if w and w not in out:
                out.append(w)
    return out


def load(path):
    with open(path) as f:
        return json.load(f)


def save(chart, path):
    with open(path, "w") as f:
        json.dump(chart, f, indent=1, ensure_ascii=False)


def compact(chart):
    """'D | A7 | D | D A | ...' one-line rendering for notes."""
    return " | ".join(" ".join(sym for sym, _ in bar) for bar in chart["bars"])


# ------------------------------------------------------------------ chart -> time

def spans(chart, beat_sec):
    """[(start_sec, end_sec, parsed_chord)] with identical neighbours merged."""
    out, t = [], 0.0
    bpb = chart["beats_per_bar"]
    for bi, bar in enumerate(chart["bars"]):
        t = bi * bpb * beat_sec
        for sym, beats in bar:
            c = parse_symbol(sym)
            end = t + beats * beat_sec
            if out and out[-1][2]["symbol"] == c["symbol"] and abs(out[-1][1] - t) < 1e-6:
                out[-1] = (out[-1][0], end, out[-1][2])
            else:
                out.append((t, end, c))
            t = end
    return out


def per_beat(chart):
    """One parsed chord per beat, in order (len = bars * beats_per_bar)."""
    labels = []
    for bar in chart["bars"]:
        for sym, beats in bar:
            c = parse_symbol(sym)
            n = int(round(beats))
            labels.extend([c] * n)
    return labels


def chord_at(spans_, t):
    for s, e, c in spans_:
        if s - 1e-6 <= t < e - 1e-6:
            return c
    return spans_[-1][2] if spans_ and t >= spans_[-1][1] - 1e-6 else None


def block_voicing(c):
    """Root-position block chord around C3-C4 (root in C3..B3); slash bass one octave below the root."""
    root = 48 + c["root"]
    pitches = [root + i for i in c["intervals"]]
    if c["bass"] != c["root"]:
        pitches.append(36 + c["bass"])
    return sorted(set(pitches))


def block_notes(chart, beat_sec, velocity=60, gate=0.97):
    """[(start, end, pitch, velocity)] block chords, one per chord span."""
    notes = []
    for s, e, c in spans(chart, beat_sec):
        for p in block_voicing(c):
            notes.append((s, s + (e - s) * gate, p, velocity))
    return notes


def write_blocks(chart, melody_path, out_path, chords_only=False, chord_program=0):
    """melody (program 0, track 'melody') + block chords (track 'chords') -> MIDI."""
    import pretty_midi
    meta = melody_meta(melody_path)
    pm = pretty_midi.PrettyMIDI(initial_tempo=meta["bpm"])
    pm.time_signature_changes.append(pretty_midi.TimeSignature(meta["numerator"], meta["denominator"], 0))
    src = pretty_midi.PrettyMIDI(str(melody_path))
    pm.key_signature_changes.extend(src.key_signature_changes[:1])
    if not chords_only:
        mel = pretty_midi.Instrument(program=0, name="melody")
        mel.notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, n.end) for n in meta["notes"]]
        pm.instruments.append(mel)
    ch = pretty_midi.Instrument(program=chord_program, name="chords")
    ch.notes = [pretty_midi.Note(v, p, s, e) for s, e, p, v in block_notes(chart, meta["beat_sec"])]
    pm.instruments.append(ch)
    pm.write(str(out_path))
    return pm


# ------------------------------------------------------------------ keys

def parse_key(key_str):
    """'D major' / 'A minor' / 'F major (pentatonic)' -> (tonic_pc, is_minor)."""
    m = re.match(r"\s*([A-G])([#b]?)\s*(major|minor|maj|min|m)?", key_str or "", re.I)
    if not m:
        raise ValueError(f"cannot parse key {key_str!r}")
    mode = (m.group(3) or "major").lower()
    return _pc(m.group(1), m.group(2)), mode in ("minor", "min", "m")


def key_name(tonic, minor):
    return f"{PC_NAME[tonic]} {'minor' if minor else 'major'}"


def scale_pcs(tonic, minor):
    """Diatonic pitch classes; minor = natural minor plus raised 6th and 7th (harmonic/melodic)."""
    steps = [0, 2, 3, 5, 7, 8, 10, 9, 11] if minor else [0, 2, 4, 5, 7, 9, 11]
    return sorted({(tonic + s) % 12 for s in steps})


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "validate":
        chart = load(sys.argv[2])
        meta = melody_meta(sys.argv[3])
        probs = validate(chart, meta["n_bars"])
        print("valid" if not probs else "\n".join(probs))
        sys.exit(1 if probs else 0)
    if len(sys.argv) >= 5 and sys.argv[1] == "blocks":
        write_blocks(load(sys.argv[2]), sys.argv[3], sys.argv[4])
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
