# Lead check (lead, r1): Pianist Transformer spot-check — 2026-11-21

1. Claim: The rendering GUI loads "the score MIDI file you want to render"; no MusicXML mentioned. Source: https://github.com/yhj137/PianistTransformer README · accessed 2026-11-21 · high · capability
2. Claim: README: "A standard CPU is sufficient, though a GPU will accelerate the process"; install line for "macOS or CPU-only" is pip install torch==2.7.1; Python 3.11. No MPS mention. Same source · high · compat
3. Claim: Output is an editable MIDI where "expressive timing variations are represented as a dynamic tempo curve", preserving velocity, articulation, pedal. Note-for-note preservation is not stated explicitly (tempo-curve representation suggests notes stay on score grid — inference). Same source · med · capability
4. Claim: HF weights yhj137/pianist-transformer-rendering carry license tag apache-2.0; card says "The full pipeline is required for correct usage" and asks for citation. Source: https://huggingface.co/yhj137/pianist-transformer-rendering · accessed 2026-11-21 · high · licence
5. CLI: python -m src.utils.download_model --source huggingface; sh script/inference.sh → data/midis/testset/inference/0.mid. GUI: python -m src.gui.ui (PyQt5, pygame). Source: README · high · capability
