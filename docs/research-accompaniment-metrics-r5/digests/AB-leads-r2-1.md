# AB leads, round 2, part 1: exact metric definitions

The question these metrics serve: which objective metrics should rank 8 generated symbolic piano accompaniments, given a melody and a fixed chord chart? The generator is conditioned on block chords and sometimes just replays them.

Method: I fetched the arXiv PDFs, pulled out their text locally with macOS PDFKit, and searched it. I read mir_eval's source as raw text from GitHub. All accessed 2026-11-22.

## Findings

- **Yeh et al., CTnCTR (Eq. 11).** CTnCTR = (n_c + n_p) / (n_c + n_n).
  - Chord tones (n_c) are melody notes whose pitch class is in the current triad for that half-bar. All other melody notes are non-chord tones (n_n).
  - n_p counts "proper" non-chord tones: those "two semitones within the notes which are right after them".
  - The value equals 1 when there are no non-chord tones, or when n_p = n_n.
  - Source: Automatic Melody Harmonization with Triad Chords: A Comparative Study, https://arxiv.org/abs/2001.02360 | JNMR (arXiv preprint) | 2020-01 (arXiv v1) | accessed 2026-11-22 | high | primary-text.
- **Yeh et al., PCS.** Each melody note is scored against each of the 3 chord notes, with the melody assumed to be above the chord.
  - Score +1 for unison, major/minor 3rd, perfect 5th and major/minor 6th. Score 0 for a perfect 4th. Score -1 for any other interval.
  - The scores are averaged over 16th-note windows, excluding rests.
  - Human-composed reference values: CTnCTR 0.74, PCS 1.42, MCTD 1.03.
  - Caveat: template matching scores higher than human on CTnCTR and PCS (0.91, 1.97). So "higher" is not "better", and chord replay would likely be over-rewarded.
  - Source: same | high | primary-text.
- **Yeh et al., MCTD.** Each melody note becomes a one-hot PCP (pitch-class profile) vector. Its distance to the chord's PCP is measured in the 6-D tonal space of Harte et al. 2006. MCTD is the average of these distances, weighted by each melody note's duration.
  - The authors advise using the metrics "to gain practical insights … rather than to judge their quality".
  - Source: same | high | primary-text.
- **mir_eval transcription defaults.** `precision_recall_f1_overlap` and `match_notes` use onset_tolerance=0.05 s, pitch_tolerance=50 cents, offset_ratio=0.2, offset_min_tolerance=0.05 s, strict=False. `precision_recall_f1_overlap` also has beta=1.0.
  - Offset window = max(0.2 × reference duration, 50 ms).
  - Notes are paired by bipartite maximum matching, not greedy matching.
  - offset_ratio=None ignores offsets (reported as the `_no_offset` scores).
  - Separate onset-only and offset-only P/R/F functions ignore pitch.
  - Average overlap ratio = overlap time / (latest offset − earliest onset), averaged over matched pairs.
  - Source: mir_eval/transcription.py, https://github.com/craffel/mir_eval/blob/main/mir_eval/transcription.py | official source code | main branch | accessed 2026-11-22 | high (read via a summarizing fetch of the raw source, not line by line) | primary-code.
- **FIGARO, description fidelity (Sec. 5.2, App. D).**
  - Categorical features: mean F1 for instruments and for chords (multi-label), plain accuracy for time signature. The table calls the chord metric "chord F1-score (C)", not "chord accuracy".
  - Note density: bar-wise NRMSE = RMSE(x, x̂) / mean(x).
  - Pitch, velocity and duration: Macro Overlapping Area (MOA). For each bar, fit a Gaussian to the feature in each sequence and take the overlapping area. MOA is the mean over the N bars. It fixes the problem that whole-piece OA (overlapping area) is maximal even for a reversed sequence.
  - Chroma and grooving similarity: bar-wise cosine similarity, following Wu & Yang 2021. Grooving vectors follow Dixon et al. 2004.
  - Source: FIGARO: Generating Symbolic Music with Fine-Grained Artistic Control, https://arxiv.org/abs/2201.10936 | ICLR 2023 | 2023 | accessed 2026-11-22 | high | primary-text.
