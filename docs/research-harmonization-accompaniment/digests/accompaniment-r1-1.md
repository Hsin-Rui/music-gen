# Digest: Symbolic accompaniment generation (melody + chords -> piano), round 1, part 1

Accessed 2026-11-21. Every finding comes from a source retrieved in this run. Mac/CPU notes come from README text only. I did not grep the code for hard-coded `.cuda()` (marked "not code-checked").

## Findings

1. **Claim:** FGG ("Efficient Fine-Grained Guidance for Diffusion Model Based Symbolic Music Generation", Zhu, Liu, Wang, Jiang, Zheng) generates 4-bar piano-roll accompaniment from melody + chords (rhythm condition optional). At sampling time it applies a hard control that suppresses out-of-key/out-of-chord pitches. Trained on POP909 (15,761 four-bar segments).
   - URL: https://arxiv.org/html/2410.08435 | arXiv (v3) | 2025-06-06 | accessed 2026-11-21 | conf high | class capability
2. **Claim:** FGG reports these results vs WholeSongGen vs GETMusic. Out-of-key steps: 0.0% / 2.1% / 3.5%. Chord accuracy: 0.485 / 0.314 / 0.153. Chord similarity (VAE latent cosine): 0.767 / 0.611 / 0.394. The listening test used 6 melodies with 4 conditions each, rated by experienced listeners on harmony, naturalness, overall quality and more; FGG rated best. The 0% out-of-key figure follows from the constraint by construction.
   - URL: https://arxiv.org/html/2410.08435 | arXiv | 2025-06-06 | accessed 2026-11-21 | conf high | class evaluation
3. **Claim:** The FGG code is at github.com/huajianduzhuo-code/FGG-music-code and the README cites it as ICML 2025. Checkpoints are linked via `download_link.txt`, and a separate-melody/accompaniment mode conditions on chords + melody. No LICENSE was visible, and the README does not document importing a user MIDI (only notebooks `generation.ipynb` and `generation_style.ipynb`).
   - URL: https://github.com/huajianduzhuo-code/FGG-music-code | GitHub | n/a | accessed 2026-11-21 | conf med | class licence
4. **Claim:** D3PIA (Choi, Kim, Bang, Kwon, Nam, KAIST; ICASSP 2026) is a discrete denoising diffusion model with a Neighborhood-Attention lead-sheet encoder. Its input is a lead-sheet piano roll (melody + chord pitches) and its output is an 8-bar, 88-key accompaniment piano roll without velocity. It has 2.2M params and takes about 1.7 s per 8 bars. Trained on POP909.
   - URL: https://arxiv.org/html/2602.03523 ; https://jech2.github.io/D3PIA/ | arXiv / project page | 2026-02-03 | accessed 2026-11-21 | conf high | class capability
5. **Claim:** D3PIA benchmark on the POP909 test set (905 segments), reporting OOK / chord accuracy / chord similarity:
   - Polyffusion: 0.0 / 37.5 / 54.0
   - C&E-Embellish: 14.8 / 58.1 / 70.6
   - D3PIA: 0.0 / 80.1 / 93.6
   - WSG-4th: 2.4 / 87.6 / 94.6
   - FGG: 0.0 / 62.0 / 77.3

   WSG-4th and FGG use extra inputs. The listening test had 13 expert participants (piano/composition degree) rating 10 excerpts; D3PIA rated highest. WSG had higher chord accuracy but lower perceived harmony, attributed to dissonant notes. The comparison therefore shows that chord accuracy does not equal perceived harmony.
   - URL: https://arxiv.org/html/2602.03523 | arXiv | 2026-02-03 | accessed 2026-11-21 | conf high | class evaluation
6. **Claim:** The paper says D3PIA training code and samples are public at the project page, but the page as retrieved showed no GitHub, weights or licence link.
   - URL: https://jech2.github.io/D3PIA/ | project page | n/a | accessed 2026-11-21 | conf med | class licence
7. **Claim:** Whole-song hierarchical generation (Wang, Min, Xia, ICLR 2024) is MIT-licensed. Only a portion of the checkpoints is released ("sufficient for testing"). The CLI takes a form string + key. It has 2 commits, the last status note is dated Apr-03-2024, and there are 3 open issues.
   - URL: https://github.com/ZZWaang/whole-song-gen | GitHub | 2024-04-03 | accessed 2026-11-21 | conf high | class licence
