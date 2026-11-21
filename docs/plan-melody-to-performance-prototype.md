---
title: 'Prototype: melody → AMT accompaniment → expressive piano rendering'
type: feature
ticket: ''
created: '2026-11-21'
status: built
baseline_revision: 'fae8a805e3bcac60970b340d0fbb0e86765d747f'
route: full
route_source: auto
risk: low
review: quick
review_source: pinned
lenses_ran: [quick]
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
- [x] `prototype/melody-to-performance/setup.sh` -- create the three uv envs (`envs/amt`, `envs/pianoflow`, `envs/pianist`), clone/download models and the SoundFont into `models/` -- one reproducible setup step
- [x] `prototype/melody-to-performance/examples/make_examples.py` + 3 `.mid` -- three short public-domain melodies in different styles (e.g. Ode to Joy, Greensleeves, 望春風 or another PD folk tune), single track, quantized -- inputs for the drop-bar test
- [x] `prototype/melody-to-performance/steps/amt_accompany.py` -- melody MIDI → accompaniment MIDI; `--prompt none|chords` (chords = a few bars of simple block chords in the melody's key as history) -- the two prompt variants the plan requires
- [x] `prototype/melody-to-performance/steps/merge_piano.py` -- remap all accompaniment to piano, merge with melody into one track → `plain.mid` -- renderers expect single-track piano
- [x] `prototype/melody-to-performance/steps/render_pianoflow.py`, `steps/render_pianist.py` -- score MIDI → performance MIDI -- the two options compared
- [x] `prototype/melody-to-performance/steps/to_wav.sh` -- FluidSynth MIDI → WAV
- [x] `prototype/melody-to-performance/steps/fidelity.py` -- compare pitch sequence (onset-ordered) of input vs rendered; report % notes kept / added / dropped -- the plan's note-fidelity check
- [x] `prototype/melody-to-performance/smoke_test.py` -- run each model on a short clip on CPU then MPS, record wall time, peak RSS, success, fidelity → `output/smoke-test.md`
- [x] `prototype/melody-to-performance/run.py` -- `uv run run.py examples/<name>.mid` orchestrates the above, writes outputs and `run-notes.md` (timings, failures, fidelity)
- [x] `prototype/melody-to-performance/README.md` -- setup, usage, output layout, licences, known limitations (zh-TW)

**Acceptance Criteria:**
- Given setup has run, when `uv run smoke_test.py` runs, then `output/smoke-test.md` lists, for AMT, PianoFlow and Pianist Transformer, CPU and MPS each as works/fails with time and an error excerpt on failure.
- Given an example melody, when `uv run run.py examples/<name>.mid` runs, then the output folder holds every version listed in the I/O matrix that its model could produce, each WAV audible in a player, and `run-notes.md` names any missing version and why.
- Given a rendered MIDI, when fidelity runs, then run-notes reports how many input notes were kept, changed or dropped.

## Implementation Notes

- **SoundFont (coordinator instruction, 2026-11-21):** no SoundFont is downloaded. `steps/to_wav.sh` uses the user's existing `/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2` by path (not copied into the repo), overridable via `run.py --soundfont PATH`, `SOUNDFONT` env var, or the script's 3rd arg; alternative `/Applications/MuseScore 4.app/Contents/Resources/sound/MS Basic.sf3`. `setup.sh` only checks the file exists. README notes that output MIDI can be dragged into Logic/GarageBand/Vienna Synchron Player, since FluidSynth only reads SF2/SF3. A Salamander SF2 download had been started and was deleted.
- **Orchestrator env:** `pyproject.toml` (pretty_midi, numpy, psutil) so `uv run run.py` / `uv run smoke_test.py` work; model envs are `envs/{amt,pianoflow,pianist}` created with `uv venv` + `uv pip`. Added `prototype/**/envs/` to the root `.gitignore`.
- **AMT:** melody on program 1 (bright piano) as `controls`; chord prompt on program 0. Chord history is ~2 bars, extended to 3 when 2 bars < 4 s (issue #18 reports ~5 s of history helps); I–IV–V–I stretched over the bars, harmonic rhythm half-bar (even meters) or bar (odd). Key from MIDI key signature, else Krumhansl–Kessler. Installed from requirements minus matplotlib/midi2audio; `numpy<2` for transformers 4.29.2.
- **Merge:** besides remapping to program 0, accompaniment is snapped to the melody's 16th-note grid (AMT is 10 ms real time; renderers want a quantized score), drum notes are dropped, duplicates of melody notes are dropped, same-pitch overlaps trimmed.
- **PianoFlow:** `num_samples=1` (default is 8) and fixed seed; writes `perf_midi_sus`. MPS failed on float64 → small local shim `mps_float64_shim` in `render_pianoflow.py` (casts float64 arrays to float32 before `.to(mps)`), only applied for MPS.
- **Pianist Transformer:** `render_pianist.py` reproduces upstream `src/inference/inference.py` (bf16, temperature 1.0, top_p 0.95, `map_midi`) with input/output/device args instead of the hard-coded `data/midis/testset/score/0.mid`; falls back to the raw performance if `map_midi` asserts. Installed requirements minus GUI/wandb/modelscope.
- **Fidelity:** onset-ordered pitch sequences (50 ms chord window, pitch-sorted) aligned with difflib → kept/changed/dropped/added; plus an order-free per-pitch count so pure re-orderings are not mistaken for note changes.
- **Verification run (2026-11-21, CPU):** `./setup.sh` re-run clean; `uv run smoke_test.py` → all 6 model×device cells work (PianoFlow MPS only after the shim); MPS is not faster for the small renderers and AMT s/note is lower on MPS but sample counts differ. `uv run run.py` on all three examples → 6 MIDI + 6 WAV each (RMS −25…−37 dBFS, all non-silent). AMT takes 50–250 s per variant on CPU, peak ~3.4 GB. Both renderers keep every pitch (order-free count identical in all 6 renders); PianoFlow's sequence diffs are only chord re-orderings. RENDERER_FAILS and MULTI_TRACK_INPUT checked with a 2-track clip and the pianist env made unavailable: 4/6 written, failures + warning in run-notes, exit 0.
- **Observations for listening:** PianoFlow picks its own tempo and ignores the score tempo (same output length for a score at 60 or 240 bpm); for Ode to Joy it plays 1.6–3.6× slower than written (chords: 108 s for a 29 s score), for Jasmine slightly faster. Pianist Transformer tends to play 10–30 % faster. AMT without a prompt picks non-piano instruments (harpsichord, guitar, recorder, violin, electric bass) and is sparse on Ode to Joy (35 notes in 29 s); with the chord prompt it stays on piano (program 0) and is denser.

## Plan Change Log

## Review Triage Log

### 2026-11-21 — Review pass
- verdicts: 11 findings — high 0, medium 1, low 9, false 1, maybe-false 0
- findings:
  - `[medium]` `[patch]` run.py counts a version only when its WAV exists, so FluidSynth failing everywhere exits 1 with all MIDI written — confirmed at run.py:131-141; patched to count MIDI-produced versions and report WAV failures separately.
  - `[low]` `[reject]` smoke_test.py fidelity call not wrapped in try/except — real but compare() parsed every render so far; adding a guard is new branching for an unlikely case.
  - `[low]` `[patch]` smoke_test.py renderer-input label hard-codes "AMT-cpu" — confirmed at smoke_test.py:96; patched to print the device that produced the accompaniment.
  - `[low]` `[patch]` setup.sh:57 `test -f && echo` never fails under set -e — confirmed; patched to exit non-zero with a message.
  - `[low]` `[patch]` setup.sh header says a SoundFont is downloaded — confirmed stale; comment updated.
  - `[false]` `[reject]` example melodies not quantized / duplicate-removal drift — note-offs at 0.95 × duration are a deliberate articulation gap, onsets are on the grid; merge matches on round(start, 3), which absorbs float drift, and both renderers kept 28/28 and all-pitch counts in every run.
  - `[low]` `[patch]` noprompt: upstream generate() clips controls before 50 ms, so a melody note at t=0 is unseen by AMT — confirmed at anticipation/sample.py:130; documented in README 已知限制 (behavioural fix would need shifting timelines, beyond a trivial patch).
  - `[low]` `[reject]` detect_key NaN on single-pitch-class melodies — only on the no-key-signature fallback with a degenerate melody; all examples carry key signatures; guard would add branching.
  - `[low]` `[reject]` unused `--max-seconds` option in amt_accompany.py — harmless, still a usable CLI option for single-step runs.
  - `[low]` `[patch]` run.py imports unused `summary` — removed.
  - `[low]` `[reject]` default SoundFont path duplicated in runner.py, to_wav.sh and setup.sh — throwaway prototype, user-specific path by instruction; consolidating across bash and Python adds plumbing.

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

## Auto Run Result

**Summary:** Built a CLI prototype under `prototype/melody-to-performance/`: melody MIDI → AMT accompaniment (`noprompt` / `chords` variants) → single-track piano `plain.mid` → SyMuPe/PianoFlow and Pianist Transformer renders → WAV via FluidSynth with the user's GeneralUser GS SoundFont. Smoke test and all three examples ran: 6 MIDI + 6 WAV per melody.

**Files changed:**
- `.gitignore` — also ignore `prototype/**/envs/`.
- `prototype/melody-to-performance/setup.sh` — creates the orchestrator env plus `envs/{amt,pianoflow,pianist}`, clones models, downloads weights, checks the SoundFont path.
- `prototype/melody-to-performance/pyproject.toml`, `uv.lock` — orchestrator env.
- `prototype/melody-to-performance/run.py` — end-to-end pipeline and `run-notes.md`.
- `prototype/melody-to-performance/smoke_test.py` — model × CPU/MPS check → `output/smoke-test.md`.
- `prototype/melody-to-performance/steps/*` — AMT accompaniment, piano merge and quantize, two renderers, WAV render, fidelity check, shared helpers.
- `prototype/melody-to-performance/examples/*` — three public-domain melodies (Ode to Joy, Greensleeves, 茉莉花) and their generator.
- `prototype/melody-to-performance/README.md` — zh-TW usage, layout, licences, limitations, first observations.

**Review findings:** 11 findings from the quick lens.
- Patched (6): 1 medium (exit code counted WAVs instead of MIDI); 5 low (smoke-test label, setup.sh weights check, stale setup header, unused import, README note on AMT dropping controls before 50 ms).
- Deferred: none.
- Rejected (5): the unguarded smoke-test fidelity call, `detect_key` NaN, the unused `--max-seconds` option and the duplicated SoundFont path (all low and unlikely, or the fix would add complexity); the melody-quantization claim (false — onsets are on the grid and both renderers kept every note). Reasons are in the Review Triage Log.

**Follow-up review recommended:** false. Patched: high 0, medium 1, low 5.

**Verification:**
- `./setup.sh` re-run: clean.
- `uv run smoke_test.py`: all six model × device cells work, before and after the patches.
- `uv run run.py` on all three examples: 6/6 versions each, every WAV non-silent (−25 to −37 dBFS).
- Failure paths: a two-track clip with the Pianist env made unavailable wrote 4/6 versions and exited 0; `--soundfont /nonexistent` reported 6/6 MIDI and 0/6 WAV and exited 0.
- `bash -n setup.sh`: OK.
- `git add -n`: stages no weights, envs, WAVs or SoundFonts.

**Matrix test audit:** the plan forbids tests beyond the smoke test. The I/O matrix rows were checked by the manual runs above, not by automated tests.

**Residual risks:**
- The missing-weights branch in `setup.sh` was never triggered.
- The output folders were produced before the patches (MIDI-count reporting only).
- PianoFlow ignores the score tempo, which skews the listening comparison.
- The `chords` prompt is a fixed I–IV–V–I progression.
- The GeneralUser GS and MS Basic licences in the README were written from memory and not checked.