- **Whole-Song Hierarchical Generation, ILS (Sec. 5.3, Table 2).** ILS (inter-phrase latent similarity) is computed from a cosine-similarity matrix over 2-bar segments in a pretrained VAE latent space.
  - The ratio is the average similarity of same-label phrases over the average similarity of all phrases. Higher means more structure.
  - Variants: ILS_p and ILS_r (EC2-VAE pitch and rhythm latents of the melody), ILS_chd (chord latent), ILS_txt (accompaniment texture latent from Wang et al. 2020b).
  - Ground-truth ILS_txt = 1.68.
  - Source: Whole-Song Hierarchical Generation of Symbolic Music Using Cascaded Diffusion Models, https://arxiv.org/abs/2405.09901 | ICLR 2024 | 2024-05 (arXiv) | accessed 2026-11-22 | high | primary-text.
- **Whole-Song, control efficacy (App. D, Table 6).** For each stage (chord, rhythm, texture), they report a rule-based distance dis_rb (lower is better) and a latent similarity sim_lt (higher is better) between the generated output and the external control.
  - This is the closest thing in these papers to a faithfulness-to-condition metric for texture. I did not get the exact formula for dis_rb.
  - Source: same | medium | primary-text.
- **Whole-Song, Degree of Copying (memorization appendix).** sim_rb(x, x′) = 2·n_{x∩x′} / (n_x + n_x′), where the intersection counts notes with the same pitch class and the same onset.
  - S(x) ∈ [0, 1], and the histogram of S(x) is reported as mean ± standard deviation. A latent version uses EC2-VAE to catch indirect copying of contour or rhythm.
  - This could be used as a chord-replay detector: compute sim_rb between the generated accompaniment and the block-chord condition. That is my inference.
  - Source: same | high (formula) | primary-text.
- **AccoMontage, phrase matching (Sec. 3.2).** The fitness score is the cosine similarity of rhythm features plus the cosine similarity of TIV-mapped chroma. Rhythm features are 3-D (onset, hold, rest). TIV is the 12-D Tonal Interval Vector.
  - The form term treats phrases as matching when their step-wise cosine similarity is > 0.99.
  - Evaluation is subjective only, on a 5-point scale for Coherence (fits the melody in harmony and texture), Structure and Musicality. I found no objective texture metric in the extracted text.
  - Source: AccoMontage: Accompaniment Arrangement via Phrase Selection and Style Transfer, https://arxiv.org/abs/2108.11213 | ISMIR 2021 | 2021 | accessed 2026-11-22 | medium-high | primary-text.
- **Yin et al., originality report (partial).** The Springer paper (SN Computer Science, s42979-022-01220-y) defines an "originality report" with a parameterised similarity score, and uses a cardinality score and a fingerprinting score as case studies.
  - Not confirmed this run: that the cardinality score is a translation-invariant point-set match (the maximum number of points shared under a translation, normalized by set size). This is an unverified belief.
  - Not confirmed this run: the author list and the code location.
  - Source: https://link.springer.com/article/10.1007/s42979-022-01220-y | SN Computer Science | 2022 | accessed 2026-11-22 | low (search snippet only) | secondary-snippet.

## Leads
- Yin et al.: fetch the Springer full text (open access?) to get the cardinality-score formula and the code link (possibly a GitHub repo by Z. Yin, unverified).
- Whole-Song App. D: get the exact dis_rb definitions for texture and rhythm control.
- FIGARO App. D.3: get the exact grooving-vector definition and the code, which is in the FIGARO GitHub repo (unverified).
- Polyffusion: the arXiv PDF was fetched (2307.10304), but searching the extracted text for "accuracy", "chord accuracy" and "overlapping area" found nothing. The metrics may be named differently, or the extraction may be faulty. Re-read Sec. 4/5 directly.
- For replay detection, Whole-Song's sim_rb applied to accompaniment vs. block chords looks like the simplest ready-made definition.

## Looked for but not found
- GETMusic (2023) objective metrics: not fetched (tool budget).
- Polyffusion chord accuracy definition: not found in the extracted text (see Leads).
- A "faithfulness vs creativity" metric pair in AccoMontage or FIGARO: none found. Whole-Song's DoC/memorization analysis and its control-efficacy table come closest.
- A rhythm/texture diversity metric (a diversity measure across samples) in any of the 5 papers: not found. FIGARO grooving similarity and Whole-Song ILS_txt measure similarity, not diversity.
