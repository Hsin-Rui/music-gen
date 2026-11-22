---
title: 'Prototype 02 round 3: gate-then-rank selection, re-score saved candidates, player + report'
type: feature
ticket: ''
created: '2026-11-22'
status: built
baseline_revision: '5badb70fb80a3801b72d3903ceafe8d67c666b1f'
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
warnings: [oversized]
deferred:
  - summary: >-
      Tests do not cover plain.wav production for LLM cells or main() exit code.
    evidence: |-
      test_llm_cell_is_scored_not_selected uses render=False; no test calls main(). Manually verified this run.
    location: >-
      prototype/harmony-first/tests/test_round3.py
    severity: medium
---

<intent-contract>

## Intent

**Problem:** The current selector (z-sum of CTnCTR, OOK, dissonance, copy) sometimes picks candidates that mostly repeat the block-chord prompt. The user wants a selector that keeps chart fidelity as a gate, penalises copying the prompt, penalises rule violations, and prefers variety. It must be judged by ear against the old pick.

**Approach:** Add a round-3 gate-then-rank selector to `steps/metrics.py`, with the old one kept intact. A new `round3.py` re-scores the saved round-2 candidates for 16 cells and writes the new picks with plain playback only. A new player shows ranks, gates and old vs new pick, with blind modes. A committed zh-TW HTML report summarises the results.

## Boundaries & Constraints

**Always:**
- **Scope:** melodies ode_to_joy and greensleeves; chart sources `llm` (Claude) and `gemini`; models amt, accomontage, claude and gemini.
- **Selection:** AMT and AccoMontage cells select among their existing `candidates/cand-*.mid`. Claude and Gemini cells have one candidate, which is scored and shown but not "selected".
- **Old pick:** record it from the existing `output/<m>/<s>/<model>/candidates/scores.json` `best`, read as an index into its `candidates` list, which gives `k`.
- **Rendering:** plain version only, made with the existing merge (`P01_STEPS/merge_piano.py`) and `to_wav.sh`.
- **Language:** all user-facing text in zh-TW.

**Never:**
- Call Gemini, or any model generation.
- Modify `run.py` behaviour, `make_player.py` output, or the round-2 files in `output/<melody>/...`.
- Print or commit `.env`, audio, MIDI under output/, envs or weights.
- Run PianoFlow or Pianist.
- Tune parameters.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Normal cell | 8 candidates, ≥1 passes all gates | Borda winner among passers. `fallback: false`. | none |
| No passer | every candidate fails ≥1 gate | Rank those with the fewest failed gates. `fallback: true`, shown on the page and in the report. | none |
| Empty/broken candidate | a cand MIDI with 0 notes, or unreadable | Fails the "彈得夠多" gate. The error is stored in its record. | Caught per candidate, never fatal. |
| LLM-written cell | claude/gemini, a single cand-0 | Metrics and gate results shown. `selected: false`. Its plain.wav is still produced. | none |
| Missing round-2 cell | candidates dir absent | Cell marked missing with reason; other cells continue. | Message printed; exit non-zero only if no cell was produced. |

</intent-contract>

## Code Map

