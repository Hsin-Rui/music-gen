# Red team C1: "Adopt and fine-tune existing open symbolic models"

Run date: 2026-11-19. Budget: 15 tool calls. Sources were retrieved this run. Anything marked "unverified belief" was not evidenced.

## Verdict

**Weakened, not overturned.** I found no evidence that training a small model from scratch beats fine-tuning these four models, whether in general or for non-Western or Chinese-opera material. No study made that comparison directly, so the core "adopt, don't train" strategy stands. But several parts of the conclusion as written are overstated:

1. **"Feasible on 24GB" holds only partly.** The NotaGen README says NotaGen-large needs *at least* 24GB to train, so a 24GB card is at the ceiling and in practice means NotaGen-small or NotaGen-medium. The Aria model card gives no fine-tuning instructions and no memory figures.
2. **The licence and provenance situation is weaker than "open" suggests.** The AMT authors say Lakh MIDI's CC-BY label hides heterogeneous, mostly undocumented copyright on derivative pop transcriptions. They say outputs "should be presumed to risk infringing". The NotaGen repo does not name its 1.6M-piece pretraining sources. The Aria-MIDI dataset is CC-BY-NC-SA, although the Aria weights are Apache-2.0. Stimuli for non-commercial academic use are probably still publishable. That is an unverified belief, not legal advice. But stimulus sets cannot be called "clean", and commercial reuse is unclear.
3. **"Culturally diverse" is the weakest part.** Western-default behaviour is documented, but for *audio* models (MusicGen, Mustango) and as an argument about the MIDI format. Symbolic studies make the same case from data and format analysis rather than benchmarks. Machine-readable Peking-opera (jingju) scores exist, but no prior symbolic jingju generation model turned up. The related jingju data is CC-BY-NC. A small pretrained-then-fine-tuned Music Transformer memorised a 32-piece fine-tuning set. That makes overfitting and copying a concrete risk at jingju-corpus scale. It also means the evaluation layer has to include memorisation checks such as LCS or n-gram overlap.
4. **Text2midi has thin evaluation.** Its listening test used 5 generated files, and later work had to realign test splits to compare against it.

The strongest good-faith case for a small custom model is this. For a tradition whose pitch inflection and ornamentation fit 12-TET MIDI or ABC tokens poorly, a custom tokenizer may matter more than pretrained weights. It is also the only way to control training-data provenance fully. A small model trained on a few hundred scores has little capacity to memorise beyond what it is given, and both the data and its licence are fully known. This argument is plausible but **unverified**: no paper retrieved this run shows it winning.

## Disconfirming evidence

