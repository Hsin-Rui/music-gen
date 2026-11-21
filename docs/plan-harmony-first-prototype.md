---
title: 'Prototype 02: harmony-first accompaniment (harmonizers × accompaniment models)'
type: feature
ticket: ''
created: '2026-11-21'
status: in-progress
baseline_revision: '438fe4434a5cfcd345e5098bbebe70ba3cf700d2'
route: full
route_source: auto
risk: low
review: ''
review_source: ''
lenses_ran: []
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
- [ ] `prototype/harmony-first/setup.sh` -- envs + clones + data/ckpt downloads for MelodyT5, AccoMontage2, AccoMontage, Polyffusion; checks that the prototype-01 envs exist -- reproducible setup
- [ ] `prototype/harmony-first/steps/chart.py` -- chord-symbol parsing, chart validation, chart ↔ block-chord MIDI, chart → per-beat chord labels -- one shared chart format
- [ ] `prototype/harmony-first/steps/harmonize_melodyt5.py`, `steps/harmonize_accomontage2.py` -- melody MIDI → normalised chart JSON (AccoMontage2: skip non-4/4, merge 2/4 pairs) -- harmonizers
- [ ] `prototype/harmony-first/steps/accomp_amt.py`, `steps/accomp_accomontage.py`, `steps/accomp_polyffusion.py` -- melody + chart → N accompaniment MIDI samples -- accompaniment models
- [ ] `prototype/harmony-first/steps/metrics.py` -- CTnCTR, PCS, out-of-key ratio, melody–accompaniment dissonant-overlap ratio, combined score -- ranking
- [ ] `prototype/harmony-first/smoke_test.py` -- each new model on a short clip; works/fails, time, RSS → `output/smoke-test.md`
- [ ] `prototype/harmony-first/run.py` -- orchestrates harmonize → chord audio → accompaniment ×8 → rank → merge → render → WAV for one melody; writes run-notes.md/json -- the pipeline
- [ ] `prototype/harmony-first/make_player.py` -- page with a harmony section (melody + block chords per source) and a cross grid (source × model × 3 versions) with scores, blind mode and a zh-TW explainer
- [ ] `prototype/harmony-first/README.md` -- zh-TW setup, usage, layout, licences, limitations, first observations

**Acceptance Criteria:**
- Given setup has run, when `uv run smoke_test.py` runs, then `output/smoke-test.md` lists MelodyT5, AccoMontage2, AccoMontage and Polyffusion as works/fails with time and an error excerpt.
- Given the three melodies, when `uv run run.py examples/<name>.mid` runs for each, then every cell the matrix says should exist is either produced or listed as missing with a reason in run-notes.
- Given a cell's 8 candidates, when ranking runs, then run-notes shows each candidate's four metrics and combined score, and which one was chosen.
- Given outputs exist, when `uv run make_player.py` runs, then `output/player.html` plays the harmony section and the cross grid, with blind mode working.

## Implementation Notes

## Plan Change Log

## Review Triage Log

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
