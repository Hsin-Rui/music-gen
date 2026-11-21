"""Harmonic metrics for one accompaniment against its melody and chart, and the ranking of N candidates.

    uv run steps/metrics.py MELODY.mid CHART.json CAND.mid [CAND.mid ...]

Per candidate (accompaniment notes only, melody excluded):
- ctnctr  chord-tone to non-chord-tone ratio (Yeh et al. 2021 style), accompaniment vs chart:
          (n_chord + n_proper) / (n_chord + n_nonchord); a non-chord tone is "proper" when a note
          at the next accompaniment onset lies 1-2 semitones away and is a chord tone there.
          Higher = follows the chart more closely.
- pcs     pitch consonance score, melody vs accompaniment, every 16th note: each sounding
          (melody, accompaniment) pitch pair scores +1 for unison/3rds/5th/6ths/octaves (0,3,4,7,8,9
          semitones mod 12), 0 for a 4th (5), -1 otherwise; averaged over all pairs. Higher = more consonant.
- ook     out-of-key ratio: share of accompaniment notes whose pitch class is outside the chart's key
          (major scale; minor = natural minor + raised 6th/7th). Lower = better.
- dissonant_overlap  duration-weighted share of melody/accompaniment overlap time where the two
          pitches form a minor 2nd/minor 9th, tritone or major 7th (1, 6, 11 semitones mod 12). Lower = better.
- copy    melody-shadowing ratio: share of accompaniment notes that start together with a melody note
          (within 40 ms) at a near-constant distance from it. For every such pair d = acc - melody
          (semitones); the densest 2-semitone band of d (e.g. {0} unison, {12} octave, {-3,-4} diatonic
          parallel thirds) is counted, divided by all accompaniment notes. Catches pure repetition
          (d = 0), octave doubling and the melody moved by an interval. Lower = better.
Ranking (revised 2026-11-21 at the user's request: PCS dropped, copying penalised):
score = z(ctnctr) - z(ook) - z(dissonant_overlap) - z(copy), z-scores within the ranked candidates
(a metric with zero spread contributes 0). PCS is still computed and reported, not scored.
Not ranked, unless no candidate passes both: fewer notes than bars (min_notes), or copy >= COPY_MAX.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart as C  # noqa: E402

CONSONANT = {0, 3, 4, 7, 8, 9}
PERFECT_FOURTH = {5}
HARSH = {1, 6, 11}
COPY_MAX = 0.5
ONSET_TOL = 0.04


def _notes(path, melody=False):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI(str(path))
    notes = [n for i in pm.instruments if not i.is_drum for n in i.notes]
    return sorted(notes, key=lambda n: (n.start, n.pitch))


def interval_score(a, b):
    iv = abs(a - b) % 12
    return 1 if iv in CONSONANT else 0 if iv in PERFECT_FOURTH else -1


def compute(melody_path, chart_obj, acc_path):
    meta = C.melody_meta(melody_path)
    mel = meta["notes"]
    acc = _notes(acc_path)
    beat = meta["beat_sec"]
    sp = C.spans(chart_obj, beat)
    tonic, minor = C.parse_key(chart_obj.get("key", ""))
    scale = set(C.scale_pcs(tonic, minor))
    res = {"notes": len(acc)}
    if not acc:
        return {**res, "ctnctr": None, "pcs": None, "ook": None, "dissonant_overlap": None, "copy": None}

    # CTnCTR
    onsets = sorted({round(n.start, 4) for n in acc})
    by_onset = {}
    for n in acc:
        by_onset.setdefault(round(n.start, 4), []).append(n)
    nxt = {t: onsets[i + 1] if i + 1 < len(onsets) else None for i, t in enumerate(onsets)}
    n_c = n_n = n_p = 0
    for n in acc:
        c = C.chord_at(sp, n.start)
        if c is None:
            continue
        if n.pitch % 12 in c["pcs"]:
            n_c += 1
            continue
        n_n += 1
        t2 = nxt[round(n.start, 4)]
        if t2 is not None:
            c2 = C.chord_at(sp, t2)
            if c2 and any(1 <= abs(m.pitch - n.pitch) <= 2 and m.pitch % 12 in c2["pcs"] for m in by_onset[t2]):
                n_p += 1
    res["ctnctr"] = round((n_c + n_p) / (n_c + n_n), 4) if (n_c + n_n) else None
    res["chord_tones"], res["non_chord_tones"], res["proper_non_chord"] = n_c, n_n, n_p

    # PCS on a 16th grid over the melody
    step = beat / 4
    end = max(n.end for n in mel)
    total, count = 0, 0
    t = 0.0
    ai = 0
    while t < end:
        mp = [n.pitch for n in mel if n.start <= t < n.end]
        if mp:
            ap_ = [n.pitch for n in acc if n.start <= t < n.end]
            for a in mp:
                for b in ap_:
                    total += interval_score(a, b)
                    count += 1
        t += step
        ai += 1
    res["pcs"] = round(total / count, 4) if count else None

    # OOK
    res["ook"] = round(sum(1 for n in acc if n.pitch % 12 not in scale) / len(acc), 4)

    # dissonant overlap (duration-weighted)
    ov_total = ov_bad = 0.0
    for m in mel:
        for n in acc:
            if n.start >= m.end:
                break
            ov = min(m.end, n.end) - max(m.start, n.start)
            if ov > 1e-6:
                ov_total += ov
                if abs(m.pitch - n.pitch) % 12 in HARSH:
                    ov_bad += ov
    res["dissonant_overlap"] = round(ov_bad / ov_total, 4) if ov_total > 0 else None

    # copy: accompaniment shadowing the melody at a near-constant interval
    diffs = []
    for n in acc:
        same = [m.pitch for m in mel if abs(m.start - n.start) <= ONSET_TOL]
        if same:
            diffs.append([n.pitch - p for p in same])
    best_lo, best_cnt = 0, 0
    for lo in range(-36, 36):
        cnt = sum(1 for ds in diffs if any(lo <= d <= lo + 1 for d in ds))
        if cnt > best_cnt:
            best_lo, best_cnt = lo, cnt
    res["copy"] = round(best_cnt / len(acc), 4)
    res["copy_interval"] = [best_lo, best_lo + 1] if best_cnt else None
    return res


def _z(values):
    xs = [v for v in values if v is not None]
    if len(xs) < 2:
        return [0.0 if v is not None else None for v in values]
    mu = sum(xs) / len(xs)
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / len(xs))
    return [None if v is None else (0.0 if sd < 1e-12 else (v - mu) / sd) for v in values]


def rank(results, min_notes=1):
    """results: list of metric dicts -> adds z_*, score, ranked; returns index of the best (or None)."""
    ranked = [r for r in results if (r.get("notes") or 0) >= max(1, min_notes)
              and (r.get("copy") or 0) < COPY_MAX]
    if not ranked:  # nobody passes: rank every non-empty candidate
        ranked = [r for r in results if r.get("notes")]
    for r in results:
        r["ranked"] = any(r is x for x in ranked)
    if not ranked:
        for r in results:
            r["score"] = None
        return None
    signs = {"ctnctr": 1, "ook": -1, "dissonant_overlap": -1, "copy": -1}
    for key, sign in signs.items():
        zs = _z([r[key] for r in ranked])
        for r, z in zip(ranked, zs):
            r["z_" + key] = None if z is None else round(z, 3)
    for r in results:
        if not r["ranked"]:
            r["score"] = None
            continue
        # a missing metric (e.g. no overlap at all) counts as the cell average (z = 0)
        r["score"] = round(sum(sign * (r.get("z_" + k) or 0.0) for k, sign in signs.items()), 3)
    best = max((i for i, r in enumerate(results) if r["score"] is not None), key=lambda i: results[i]["score"])
    return best


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    mel, chart_path, cands = sys.argv[1], sys.argv[2], sys.argv[3:]
    ch = C.load(chart_path)
    results = [{"file": c, **compute(mel, ch, c)} for c in cands]
    best = rank(results)
    print(json.dumps({"best": best, "candidates": results}, indent=1))


if __name__ == "__main__":
    main()