8. **Claim:** AccoMontage (Zhao & Xia, ISMIR 2021) is MIT-licensed. It is phrase-retrieval + style-transfer arrangement from a POP909 phrase bank, and takes MIDI with a melody track + chords (1-beat chord granularity, 9th chords allowed). It offers velocity/pedal control and 1-16-bar phrases. Data + checkpoints are on Google Drive (updated 2024-02-27), with a Colab notebook. No CUDA mention in the README.
   - URL: https://github.com/zhaojw1998/AccoMontage | GitHub | 2024-02-27 | accessed 2026-11-21 | conf high | class capability
9. **Claim:** AccoMontage2 (Yi, Hu, Zhao, Xia, ISMIR 2022) is MIT-licensed. From a melody MIDI + tonic + mode + phrase segmentation string, it does **both harmonization and accompaniment**. Chord styles are pop_standard / pop_complex / r&b / dark, plus texture prefilters for rhythmic density and voice number (0-4). Outputs are chord_gen.mid, a JSON log and textured_chord_gen.mid. It is 4/4 only with 4- or 8-bar phrases, and ships a Flask GUI. It has 170 stars and 5 open issues.
   - URL: https://github.com/billyblu2000/AccoMontage2 | GitHub | n/a | accessed 2026-11-21 | conf high | class capability
10. **Claim:** The zhaojw1998/AccoMontage-3 URL resolves to "Structured-Arrangement-Code" (Zhao et al., NeurIPS 2024, arXiv 2310.16334). Stage 1 is lead sheet -> piano accompaniment; stage 2 is piano -> multitrack. It is MIT-licensed with checkpoints on Google Drive. It pins PyTorch 1.10.1+cu111 and Python ≤3.9. The prior was trained on LMD and the autoencoder on Slakh2100.
    - URL: https://github.com/zhaojw1998/AccoMontage-3 | GitHub | 2024-10-28 | accessed 2026-11-21 | conf high | class compat
11. **Claim:** Polyffusion (Min, Jiang, Xia, Zhao, ISMIR 2023) is MIT-licensed with checkpoints on SharePoint. It supports chord conditioning (latent or vanilla), texture conditioning and melody->accompaniment inpainting (`--inpaint_type=above`), optionally with chords from another MIDI. Trained on POP909. No device mention in the README.
    - URL: https://github.com/aik2mlj/polyffusion | GitHub | n/a | accessed 2026-11-21 | conf high | class capability
12. **Claim:** GETMusic (microsoft/muzic) pins torch 1.12.1+cu113 and lists no checkpoint download location in the README. Chords are inferred from the input tracks, and interactive chord-progression input is not released. Training data is unreleased (crawled pop). There are 101 open issues. The muzic repo was **archived on 2026-10-01**.
    - URL: https://github.com/microsoft/muzic/tree/main/getmusic | GitHub | 2026-10-01 | accessed 2026-11-21 | conf high | class ecosystem
13. **Claim:** Compose & Embellish (Wu & Yang, ICASSP 2023) is MIT-licensed with weights on HF (`slseanwu/compose-and-embellish-pop1k7`). The Embellish stage generates a piano performance conditioned on a lead sheet (melody + chords). Trained on Pop1K7. It recommends CUDA 10.2, and the last changelog entry is 2024-07-29.
    - URL: https://github.com/slSeanWU/Compose_and_Embellish | GitHub | 2024-07-29 | accessed 2026-11-21 | conf high | class licence
14. **Claim:** FIGARO is MIT-licensed with a downloadable checkpoints.zip of about 2.3 GB. Its controls are expert descriptions (instruments, chords, meta) plus a learned VQ-VAE description. Trained on LMD with a 32-bar default cap. It is multi-instrument and not melody-conditioned.
    - URL: https://github.com/dvruette/figaro | GitHub | n/a | accessed 2026-11-21 | conf med | class capability
