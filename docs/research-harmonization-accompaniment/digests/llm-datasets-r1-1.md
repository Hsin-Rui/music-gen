# Digest: LLM harmonization evidence + chord-annotated melody datasets (round 1, pass 1)

Accessed 2026-11-21 for all sources. Evidence comes only from sources retrieved this run. Most were read as abstract or landing pages, not full PDFs, so numeric detail is thin where noted.

## Findings

### Q1: LLM harmonization / music-theory evidence

1. **claim:** Gemini 2.5 Pro, Gemini 2.5 Flash and Qwen2.5-Omni were tested on chord-quality identification, transposition detection and syncopation scoring. Models are "near ceiling" on symbolic MIDI input but drop sharply on audio. Few-shot prompting and reasoning strategies (CoT, LogicLM, where the LLM emits a machine-checkable schema run by a deterministic solver) gave minimal gains. Chord-quality accuracy was "slightly below" syncopation; the landing page gives no figures. Implication: symbolic text in works better than audio in. This is weak evidence for a text-in "conductor".
   - source: https://proceedings.mlr.press/v303/carone26a.html | publisher: PMLR vol. 303 (Carone, Roman, Ripollés) | pub_date: 2026-01 | confidence: med (abstract-level) | class: capability
2. **claim:** In an informal blog test, Claude Opus 5, Gemini 3.1 Pro and Grok 4.5 Expert did Roman-numeral analysis of Bach BWV 269, Chopin Op. 9/1 and Scriabin Op. 2/1. Score images failed, while LilyPond code input worked (MusicXML is also said to be usable). Scores were Gemini 95/100/75%, Grok 80/92/40% and Opus 5 88% (the hard Scriabin case). Shared failure modes: suspensions ignored, a modulation cue (A#) missed, a secondary dominant misread as a leading-tone chord, wrong inversion. Accuracy falls as chromaticism increases. There was no comparison with music21 or other tools.
   - source: https://aug5th.substack.com/p/llms-vs-harmonic-analysis | publisher: Augmented Fifth (Substack, "Auggie") | pub_date: 2026-08-06 | confidence: low (n=3 excerpts, single grader) | class: capability
3. **claim:** ChatGPT, Claude and Gemini (versions not given on the page) were tested on RCM Level 6 theory exam questions in ABC, Humdrum, MEI and MusicXML. Best result without context: ChatGPT with MEI, 52%. Best with in-context teaching: Claude with MEI, 75%. A search snippet says chord analysis improved least, while intervals, scales, transposition and cadences improved most. Encoding choice matters, and MEI was best for the best runs.
   - source: https://arxiv.org/abs/2503.22853 | publisher: arXiv / CSME 2025 (Pond & Fujinaga, McGill) | pub_date: 2025-03-28 | confidence: med (headline numbers verified; chord-specific claim from snippet only) | class: evaluation
4. **claim:** MSU-Bench (Musical Score Understanding Benchmark) has 1,800 generative QA pairs over complete scores (Bach to Debussy), in ABC text and PDF image modalities, at four levels from onset to texture/form. A search snippet says a harmony level covers chord analysis. More than 15 models were tested. Findings: modality gaps, unstable per-level performance, and trouble keeping correctness across levels. A snippet adds that models fail to locate specific bars, which hurts harmony questions. Fine-tuning improves results while keeping general knowledge, which conflicts with the known "trade-off" finding. Accepted at ACL 2026 Main.
   - source: https://arxiv.org/abs/2511.20697 | publisher: arXiv (Dai et al., incl. Maosong Sun) | pub_date: 2025-11-24 (v4 2026-04-23) | confidence: med (model names and per-task numbers not read) | class: evaluation
5. **claim:** ZIQI-Eval evaluated 16 LLMs on music comprehension and generation (theory, composition, genres, history). API models scored notably higher than open-source models. 2024 models only.
   - source: https://arxiv.org/html/2406.15885v1 | publisher: arXiv | pub_date: 2024-06 | confidence: low (snippet only, not deeply read) | class: evaluation
6. **claim:** ChatMusician / MusicTheoryBench is described as a "college-level" benchmark. ChatMusician beats LLaMA2 and GPT-3.5 "by a noticeable margin". The abstract makes no GPT-4 claim. Corpus (MusicPile), benchmark, code and model are released; their licences are not stated on the Anthology page. The paper itself is CC BY 4.0. These are 2023-era models, so this says nothing about current models.
   - source: https://aclanthology.org/2024.findings-acl.373/ | publisher: ACL Findings 2024 | pub_date: 2024-08 | confidence: med | class: evaluation
7. **claim (hybrid):** ComposerX is a multi-agent GPT-4 system with Melody, Harmony, Instrument and Arrangement agents. The Harmony agent adds chords and counterpoint and checks the progression against the melody's tonality, with output in ABC. It is described as the first LLM multi-agent polyphonic symbolic composition system. This is the closest prior design to an "LLM conductor".
   - source: https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/98627/ (ComposerX, Deng et al., incl. Benetos) | publisher: QMUL repository / ISMIR 2024 (venue unverified) | pub_date: 2024 | confidence: low-med (search snippet, not read in full) | class: capability
8. **claim (hybrid):** Libretto is a framework that gives LLM agents a grammar with explicit onset slots, voices and bars. Each piece is scored in a corpus-calibrated statistical space (rhythm, harmony, melody, texture, form, variation) used for diagnosis and self-revision. The abstract names no LLMs and reports no quantitative harmony results. The paper is CC BY 4.0.
   - source: https://arxiv.org/abs/2606.22708 | publisher: arXiv (Yichen Xu) | pub_date: 2026-06-21 | confidence: low | class: capability
9. **claim (hybrid):** CoComposer (LLM multi-agent collaborative composition, 2025) and ByteComposer (2024, a melody-only agent pipeline) exist as further agent designs. A LLaMA 3.1 LoRA multi-task framework includes chord-progression generation and is trained on POP909.
   - source: https://arxiv.org/pdf/2509.00132 ; https://arxiv.org/pdf/2402.17785 ; https://link.springer.com/chapter/10.1007/978-981-95-9843-4_17 | publisher: arXiv / Springer | pub_date: 2025 / 2024 / 2025 | confidence: low (titles/snippets only) | class: capability
10. **claim:** Search found no rigorous benchmark of a general LLM (GPT-4/5, Claude, Gemini) on melody harmonization measured against dedicated harmonizers such as AccoMontage2 or CMD-trained models. GPT-4 harmonization evidence is informal: blog and HN posts, where a commenter warns its chord output "can't be relied on".
    - source: https://news.ycombinator.com/item?id=36497414 ; https://www.audiocipher.com/post/chatgpt-music | publisher: HN / AudioCipher | pub_date: 2023 | confidence: med (absence after two searches) | class: evaluation

### Q2: Datasets (verified items)

11. **claim:** POP909 has 909 pop songs. Each has a MIDI file with MELODY (vocal), BRIDGE (sub-melody) and PIANO (accompaniment) tracks plus alternate versions. Beat, chord and key are in time-stamped .txt files. Chords and keys come from MIR algorithms (paper: tempo hand-labelled, the rest algorithmic). The chord vocabulary includes sus, 6th, 7th and inversions. The repo is MIT-licensed (LICENSE text not quoted). This run did not verify that the songs are Chinese pop: the repo says only "pop-song dataset", and only a third-party summary says Chinese.
    - source: https://github.com/music-x-lab/POP909-Dataset ; https://arxiv.org/pdf/2008.07142 | publisher: Music X Lab, NYU Shanghai / ISMIR 2020 | pub_date: 2020 | confidence: high (contents), med (licence) | class: dataset, licence
12. **claim:** Hooktheory.json.gz (about 20 MB) holds 50 hours of melody and harmony annotations aligned to audio (audio not included), with artist-stratified 8:1:1 splits and tags. The data is CC BY-NC-SA 3.0; the code is MIT.
    - source: https://github.com/chrisdonahue/sheetsage | publisher: Donahue, Thickstun, Liang (ISMIR 2022, arXiv 2212.01884) | pub_date: 2022 | confidence: high | class: dataset, licence
13. **claim:** Chordonomicon has 679,807 rows (more than 666k songs) of chord progressions with section tags (intro, verse, chorus), genre, decade and Spotify IDs. It has no melody. CC BY-NC 4.0. CSV/Parquet on Hugging Face.
    - source: https://huggingface.co/datasets/ailsntua/Chordonomicon | publisher: Kantarelis et al. (NTUA), arXiv 2410.22046 | pub_date: 2024 | confidence: high | class: dataset, licence
14. **claim:** When-in-Rome holds about 2,000 Roman-numeral analyses of about 1,500 works in RomanText, with scores as MusicXML or remote links. Contents: 371 Bach chorales, Beethoven quartets (ABC/DCML, 70 movements), Mozart sonatas, Chopin mazurkas, Haydn Op. 20, BPS-FH, TAVERN, Monteverdi madrigals, WTC I preludes, and Lieder (Winterreise, Schwanengesang, Dichterliebe). New content is CC BY-SA 4.0. Externally sourced analyses keep their own licences.
    - source: https://github.com/MarkGotham/When-in-Rome | publisher: Mark Gotham et al. | pub_date: continuously updated | confidence: high | class: dataset, licence
15. **claim:** Chord Melody Dataset (CMD) is jazz and standards lead sheets ("all_of_me", "blue_bossa") in MusicXML, OCR-scanned with SmartScore. It has 2 chords per 4/4 bar, a monophonic melody and no triplets. MIT licence on the repo. The count is not shown on the page; a 2025 paper says CMD is smaller than 650 pieces. The source sheets may be copyrighted songs regardless of the repo licence.
    - source: https://github.com/shiehn/chord-melody-dataset ; https://doi.org/10.3390/app15179513 | publisher: shiehn (GitHub) / MDPI Appl. Sci. 2025 | pub_date: n.d. / 2025 | confidence: med | class: dataset, licence
16. **claim:** OpenGufeng is a melody-plus-chord dataset of Gufeng (Chinese-style pop) in a single key, played at four tempi. It is raw MIDI, with cleaning still a to-do. Chords are reduced to major/minor triads (per snippet). MIT licence label. No paper yet.
    - source: https://github.com/yongyizang/OpenGufeng | publisher: Yongyi Zang (GitHub) | pub_date: n.d. | confidence: med | class: dataset, licence
17. **claim:** The Chinese Chorales Dataset has 125 Chinese chorales in 441 score segments with chord annotations, hosted on GitHub.
    - source: https://www.springerprofessional.de/en/chinese-chorales-dataset-a-high-quality-music-dataset-for-score-/26698008 | publisher: Springer | pub_date: ~2024 | confidence: low (snippet; licence unread) | class: dataset
18. **claim:** Diao annotations cover 219 heptatonic Chinese folk melodies from Essen (diao category, gong, diao tou, pitch-class profiles). CC BY 4.0 but labelled "Dataset Restricted". These are modal labels, not chords.
    - source: https://zenodo.org/records/14607710 | publisher: Meng, Moss, Rohrmeier (Zenodo) | pub_date: 2025 | confidence: med | class: dataset, licence
19. **claim:** HarmonyTok (2025) used more than 17,000 lead-sheet charts with melody and chords as separate MIDI tracks. MelodyHub (MelodyT5) has 261,900 ABC melodies, with harmonization as one of seven tasks. A curated jazz-standards harmonization set (650 pieces) is available on request only, for copyright reasons.
    - source: https://doi.org/10.3390/info16090759 ; https://arxiv.org/pdf/2407.02277 ; https://doi.org/10.3390/app15179513 | publisher: MDPI Information / arXiv / MDPI | pub_date: 2025 / 2024 / 2025 | confidence: low (snippets) | class: dataset

## Dataset catalogue

| Name | Size | Melody | Chords | Accomp. | Key/structure | Format | Licence (verified?) | Style/culture | Paper |
|---|---|---|---|---|---|---|---|---|---|
| POP909 | 909 songs (+versions) | yes (vocal + bridge) | yes, algorithmic, extended vocab | yes (piano) | key (alg.), beat; tempo hand-labelled | MIDI + txt | MIT (repo label; text unread) | Pop (Chinese: unverified this run) | ISMIR 2020, arXiv 2008.07142 |
| Hooktheory (Sheet Sage) | ~50 h, 20 MB JSON | yes | yes | no | splits, tags; key unclear | JSON | CC BY-NC-SA 3.0 (verified) | Western pop/various | ISMIR 2022, arXiv 2212.01884 |
| Chordonomicon | 679,807 progressions | no | yes (user tabs) | no | sections, genre, decade | CSV/Parquet | CC BY-NC 4.0 (verified HF card) | Western pop/rock etc. | arXiv 2410.22046 |
| When-in-Rome | ~2,000 analyses / 1,500 works | via scores | Roman numerals | via scores | keys, modulations | RomanText + MusicXML | CC BY-SA 4.0 for new content; external ones vary (verified) | Classical (Bach to Schumann), Monteverdi | Gotham et al. (several) |
| Bach chorales (in When-in-Rome) | 371 | yes (SATB) | RN | yes (4-part) | key | RomanText + score | per When-in-Rome / Tymoczko source | Baroque chorale | - |
| ABC Beethoven quartets (DCML) | 16 quartets / 70 mvts | in score | RN (DCML standard) | yes | yes | DCML TSV / RomanText | not verified this run | Classical | Neuwirth et al. 2018 (unverified) |
| Chord Melody Dataset | <650 (count unread) | yes, monophonic | yes, 2/bar | no | 4/4 only | MusicXML | MIT repo (underlying songs likely copyrighted) | Jazz standards | none |
| OpenGufeng | unstated | yes | triads | no | single key | raw MIDI | MIT label | Chinese Gufeng pop | none yet |
| Chinese Chorales Dataset | 125 chorales / 441 segments | yes | yes | choral | ? | ? (GitHub) | unread | Chinese choral | Springer ~2024 |
| Essen Chinese diao annotations | 219 melodies | via Essen | no (modal labels) | no | diao/gong | Zenodo | CC BY 4.0, restricted access | Chinese folk | Meng/Moss/Rohrmeier |
| HarmonyTok lead sheets | >17,000 | yes | yes | no | ? | MIDI (2 tracks) | unread | lead sheets (source unread) | MDPI Information 2025 |
| MelodyHub | 261,900 melodies | yes | partial (harmonization task) | no | ABC headers | ABC | unread | mostly folk/Western | MelodyT5, ISMIR 2024 |
| Tegridy MIDI chords-melody subset | ? | yes | yes | no | ? | MIDI | unread | mixed | none |

Not verified this run (mention only as candidates): Wikifonia (past availability unclear), Nottingham (ABC folk with chords), McGill Billboard (chords on audio, no melody), Rock Corpus (de Clercq & Temperley; RN + melody transcriptions), DCML corpora (believed CC BY-NC-SA 4.0, unverified), the Lead-Sheet Dataset (TheoryTab-derived, used by LeadsheetGAN), FaiSonic MMD (arXiv 2611.13503, pop with multidimensional annotations, chords unknown), CCMusic (Chinese MIR; no chords seen).

## Leads worth chasing

- Read the full MSU-Bench PDF for harmony-level per-model numbers and model names (may include GPT-5 / Claude / Gemini 2.5+).
- Read the Carone et al. PDF for chord-quality numbers on MIDI versus audio, and for the LogicLM schema, which is a model for an LLM that emits a checkable spec and a tool that executes it.
- Read Pond & Fujinaga for per-encoding results on chord questions (ABC vs MEI vs MusicXML) to choose a prompt format.
- ComposerX / CoComposer full text: how the Harmony agent is prompted, and whether chord-fit validation exists.
- Verify the POP909 paper's statement on song origin (Chinese pop) and read the LICENSE text.
- DCML corpora licence (GitHub DCMLab), Rock Corpus availability, the Nottingham cleaned version (jukedeck/nottingham-dataset) licence, the Wikifonia status.
- FaiSonic MMD (2026-11): check for chord and melody alignment and Chinese content.
- Chinese Chorales Dataset GitHub licence.
- Augmented Fifth's other post, "Testing LLMs on Undergraduate Music Theory" (2025–26 models, chord spelling).

## Looked for, could not find

- A dedicated benchmark of general LLMs on melody harmonization (melody in, chords out) with objective metrics compared against trained harmonizers: none found in two searches.
- A music-theory Roman-numeral benchmark specifically for LLMs: the search returned only numeracy (Roman numbers) papers.
- A chord-annotated Chinese folk-song corpus: none found. The closest are the Essen diao (modal) labels, OpenGufeng (pop) and the Chinese Chorales Dataset.
- Licence text for MusicPile / ChatMusician weights (not on the Anthology page).
- Any evaluation of voice-leading quality produced by general LLMs: none found.
