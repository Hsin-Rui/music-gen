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

Round 3 (2026-11-22, docs/plan-harmony-first-round3.md): gate-then-rank. `compute`/`rank` above stay
as they were (run.py still uses them); round3.py uses `compute_r3`, `gates_r3` and `select_r3`.
Notation: beat = beat_sec, bar = numerator * beat, prompt = chart.block_notes(chart, beat) (the block
chords AMT is conditioned on), tolerance 0.04 s unless stated.
Gates (a candidate passes only if all five pass):
- enough_notes  notes >= n_bars and empty_beat_rate <= 0.25; a beat (0 .. n_bars*bar) is empty when no
                accompaniment note sounds anywhere in it (sounding, not onsets: sustained chords count).
- melody_copy   `copy` (above) < 0.5.
- prompt_copy   Degree of Copying vs the prompt < 0.5: 2m / (n_acc + n_prompt), m = one-to-one greedy
                matches on (same pitch class, |onset diff| <= tol).
- chord_fit     chord_match >= 0.7 and ook <= 0.05; chord_match = share of non-empty beats in which >= 50%
                of the sounding accompaniment duration is chord tones of the chord at the beat start.
- playable      two-hand check per onset group (notes starting within tol): the group passes when it fits
                one hand, or when some split of its sorted pitches gives a lower and an upper part that
                each have <= 5 notes and span <= 14 semitones (two hands).
Axes (ranked among passers, 1 = best, ties share the minimum rank; Borda sum lowest wins; ties broken by
lower prompt_sim, then lower k):
- prompt_sim  (lower better) mean(F1, groove_cos). F1: mir_eval-style note matching vs the prompt (same
              MIDI pitch, onset within 0.05 s, offset within max(0.2 * prompt duration, 0.05 s), greedy
              one-to-one), 2m / (n_acc + n_prompt). groove_cos: cosine of binary 16th-grid onset vectors.
- rules       (lower better) parallel_rate + (dissonant_overlap or 0). At each melody onset the bass is the
              lowest sounding accompaniment pitch (onsets without one are skipped); consecutive onsets where
              melody and bass move in the same direction and the interval mod 12 stays 7->7 or 0->0 count
              one parallel; parallel_rate = count / melody notes.
- bass_ok     (higher better) share of chord spans whose lowest accompaniment onset in
              [start - tol, start + beat/2) has the chord's bass pitch class (no such note = not OK).
Fallback: with no passers, the candidates with the fewest failed gates are ranked the same way.
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


# ------------------------------------------------------------------ round 3: gate-then-rank

R3_GATES = ["enough_notes", "melody_copy", "prompt_copy", "chord_fit", "playable"]
R3_AXES = {"prompt_sim": "low", "rules": "low", "bass_ok": "high"}
EMPTY_BEAT_MAX = 0.25
DOC_MAX = 0.5
CHORD_MATCH_MIN = 0.7
OOK_MAX = 0.05
HAND_NOTES = 5
HAND_SPAN = 14


def _doc(acc, prompt, tol=ONSET_TOL):
    """Degree of Copying: one-to-one greedy (pitch class, onset) matches -> 2m / (n_acc + n_prompt)."""
    used = [False] * len(prompt)
    m = 0
    for n in acc:
        best, bd = None, None
        for j, (s, _e, p, _v) in enumerate(prompt):
            d = abs(s - n.start)
            if not used[j] and p % 12 == n.pitch % 12 and d <= tol and (bd is None or d < bd):
                best, bd = j, d
        if best is not None:
            used[best] = True
            m += 1
    return 2 * m / (len(acc) + len(prompt)) if (acc or prompt) else None


def _note_f1(acc, prompt, onset_tol=0.05):
    """mir_eval-style note F1 vs the prompt: same pitch, onset and offset within tolerance, greedy one-to-one."""
    used = [False] * len(prompt)
    m = 0
    for n in acc:
        best, bd = None, None
        for j, (s, e, p, _v) in enumerate(prompt):
            if used[j] or p != n.pitch:
                continue
            d = abs(s - n.start)
            if d <= onset_tol and abs(e - n.end) <= max(0.2 * (e - s), 0.05) and (bd is None or d < bd):
                best, bd = j, d
        if best is not None:
            used[best] = True
            m += 1
    return 2 * m / (len(acc) + len(prompt)) if (acc or prompt) else None