15. **Claim:** "Structure-Aware Piano Accompaniment via Style Planning and Dataset-Aligned Pattern Retrieval" (Zang, Yu, Yu; arXiv 2602.15074, Feb 2026) works as follows:
    - A 4-layer transformer plans 6 measure-level style slots, with 15 optional keywords (e.g. alberti, stride).
    - It retrieves POP909 measures, reharmonizes them, and picks one by minimizing an energy over harmonic fit, voice leading, style and repetition, then samples from the top candidates. This is effectively retrieve-and-rank.
    - There is no code, no listening test and no note-level baselines. A demo page has 60 MIDIs.
    - URL: https://arxiv.org/html/2602.15074v1 | arXiv | 2026-02-16 | accessed 2026-11-21 | conf high | class capability
16. **Claim:** These harmonic-consistency metrics are in use:
    - chord-tone to non-chord-tone ratio (CTnCTR)
    - Pitch Consonance Score (PCS)
    - Melody-Chord Tonal Distance (MCTD)
    - note-in-chord ratio (ReaLchords)
    - consonant/dissonant overlap ratios between melody and accompaniment (2026 live-jamming paper)
    - out-of-key ratio (OOK), rule-based chord accuracy and chord-embedding similarity (FGG, D3PIA)

    I saw these only in search snippets for the harmonization/jamming papers; I did not read those papers in full.
    - URL: https://arxiv.org/pdf/2001.02360 ; https://arxiv.org/pdf/2506.14723 ; https://arxiv.org/pdf/2606.11886 | arXiv | 2020 / 2025 / 2026 | accessed 2026-11-21 | conf med | class evaluation
17. **Claim:** The AccoMontage2 listening test rated harmonicity on a 5-point scale. It was significantly better than a BLSTM baseline and below the original human harmonization (snippet only).
    - URL: https://arxiv.org/pdf/2209.00353 | arXiv | 2022 | accessed 2026-11-21 | conf med | class evaluation

## Catalogue

| Model | Paper / venue / year | Repo | Code / weights licence | Weights | Inputs | Output | Data | Mac/CPU | Evaluation | Last activity | Known problems |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AccoMontage | ISMIR 2021 | github.com/zhaojw1998/AccoMontage | MIT / data+ckpt GDrive (licence unstated) | Yes (GDrive) | MIDI melody + chords; POP909 reference "spotlight" | Piano MIDI with velocity and pedal | POP909 phrase bank | Likely (retrieval + small VAE, no CUDA in README; not code-checked) | Paper listening test (not re-read) | Data 2024-02 | 3 open issues (content not read) |
| AccoMontage2 | ISMIR 2022 | github.com/billyblu2000/AccoMontage2 | MIT | Data files on GDrive | **Melody only** + tonic/mode/segmentation; chord style; texture density | Chords MIDI + accompaniment MIDI | Niko-derived chord set, POP909 | Likely (DP + AccoMontage; GUI) | Listening: harmonicity, creativity, musicality | n/a | 4/4 only, 4/8-bar phrases; 5 issues |
| Structured-Arrangement (AccoMontage-3) | NeurIPS 2024 | github.com/zhaojw1998/AccoMontage-3 | MIT / GDrive | Yes | Lead sheet | Piano, then multitrack | LMD, Slakh2100 | Old pins (torch 1.10 cu111, py≤3.9); CPU unverified | Paper (not read) | 2024-10 | 2 issues |
| Polyffusion | ISMIR 2023 | github.com/aik2mlj/polyffusion | MIT / SharePoint | Yes | Chords (latent/vanilla), texture, melody inpainting | Piano roll to MIDI | POP909 | Unverified | D3PIA: CA 37.5% | n/a | 2 issues |
| Whole-Song Gen (WSG) | ICLR 2024 | github.com/ZZWaang/whole-song-gen | MIT / partial ckpts | Partial | Form string + key (cascade: form, lead sheet, accompaniment) | Whole song | POP909 (per D3PIA/FGG usage) | Unverified; slow (79 s / 8 bars, GPU per D3PIA) | CA 87.6% but lower perceived harmony | 2024-04 | 3 issues; partial weights |
| Compose & Embellish | ICASSP 2023 | github.com/slSeanWU/Compose_and_Embellish | MIT / HF | Yes (HF) | Lead sheet (Embellish stage) | Piano performance MIDI | Pop1K7 | GPT-2 path likely CPU-able; unverified | D3PIA: OOK 14.8%, CA 58.1% | 2024-07 | 2 issues |
| FGG | ICML 2025 (per README) | github.com/huajianduzhuo-code/FGG-music-code | **No licence seen** / unstated | Yes (link files) | Chords (required), melody, rhythm | 4-bar piano roll | POP909 | DDIM, fast (0.4 s); device unverified | Out-of-key, CA, CS, IoU; listening test with 6 melodies | 2025 | No MIDI-import docs |
| D3PIA | ICASSP 2026 | (project page jech2.github.io/D3PIA) | Unknown | Not found | Lead-sheet piano roll (melody + chords) | 8-bar piano roll, no velocity | POP909 | Very small (2.2M params), so plausibly CPU-OK; unverified | OOK/CA/CS/GS + 13-expert MOS | 2026-02 | Code link not found; no velocity |
| Style Planning + Pattern Retrieval | arXiv 2602.15074, 2026 | none | n/a | No | Structured lead sheet + keywords | Piano MIDI | POP909 | Small; n/a | Diversity metrics only; no listening test | 2026-02 | No code |
| GETMusic | arXiv 2023 (venue not on page) | microsoft/muzic (archived) | Not stated on page | Not in README | Any tracks incl. chord track (inferred) | Multitrack MIDI | Crawled pop (unreleased) | torch cu113 pin; unverified | D3PIA/FGG: weakest on chord metrics | Archived 2026-10-01 | 101 open issues; out-of-domain is poor |
| FIGARO | OpenReview (ICLR 2023, unverified) | github.com/dvruette/figaro | MIT | Yes, 2.3 GB | Chords, instruments, meta description | Multitrack MIDI | LMD | Unverified | Paper (not read) | n/a | 3 issues; not melody-conditioned |

