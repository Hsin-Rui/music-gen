---
title: 'Prototype 02: harmony-first accompaniment (harmonizers × accompaniment models)'
type: feature
ticket: ''
created: '2026-11-21'
status: built
baseline_revision: '438fe4434a5cfcd345e5098bbebe70ba3cf700d2'
route: full
route_source: auto
risk: low
review: quick
review_source: pinned
lenses_ran: [quick]
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/docs/prototype-plan-harmony-first/prototype-plan-harmony-first.md'
  - '{project-root}/docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md'
  - '{project-root}/kb/experiments/prototype-01-melody-to-performance.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** In prototype 01, AMT's accompaniment had odd chords, misalignment and ugly progressions. The user wants to test whether fixing the harmony first lets off-the-shelf accompaniment models produce accompaniment that fits the melody. They also want to compare harmonizers, including an LLM.

**Approach:** A throwaway CLI prototype in `prototype/harmony-first/`, reusing prototype 01's code.
1. Three harmonizers produce chord charts for the three example melodies: MelodyT5, AccoMontage2 (4/4 only), and LLM charts that are already written.
2. Every chord chart goes to three accompaniment models: AMT with chord controls, AccoMontage and Polyffusion. Each model generates 8 samples per chart.
3. Harmonic metrics pick the best sample.
4. That sample is rendered plain, by PianoFlow and by Pianist Transformer.
5. A listening page lets the user compare everything blind.

## Boundaries & Constraints

**Always:**
- Build under `prototype/harmony-first/` on branch `prototype/harmony-first`.
- Import or call prototype 01's steps from `prototype/melody-to-performance/` (merge/quantize, renderers, `to_wav.sh`, fidelity, runner helpers) rather than copying them, and reuse its envs/models where possible.
- Give each new model its own uv env under `prototype/harmony-first/envs/`, called via subprocess.
- Run on CPU first; try MPS only if cheap.
- Use the user's SoundFont (GeneralUser GS) by path.
- Keep weights, envs, model clones, data downloads and audio git-ignored.
- Use the LLM charts in `prototype/harmony-first/harmonizations/llm/*.json` as given; never regenerate or edit them.
- If a model will not install or run after reasonable effort (small local shims are fine), record why in run notes and continue with the rest.

**Never:**
- No fine-tuning or training.
- No D3PIA or FGG.
- No block-chord intro variant.
- No tests beyond a smoke test.
- No parameter tuning beyond the sample count (8) and seeds.
- Never commit weights or audio.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 3 example melodies; harmonizers + accompaniment models all run | `output/<melody>/harmony/<source>.{json,mid,wav}` (melody + block chords per chart); `output/<melody>/<source>/<accomp>/{plain,pianoflow,pianist}.{mid,wav}` + `candidates/` (8 scored samples) + `run-notes.md`; `output/player.html` | No error expected |
| NON_4_4 | greensleeves (3/4) with AccoMontage2 | AccoMontage2 harmonization skipped for it, noted in run-notes; jasmine 2/4 merged into 4/4 bars for AccoMontage2 and its chords mapped back | note in run-notes |
| MODEL_UNAVAILABLE | a harmonizer or accompaniment model fails to install/run | its cells are marked missing with reason; all other cells still produced | continue; non-zero exit only if nothing produced |
| CHART_FORMAT | every chord chart, whatever its source | normalised to the same JSON shape as the LLM charts (`bars: [[chord, beats], …]`), validated so each bar sums to the meter | invalid chart → that source marked failed |

</intent-contract>

## Code Map

