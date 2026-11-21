#!/usr/bin/env bash
# One-shot, re-runnable setup for prototype 02 (harmony-first).
# - orchestrator env (pyproject.toml) via uv sync
# - checks prototype 01's envs/models (AMT, PianoFlow, Pianist) exist: they are reused, not rebuilt
# - clones MelodyT5, AccoMontage2, AccoMontage, Polyffusion into models/ and builds one uv env
#   per model in envs/; downloads weights/data (all git-ignored)
# Does not stop at the first failure: prints what is missing at the end and exits non-zero then.
set -uo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
P01="$ROOT/../melody-to-performance"
mkdir -p envs models/downloads output
MISSING=()
miss() { echo "MISSING: $*" >&2; MISSING+=("$*"); }

uv sync || miss "orchestrator env (uv sync)"

# ------------------------------------------------------------ prototype 01 reuse
for e in amt pianoflow pianist; do
  [ -x "$P01/envs/$e/bin/python" ] || miss "prototype-01 env envs/$e (run ../melody-to-performance/setup.sh)"
done
[ -d "$P01/models/anticipation" ] || miss "prototype-01 models/anticipation (run ../melody-to-performance/setup.sh)"
[ -f "$P01/models/PianistTransformer/models/sft/model.safetensors" ] || miss "prototype-01 Pianist weights"
ls "$P01"/examples/*.mid >/dev/null 2>&1 || miss "prototype-01 examples/*.mid"

clone() { [ -d "models/$2" ] || git clone --depth 1 "https://github.com/$1.git" "models/$2" || miss "clone $1"; }
clone sanderwood/melodyt5 melodyt5
clone billyblu2000/AccoMontage2 AccoMontage2
clone zhaojw1998/AccoMontage AccoMontage
clone aik2mlj/polyffusion polyffusion

venv() { [ -x "envs/$1/bin/python" ] || uv venv --python "$2" "envs/$1"; }

# ------------------------------------------------------------------- MelodyT5
# upstream pins py3.7 / torch 1.13+cu116 / transformers 4.18; a modern CPU torch works with
# transformers 4.30 (steps/harmonize_melodyt5.py drops GPT-2's causal-mask buffers when loading).
venv melodyt5 3.10
uv pip install --python envs/melodyt5/bin/python \
  "torch>=2.1" "transformers==4.30.2" samplings unidecode music21 "numpy<2" pretty_midi psutil \
  || miss "MelodyT5 env"
if [ ! -f models/melodyt5/weights.pth ]; then
  curl -fL -o models/melodyt5/weights.pth https://huggingface.co/sander-wood/melodyt5/resolve/main/weights.pth \
    || { rm -f models/melodyt5/weights.pth; miss "MelodyT5 weights.pth (HF sander-wood/melodyt5)"; }
fi
if [ ! -f models/melodyt5/random_model/config.json ]; then  # README step 4 (SHARE_WEIGHTS=True)
  (cd models/melodyt5 && "$ROOT/envs/melodyt5/bin/python" random_model.py) || miss "MelodyT5 random_model"
fi

# --------------------------------------------------------------- AccoMontage2
# chord module only; its data files (chorderator/static/*.pnt, *.pcls, *.mdch) ship in the repo.
venv accomontage2 3.10
uv pip install --python envs/accomontage2/bin/python \
  "torch>=2.1" "numpy<2" "pandas<2.2" openpyxl tqdm matplotlib six pretty_midi tensorboard psutil \
  || miss "AccoMontage2 env"
for f in source_base.pnt representatives.pcls dict.pcls001 transition_score.mdch minor_score.mdch; do
  [ -f "models/AccoMontage2/chorderator/static/$f" ] || miss "AccoMontage2 data chorderator/static/$f (Google Drive folder in its README)"
done

# ---------------------------------------------------------------- AccoMontage
venv accomontage 3.10
uv pip install --python envs/accomontage/bin/python \
  "torch>=2.1" "numpy<2" scipy "pandas<2.2" openpyxl pretty_midi tqdm mir_eval joblib librosa tensorboard pydub psutil \
  || miss "AccoMontage env"
venv tools 3.11
uv pip install --python envs/tools/bin/python gdown || miss "gdown (tools env)"
if [ ! -f models/AccoMontage/checkpoints/model_master_final.pt ]; then
  [ -f models/downloads/accomontage_checkpoints.zip ] || \
    envs/tools/bin/gdown 1EPj-O4dR3EWiv1kjoBo0EzM_yNoK6tNt -O models/downloads/accomontage_checkpoints.zip
  unzip -q -o models/downloads/accomontage_checkpoints.zip -d models/AccoMontage/ \
    || miss "AccoMontage checkpoints.zip (Google Drive id 1EPj-O4dR3EWiv1kjoBo0EzM_yNoK6tNt)"
fi
for f in phrase_data.npz edge_weights.npz model_master_final.pt pop909_quadraple_meters_index.xlsx; do
  [ -f "models/AccoMontage/checkpoints/$f" ] || miss "AccoMontage checkpoints/$f"
done

# ---------------------------------------------------------------- Polyffusion
venv polyffusion 3.10
grep -v -E "^(python==|wandb)" models/polyffusion/requirements.txt > models/downloads/polyffusion-req.txt
uv pip install --python envs/polyffusion/bin/python -r models/downloads/polyffusion-req.txt psutil \
  && uv pip install --python envs/polyffusion/bin/python --no-deps \
       -e models/polyffusion/polyffusion -e models/polyffusion/polyffusion/chord_extractor \
       -e models/polyffusion/polyffusion/mir_eval \
  || miss "Polyffusion env"
# Weights are on the authors' SharePoint only (README links). In Nov 2026 every link answered
# "Sorry, you cannot access this document", so they cannot be fetched here. If you obtain them:
#   trained sdf_chd8bar run -> models/polyffusion/result/<run>/{params.yaml,chkpts/weights.pt}
#   pretrained models       -> models/polyffusion/polyffusion/pretrained/chd8bar/weights.pt (etc.)
ls models/polyffusion/result/*/chkpts/weights*.pt >/dev/null 2>&1 \
  || ls models/polyffusion/result/*/*/chkpts/weights*.pt >/dev/null 2>&1 \
  || miss "Polyffusion trained checkpoint (SharePoint, access refused) -> models/polyffusion/result/"
[ -f models/polyffusion/polyffusion/pretrained/chd8bar/weights.pt ] \
  || miss "Polyffusion pretrained chord encoder (SharePoint, access refused) -> polyffusion/pretrained/chd8bar/weights.pt"

# ------------------------------------------------------------------ SoundFont
SOUNDFONT="${SOUNDFONT:-/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2}"
[ -f "$SOUNDFONT" ] && echo "SoundFont ok: $SOUNDFONT" || miss "SoundFont at $SOUNDFONT (set SOUNDFONT=...)"

echo
if [ ${#MISSING[@]} -eq 0 ]; then
  echo "setup done: all envs and models present"
else
  echo "setup finished with ${#MISSING[@]} missing item(s):"
  printf '  - %s\n' "${MISSING[@]}"
  echo "Models with missing pieces are reported as failing by smoke_test.py / run.py; the rest still run."
  exit 1
fi
