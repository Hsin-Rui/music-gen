"""Paths shared by the orchestrator scripts; reuses prototype 01's runner (subprocess + timing/RSS)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # prototype/harmony-first
P01 = ROOT.parent / "melody-to-performance"            # prototype 01
STEPS = ROOT / "steps"
P01_STEPS = P01 / "steps"
EXAMPLES = P01 / "examples"
LLM_CHARTS = ROOT / "harmonizations" / "llm"
OUTPUT = ROOT / "output"

sys.path.insert(0, str(P01_STEPS))
from runner import DEFAULT_SOUNDFONT, PY as P01_PY, excerpt, run, wav_stats  # noqa: E402,F401
from fidelity import compare  # noqa: E402,F401

PY = {
    "melodyt5": ROOT / "envs" / "melodyt5" / "bin" / "python",
    "accomontage2": ROOT / "envs" / "accomontage2" / "bin" / "python",
    "accomontage": ROOT / "envs" / "accomontage" / "bin" / "python",
    "polyffusion": ROOT / "envs" / "polyffusion" / "bin" / "python",
    "amt": P01_PY["amt"],
    "pianoflow": P01_PY["pianoflow"],
    "pianist": P01_PY["pianist"],
}

# harmony sources and accompaniment models, in page order
SOURCES = {
    "llm": "語言模型（Claude）",
    "melodyt5": "MelodyT5",
    "accomontage2": "AccoMontage2",
}
MODELS = {
    "amt": ("amt", "accomp_amt.py", "AMT + 和弦條件"),
    "accomontage": ("accomontage", "accomp_accomontage.py", "AccoMontage"),
    "polyffusion": ("polyffusion", "accomp_polyffusion.py", "Polyffusion"),
}
RENDERERS = {
    "pianoflow": ("pianoflow", "render_pianoflow.py", "SyMuPe/PianoFlow-base"),
    "pianist": ("pianist", "render_pianist.py", "Pianist Transformer"),
}
VERSIONS = ["plain", "pianoflow", "pianist"]