- `prototype/harmony-first/steps/metrics.py`: holds the old `compute` and `rank`; keep both untouched. Add the round-3 functions here. It already defines `_notes`, `HARSH`, `ONSET_TOL`, and the `copy` and `ook` metrics; reuse `compute()` for `copy`, `ook` and `dissonant_overlap`.
- `prototype/harmony-first/steps/chart.py`: `melody_meta(path)` returns notes, beat_sec, n_bars and numerator. Also use `spans(chart, beat_sec)`, `chord_at`, `block_notes(chart, beat_sec)` (the prompt AMT receives: list of (start, end, pitch, vel)) and `parse_key`/`scale_pcs`. Parsed chord dicts have `pcs`, `root`, `bass` and `symbol`.
- `prototype/harmony-first/run.py`: `accompany()` shows how a pick is merged and rendered. Reuse its `to_wav(mid, wav, soundfont, log)` pattern via `paths.run`, `P01_STEPS`, `DEFAULT_SOUNDFONT` and `wav_stats`. Do not import `run.py` itself, because importing it would execute its argparse.
- `prototype/harmony-first/steps/paths.py`: `SOURCES` and `MODELS` labels, `P01_STEPS`, `run` and `wav_stats`.
- `prototype/harmony-first/make_player.py`: style and JS reference for the page (blind toggle, reveal). Copy patterns; don't change the file.
- Inputs on disk:
  - `output/<m>/input.mid` (the melody)
  - `output/<m>/harmony/<s>.json` (chart) and `<s>.wav` (melody + block-chord prompt audio)
  - `output/<m>/<s>/<model>/candidates/{cand-k.mid,scores.json}`
  - `output/<m>/<s>/<model>/plain.wav` (the old pick's audio)
- `.gitignore` ignores `prototype/**/output/` and `*.wav`. A committed report must live outside `output/`.

## Tasks & Acceptance

**Execution:**
- [x] `prototype/harmony-first/steps/metrics.py`: add `compute_r3(melody_path, chart, acc_path)`, `gates_r3(metrics, n_bars)` and `select_r3(cands, selectable)` per Design Notes. Extend the module docstring. This is the selector the plan specifies.
- [x] `prototype/harmony-first/round3.py`: for each of the 16 cells, score every candidate and select. Write the outputs to `output/round3/<m>/<s>/<model>/`:
  - `accompaniment.mid`, `plain.mid` and `plain.wav`;
  - `scores.json`, holding the per-candidate metrics, gates, axis ranks, `chosen`, `old_chosen`, `fallback` and `selected`.

  Then write `output/round3/summary.json` and copy it to `prototype/harmony-first/reports/round3-scores.json`. Flags: `--soundfont` and `--melodies`. This re-scores without regenerating.
- [x] `prototype/harmony-first/make_player_r3.py`: write `output/round3/player.html`.
  - **Per melody:** prompt audio for each chart, using the relative `../<m>/harmony/<s>.wav`.
  - **Per cell:**
    - the new-pick plain audio;
    - for AMT and AccoMontage, the old pick's audio (`../<m>/<s>/<model>/plain.wav`), plus a "新舊相同" badge when they match;
    - a candidate table with gate ✓/✗ (the failed gate named), the three axis ranks, the Borda sum, ★ for the new pick and ○ for the old pick.
  - **Blind mode 1:** shuffle the four models per chart and hide their labels.
  - **Blind mode 2:** A/B for new vs old, in random order, only where they differ.
  - **Reveal button.**

  The page is for listening validation.
- [x] `prototype/harmony-first/make_report_r3.py` and its output `prototype/harmony-first/reports/round3-report.html`: a self-contained zh-TW page with light/dark styling and no external requests. It contains:
  - the metric definitions in plain zh-TW;
  - per-cell picks (new vs old, same or different);
  - gate pass counts per gate and per model;
  - fallback cells;
  - an axis-rank table per cell;
  - notes on the deviations listed in Design Notes;
  - a next-step line asking the user to blind-listen.

  The user asked for a regenerated report.
- [x] `prototype/harmony-first/tests/test_round3.py` -- small pytest file with synthetic pretty_midi inputs covering each I/O matrix row (normal pass, no-passer fallback, empty/broken candidate, LLM cell selected=false, missing cell handled) plus DoC=1.0 for the prompt itself vs prompt and a two-hand playable case -- matrix test audit
- [x] `prototype/harmony-first/README.md`: add a section "第三輪：新挑選指標（2026-11-22）" with the commands and the outputs.

**Acceptance Criteria:**
- Given the saved round-2 candidates, when `uv run round3.py` runs, then 16 cells are produced. Each has an audible plain.wav and a scores.json containing `chosen`, `old_chosen`, gate results and ranks. No model or Gemini process is started.
- Given the outputs, when `uv run make_player_r3.py` runs and player.html is opened, then every cell plays its new pick. AMT and AccoMontage cells also play the old pick. Both blind modes hide labels until reveal.
- Given `reports/round3-report.html`, when opened offline, then it shows, for all 16 cells, the new vs old pick and the gate statistics, in zh-TW.
- Given round-2 files, after the run, then `git status` shows no change under `output/<melody>/` (ignored anyway), and the round-2 `scores.json` files are byte-identical.

## Implementation Notes

- 2026-11-22: implemented. `round3.py` runs in ~6 s (no model processes; only merge_piano + to_wav.sh). 16/16 cells, 7/8 selectable cells pick differently from round 2, 1 fallback (greensleeves × gemini × amt). Round-2 `scores.json` md5s unchanged.
- `playable` follows the Design Notes literally: a group is split only when it spans > 14 semitones, so ≥ 6 notes inside 14 semitones fails. This, not a bug, is why most AccoMontage candidates fail the gate.
- Parallels: a pair of consecutive melody onsets is skipped when either has no sounding bass.
- A gate whose metric cannot be computed (empty/unreadable candidate) counts as failed; an all-empty cell would be marked missing.
- Follow-up (review fixes): the playable rule was amended per the Plan Change Log (pass if the group fits one hand or any two-part split fits), so the earlier note that ≥ 6 notes inside 14 semitones fail no longer holds. Empty/unreadable candidates now fail only `enough_notes` (other gates None, not evaluated); the report counts gates over non-empty candidates and lists empty ones separately. The player always plays the old pick for AMT/AccoMontage.

## Plan Change Log

- 2026-11-22 (verify, parent): the playable gate only split groups spanning > 14 semitones, so 6+ notes within 14 semitones (playable with two hands) failed and most AccoMontage candidates were rejected. Amended to: pass when the group fits one hand or any split of sorted pitches into two parts each fits one hand (<= 5 notes, span <= 14). KEEP: all other gate/axis definitions.

## Review Triage Log

### 2026-11-22 — Review pass
- verdicts: 8 findings — high 0, medium 2, low 5, false 1, maybe-false 0
- findings:
  - `medium` `patch` Empty candidate failed all five gates, inflating per-gate stats — gates_r3 now fails only enough_notes (others None); report counts gates over non-empty candidates and lists empties separately.
  - `low` `reject` Plan Design Notes/Implementation Notes contradict the amended playable rule — fix is editing this build's plan; the Plan Change Log records the amendment and a note was appended to Implementation Notes.
  - `low` `patch` Old-pick audio hidden when new == old — player now always shows it, with the 新舊相同 badge.
  - `low` `reject` round3.py does not fail on a silent/failed WAV — all 16 WAVs audible this run; enforcing needs new guard branches for a case not met in everyday use.
  - `medium` `defer` Tests do not exercise plain.wav for LLM cells or main()'s exit code — would need FluidSynth in tests; verified manually (16 audible WAVs, exit 0).
  - `low` `reject` Stale per-cell outputs survive if a cell later becomes missing — no cell is missing; fix adds cleanup logic for an unreached state.
  - `false` `reject` Blind mode 2 mislabels when old_chosen is None — every selectable cell has a round-2 best; cell is filtered when old_src missing, and the state is not reachable with the saved data.
  - `low` `patch` README runtime 約 10 秒 vs ~6 s — README now says 幾秒鐘.

## Auto Run Result

- **Summary:** round-3 gate-then-rank selector added to steps/metrics.py (old selector untouched); round3.py re-scores the saved round-2 candidates for 16 cells (no model runs, no Gemini); make_player_r3.py writes output/round3/player.html (ranks, gates, old vs new, two blind modes); make_report_r3.py writes the committed zh-TW reports/round3-report.html; tests/test_round3.py (7 tests); README section.
- **Files:** steps/metrics.py (new selector), round3.py (runner), make_player_r3.py (player), make_report_r3.py + reports/round3-report.html (report), reports/round3-scores.json (scores), tests/test_round3.py (tests), README.md (docs).
- **Review:** 3 patches (1 medium, 2 low), 1 deferred (medium, tests for WAV/exit code), 4 rejected with reasons above. Parent fix during verify: playable gate now accepts any two-hand split (Plan Change Log).
- **Follow-up review recommended:** false — one medium patched, no high.
- **Verification:** round3.py 16/16 cells exit 0, all WAVs audible; pytest 7/7; round3-scores.json 16 cells; round-2 scores.json unchanged (md5); player audio paths resolve in headless Chrome (implementer).
- **Residual risks:** gate thresholds unvalidated by ear; a single unplayable chord fails a whole candidate; blind mode can be defeated via devtools (file paths name the model).

## Design Notes

Notation:
- `beat` = beat_sec; bar length = numerator·beat.
- Accompaniment notes = all non-drum notes of the candidate.
- Prompt = `C.block_notes(chart, beat)`.
- Tolerance = 0.04 s unless stated.

**Gates** (a candidate passes only if all pass):
1. `enough_notes`: notes ≥ n_bars, and `empty_beat_rate` ≤ 0.25. A beat is empty when no accompaniment note *sounds* anywhere in it; beats run over 0..n_bars·bar. Deviation: MusPy counts onsets, but onset-counting would fail sustained-chord textures.
2. `melody_copy`: the existing `copy` < 0.5.
3. `prompt_copy`: Degree of Copying = 2·m / (n_acc + n_prompt). Here m is a one-to-one greedy match on (same pitch class, |onset diff| ≤ tol). The gate is DoC < 0.5.
4. `chord_fit`: `chord_match` ≥ 0.7 and `ook` ≤ 0.05. For `chord_match`, take each non-empty beat; the beat matches when ≥ 50% of the accompaniment sounding duration in it is chord tones of `chord_at(beat start)`. `chord_match` is matched beats / non-empty beats.
5. `playable`: for every onset group (notes starting within tol), sort the pitches and split at the largest gap when the group spans > 14 semitones. Each part must have ≤ 5 notes and a span ≤ 14 semitones; a group that would need more than two parts fails. Deviation: a literal one-hand reading (≤ 5 notes, span ≤ 14 for the whole accompaniment) would reject every bass+chord texture, including the LLM plans. The plan's intent is "playable", so this is a two-hand check.

**Axes** (rank among gate passers, 1 = best, ties get the minimum rank; Borda sum is lowest-wins; ties broken by lower `prompt_sim`, then lower k):
- `prompt_sim` (lower better) = mean(F1, groove_cos).
  - F1 follows mir_eval-style note matching against the prompt: same MIDI pitch, onset within 0.05 s, offset within max(0.2·prompt duration, 0.05 s), one-to-one greedy. F1 = 2m / (n_acc + n_prompt).
  - groove_cos = cosine between binary onset vectors on a 16th grid over the whole piece (acc vs prompt).
- `rules` (lower better) = `parallel_rate` + (`dissonant_overlap` or 0).
  - At each melody onset, bass = the lowest accompaniment pitch sounding there; skip onsets with none.
  - For consecutive onsets where melody and bass both move in the same direction and the interval mod 12 is 7→7 or 0→0, count one parallel.
  - `parallel_rate` = count / melody notes.
- `bass_ok` (higher better): for each chord span start, take the lowest accompaniment note with onset in [start − tol, start + beat/2). The span is OK when that note's pitch class equals the chord's `bass`; a span with no such note is not OK. `bass_ok` = OK spans / spans.

**Fallback:** with no passers, the candidates with the minimum count of failed gates are ranked the same way, and `fallback: true` is set.

## Verification

**Commands:**
- `cd prototype/harmony-first && uv run round3.py`: expected 16 cells, exit 0, and the printed per-cell line `new k / old k / passers n/8`.
- `uv run make_player_r3.py && uv run make_report_r3.py`: both files written.
- `python3 -c "import json;d=json.load(open('prototype/harmony-first/reports/round3-scores.json'));print(len(d['cells']))"`: expected 16.
- `cd prototype/harmony-first && uv run --with pytest pytest -q tests/test_round3.py` -- expected: all pass
- `git status --short`: only the new scripts, `reports/`, README and the plan.

**Manual checks (if no CLI):**
- Open player.html: the audio elements resolve (no 404s on the relative paths), and blind mode hides the labels.