def _groove_cos(acc_onsets, prompt_onsets, step, total):
    n = max(1, int(math.ceil(total / step + 1e-6)) + 1)
    a, b = [0] * n, [0] * n
    for t in acc_onsets:
        a[min(n - 1, max(0, int(round(t / step))))] = 1
    for t in prompt_onsets:
        b[min(n - 1, max(0, int(round(t / step))))] = 1
    na, nb = sum(a), sum(b)
    if not na or not nb:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(na * nb)


def _playable(acc, tol=ONSET_TOL):
    """Two-hand check per onset group. -> (ok, n_groups, n_bad, first_bad_onset_sec)."""
    groups, cur = [], []
    for n in sorted(acc, key=lambda n: n.start):
        if cur and n.start - cur[0].start > tol:
            groups.append(cur)
            cur = []
        cur.append(n)
    if cur:
        groups.append(cur)

    def hand_ok(ps):
        return len(ps) <= HAND_NOTES and ps[-1] - ps[0] <= HAND_SPAN

    bad, first = 0, None
    for g in groups:
        ps = sorted({n.pitch for n in g})
        # one hand, or any split of the sorted pitches into a left- and a right-hand part
        ok = hand_ok(ps) or any(hand_ok(ps[:i]) and hand_ok(ps[i:]) for i in range(1, len(ps)))
        if not ok:
            bad += 1
            if first is None:
                first = round(g[0].start, 3)
    return bad == 0, len(groups), bad, first


def compute_r3(melody_path, chart_obj, acc_path):
    """Round-3 metrics for one candidate (see the module docstring). Raises if the MIDI is unreadable."""
    meta = C.melody_meta(melody_path)
    mel = meta["notes"]
    beat = meta["beat_sec"]
    bar = meta["numerator"] * beat
    n_bars = meta["n_bars"]
    acc = _notes(acc_path)
    base = compute(melody_path, chart_obj, acc_path)
    res = {"notes": len(acc), "copy": base.get("copy"), "copy_interval": base.get("copy_interval"),
           "ook": base.get("ook"), "dissonant_overlap": base.get("dissonant_overlap")}
    keys = ["empty_beat_rate", "prompt_doc", "chord_match", "playable", "playable_bad_groups",
            "playable_first_bad_sec", "prompt_f1", "groove_cos", "prompt_sim", "parallels",
            "parallel_rate", "rules", "bass_ok"]
    if not acc:
        return {**res, **{k: None for k in keys}}
    sp = C.spans(chart_obj, beat)
    prompt = C.block_notes(chart_obj, beat)

    # empty beats and per-beat chord match (sounding duration)
    n_beats = n_bars * meta["numerator"]
    empty = matched = nonempty = 0
    for i in range(n_beats):
        b0, b1 = i * beat, (i + 1) * beat
        dur = tone = 0.0
        for n in acc:
            ov = min(n.end, b1) - max(n.start, b0)
            if ov > 1e-6:
                dur += ov
                c = C.chord_at(sp, b0)
                if c is not None and n.pitch % 12 in c["pcs"]:
                    tone += ov
        if dur <= 0:
            empty += 1
            continue
        if C.chord_at(sp, b0) is None:
            continue
        nonempty += 1
        if tone >= 0.5 * dur:
            matched += 1
    res["empty_beat_rate"] = round(empty / n_beats, 4) if n_beats else None
    res["chord_match"] = round(matched / nonempty, 4) if nonempty else None

    doc = _doc(acc, prompt)
    res["prompt_doc"] = None if doc is None else round(doc, 4)
    ok, _ng, nbad, first = _playable(acc)
    res["playable"], res["playable_bad_groups"], res["playable_first_bad_sec"] = ok, nbad, first

    f1 = _note_f1(acc, prompt)
    total = max(n_bars * bar, max(n.start for n in acc), max(s for s, *_ in prompt) if prompt else 0)
    gc = _groove_cos([n.start for n in acc], [s for s, *_ in prompt], beat / 4, total)
    res["prompt_f1"] = round(f1, 4)
    res["groove_cos"] = round(gc, 4)
    res["prompt_sim"] = round((f1 + gc) / 2, 4)

    # parallel fifths / octaves between melody and bass
    def bass_at(t):
        ps = [n.pitch for n in acc if n.start - ONSET_TOL <= t < n.end - 1e-6]
        return min(ps) if ps else None
    pairs = [(m.pitch, bass_at(m.start)) for m in mel]
    par = 0
    for (m1, b1_), (m2, b2_) in zip(pairs, pairs[1:]):
        if b1_ is None or b2_ is None:
            continue
        dm, db = m2 - m1, b2_ - b1_
        if dm * db > 0 and (m1 - b1_) % 12 == (m2 - b2_) % 12 and (m1 - b1_) % 12 in (0, 7):
            par += 1
    res["parallels"] = par
    res["parallel_rate"] = round(par / len(mel), 4) if mel else 0.0
    res["rules"] = round(res["parallel_rate"] + (res["dissonant_overlap"] or 0), 4)

    # bass at chord changes
    okc = 0
    for s, _e, c in sp:
        lows = [n.pitch for n in acc if s - ONSET_TOL <= n.start < s + beat / 2]
        if lows and min(lows) % 12 == c["bass"]:
            okc += 1
    res["bass_ok"] = round(okc / len(sp), 4) if sp else None
    return res