Reuse (read-only, call or import; don't modify unless a tiny shared fix is unavoidable):
- `prototype/melody-to-performance/steps/merge_piano.py` -- remap/quantize accompaniment and merge with melody into a single piano track → `plain.mid`.
- `prototype/melody-to-performance/steps/render_pianoflow.py`, `steps/render_pianist.py` -- renderers. Their envs are `prototype/melody-to-performance/envs/{pianoflow,pianist}`.
- `prototype/melody-to-performance/steps/amt_accompany.py` -- AMT wrapper, with piano-only logit masking (`restrict_to_piano`), `to_tokens`, `MELODY_PROGRAM = 1` and controls. Its env is `envs/amt`; the HF cache is in `models/hf-cache` (see `steps/runner.py`, which sets `HF_HOME`).
- `prototype/melody-to-performance/steps/{to_wav.sh,fidelity.py,runner.py,midi_utils.py}` -- WAV render, note fidelity, subprocess runner with timing/RSS, melody track pick.
- `prototype/melody-to-performance/make_player.py` -- listening page pattern (blind mode, one-at-a-time playback, zh-TW explainer). Extend the pattern in a new page builder.
- `prototype/melody-to-performance/examples/*.mid` -- inputs (ode_to_joy D major 4/4 16 bars; greensleeves A minor 3/4 17 bars incl. pickup bar; jasmine F 2/4 14 bars).
- `prototype/harmony-first/harmonizations/llm/*.json` -- LLM charts: `bars` = per-bar list of `[chord_symbol, beats]`; bar 1 = first MIDI bar.

External facts (R3 research, README level, unverified on Mac):
- MelodyT5: github.com/sanderwood/melodyt5, HF `sander-wood/melodyt5` `weights.pth` (MIT). ABC in → ABC with quoted chord symbols; task prompt `%%harmonization`. Pins Python 3.7/torch 1.13 cu116; try a modern torch CPU env. Convert MIDI ↔ ABC with music21.
- AccoMontage2: github.com/billyblu2000/AccoMontage2 (MIT). API `set_melody`, `set_meta(tonic, mode)`, `set_segmentation('A8A8B8B8')` (4/8-bar phrases, 4/4 only), `generate_save(folder)` → `chord_gen.mid`. It needs data files from Google Drive in `chorderator/static`. Read its chords from chord_gen.mid / JSON log.
- AccoMontage: github.com/zhaojw1998/AccoMontage (MIT). Melody + chord MIDI → piano accompaniment; data/ckpt on Google Drive.
- Polyffusion: github.com/aik2mlj/polyffusion (MIT). Chord-conditioned, melody inpainting `--inpaint_type=above`; checkpoints on SharePoint.
- AMT chord conditioning: put the chart's block chords on a third program as extra `controls` with the melody; drop that program from the output.

## Tasks & Acceptance

**Execution:**
- [x] `prototype/harmony-first/setup.sh` -- envs + clones + data/ckpt downloads for MelodyT5, AccoMontage2, AccoMontage, Polyffusion; checks that the prototype-01 envs exist -- reproducible setup
- [x] `prototype/harmony-first/steps/chart.py` -- chord-symbol parsing, chart validation, chart ↔ block-chord MIDI, chart → per-beat chord labels -- one shared chart format
- [x] `prototype/harmony-first/steps/harmonize_melodyt5.py`, `steps/harmonize_accomontage2.py` -- melody MIDI → normalised chart JSON (AccoMontage2: skip non-4/4, merge 2/4 pairs) -- harmonizers
- [x] `prototype/harmony-first/steps/accomp_amt.py`, `steps/accomp_accomontage.py`, `steps/accomp_polyffusion.py` -- melody + chart → N accompaniment MIDI samples -- accompaniment models
- [x] `prototype/harmony-first/steps/metrics.py` -- CTnCTR, PCS, out-of-key ratio, melody–accompaniment dissonant-overlap ratio, combined score -- ranking
- [x] `prototype/harmony-first/smoke_test.py` -- each new model on a short clip; works/fails, time, RSS → `output/smoke-test.md`
- [x] `prototype/harmony-first/run.py` -- orchestrates harmonize → chord audio → accompaniment ×8 → rank → merge → render → WAV for one melody; writes run-notes.md/json -- the pipeline
- [x] `prototype/harmony-first/make_player.py` -- page with a harmony section (melody + block chords per source) and a cross grid (source × model × 3 versions) with scores, blind mode and a zh-TW explainer
- [x] `prototype/harmony-first/README.md` -- zh-TW setup, usage, layout, licences, limitations, first observations

**Acceptance Criteria:**
- Given setup has run, when `uv run smoke_test.py` runs, then `output/smoke-test.md` lists MelodyT5, AccoMontage2, AccoMontage and Polyffusion as works/fails with time and an error excerpt.
- Given the three melodies, when `uv run run.py examples/<name>.mid` runs for each, then every cell the matrix says should exist is either produced or listed as missing with a reason in run-notes.
- Given a cell's 8 candidates, when ranking runs, then run-notes shows each candidate's four metrics and combined score, and which one was chosen.
- Given outputs exist, when `uv run make_player.py` runs, then `output/player.html` plays the harmony section and the cross grid, with blind mode working.

## Implementation Notes

- Results: 16/24 cells produced (Polyffusion 0/8, no weights; greensleeves × AccoMontage2 skipped as planned). 59 WAVs, none silent. Renderers kept every pitch (multiset equal in all 32 renderings).
- Polyffusion: env installs, wrapper `steps/accomp_polyffusion.py` written, but weights are SharePoint-only and every link returned "Sorry, you cannot access this document" (2026-11-21); no mirror on GitHub/HF. All Polyffusion cells are MODEL_UNAVAILABLE. Wrapper is untested end to end.
- Polyffusion inpaint type: upstream defines `below` as "inpaint accompaniment for melody"; the plan's `above` is the reverse, so `below` is used.
- AccoMontage2 chord-only path crashes upstream (`Pipeline.__add_textures()` missing `log`); local shim gives a default. Segmentation = consecutive 4-bar phrases; melody padded to whole phrases by holding the last note.
- AccoMontage (and Polyffusion) are also 4/4-only: 2/4 and 3/4 melodies are re-barred into 4-beat bars on the same beat grid (harmony beat-aligned, texture metre 4/4); flagged in run-notes and on the page. Chart fed directly as chord roll (no chord re-detection). CPU shims (map_location, Tensor.cuda no-op).
- AccoMontage needs phrase-selection randomness > 0 for 8 distinct samples; 0.1 (upstream demo notebook value) used. Only parameter touched besides sample count/seeds.
- AMT: chords as extra controls on program 48; empty samples (AMT wrote nothing) are kept as 0-note candidates and not ranked. AMT ran on MPS for the full runs: CPU with chord controls took 5-8 min/sample under load (~1 min on MPS); everything else CPU.
- MelodyT5: modern torch + transformers 4.30.2; causal-mask buffers filtered when loading weights. Upstream default sampling params; output often sparse (few chord symbols, carried over).

## Plan Change Log

- 2026-11-21: ranking excludes candidates with fewer notes than bars (unless none qualify) — near-empty AMT samples otherwise won on PCS/dissonance. Smoke test clip is 8 bars (AccoMontage's dp_search crashes on a single phrase). Polyffusion inpaint type `below` (not `above`).

## Review Triage Log

### 2026-11-21 — Review pass
- verdicts: 11 findings — high 0, medium 2, low 7, false 0, maybe-false 2
- findings:
  - `medium` `patch` Resumed cell loses its warnings, so greensleeves LLM×AccoMontage lacked the 3/4 re-barring flag on the page — confirmed in run-notes.json; make_player now derives the flag from the melody meter for AccoMontage/Polyffusion cells.
  - `medium` `patch` AccoMontage2 log phrases concatenated without length check (ode_to_joy D4 came back 8 bars) — each phrase now cut to its segment length; error if count differs or a phrase is short.
  - `low` `patch` chart.validate accepts fractional beats that per_beat rounds — validate now rejects non-integer beat counts (checked with a 1.5/2.5 bar).
  - `maybe-false` `reject` MelodyT5 chart key "unknown" would make every candidate error out — all inputs carry key signatures; would only matter for a keyless melody; fix needs a new guard. Rejected as unlikely low.
  - `low` `patch` Any Polyffusion failure shown as "weights unavailable" — zh_reason now checks the stored error text.
  - `maybe-false` `reject` Polyffusion single-track fallback could return the melody — wrapper never runs (no weights); unreachable today; would need an end-to-end run to settle.
  - `low` `reject` Resume with a different --seed mislabels reused seeds — unlikely in practice; fix adds stored-seed bookkeeping.
  - `low` `patch` accomp_accomontage docstring contradicts remainder handling — docstring corrected.
  - `low` `patch` smoke_test docstring / README say 4 bars, default 8 — corrected to 8.
  - `low` `patch` README misstates the ranking floor — now states "fewer notes than bars are not ranked unless none qualify".
  - `low` `reject` accomp_amt melody vs metrics use different track selection on multi-track input — all inputs are single-track; fix adds branching.

## Design Notes

Chart JSON is the pivot: every harmonizer's output is converted to the LLM-chart shape, so the accompaniment models, the block-chord audio and the metrics all read one format. Block chords for the harmony section are root-position triads/sevenths around C3–C4, one per chord span, under the melody.

Combined score example: `score = z(CTnCTR) + z(PCS) − z(OOK) − z(dissonant_overlap)`, with z-scores taken within a cell's 8 candidates. Keep it simple and log every component.

## Verification

**Commands:**
- `cd prototype/harmony-first && ./setup.sh` -- expected: envs and models present, or a failure message naming what is missing
- `uv run smoke_test.py` -- expected: `output/smoke-test.md` written
- `uv run run.py ../melody-to-performance/examples/<each>.mid` for all three -- expected: outputs per I/O matrix; run-notes written
- `uv run make_player.py` -- expected: `output/player.html`
- `git status --short` / `git add -n .` -- expected: no weights, envs, data downloads, WAVs or SoundFonts staged

**Manual checks (if no CLI):**
- Probe every WAV as non-silent (duration/RMS), as in prototype 01.

## Auto Run Result

**Summary:** Prototype 02 built under `prototype/harmony-first/`: 3 harmonizers (LLM charts as given, MelodyT5, AccoMontage2) × 3 accompaniment models (AMT with chord controls, AccoMontage, Polyffusion), 8 samples per cell ranked by CTnCTR/PCS/OOK/dissonant overlap, chosen sample rendered plain / PianoFlow / Pianist Transformer, plus a blind-mode listening page. 8 harmony charts and 16 of 24 cells produced; all 8 Polyffusion cells missing (weights SharePoint-only, access refused); 3 AccoMontage2 cells missing for greensleeves (3/4).

**Files:** `setup.sh` (envs, clones, downloads), `steps/chart.py` (chart format), `steps/harmonize_{melodyt5,accomontage2}.py`, `steps/accomp_{amt,accomontage,polyffusion}.py`, `steps/metrics.py`, `steps/paths.py` (reuses prototype 01), `run.py`, `smoke_test.py`, `make_player.py`, `README.md`, `pyproject.toml`/`uv.lock`.

**Review:** 11 findings; 7 patched (2 medium, 5 low), 0 deferred, 4 rejected (2 maybe-false unreachable with current inputs/untested wrapper, 2 low unlikely needing new guards) — reasons in the triage log.

**Follow-up review recommended:** false (patched: high 0, medium 2, low 5; the two medium patches were verified directly — page flags rebuilt, AccoMontage2 charts reproduced).

**Verification:** smoke test written (4 models work, Polyffusion fails with reason); full runs for all three melodies (by the implementer; AMT on MPS); 59 WAVs probed non-silent (≥5 s, RMS > 0); `make_player.py` rebuilt after patches; all Python compiles; `git add -n .` stages no weights, envs, data or audio. Full pipeline not re-run after patches (patches touch page/docs/validation/AccoMontage2 parsing; AccoMontage2 re-run reproduced stored charts).

**Residual risks:** Polyffusion wrapper untested; player blind mode not clicked through in a browser; MelodyT5 charts sparse at default sampling; AccoMontage texture is 4/4 over 2/4 and 3/4 melodies; timings inflated (parallel runs, reused samples show 0 s).

