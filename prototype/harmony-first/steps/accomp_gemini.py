"""Melody + chart -> accompaniment from Gemini's per-bar texture plan (runs in this prototype's .venv).

    .venv/bin/python steps/accomp_gemini.py MELODY.mid CHART.json OUTDIR

Same realiser as accomp_claude.py; the plan is accompaniments/gemini/<melody>.<chart source>.json,
written by Gemini (steps/plan_gemini_accomp.py) for that chart, so this model only has cells for the
chart sources Gemini planned (llm = Claude's chart, gemini = its own).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import accomp_claude as A  # noqa: E402


def gemini_plan(melody, chart):
    return A.ROOT / "accompaniments" / "gemini" / f"{melody.stem}.{chart.get('source', 'unknown')}.json"


if __name__ == "__main__":
    A.main(plan_for=gemini_plan, author="gemini")
