#!/usr/bin/env bash
# One-shot, re-runnable setup for the melody-to-performance prototype.
# Creates three isolated uv envs (conflicting pins), clones/downloads models
# into models/ (all git-ignored), and checks that the existing SoundFont path exists
# (no SoundFont is downloaded).
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
mkdir -p envs models output

export HF_HOME="$ROOT/models/hf-cache"   # keep HF weights inside models/

# ---------------------------------------------------------------- orchestrator
# run.py / smoke_test.py use the project env defined by pyproject.toml.
uv sync

# ---------------------------------------------------------------- AMT (py3.10)
if [ ! -d models/anticipation ]; then
  git clone --depth 1 https://github.com/jthickstun/anticipation.git models/anticipation
fi
if [ ! -x envs/amt/bin/python ]; then
  uv venv --python 3.10 envs/amt
fi
# requirements.txt pins transformers==4.29.2 (needs py<=3.11); drop matplotlib/midi2audio pins (unused here)
uv pip install --python envs/amt/bin/python \
  "torch>=2.0.1" "transformers==4.29.2" "mido==1.2.10" "numpy<2" "tqdm" "pretty_midi" "psutil"
uv pip install --python envs/amt/bin/python --no-deps -e models/anticipation
envs/amt/bin/python -c "
from transformers import AutoModelForCausalLM
AutoModelForCausalLM.from_pretrained('stanford-crfm/music-medium-800k')
print('AMT weights ok')"

# ---------------------------------------------------------- PianoFlow (py3.11)
if [ ! -x envs/pianoflow/bin/python ]; then
  uv venv --python 3.11 envs/pianoflow
fi
# symupe misses numba + needs newer scipy (SyMuPe issue #9)
uv pip install --python envs/pianoflow/bin/python -U symupe numba scipy pretty_midi psutil
envs/pianoflow/bin/python -c "
from symupe import AutoGenerator
AutoGenerator.from_pretrained('SyMuPe/PianoFlow-base', device='cpu')
print('PianoFlow weights ok')"

# ------------------------------------------------- Pianist Transformer (py3.11)
if [ ! -d models/PianistTransformer ]; then
  git clone --depth 1 https://github.com/yhj137/PianistTransformer.git models/PianistTransformer
fi
if [ ! -x envs/pianist/bin/python ]; then
  uv venv --python 3.11 envs/pianist
fi
# requirements.txt minus GUI (PyQt5/pygame), wandb and modelscope (not needed for inference)
uv pip install --python envs/pianist/bin/python \
  "torch==2.7.1" "transformers==4.54.0" "datasets==4.0.0" "accelerate==1.10.1" \
  "miditoolkit==1.0.1" "partitura==1.7.0" "huggingface_hub==0.35.3" pretty_midi psutil
if [ ! -f models/PianistTransformer/models/sft/model.safetensors ]; then
  (cd models/PianistTransformer && "$ROOT/envs/pianist/bin/python" -m src.utils.download_model --source huggingface)
fi
if [ -f models/PianistTransformer/models/sft/model.safetensors ]; then
  echo "Pianist weights ok"
else
  echo "ERROR: Pianist weights missing (models/PianistTransformer/models/sft/model.safetensors)" >&2
  exit 1
fi

# ------------------------------------------------------------------ SoundFont
# Not downloaded: use the user's existing SoundFont by path (SOUNDFONT env var
# overrides; see steps/to_wav.sh). Just check it exists.
SOUNDFONT="${SOUNDFONT:-/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2}"
if [ -f "$SOUNDFONT" ]; then
  echo "SoundFont ok: $SOUNDFONT"
else
  echo "WARNING: SoundFont not found at $SOUNDFONT — set SOUNDFONT=/path/to/file.sf2 (or .sf3)" >&2
fi

# ------------------------------------------------------------------- examples
uv run examples/make_examples.py

echo "setup done"
