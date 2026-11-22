"""One-off: ask Gemini to write chord charts for the three example melodies (prototype 02).

    .venv/bin/python steps/harmonize_gemini.py            # writes harmonizations/gemini/<melody>.json

The user allowed exactly one round of Gemini calls (2026-11-22), with GEMINI_API_KEY in the repo's
.env, and asked that Gemini not be called again afterwards. So this script refuses to run when
harmonizations/gemini/ already holds charts or a LOCK file, and writes LOCK when it finishes.
The saved charts are then used as given, like the Claude charts.

Gemini gets the same information Claude had: title, key, meter, tempo and every melody note
(bar, beat, pitch name, length), and is asked for the same JSON shape as harmonizations/llm/.
Model: gemini-3.1-pro-preview (the newest Pro model the API listed on 2026-11-22), default
sampling and thinking. At most 2 attempts per melody; prompt and raw replies are saved.
"""
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(HERE))
import chart as C  # noqa: E402

MODEL = "gemini-3.1-pro-preview"
OUT = ROOT / "harmonizations" / "gemini"
EXAMPLES = ROOT.parent / "melody-to-performance" / "examples"
TITLES = {"ode_to_joy": "Ode to Joy (Beethoven, Symphony No. 9)",
          "greensleeves": "Greensleeves (English folk tune)",
          "jasmine": "Mo Li Hua / Jasmine Flower (Chinese folk tune)"}
SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLATS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


def note_name(p, flats):
    return f"{(FLATS if flats else SHARPS)[p % 12]}{p // 12 - 1}"


def q(x):  # notated value: MIDI note ends are slightly gated
    return f"{round(x * 4) / 4:g}"


def describe(path):
    meta = C.melody_meta(path)
    beat, bpb = meta["beat_sec"], meta["beats_per_bar"]
    bars = [[] for _ in range(meta["n_bars"])]
    tonic, minor = meta["key"] if meta["key"] else (0, False)
    flats = (tonic in (5, 10, 3, 8, 1)) if not minor else (tonic in (2, 7, 0, 5, 10))
    for n in meta["notes"]:
        b = round(n.start / beat * 4) / 4
        bi = min(int(b // bpb + 1e-6), meta["n_bars"] - 1)
        bars[bi].append(f"{note_name(n.pitch, flats)}@beat {q(b - bi * bpb + 1)} for {q((n.end - n.start) / beat / 0.95)}")
    key = C.key_name(*meta["key"]) if meta["key"] else "unknown"
    lines = [f"bar {i + 1}: " + (", ".join(x) if x else "(rest)") for i, x in enumerate(bars)]
    return meta, key, "\n".join(lines)


def prompt_for(name, meta, key, listing):
    m = f"{meta['numerator']}/{meta['denominator']}"
    return f"""You are an experienced arranger. Write a chord chart (chord symbols) for this melody, to be used as the harmony of a piano accompaniment.

Title: {TITLES.get(name, name)}
Key: {key}
Meter: {m} ({meta['beats_per_bar']} beats per bar)
Tempo: {meta['bpm']:.0f} bpm
Bars: {meta['n_bars']} (bar 1 is the first bar of the file; a pickup bar counts as a full bar)

Melody notes, per bar ("pitch@beat b for d" = starts on beat b of the bar, lasts d beats):
{listing}

Return JSON only, in exactly this shape:
{{"key": "<key>", "meter": "{m}", "beats_per_bar": {meta['beats_per_bar']},
 "bars": [[["<chord>", <beats>], ...], ...],
 "why": ["<short reasons, in Traditional Chinese, one item per bar group>"]}}

Rules: exactly {meta['n_bars']} bars; inside each bar the beats are whole numbers and add up to {meta['beats_per_bar']}; chord symbols like C, Am, G7, Bb, F#m, Dm7, Bdim, Csus4, C/E."""


def call(key, prompt):
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "LOCK").exists() or list(OUT.glob("*.json")):
        sys.exit(f"{OUT} already has Gemini charts (or LOCK): Gemini is not called again.")
    key = next(l.split("=", 1)[1].strip().strip("'\"") for l in (REPO / ".env").read_text().splitlines()
               if l.startswith("GEMINI_API_KEY="))
    log = {"model": MODEL, "date": f"{dt.datetime.now():%Y-%m-%d %H:%M}", "melodies": {}}
    for name in ["ode_to_joy", "greensleeves", "jasmine"]:
        meta, k, listing = describe(EXAMPLES / f"{name}.mid")
        prompt = prompt_for(name, meta, k, listing)
        (OUT / f"{name}.prompt.txt").write_text(prompt)
        rec = {"attempts": []}
        for attempt in range(2):
            t0 = time.time()
            try:
                resp = call(key, prompt)
            except Exception as e:
                rec["attempts"].append({"ok": False, "error": str(e)[:500]})
                continue
            text = "".join(p.get("text", "") for p in resp["candidates"][0]["content"]["parts"])
            (OUT / f"{name}.raw-{attempt}.json").write_text(text)
            try:
                ch = json.loads(text)
                ch["bars"] = [[[str(s), int(b)] for s, b in bar] for bar in ch["bars"]]
                problems = C.validate(ch, meta["n_bars"])
            except Exception as e:
                problems = [f"unparseable: {e}"]
            rec["attempts"].append({"ok": not problems, "problems": problems, "sec": round(time.time() - t0, 1),
                                    "usage": resp.get("usageMetadata"), "model_version": resp.get("modelVersion")})
            if not problems:
                ch.update({"melody": name, "source": "gemini", "model": f"{resp.get('modelVersion', MODEL)} (API, {log['date']})"})
                C.save(ch, OUT / f"{name}.json")
                print(f"{name}: ok — {C.compact(ch)}")
                break
            print(f"{name}: attempt {attempt + 1} invalid: {problems[:3]}")
        log["melodies"][name] = rec
    (OUT / "gemini-log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
    (OUT / "LOCK").write_text("Gemini was called once on " + log["date"] + ". Do not call it again (user instruction).\n")


if __name__ == "__main__":
    main()
