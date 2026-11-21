# D1 round 1: melody + chords → piano accompaniment models (accessed 2026-11-21)

Researcher assistant; ~13 primary sources, 20 tool calls.

## Candidates

| Name | Year/venue | Code | Weights | Licence | I/O | Training | Hardware | Quality | Meter | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| AccoMontage-3 | NeurIPS 2024, arXiv 2310.16334 (v4 Nov 2024) | github.com/zhaojw1998/AccoMontage-3 | Google Drive + Colab | code MIT; weights unstated | lead sheet → stage 1 piano (AccoMontage, POP909) → stage 2 multitrack | Slakh2100 (AE), ~110k LMD pieces 2/4+4/4 (prior) | Py3.8, torch 1.10.1+cu111; ~19M+30M params; CPU/MPS undocumented | chord acc 0.567 vs AMT 0.446, GETMusic 0.423, PopMAG 0.470; 0.46 s/bar vs AMT 6.32; 23-rater Likert, beats all baselines p<0.05 | 4/4 only | lead-sheet input format undocumented in README |
| Compose & Embellish | ICASSP 2023, arXiv 2209.08212 | github.com/slSeanWU/Compose_and_Embellish | HF slseanwu/compose-and-embellish-pop1k7 | MIT | stage 2 Embellish: lead sheet → piano performance MIDI | LMD + Pop1K7 | Embellish 38.2M; README Py3.8 + CUDA 10.2; GPT-2 Embellish (2024-07-29) drops fast-transformers | "halves structural gap" (no numbers retrieved) | not retrieved | user lead-sheet input undocumented; need REMI converter; last update Jul 2024 |
| CoCoMulla | ISMIR 2024, arXiv 2310.17162 | github.com/kikyo-16/coco-mulla-repo | Google Drive | none listed | audio+MIDI+chords+text → AUDIO (MusicGen PEFT) | <300 songs | MusicGen-scale | reviewer: weak evaluation | n/a | not symbolic |
| Zang, Yu, Yu: structure-aware piano accompaniment (style planning + retrieval) | arXiv 2602.15074, Feb 2026 | none | none | arXiv | functional-harmony lead sheet + section cues + keywords → piano MIDI (planner + POP909 bar retrieval) | POP909 | tiny (4 layers, d=256) | no listening test; slot acc 0.636 | POP909 mostly 4/4 | demo 60 MIDI at piano-paper-demos.github.io/pianocomp-demo |
| Unpaired piano accompaniment style transfer | APSIPA 2025 P424 | unknown | unknown | unknown | lead sheet anchor → restyled piano | unknown | unknown | unknown | unknown | PDF text not extracted |
| Florence Price accompaniment generator | ISMIR 2025, arXiv 2506.23130 | said released | said released | paper CC BY 4.0 | melody → piano (Price art-song style), chords not mentioned | 112 Price songs | base model unnamed | blind test: judged Price-like more often than baseline | unknown | narrow style |
| STAGE | ISMIR 2025, arXiv 2504.05690 | — | — | — | audio → audio stem | MoisesDB | MusicGen Small | — | — | out of scope |
| LeadsheetArrangement (Liu & Yang) | ~2018 | github.com/liuhaumin/LeadsheetArrangement | unknown | unknown | lead sheet → 5-track pianoroll | Lakh Pianoroll | — | — | — | GAN-era |
| PopMAG | baseline in AccoMontage-3 | — | — | — | lead sheet → multitrack | — | — | chord acc 0.470 | — | not investigated |

## Claims
1. AccoMontage-3 code MIT, checkpoints Google Drive, Colab/notebook inference — github.com/zhaojw1998/AccoMontage-3 — high — licence
2. AccoMontage-3 pins Py3.8, torch 1.10.1+cu111; CPU/MPS undocumented — same — high — version/compat
3. AccoMontage-3 stage 1 = lead sheet → piano, evaluated separately (Table 5) — arxiv.org/html/2310.16334v4 (Nov 2024) — high — landscape
4. AccoMontage-3 quadruple meter only — same — high — version/compat
5. AccoMontage-3 chord acc 0.567 vs AMT 0.446 / GETMusic 0.423 / PopMAG 0.470; 0.461 s/bar vs AMT 6.32 — same — high — performance
6. AccoMontage-3 listening test 23 raters, 5 criteria, above all baselines p<0.05 — same — medium — performance
7. C&E weights on HF, MIT; Embellish ~38.2M params — huggingface.co/slseanwu/compose-and-embellish-pop1k7 — high — licence
8. C&E GPT-2 Embellish (2024-07-29) removes fast-transformers dependency — github.com/slSeanWU/Compose_and_Embellish — high — version/compat
9. C&E README does not document user lead-sheet input — same — high — version/compat
10. CoCoMulla = MusicGen PEFT with chord/pitch/drum controls, <300 songs, <4% params; audio output — arxiv.org/abs/2310.17162; ISMIR 2024 poster 61 — high — landscape
11. CoCoMulla repo: no licence — github.com/kikyo-16/coco-mulla-repo — high — licence
12. Zang et al. 2026: planner+retrieval, no code/weights, no listening test, slot acc 0.636 — arxiv.org/html/2602.15074 (2026-02-16) — high — landscape/performance
13. MIREX 2024 symbolic generation task: lead sheet → piano accompaniment, 8 bars 4/4 — music-ir.org/mirex/wiki/2024:Symbolic_Music_Generation (snippet only) — medium — landscape
14. Florence Price generator (ISMIR 2025) fine-tunes an unnamed symbolic model on melody → accompaniment; release claimed — arxiv.org/abs/2506.23130 (Jun 2025) — medium — landscape
15. STAGE is audio-domain — arxiv.org/html/2504.05690v2 — high — landscape

## Leads
APSIPA 2025 P424 contents; MIREX 2024 submissions; Florence Price release link/base model; AccoMontage-3 stage-1 CPU feasibility and lead-sheet format; C&E Embellish dataloader format; PopMAG code.

## Not found
No 2025–2026 public runnable melody+chords → piano repo beyond the known list; no Mac/CPU notes for AccoMontage-3, C&E, CoCoMulla; AccoMontage-3 Likert means; C&E listening numbers and meter.