| Claim | Title | URL | Publisher | Pub date | Peer review |
|---|---|---|---|---|---|
| NotaGen-large needs at least 24GB GPU memory to train; the pretrained weights cannot do period-composer-instrumentation conditional generation; the pretraining data sources are not named | NotaGen GitHub README | https://github.com/ElectricAlexis/NotaGen | GitHub (authors) | not stated (repo, accessed 2026-11-19) | Not peer-reviewed (code repo); paper in IJCAI 2025 |
| NotaGen fine-tuning used ~9K classical pieces from 152 composers, not folk or non-Western music | NotaGen: Advancing Musicality in Symbolic Music Generation with LLM Training Paradigms | https://arxiv.org/abs/2502.18008 | arXiv / IJCAI 2025 | 2025-02 | Peer-reviewed (IJCAI 2025) |
| Lakh MIDI's CC-BY label covers heterogeneous, mostly undocumented copyright on derivative transcriptions; AMT outputs "should be presumed to risk infringing" | Anticipatory Music Transformer | https://arxiv.org/pdf/2306.08620 | arXiv (later TMLR) | 2023-06 | Peer-reviewed (TMLR; unverified belief, venue not confirmed this run) |
| LMD has "documented licensing violations"; PDMX (public domain) offered as the alternative | PDMX: A Large-Scale Public Domain MusicXML Dataset | https://arxiv.org/html/2409.10831 | arXiv | 2024-09 | Preprint (venue not confirmed this run) |
| MIDI-GPT authors limit the model to non-commercial use because its legal status is unclear | MIDI-GPT: A Controllable Generative Model for Computer-Assisted Multitrack Music Composition | https://arxiv.org/pdf/2501.17011 | arXiv | 2025-01 | Preprint (venue not confirmed) |
| Aria-MIDI training corpus is CC-BY-NC-SA 4.0, crawled from internet audio by an LM pipeline; audio and raw metadata withheld for copyright reasons | Aria-MIDI: A Dataset of Piano MIDI Files for Symbolic Music Modeling | https://arxiv.org/abs/2504.15071 | ICLR 2025 | 2025-04 | Peer-reviewed (ICLR 2025) |
| Aria model card has an inference quickstart only; no fine-tuning instructions or memory needs; parameter count (0.7B) and stated architecture (LLaMA 3.2 1B) disagree | loubb/aria-medium-base model card | https://huggingface.co/loubb/aria-medium-base | Hugging Face | not stated | Not peer-reviewed |
| Text2midi listening study used only 15 files (5 generated); later work had to take the intersection of mismatched MidiCaps test splits (896 samples) to compare | Text2midi: Generating Symbolic Music from Captions; MIDI-LLM | https://arxiv.org/abs/2412.16526 ; https://arxiv.org/pdf/2511.03942 | arXiv (Text2midi at AAAI 2025: unverified belief) | 2024-12; 2025-11 | Text2midi peer-reviewed (unverified); MIDI-LLM preprint |
| Music models fall back on Western tonal and rhythmic structures for Indian and Middle Eastern genres; only 5.7% of dataset hours are non-Western (audio models) | Missing Melodies: AI Music Generation and its "Nearly" Complete Omission of the Global South | https://arxiv.org/abs/2412.04100 | arXiv | 2024-12 | Preprint |
| MIDI-style formats encode Western tonal and rhythmic defaults and marginalise microtonality, heterophony and non-metric rhythm | Who Gets Heard? Rethinking Fairness in AI for Music Systems | https://arxiv.org/pdf/2511.05953 | arXiv | 2025-11 | Preprint |
| Adapting music generators to Hindustani and Makam needed purpose-built adapters; different adapter types capture ornamentation and long-range structure differently (audio models) | Exploring Adapter Design Tradeoffs for Low Resource Music Generation | https://arxiv.org/abs/2506.21298 | arXiv | 2025-06 | Preprint |
| A Music Transformer pretrained on ~700 classical MIDI files then fine-tuned on 32 Beethoven sonatas memorised the pieces and failed to generate new ones | (Tamim et al.; Beethoven sonata generation) | https://lamsade.dauphine.fr/~cazenave/papers/Tamim.pdf | LAMSADE, Univ. Paris-Dauphine | not confirmed | Unknown (not confirmed) |
| Large models trained on a small piano corpus (MAESTRO) face a tradeoff: they must partly overfit to learn high-level structure | (2025 piano generation / Moonbeam fine-tuning study) | https://arxiv.org/html/2511.07268v2 | arXiv | 2025-11 | Preprint |
| Machine-readable jingju scores exist (first for computational analysis); related a cappella dataset is CC-BY-NC 4.0; Peking opera "has received little effort" and few datasets exist | Jingju score corpus (ISMIR 2017); Jingju a cappella dataset; Synthesising Expressiveness in Peking Opera via DurIAN | https://archives.ismir.net/ismir2017/paper/000119.pdf ; https://zenodo.org/record/842229 ; https://arxiv.org/pdf/1912.12010 | ISMIR; Zenodo; arXiv | 2017; 2018; 2019 | ISMIR 2017 peer-reviewed; Zenodo dataset n/a; arXiv preprint |
| Fine-tuning that adapts more to music loses more general capability; long sequences are harder to adapt to (general LLMs, not the four target models) | How Far Can Pretrained LLMs Go in Symbolic Music? | https://arxiv.org/html/2601.22764 | arXiv | 2026-01-30 | Preprint |

## Searched, not found

- Any report of fine-tuning NotaGen on Chinese folk, opera or other non-Western ABC corpora, whether it succeeded or failed.
- GitHub issues or reports of AMT (jthickstun/anticipation) fine-tuning failing or ignoring conditioning on small datasets. The training notes say only that Lakh preprocessing needs a lot of memory.
- A direct symbolic-domain comparison of pretrained-then-fine-tuned versus from-scratch models on makam, Carnatic, Hindustani or jingju.
- A published symbolic (score-level) jingju generation model.
- Evidence that any of the four models' code is abandoned or broken (not checked in depth; issue trackers were not read).
- The MidiCaps / Text2midi licence terms (not retrieved).
- The jingju score corpus size, format and licence (the PDF could not be parsed this run).
- Peer-reviewed benchmarks showing Western-bias failure of the *symbolic* models specifically. All direct failure evidence found was for audio models.
- Any court ruling or legal analysis on publishing research stimuli generated by models trained on Lakh or internet-transcribed data.
