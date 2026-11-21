#!/usr/bin/env bash
# MIDI -> WAV with FluidSynth.
#   steps/to_wav.sh IN.mid OUT.wav [SOUNDFONT]
# SoundFont: 3rd arg, else $SOUNDFONT, else the user's GeneralUser GS.
# FluidSynth only reads SF2/SF3; for other sample libraries open the MIDI in a DAW.
set -euo pipefail
IN="$1"; OUT="$2"
SF="${3:-${SOUNDFONT:-/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2}}"
[ -f "$SF" ] || { echo "SoundFont not found: $SF (set SOUNDFONT or pass --soundfont)" >&2; exit 2; }
FLUIDSYNTH="${FLUIDSYNTH:-$(command -v fluidsynth || echo /opt/homebrew/bin/fluidsynth)}"
# -n no MIDI in, -i no shell, -q quiet, -F render to file, -r sample rate, -g gain
"$FLUIDSYNTH" -niq -g 0.8 -r 44100 -F "$OUT" "$SF" "$IN"
[ -s "$OUT" ] || { echo "fluidsynth wrote no audio: $OUT" >&2; exit 3; }
