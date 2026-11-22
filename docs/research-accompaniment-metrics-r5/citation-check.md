# Citation check: research-accompaniment-metrics-r5

I checked each citation against digests/ (A, AB-leads, B, C-leads, C-rules, D). I spot-checked [3] (D3PIA HTML) and [15] (Bach or Mock HTML v3) on the web on 2026-11-22. I did not spot-check [1], [5] or [7] because the AB and D digests read their primary text.

Format: [n] | sentence gist | verdict | note

## Summary
- [1] | Template harmonisation beats humans on CTnCTR/PCS (0.91, 1.97 vs 0.74, 1.42) | supported | AB digest, primary text.
- [3] | In D3PIA's test the system with higher chord accuracy had worse perceived harmony | supported | Web check agrees: CA 87.6 vs 80.1, 13 participants, OOK 2.4% vs 0%.
- [7] | Degree-of-copying formula (same pitch class and onset, x2 / sum) | supported | AB digest, primary text.
- [8] | mir_eval matching, onset ±50 ms plus a length check | supported | AB digest.
- [5] | Human music has lower PC entropy and higher GS than model output | supported | D digest, Table 2 values.
- [23] | Maximising one quality score loses diversity and produces odd output | supported | D digest (SMART).
- [4][5][25] | No per-piece metric-to-listener correlation evidence | partly | [4] and [5] support this. The digest says only that [25] finds "no general solution for evaluating generative music". It does not say [25] lacks correlation numbers.

## 1. Harmonic fidelity
- [1] | CTnCTR, PCS and MCTD formulas "confirmed from the original paper" | supported | AB digest read the primary text (round 2). Digest A (round 1) had only a search summary, which round 2 superseded.
- [1] | Authors say to use the metrics for trends, not to judge quality | supported | "practical insights ... rather than to judge their quality".
- [2] | Chord accuracy via automatic chord recognition, per beat, root plus quality | supported | Digest A (Zhao et al.). Note: digest D gives the venue as "NeurIPS 2023 (unverified)" and digest A as NeurIPS 2024 (high). The report uses 2024.
- [3] | Chord Similarity is a cosine of chord embeddings | supported | Digest A.
- [6] | FIGARO uses multi-label chord F1 | supported | AB digest.
- [3] | WSG 87.6% vs D3PIA 80.1%, worse harmony rating, 2.4% out-of-key, 13 participants | supported | The authors attribute it to dissonance and point to the out-of-key ratio. The web check agrees.
- [2] | Chord recognition compares the label root, not the sounding bass | supported | Digest A bass section.

## 2. Prompt copying
- [11][12] | Existing copy metrics compare output against training data | supported | Digest B, "looked for but not found".
- [7] | Degree of copying, range 0 to 1, originally a memorisation check | supported | AB digest. Applying it to the prompt is the report's own extension, and the report says so.
- [8] | 50 ms / 50 cent, duration within 20% (min 50 ms), bipartite matching | supported (wording) | The source sets an offset window of max(0.2 x reference duration, 50 ms). The report calls this a duration window, which is roughly equivalent but not literal.
- [8] | Onset-only vs offset-aware variants | supported | offset_ratio=None.
- [5] | GS uses a 64-cell grid with XOR | supported | Digests B and D. The sparse-prompt pitfall is the digest's own inference, not the paper's claim.
- [6][13] | FIGARO and the 2026 arrangement paper use cosine similarity | supported | AB digest (FIGARO), digest B (2608.03050).
- [12] | SSIMuse applies SSIM to piano-rolls (preprint) | supported | Digest B, search summary only.
- [11] | Yin et al. use human borrowing as the baseline; formula unconfirmed | supported | Digests B and AB.
- [27] | XOR/Hamming correlates weakly with perceived similarity | supported | Digest B: it correlates less well than a structural measure.

## 3. Rules and playability
- [14] | music21 VoiceLeadingQuartet checks; needs monophonic lines; no leading-tone, 7th or spacing checks | supported | Digests C-rules and C-leads.
- [17] | McLeod & Steedman HMM voice separation, has code, tested on Bach | supported | C-leads.
- [15] | Errors per note relative to Bach; 6 features; 92% vs 86.7%; 5 experts; a discrimination task | supported | The web check agrees. The text says 92.6% and the figure 92%. The 6 categories make 9 distributions.
- [16] | Coconet training data has many parallel 5ths/8ves | supported | C-leads, snippet only (the report says so).
- [18] | incon has 17 models, takes symbolic input, is an R package | supported | C-rules.
- [19] | Tension Ribbons give three tension measures, definitions only partly confirmed | supported | C-rules.
- [20] | RubricNet features per hand (entropy, range, jumps), no hand span or polyphony | supported | C-rules.
- [21] | PIG fingering model has no span or polyphony rules | partly | The digest describes the dataset and model but does not say whether they include span rules. The "no rules" claim rests on the digest finding no peer-reviewed playability metric.

## 4. Variety and combination
- [5][9][10] | List of variety metrics plus MusDr, MusPy, mgeval code | supported | Digests D and B.
- [5] | Values 1.94 vs 2.17-2.45; 0.86 vs 0.69-0.76 | supported | Digest D.
- [9] | Compare against reference distributions, do not maximise | supported | Digest D.
- [23] | SMART: over-optimisation cuts diversity, repeats patterns, rates generated music above real | supported | Digest D.
- [24] | YuE2: Pareto pruning, then 0.10 tolerance windows, then pick the best | supported (low) | The digest calls the source a "search snippet". The report says "只讀到摘要" ("only read the abstract"), which is not quite the same thing.
- [28] | Borda rank sum | supported | Digest D, snippet only.
- [5] | Jazz Transformer, 59 listeners, no correlation computed | supported | Digest D.
- [4][25] | Neither 2025 survey lists symbolic human-correlation numbers | partly | [4] is supported. For [25] the digest says only "no general solution".
- [26] | AccoMontage is evaluated by listening tests only | supported | AB digest ("in the extracted text").
- [22] | Workshop paper, 5 raters, model-level ranking | supported | Digest D.

## Recommendation tables
- [10] | Minimum-notes and empty-beat gate | supported | MusPy has empty_beat_rate. The thresholds themselves are the report's own.
- [1][2][3] | Chord gate (per-beat match ≥0.7, out-of-key ≤5%) | partly | [2] and [3] support the metrics. [1] supports only the "fidelity is a floor, not a maximum" rationale, not a per-beat match metric. The thresholds have no source.
- [28] | Rank-sum selection | supported | Digest D.
- [23] | "Not z-score sums, to avoid one extreme value dominating" | not supported | SMART concerns over-optimising one learned reward during training. No digest covers z-score sums or extreme values dominating. Digest D says no paper compares z-score sums with other rules.
- [7][8][6][13] | Prompt-similarity rank term | supported | See section 2.
- [14][15] | Parallel 5ths/8ves per note plus harsh overlap | supported | See section 3.
- [5][9][10] | Distance to reference range | supported | See section 4.

## Sources table / recheck table
- [16] | Confidence given as "低到中" (low to medium) | minor | The C-leads digest says "medium". Lower is conservative, so this is fine.
- [4] | Recheck "expired (2026-02)" | consistent | Published 2025-08 plus 6 months.