def gates_r3(m, n_bars):
    """metrics dict -> {gate: True/False/None}. An empty or unreadable candidate (0 notes) fails only
    enough_notes; its other gates are None (not evaluated) and are not counted as failed."""
    def le(v, x):
        return v is not None and v <= x

    def lt(v, x):
        return v is not None and v < x
    if not m.get("notes"):
        return {g: (False if g == "enough_notes" else None) for g in R3_GATES}
    return {
        "enough_notes": (m.get("notes") or 0) >= n_bars and le(m.get("empty_beat_rate"), EMPTY_BEAT_MAX),
        "melody_copy": lt(m.get("copy"), COPY_MAX),
        "prompt_copy": lt(m.get("prompt_doc"), DOC_MAX),
        "chord_fit": (m.get("chord_match") is not None and m["chord_match"] >= CHORD_MATCH_MIN)
                     and le(m.get("ook"), OOK_MAX),
        "playable": m.get("playable") is True,
    }


def _min_ranks(values, higher_better):
    """1 = best, ties share the minimum rank; None is ranked after every value."""
    def key(v):
        return (1, 0) if v is None else (0, -v if higher_better else v)
    ks = [key(v) for v in values]
    return [1 + sum(1 for o in ks if o < k) for k in ks]


def select_r3(cands, selectable=True):
    """cands: list of dicts with 'k', metrics and 'gates' (from gates_r3). Adds 'failed', 'pool', 'ranks',
    'borda' to each. -> {'chosen': k or None, 'fallback': bool, 'passers': n, 'selected': bool}.
    selectable=False (one LLM-written candidate): scored and ranked for display, never 'selected'."""
    for c in cands:
        c["failed"] = [g for g in R3_GATES if (c.get("gates") or {}).get(g) is False]
    passers = [c for c in cands if not c["failed"]]
    fallback = False
    if passers:
        pool = passers
    else:
        live = [c for c in cands if c.get("notes")]
        fewest = min((len(c["failed"]) for c in live), default=None)
        pool = [c for c in live if len(c["failed"]) == fewest]
        fallback = bool(pool)
    for c in cands:
        c["pool"] = any(c is p for p in pool)
        c["ranks"], c["borda"] = None, None
    if pool:
        per_axis = {a: _min_ranks([p.get(a) for p in pool], d == "high") for a, d in R3_AXES.items()}
        for i, p in enumerate(pool):
            p["ranks"] = {a: per_axis[a][i] for a in R3_AXES}
            p["borda"] = sum(p["ranks"].values())
    if not pool:
        chosen = None
    else:
        win = min(pool, key=lambda p: (p["borda"], p["prompt_sim"] if p.get("prompt_sim") is not None
                                       else float("inf"), p["k"]))
        chosen = win["k"]
    return {"chosen": chosen, "fallback": fallback if selectable else False,
            "passers": len(passers), "selected": bool(selectable and chosen is not None)}


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
