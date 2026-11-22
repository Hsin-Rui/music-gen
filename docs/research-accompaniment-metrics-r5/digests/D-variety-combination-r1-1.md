# D-variety-combination-r1-1: metrics for variety/creativity, their link to listening judgments, and how to combine them for best-of-N selection

Decision served: choosing objective metrics to pick the best of 8 generated piano accompaniments (symbolic MIDI) and combining them into one selection rule.
Accessed 2026-11-22. 14 tool calls. Only web sources were used; no project files were read.

## Findings

### Metric definitions
- **Pitch-class histogram entropy** H = -sum_{i=0..11} h_i log2 h_i, where h is the normalised 12-bin pitch-class histogram. It is computed over 1 bar (H1) or 4 bars (H4). Lower means clearer tonality. Real jazz: H1=1.94, H4=2.87. Generated music: H1 2.17-2.45, H4 2.91-3.12. In other words, the generated music had HIGHER entropy than the real music, so maximising entropy is not "better". | Wu & Yang, "The Jazz Transformer on the Front Line", https://arxiv.org/abs/2008.01307 | ISMIR 2020 (peer-reviewed) | 2020 | accessed 2026-11-22 | high | metric-definition
- **Grooving pattern similarity** GS(g^a, g^b) = 1 - (1/Q) sum_i XOR(g^a_i, g^b_i), where g is a binary vector marking the onset positions in a bar (Q=64), averaged over all pairs of bars. Higher means more consistent rhythm. Real = 0.86, models = 0.69-0.76. | same | ISMIR 2020 | 2020 | accessed 2026-11-22 | high | metric-definition
- **Chord progression irregularity** CPI = % of unique chord trigrams in a piece. The paper does not state the exact denominator. Real = 40.4%, models = 72.6-81.2%. A second source warns that very low CPI can mean a boring progression. | same; Kader & Karmaker survey (below) | | | accessed 2026-11-22 | high (definition) / medium (denominator) | metric-definition
- **Structureness indicator** SI_l^u = max over l<=i<=u, 1<=j<=N of S_ij, where S is the fitness scape plot (values in [0,1]) and N is the duration in seconds. It is reported at three timescales: SI(3-8), SI(8-15) and SI(15+). Real values are 0.35-0.36. Model values are 0.10-0.27, so the models fall short of the real music. | same | ISMIR 2020 | 2020 | accessed 2026-11-22 | high | metric-definition
- **Code:** MusDr implements H, GS, CPI and SI: https://github.com/slSeanWU/MusDr | same | | | accessed 2026-11-22 | high | code-availability
- **MusPy metrics:**
  - pitch_entropy: Shannon entropy of the normalised pitch histogram. Returns NaN if there are no notes.
  - pitch_class_entropy: the same entropy over a 12-bin pitch-class histogram.
  - polyphony: mean number of pitches sounding at once.
  - polyphony_rate: fraction of time steps where at least 2 pitches sound.
  - groove_consistency: mean Hamming distance between neighbouring measures. The docs give no explicit 1- normalisation, so check the code.
  - Also included: pitch_in_scale_rate, scale_consistency, empty_beat_rate, pitch_range, n_pitches_used.

  | MusPy docs https://salu133445.github.io/muspy/doc/metrics.html ; Dong et al., "MusPy: A Toolkit for Symbolic Music Generation", https://arxiv.org/abs/2008.01951 | ISMIR 2020 (peer-reviewed) | 2020 | accessed 2026-11-22 | high | metric-definition / code-availability (https://github.com/salu133445/muspy)
