---
title: 'Prototype: melody → AMT accompaniment → expressive piano rendering'
type: feature
ticket: ''
created: '2026-11-21'
status: in-progress
baseline_revision: 'fae8a805e3bcac60970b340d0fbb0e86765d747f'
route: full
route_source: auto
risk: low
review: ''
review_source: ''
lenses_ran: []
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/docs/prototype-plan-melody-to-performance/prototype-plan-melody-to-performance.md'
  - '{project-root}/docs/research-prototype-model-check/research-prototype-model-check.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** The user (a music psychologist) wants to learn whether off-the-shelf open models, wired together locally on a Mac M3 Pro 18GB (no CUDA), can turn a single melody into piano music they would share. Nothing is built yet.

**Approach:** A throwaway CLI prototype: one command takes a single-melody MIDI, generates accompaniment with AMT (two prompt variants), merges to one piano track, renders it with SyMuPe/PianoFlow and Pianist Transformer, and writes MIDI + WAV for each version. A smoke test runs first to record speed, CPU/MPS viability and note fidelity.

## Boundaries & Constraints

**Always:** Everything under `prototype/melody-to-performance/`. Each model in its own uv-managed env (they have conflicting pins); the orchestrator calls them via subprocess. CPU first, try MPS (`PYTORCH_ENABLE_MPS_FALLBACK=1`) and record result. Model weights, cloned model repos, soundfonts and audio stay git-ignored (`models/`, `output/`, `*.wav`, `*.sf2`, see root `.gitignore`). Research/non-commercial use only. If one model will not install or run after reasonable effort, record why in the run notes and continue with the others — do not hard-fix upstream code beyond small local shims.

**Never:** No fine-tuning, transcription, MusicXML output or GUI. No tests beyond the smoke test. No parameter tuning (use defaults). Do not use Aria. Do not reuse any old melody generator. Do not commit weights or audio.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `examples/<name>.mid`, one melody track | `output/<name>/{noprompt,chords}/{plain,pianoflow,pianist}.{mid,wav}` (6 MIDI + 6 WAV) + `output/<name>/run-notes.md` | No error expected |
| RENDERER_FAILS | one renderer env broken | other versions still written; run-notes records failure + error excerpt | continue, non-zero exit only if all fail |
| MULTI_TRACK_INPUT | input MIDI with >1 non-drum track | uses the first non-drum track as melody, warns | warning in run-notes |
| AMT_NON_PIANO | AMT emits other instruments | all accompaniment notes remapped to piano (program 0) before merge | none |

</intent-contract>

## Code Map

Greenfield; no existing code. External facts (from the model-check research, accessed 2026-11-21):

- AMT: `github.com/jthickstun/anticipation`, HF `stanford-crfm/music-medium-800k` (~360M, Apache-2.0). Pin `transformers==4.29.2` fails on Python 3.12 → use Python 3.10 env. Call `anticipation.sample.generate(model, start_time, end_time, inputs=history, controls=melody, top_p=.98)` directly; README pattern: `events, melody = extract_instruments(events, [instr])`, then `ops.combine(accompaniment, melody)`; conversion via `anticipation.convert.midi_to_events` / `events_to_midi`. Melody must sit on its own MIDI program. `humaneval/*.py` hard-code `.cuda()` — don't use. No KV cache → slow; keep example melodies ≈20–30 s.
- SyMuPe/PianoFlow: `pip install -U symupe` (+ manual `numba`, `scipy -U`, issue #9), HF `SyMuPe/PianoFlow-base` (CC BY-NC-SA). API: `AutoGenerator.from_pretrained(..., device=...)`, `generator.perform_score("score.mid", ...)`; input is a quantized score MIDI, single track. No emotion-text API.
- Pianist Transformer: clone `github.com/yhj137/PianistTransformer` into `models/`; Python 3.11, `torch==2.7.1`; `python -m src.utils.download_model --source huggingface`; inference via `script/inference.sh` (writes `data/midis/testset/inference/0.mid`) — wrap it, reading its script to find how to pass an input file.
- FluidSynth already at `/opt/homebrew/bin/fluidsynth`. Need a free piano SoundFont downloaded to `models/` (state its licence in README).

## Tasks & Acceptance

**Execution:**
- [ ] `prototype/melody-to-performance/setup.sh` -- create the three uv envs (`envs/amt`, `envs/pianoflow`, `envs/pianist`), clone/download models and the SoundFont into `models/` -- one reproducible setup step
- [ ] `prototype/melody-to-performance/examples/make_examples.py` + 3 `.mid` -- three short public-domain melodies in different styles (e.g. Ode to Joy, Greensleeves, 望春風 or another PD folk tune), single track, quantized -- inputs for the drop-bar test
- [ ] `prototype/melody-to-performance/steps/amt_accompany.py` -- melody MIDI → accompaniment MIDI; `--prompt none|chords` (chords = a few bars of simple block chords in the melody's key as history) -- the two prompt variants the plan requires
- [ ] `prototype/melody-to-performance/steps/merge_piano.py` -- remap all accompaniment to piano, merge with melody into one track → `plain.mid` -- renderers expect single-track piano
- [ ] `prototype/melody-to-performance/steps/render_pianoflow.py`, `steps/render_pianist.py` -- score MIDI → performance MIDI -- the two options compared
- [ ] `prototype/melody-to-performance/steps/to_wav.sh` -- FluidSynth MIDI → WAV
- [ ] `prototype/melody-to-performance/steps/fidelity.py` -- compare pitch sequence (onset-ordered) of input vs rendered; report % notes kept / added / dropped -- the plan's note-fidelity check
- [ ] `prototype/melody-to-performance/smoke_test.py` -- run each model on a short clip on CPU then MPS, record wall time, peak RSS, success, fidelity → `output/smoke-test.md`
- [ ] `prototype/melody-to-performance/run.py` -- `uv run run.py examples/<name>.mid` orchestrates the above, writes outputs and `run-notes.md` (timings, failures, fidelity)
- [ ] `prototype/melody-to-performance/README.md` -- setup, usage, output layout, licences, known limitations (zh-TW)

**Acceptance Criteria:**
- Given setup has run, when `uv run smoke_test.py` runs, then `output/smoke-test.md` lists, for AMT, PianoFlow and Pianist Transformer, CPU and MPS each as works/fails with time and an error excerpt on failure.
- Given an example melody, when `uv run run.py examples/<name>.mid` runs, then the output folder holds every version listed in the I/O matrix that its model could produce, each WAV audible in a player, and `run-notes.md` names any missing version and why.
- Given a rendered MIDI, when fidelity runs, then run-notes reports how many input notes were kept, changed or dropped.

## Implementation Notes

## Plan Change Log

## Review Triage Log

## Design Notes

Prompt variant "chords": history = block chords (I–IV–V–I or I–V) over the first ~2 bars, on a piano program distinct from the melody's program, so AMT continues accompaniment from there; generation spans from end of history to end of melody. Variant "none": empty history.

## Verification

**Commands:**
- `cd prototype/melody-to-performance && ./setup.sh` -- expected: three envs created, models present in `models/`
- `uv run smoke_test.py` -- expected: `output/smoke-test.md` written with all three models
- `uv run run.py examples/<each>.mid` for all three examples -- expected: outputs per I/O matrix; run-notes written
- `git status --short` -- expected: no weights, WAVs or SoundFonts staged

**Manual checks (if no CLI):**
- Open one WAV per version and confirm it is audible piano (agent: check non-silent with a duration/RMS probe).
