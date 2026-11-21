# Red team: claim C3, "neural generation + IRT for music-ability testing is an open gap"

Skeptic pass, 2026-11-19. Budget: 15 tool calls (14 used). Web only; no local files read.

## Verdict

**Survives, with one wording fix.** I searched 12 times and fetched one page. None of it turned up a paper, preprint or thesis that uses a neural generator (transformer, VAE, diffusion or LLM) to make music-ability test items and then calibrates them with IRT or adaptive testing. The factual premise checks out against the primary source. Harrison, Collins & Müllensiefen (2017) generated their melodic discrimination base melodies with a Markov-chain model trained on Irish folk tunes from the Essen collection. Item difficulty was explained by a few controlled "radicals": length, plus contour and tonality violations (Study 1 regression, adjusted R² = 0.869). The same AIG + IRT + CAT approach was reused for CA-BAT (2018) and aPIAT (2020–21), and I found no 2024–2026 successor that uses neural generation.

The nearest work falls short of the claim in specific ways:
- An ICMPC 2023 study used an EC2-VAE to make interpolated melodies for similarity ratings. These are perception stimuli, not calibrated test items, and there is no IRT.
- A 2025 UAB bachelor's thesis aimed to build a set of AI-generated music stimuli for cognition research. Its own diffusion model failed, so it fell back on Suno, and it has no difficulty calibration.
- A JHU paper (ICASSP 2020) synthesised surprisal-maximising melodies with the D-REX model. That is a statistical model, not a neural one, and the paper measures engagement, not ability.

**Wording fix.** "No published work" is a claim that something does not exist, and a 15-call web search cannot prove that. Phrase it as "no such work found in a targeted search of 2017–2026 literature."

**Strongest good-faith counter-argument (my own reasoning, not taken from a retrieved source).** The gap may be open because filling it is not worth much, not because nobody thought of it:
1. The Markov-chain approach already explains about 87% of difficulty variance. That leaves little room for a neural generator to improve calibration.
2. Explanatory IRT and AIG get their construct validity from interpretable, manipulable radicals (complexity, similarity). A black-box neural generator weakens that validity unless its outputs are mapped back onto those features.
3. Neural models trained on large corpora may reproduce familiar tunes or idioms. That brings in familiarity and enculturation confounds, the problem the UAB thesis was trying to avoid.

So the gap is real, but the case for filling it has to show what neural generation adds, such as stylistic range, ecological validity or new constructs. It cannot just say "nobody has done it."

## Disconfirming evidence

None of these overturns the claim. They are listed because they come closest or qualify it.

| Claim | Title | URL | Publisher | Pub date | Peer-review status |
|---|---|---|---|---|---|
| Confirms the premise: MDT items came from a Markov chain trained on Essen Irish folk tunes; difficulty explained by length, contour and tonality violations (adj. R² = 0.869) | Applying modern psychometric techniques to melodic discrimination testing: IRT, CAT, and AIG | https://pmc.ncbi.nlm.nih.gov/articles/PMC5472621/ | Scientific Reports (Nature) | 2017-06 | Peer-reviewed |
| AIG + IRT + CAT reused for a beat test, no neural generation (shows how far the paradigm spread) | Development and validation of the Computerised Adaptive Beat Alignment Test (CA-BAT) | https://pmc.ncbi.nlm.nih.gov/articles/PMC6097996 | Scientific Reports | 2018 | Peer-reviewed |
| AIG + adaptive testing for pitch imagery, no neural generation | aPIAT (adaptive Pitch Imagery Arrow Task) | https://link.springer.com/article/10.1007/s00426-020-01322-3 | Psychological Research (Springer) | 2020–21 | Peer-reviewed |
| Nearest neural case: VAE-generated melodies used as perception stimuli with similarity ratings (N = 33); no IRT, not test items | Kim et al., human vs. AI (EC2-VAE) melody interpolation | https://mac.kaist.ac.kr/pubs/kim-icmpc2023.pdf | ICMPC 2023 proceedings (KAIST) | 2023 | Conference paper, review level unverified |
| Aimed to build a set of generative-AI music stimuli for cognition research; its own diffusion model failed, so it used Suno; no difficulty calibration | Generative AI Framework for Creating a Music Dataset with Quantifiable Acoustic and Cognitive Features | https://ddd.uab.cat/record/317789/?ln=en | Universitat Autònoma de Barcelona (TFG) | 2025 (approx.) | Bachelor's thesis, not peer-reviewed |
| Model-generated melodies designed to maximise surprisal (statistical D-REX model, not neural); measures engagement, not ability | Kothinti et al., ICASSP 2020 | https://engineering.jhu.edu/lcap/data/uploads/pdfs/icassp2020_kothinti.pdf | IEEE ICASSP | 2020 | Peer-reviewed conference |
| Neural difficulty modelling exists next door: generating piano scores with a target difficulty (an education tool, no IRT, not an ability test) | Difficulty-Aware Score Generation for Piano Sight-Reading | https://arxiv.org/pdf/2509.16913 | arXiv | 2025-09 | Preprint |

## Searched, not found

- Deep-learning-generated melodies combined with IRT in a music-ability test
- Neural networks or transformers in automatic item generation for auditory tests with IRT calibration; the only hits were text-item AIG and AUDITA, an audio-QA benchmark that reports IRT difficulty but generates no items
- Transformer-generated melodies used as calibrated experimental stimuli
- Psychometric validation of tests built from AI-generated music stimuli; the only hits were emotion studies such as Fišer et al., PLOS ONE 2025
- Neural prediction of item difficulty for music-ability tests
- LLM-generated ear-training or music-theory items with difficulty calibration against human response data
- Generative-model stimulus work at PsyNet or the Max Planck Institute for Empirical Aesthetics; nothing relevant came back, but that search was shallow and is not strong evidence of absence
- 2024–2026 successors to the Goldsmiths AIG tests (MDT, CA-BAT, aPIAT) that use neural generators
- Published critiques of AI-generated test items on validity grounds; none found, so the counter-argument above is my own reasoning