- **Yang & Lerch, MGEval-style evaluation:** they compute per-feature distributions of pitch/rhythm descriptors (pitch range, note count, pitch-class histogram, IOI, note-length histogram, etc.). They then compare generated and reference sets via KL divergence and overlapping area (OA) of the distributions, instead of maximising any feature. Their key finding is that models can misrepresent even low-level distributions such as pitch range and note count. | Yang & Lerch, "On the evaluation of generative models in music", https://musicinformatics.gatech.edu/wp-content_nondefault/uploads/2018/11/postprint.pdf | Neural Computing and Applications (peer-reviewed journal) | 2018 online / 2020 issue | accessed 2026-11-22 | high (approach) / medium (exact feature list, taken from survey excerpts, not the full text) | metric-definition / combination-method ("closeness to reference distribution")
- **Accompaniment-specific metrics:**
  - Chord accuracy: generated harmony is checked against the given chord sequence.
  - Texture similarity: measured in the 256-D latent space of a pretrained texture VAE.
  - MUTE F1: computed at the 128-pitch level and at the pitch-class level.

  Only search snippets were read, not the full texts. | Zhao et al., "Structured Multi-Track Accompaniment Arrangement via Style Prior Modelling", https://arxiv.org/abs/2310.16334 (NeurIPS 2023, unverified this run); "Emotion-Guided Music Accompaniment Generation Based on VAE", https://arxiv.org/abs/2307.04015 | | 2023 | accessed 2026-11-22 | medium | metric-definition

### Evidence on correlation with listening judgments
- **No correlation computed in the Jazz Transformer paper.** Its 59-listener study (27 "pros") rated the model below real pieces on every aspect (overall quality, impression, structureness, richness; one-tailed Z, p<0.05). The authors did NOT correlate the metrics with the ratings and left this as future work. The link is only suggestive. | Wu & Yang 2020 (above) | ISMIR 2020 | | accessed 2026-11-22 | high | empirical-correlation (negative evidence)
- **FMD, KLD and OA track listener rankings better than perplexity.** For model-level ranking, FMD, KLD and OA "closely align with human judgments", while perplexity (PPL) diverges for the two largest models. No correlation coefficient is reported. There were only 5 raters, and the comparison is at model level, not per sample. A counter-example: Moonbeam has the highest OA (82.2%) but a mid-range subjective score (2.91 vs 3.22 for the best model). | Lehmkuhl et al., "Generating Piano Music with Transformers: A Comparative Study of Scale, Data, and Metrics", https://arxiv.org/abs/2511.07268 | AI for Music workshop / arXiv (not a full peer-reviewed venue) | v2 Jan 2026 | accessed 2026-11-22 | medium-low | empirical-correlation
- **The 2025 survey finds no symbolic correlation numbers.** It reports poor metric-perception correlation in general, but cites no symbolic-specific correlation study. The only numbers it relies on are for audio metrics (Yuan et al. 2025: CLAP/FAD/KLD align poorly with human preference). It also says OA and KLD have no meaningful thresholds, and that a higher score does not guarantee better-sounding music. It proposes, but does not build, a learned quality scorer trained on preferences. | Kader & Karmaker, "A Survey on Evaluation Metrics for Music Generation", https://arxiv.org/abs/2509.00051 | arXiv preprint | Aug 2025 | accessed 2026-11-22 | medium | empirical-correlation
- **Another evaluation-methods survey.** A 2025 survey says no general solution exists for evaluating generative music. | Lerch et al., "Survey on the Evaluation of Generative Models in Music", https://arxiv.org/abs/2506.05104 | arXiv (v4; venue not checked) | 2025 | accessed 2026-11-22 | medium | empirical-correlation (context)
- **Learned evaluators / reward models for symbolic music: none trained on human preferences over MIDI was found.** The nearest are:
  - SMART renders MIDI to piano audio and uses Meta Audiobox Aesthetics "Content Enjoyment" as the reward. In a 14-listener study (399 observations), ratings rose by about 1.22 points (p=0.002).
  - NotaGen's CLaMP-DPO labels chosen/rejected samples by CLaMP 2 similarity to fine-tuning references, with no human labels. The exact formula was not retrieved.

  | Jonason, Casini & Sturm, "SMART", https://arxiv.org/abs/2504.16839 (arXiv, Apr 2025); Wang et al., "NotaGen", https://arxiv.org/abs/2502.18008 (arXiv, Feb 2025) | preprints | 2025 | accessed 2026-11-22 | medium | empirical-correlation / code-availability (code URL for neither was confirmed)

