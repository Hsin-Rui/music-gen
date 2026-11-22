"""One-off (second Gemini round): ask Gemini for a per-bar accompaniment texture plan.

    .venv/bin/python steps/plan_gemini_accomp.py      # writes accompaniments/gemini/<melody>.<chart>.json

The user allowed one more round of Gemini calls on 2026-11-22: Gemini writes an accompaniment for
its own chord charts (harmonizations/gemini/) and for Claude's (harmonizations/llm/). Gemini gets
the same task Claude had for "Claude 寫伴奏": melody notes and chart, one texture per bar from
the same fixed vocabulary, with reasons. steps/accomp_gemini.py realises it with the same code.
Refuses to run when accompaniments/gemini/ has plans or a LOCK; writes LOCK at the end.
"""
import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402
import harmonize_gemini as G  # noqa: E402
from accomp_claude import TEXTURES  # noqa: E402

OUT = G.ROOT / "accompaniments" / "gemini"
CHARTS = {"gemini": G.ROOT / "harmonizations" / "gemini", "llm": G.ROOT / "harmonizations" / "llm"}

VOCAB = """- "halves": block chord (bass + chord) on beats 1 and 3 (half notes)
- "broken8": held bass + eighth-note broken chord going up and down
- "alberti": held bass + eighth-note Alberti figure (low-high-middle-high)
- "oompah": bass on beat 1, chord on each other beat (waltz/march feel)
- "open8": eighth notes root-fifth-octave-fifth, no third (open, hollow)
- "sustain": one held block chord for the whole chord span
- "bass": a single held bass note only
- "final": held bass with a quick rolled chord (ending)
- "rest": nothing"""


def prompt_for(name, meta, key, listing, chart):
    m = f"{meta['numerator']}/{meta['denominator']}"
    chords = "\n".join(f"bar {i + 1}: " + " ".join(f"{s}({b} beat{'s' if b > 1 else ''})" for s, b in bar)
                       for i, bar in enumerate(chart["bars"]))
    return f"""You are an experienced piano arranger. Plan a piano accompaniment for this melody over the given chord chart.

Title: {G.TITLES.get(name, name)}
Key: {key}
Meter: {m} ({meta['beats_per_bar']} beats per bar)
Tempo: {meta['bpm']:.0f} bpm
Bars: {meta['n_bars']} (bar 1 is the first bar of the file; a pickup bar counts as a full bar)

Melody notes, per bar ("pitch@beat b for d" = starts on beat b of the bar, lasts d beats):
{listing}

Chord chart (fixed, do not change it):
{chords}

Choose ONE accompaniment texture per bar from this list (exact names):
{VOCAB}

How it is played: the melody stays on its own piano part; the accompaniment chord is voiced below the melody (top note at least a minor third under the lowest melody note, never above G4), the bass between E2 and D#3; a bar with two chords applies the texture to each chord's span.

Return JSON only, in exactly this shape:
{{"bars": ["<texture for bar 1>", "<texture for bar 2>", ...],
 "why": ["<short reasons, in Traditional Chinese, one item per bar group>"]}}

Rules: exactly {meta['n_bars']} items in "bars", each one of the names above."""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "LOCK").exists() or list(OUT.glob("*.json")):
        sys.exit(f"{OUT} already has Gemini plans (or LOCK): Gemini is not called again.")
    key = next(l.split("=", 1)[1].strip().strip("'\"") for l in (G.REPO / ".env").read_text().splitlines()
               if l.startswith("GEMINI_API_KEY="))
    log = {"model": G.MODEL, "date": f"{dt.datetime.now():%Y-%m-%d %H:%M}", "plans": {}}
    for name in ["ode_to_joy", "greensleeves", "jasmine"]:
        meta, k, listing = G.describe(G.EXAMPLES / f"{name}.mid")
        for src, cdir in CHARTS.items():
            chart = C.load(cdir / f"{name}.json")
            tag = f"{name}.{src}"
            prompt = prompt_for(name, meta, k, listing, chart)
            (OUT / f"{tag}.prompt.txt").write_text(prompt)
            rec = {"attempts": []}
            for attempt in range(2):
                t0 = time.time()
                try:
                    resp = G.call(key, prompt)
                except Exception as e:
                    rec["attempts"].append({"ok": False, "error": str(e)[:500]})
                    continue
                text = "".join(p.get("text", "") for p in resp["candidates"][0]["content"]["parts"])
                (OUT / f"{tag}.raw-{attempt}.json").write_text(text)
                try:
                    plan = json.loads(text)
                    bars = [str(b) for b in plan["bars"]]
                    problems = ([f"{len(bars)} bars, melody has {meta['n_bars']}"] if len(bars) != meta["n_bars"] else []) \
                        + [f"unknown texture {b}" for b in sorted(set(bars) - TEXTURES)]
                except Exception as e:
                    problems = [f"unparseable: {e}"]
                rec["attempts"].append({"ok": not problems, "problems": problems, "sec": round(time.time() - t0, 1),
                                        "usage": resp.get("usageMetadata"), "model_version": resp.get("modelVersion")})
                if not problems:
                    out = {"melody": name, "chart_source": src, "bars": bars, "why": plan.get("why", []),
                           "author": f"{resp.get('modelVersion', G.MODEL)} (API, {log['date']})"}
                    (OUT / f"{tag}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
                    print(f"{tag}: ok — {' '.join(bars)}")
                    break
                print(f"{tag}: attempt {attempt + 1} invalid: {problems[:3]}")
            log["plans"][tag] = rec
    (OUT / "gemini-log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
    (OUT / "LOCK").write_text("Gemini was called for accompaniment plans on " + log["date"]
                              + " (second and last round the user allowed). Do not call it again.\n")


if __name__ == "__main__":
    main()