## Leads worth chasing

- **D3PIA code:** look for a GitHub repo by jech2 / KAIST MAC lab. It is the strongest 2026 POP909 result and tiny, so it fits the Mac. Check its licence and weights.
- **FGG repo LICENSE file and MIDI-input path.** Its hard control (masking non-chord/out-of-key pitches) is directly reusable as a constraint on any piano-roll diffusion model.
- **"Learning Music Style for Piano Arrangement Through Cross-Modal Bootstrapping"** (arXiv 2608.03050, 2026). Seen only in a reference list.
- **Etude** (arXiv 2509.16522): piano cover in three stages. **Piano2Pop** (arXiv 2610.31510). **STAGE** (ISMIR 2025, zenodo 17706555): stemmed accompaniment with prefix conditioning. **MIDI-SAG** (arXiv 2602.22029): audio output.
- **ReaLchords** (arXiv 2506.14723): online chord accompaniment with an RL reward on note-in-chord. Its reward/metric is reusable for ranking.
- **"Incorporating Structure and Chord Constraints in Symbolic Transformer-based Melodic Harmonization"** (arXiv 2512.07627). Relevant to the chord-assignment stage.
- **Function alignment** (Jiang et al., ISMIR 2025, arXiv 2506.15548). Music-for-music seq2seq with public weights; tasks include chord recognition and melody/drum generation, not confirmed for piano accompaniment.
- **Generate-and-rank recipe:** sample N accompaniments (Polyffusion, FGG or D3PIA), then score each with chord accuracy against the target chords, OOK, and the melody-accompaniment consonant-overlap ratio. Penalize the dissonance that D3PIA's listeners flagged in WSG. No published system was found that does exactly this for piano accompaniment. The pattern-retrieval paper's energy function is the closest.

## Looked for, could not find (this run)

- MuseCoco: not checked this run (budget).
- A symbolic "Music ControlNet" for accompaniment: not found.
- A dedicated generate-many-and-rank accompaniment paper: not found.
- Code-level Mac/MPS verification (grep for `.cuda()`) for any repo: not done. All Mac notes are README-level.
- Licence of the FGG and D3PIA code, and of GETMusic weights: not found.
- An ISMIR 2025 accepted paper specifically on melody + chord -> piano accompaniment: not found via search.