### Combination methods and pitfalls
- **Goodhart evidence: optimising one learned quality score caused collapse.** In SMART, strong over-optimisation (1000 iterations, beta=0):
  - "dramatically reduces diversity of model outputs";
  - produced repeated patterns;
  - pushed note counts to about 70, empty-beat rate to 0, and widened pitch and velocity range;
  - gave scale consistency a heavier tail (more chromaticism);
  - made the reward score generated music ABOVE real piano recordings.

  Lesson: a single maximised score drifts away from what real music looks like, so gate it or anchor it to a reference range. | SMART (above) | arXiv | 2025 | accessed 2026-11-22 | medium-high | combination-method (pitfall)
- **Target ranges instead of maximising, supported by the data.** On H, CPI, GS and SI, real music is NOT at the extreme: entropy and CPI are lower in real music, GS and SI higher. A "closeness to the reference distribution" score (|x - mu_ref|/sd_ref, or OA/KLD as in Yang & Lerch) is therefore better supported than "maximise variety". | derived from Wu & Yang 2020 Table 2 + Yang & Lerch | | | accessed 2026-11-22 | medium (inference) | combination-method
- **Best-of-8 selection in a frontier system (YuE2), as described in a search snippet:**
  1. Pareto-dominance pruning across 3 metrics (Musicality, Q3O, PER).
  2. Lexicographic tolerance windows: keep candidates within 0.10 of the best Musicality, then within 0.10 of the best remaining Q3O.
  3. Pick the lowest PER.

  The full text could not be parsed, so this is unverified beyond the snippet. | Yuan et al., "YuE2: Unifying Symbolic and Audio Music Generation at Frontier Quality", https://arxiv.org/abs/2609.33757 | arXiv | ~Sep 2026 | accessed 2026-11-22 | low-medium | combination-method
- **Rank aggregation instead of z-scores.** One challenge paper ranks entries on each metric separately and sums the Borda ranks. This avoids putting different metric scales on a common footing, but it is coarse when N=8. | "Academic Text-to-Music Grand Challenge", https://arxiv.org/abs/2605.21538 | arXiv | 2026 | accessed 2026-11-22 | low-medium (snippet only) | combination-method
- **Weighted sum of normalised verifiers.** SCORE (text-to-audio) normalises CLAP + Audiobox PQ and takes a weighted sum, warning against over-optimising a single verifier. | snippet from search https://arxiv.org/abs/2610.03589 / related; exact paper attribution unverified | arXiv | 2026 | accessed 2026-11-22 | low | combination-method

## Leads worth chasing
- Read the full text of YuE2's best-of-N section: dominance filter plus lexicographic tolerance. It is the closest published analogue to an "8 candidates, gate then maximise" rule.
- Read Yang & Lerch's full text for the exact feature list and the OA/KLD procedure. Possibly use their MGEval code (github.com/RichardYang40148/mgeval; repo unverified this run).
- Pearce's IDyOM, unverified belief: IC = -log2 p(event | context). Find studies that relate mean IC to ratings of interest or complexity (e.g. inverted-U preference). The search this run returned nothing relevant.
- Syncopation measures (Longuet-Higgins & Lee; Witek et al. 2014, inverted-U between syncopation and groove/pleasure) could serve as a "creative within limits" target range. Unverified this run.
- Zhao et al. 2023 and D3PIA (arXiv 2602.03523): check their definitions of chord-fidelity and texture-diversity metrics for accompaniment on POP909.
- Check whether the NotaGen CLaMP 2 score could serve as a reference-similarity reranker for symbolic accompaniment, and find the code.

## Looked for but not found
- Per-sample correlation coefficients (r or rho) between symbolic feature metrics (entropy, GS, SI, polyphony) and listener ratings. No source this run reported any.
- A reward model or learned evaluator trained on human preferences over symbolic music. Only audio-proxy (SMART) and reference-similarity (CLaMP-DPO) approaches were found.
- Xiong et al. 2023, "A comprehensive survey for evaluation methodologies of AI-generated music", was not retrieved.
- IDyOM information content as a creativity or interest predictor for generated music (search returned off-topic results).
- Compression-based complexity metrics applied to generated accompaniment.
- Music papers that explicitly compare z-score sums vs Pareto vs lexicographic rules for reranking.
