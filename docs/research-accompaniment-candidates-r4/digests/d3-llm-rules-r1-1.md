# D3 round 1: LLM harmonization evidence + rule-based harmonizers (accessed 2026-11-21)

Researcher assistant; ~11 sources, 20 tool calls. Headline: no study tests GPT-4o/GPT-5/Claude/Gemini/DeepSeek on harmonizing a given melody, and none on writing piano accompaniment from chords.

## Studies
| Study | Year | Models | Setup | Judged / numbers | Failure modes | Code |
|---|---|---|---|---|---|---|
| ChatMusician / MusicTheoryBench, arXiv 2402.16153 (ACL Findings 2024) | 2024 | ChatMusician (LLaMA2-7B on ABC), GPT-4, GPT-3.5, LLaMA2 | ABC melody + "Formulate chord combinations..."; chord-conditioned generation | edit distance to prompt melody/chords (percentiles); valid ABC: ChatMusician 99.6%, GPT-4 94.6%, GPT-3.5 65.4%; listening N=80: ChatMusician preferred over GPT-4 76% (general musicality); per-task numbers in Fig. 8 (not read) | GPT-4 malformed ABC; ChatMusician Irish-folk bias; metric checks retention, not harmonic quality | shanghaicannon.github.io/ChatMusician |
| "Can LLMs 'Reason' in Music?" arXiv 2407.21531 (ISMIR 2024) | 2024 | GPT-4, Gemma-7B, Llama2-7B, Qwen-7B | 355 ABC melody-harmonization items, expert multi-turn prompts, CoT vs default | experts 0–10: GPT-4 instruction following 6.5 (SD 3.5), condition adherence 5.5 (SD 2.5); Gemma 3.0 / 4.5; GPT-4 won A/B musicality | invalid ABC, motif copying, unstructured harmonic repetition, off-key notes, conditions ignored; GPT-4 "well short of human expectations" | github.com/SylviaZiyaZhou/LLMs_music_reasoning |
| ABC-Eval arXiv 2509.23350 | 2025 | GPT-5 family, Gemini 2.5, DeepSeek | 10 ABC understanding tasks, 1,086 items, no harmony task | bar counting GPT-5 93, GPT-5-mini 99, Gemini-pro 66, DeepSeek-chat 30; overall GPT-5 55.0 | prompt sensitivity, weak segment reasoning | anonymous.4open.science/r/ABC-Eval-B622 |
| Kruspe, Harmonic reasoning in LLMs, arXiv 2409.05521 | 2024 | GPT-3.5, GPT-4o | interval/chord/scale reasoning | snippet: ~100% simple intervals, struggles with chords/scales | — | — |
| MusiChat arXiv 2607.24873; Libretto arXiv 2606.22708 | 2026 | unnamed | LLM + symbolic engine; agent framework with harmony as one axis | no harmonization numbers in abstracts | — | none |

## Tools
| Tool | Link | Licence | Status | I/O | Method | Eval |
|---|---|---|---|---|---|---|
| VeeHarmGen | github.com/RedFerret61/VeeHarmGen | license.txt (not read) | v3.1.0 2025 | monophonic MusicXML → MusicXML with chord symbols per style | pitch-class set lookup in style files (pop/jazz/classical/blues); music21 9.1, Py3.10–3.12 | qualitative only |
| AutoHarmonizer | github.com/sander-wood/autoharmonizer | MIT | Py3.7, TF2.2, music21 6.7.1 | music21-parsable → harmonized | neural (Keras, Wikifonia), harmonic density control | arXiv 2112.11122 (not read) |
| meagtan/harmonizer | github.com/meagtan/harmonizer | MIT (snippet) | ~15 stars | melody → key + chords | DBN/Viterbi (HMM-style) | none |
| romanyh | github.com/napulen/romanyh | — | — | Roman numerals → 4-part voicing | voice leading (does not harmonize) | — |
| Impro-Visor | github.com/Impro-Visor/Impro-Visor | GPLv2 (SourceForge) | active download on SourceForge | lead sheet → accompaniment styles | Java grammar/style | — |
| Others: 383-Harmonizer, MusicPlusOne, sebas673/Harmonizer, SunChungEn NADE | — | mostly unknown | student/research | MIDI/music21 | rules/Markov/neural | none |

## Claims (accessed 2026-11-21)
1. ChatMusician harmonization scored by edit distance to the prompt melody (retention, not harmony quality) — arxiv.org/html/2402.16153v1 — 2024-02 — high — performance
2. Valid ABC: ChatMusician 99.6%, GPT-4 94.6%, GPT-3.5 65.4%; listeners preferred ChatMusician over GPT-4 76% (N=80) — same — high — performance
3. GPT-4 experts 6.5/10 instruction following, 5.5/10 condition adherence on 355 harmonization items; Gemma 3.0/4.5 — arxiv.org/html/2407.21531v1 — 2024-07 — high — performance
4. Reported LLM harmonization failures: off-key notes, unstructured harmonic repetition, motif copying, conditions ignored — same — high — performance
5. Prompts/code public — github.com/SylviaZiyaZhou/LLMs_music_reasoning — medium — landscape
6. ABC-Eval has no harmony task; bar counting 30% (DeepSeek-chat) to 93–99% (GPT-5 family) — arxiv.org/html/2509.23350v1 — 2025-09 — high — performance
7. GPT-4o strong on intervals, weak on chord/scale recognition — arxiv.org/html/2409.05521v1 — 2024-09 — low (snippet) — performance
8. VeeHarmGen v3.1.0 (2025), music21-based style lookup, no quantitative eval — github.com/RedFerret61/VeeHarmGen — high — landscape
9. AutoHarmonizer MIT, neural, 2020-era stack — github.com/sander-wood/autoharmonizer — high — licence/compat
10. Impro-Visor GPLv2 — sourceforge.net/projects/impro-visor — medium — licence
11. meagtan/harmonizer MIT DBN/Viterbi on music21 — github.com/meagtan/harmonizer — medium — licence
12. Yeh et al.: chord accuracy alone is a poor harmonization measure; pairs CTnCTR/PCS/MCTD with listener ratings (202 participants) — arxiv.org/pdf/2001.02360 — medium — landscape

## Leads
ChatMusician Fig. 8; Yeh et al. template/HMM baselines; LilyBench arXiv 2606.08722; VeeHarmGen licence; AutoHarmonizer numbers.

## Not found
Harmonization evals of GPT-4o/5, Claude, Gemini, DeepSeek, NotaGen/MuPT; any LLM chords→piano accompaniment eval; music21 built-in harmonizer (believed absent, unverified).
