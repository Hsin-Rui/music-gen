# D2 round 1: melody harmonization models (accessed 2026-11-21)

Researcher assistant; ~19 tool calls. preprints.org and mdpi.com returned 403 (snippets only).

## Candidates
| Name | Year/venue | Code | Weights | Licence | I/O | Training | Hardware | Quality | Meter |
|---|---|---|---|---|---|---|---|---|---|
| BART (and GPT-2) harmonizer, Kaliakatsos-Papakostas et al. (NeuraLLMuse) = "BART harmonization" | arXiv 2512.07627 (2025-12); baseline in Applied Sciences 15(17):9513 | github.com/NeuraLLMuse/BStarConstraintHarmonization; NeuraLLMuse/HarmonyTok | none found | code Apache-2.0; paper CC BY 4.0 | MusicXML melody tokens → chord symbols (348 tokens = 12 roots × 29 qualities; or 12 pitch-class tokens) | HookTheory 17,476 lead sheets (transposed to C/Am) | ~50M params (8L/8H/d512) | val token acc ~80% (symbols)/85% (PC); CHE, CC, CTD, CTnCTR, PCS, MCTD, HRHE, HRC, CBS reported | time-sig token num 1–10, den 4/8 |
| B* constrained decoding | arXiv 2512.07627 (AIMC 2025 unconfirmed) | same repo | none | Apache-2.0 | as above + hard chord constraints | HookTheory | beam 4, lookahead 2; 290–1,925 mean model calls | constraint success 0.91–0.99 vs 0.20–0.27 unconstrained, 0.53–0.63 soft prompts | as above |
| EMO_Harmonizer | 2024–25 (repo 2025-12-15) | github.com/Yuer867/EMO_Harmonizer | Google Drive | no licence file | MIDI → events → chords/accompaniment | EMOPIA, HookTheory | Py3.8, CUDA 10.2, fast-transformers | not checked | not checked |
| MuPT | ICLR 2025, arXiv 2404.06393 | — | HF m-a-p/MuPT-v1-8192-{110M..1.3B} | Apache-2.0 (190M card) | ABC prefix continuation | 7M ABC pieces | card uses .cuda(); 110M plausible on CPU | no harmonization eval; not trained to harmonize a fixed melody | ABC M: header |
| HarmonyRL | 2026-11-16, no paper | github.com/HarmonyRL/HarmonyRL (pip harmonyrl) | HF CloudHolic/harmonyrl-{base,smooth,chromatic} (gated) | code MIT; weights CC BY-NC-SA 3.0 | MusicXML/MIDI lead sheet → chord symbols (MusicXML/MIDI); ≤32 bars per window; redraw selected bars | HookTheory (Sheet Sage release); transformer + RL fine-tune | "runs on CPU"; Py ≥3.12 | eval on gated cards, not read | splits at time-signature changes |
| SplitEncoder (NeuraLLMuse) | repo 2026-11-03 | github.com/NeuraLLMuse/SplitEncoder | promised, none in tree | Apache-2.0 | melody + masked harmony grid → harmony | presumably HookTheory | — | — | — |
| GridMLMelHarm | Applied Sciences 2025 | NeuraLLMuse/GridMLMelHarm | none | Apache-2.0 | 16th-grid melody → harmony (masked LM) | HookTheory + jazz | — | compared vs GPT-2/BART (numbers 403) | — |
| LatentTraceGuidance | ISMIR 2026 | NeuraLLMuse/LatentTraceGuidance | unknown | Apache-2.0 | controllable harmonization | — | — | — | — |
| GraphGuidanceMelodicHarmonization | 2026 | NeuraLLMuse repo | unknown | Apache-2.0 | GNN + PEFT | — | — | — | — |
| NeuraLLMuse MelodicHarmonizationDataset | 2026-10 | NeuraLLMuse repo | — | Apache-2.0 | 2-part MIDI dataset | — | — | — | — |
| CPFG-Net | arXiv 2511.14600 | github.com/huang0251/CPFG_model | not checked | MIT | melody → chords, tension control (Spiral Array CVAE) | — | Py3.11 | — | — |
| SurpriseNet | earlier (repo 2026-08) | github.com/scmvp301135/SurpriseNet | not checked | MIT | surprise-contour harmonization | — | — | — | — |
| Function Alignment (Jiang, Chin, Lin, Liu, Xia) | ISMIR 2025 poster 25 | claimed public, no URL | unclear | — | pretrained symbolic LM + adapter; melody→chord, chord recognition | — | — | CTnCTR, mir_eval (no numbers) | — |
| RL-Chord | IEEE TNNLS 2024 | not found | not found | — | melody → chords; zero-shot Chinese folk via style classifier | — | — | DQN best (snippet) | — |
| AI Harmonizer | NIME 2025, arXiv 2506.18143 | MIT Media Lab GitHub | — | — | vocal audio → voices | — | — | — | out of scope |
| Fernandes rule-based Harmonizer | arXiv 2501.02642 | GitHub (per paper) | n/a | — | melody → chords (Schoenberg regions, Giant Steps, modes) | — | CPU | — | — |
| Explainable Melody Harmonizer | arXiv 2610.22416 | quantum-inspired-music-research | n/a | — | rule-based scoring on HookTheory | HookTheory | CPU | — | — |
| Collaborative Harmonization | arXiv 2509.00120 | EyalBriman/CollaborativeHarmonization | — | none | aggregates human chord choices | — | — | — | — |
| asigalov61 Melody-Harmonizer-Transformer, Seq2Seq-Melody-Harmonizing-Transformer | HF 2024-08 / 2025-03 | HF | yes | Apache-2.0 (card) | MIDI → MIDI harmony | — | — | none | — |
| Hookpad Aria (AMT fine-tune, melody↔harmony) | 2024, arXiv 2502.08122 (likely) | product | not public | proprietary? | lead sheet | HookTheory | — | — | — |
| hobby repos (lamiazahid POP909, harmonyhmm, ECHO GA, maqam transformer, …) | 2026 | GitHub | mostly none | mixed | — | — | — | — | — |

## Claims (accessed 2026-11-21)
1. BART harmonizer: 8L/8H/d512 ~50M, 17,476 HookTheory sheets, 348 chord tokens or 12 PC tokens, time-sig token 1–10 / 4,8 — arxiv.org/html/2512.07627v1 (2025-12-08) — high — version/compat
2. BART/GPT-2 are baselines in GridMLMelHarm (Applied Sciences 2025) — mdpi.com/2076-3417/15/17/9513 (snippet) — medium — landscape
3. preprints.org 202505.1325 trains RoBERTa and GPT-2/BART on >17k charts — snippet — medium — landscape
4. BStar repo Apache-2.0, no checkpoints; HF NeuraLLMuse empty — github.com/NeuraLLMuse/BStarConstraintHarmonization (2025-07-10) — high — licence
5. B* constraint success 0.91–0.99 vs 0.20–0.27 unconstrained, 0.53–0.63 soft prompts — arxiv 2512.07627 — high — performance
6. AIMC 2025 venue for B* unconfirmed — same — medium — landscape
7. EMO_Harmonizer: no licence, Drive checkpoints, CUDA 10.2 + fast-transformers — github.com/Yuer867/EMO_Harmonizer (2025-12-15) — high — licence/compat
8. MuPT weights HF, 190M card Apache-2.0, .cuda() prefix continuation — huggingface.co/m-a-p/MuPT-v1-8192-190M — high — licence/compat
9. No evidence MuPT harmonizes a fixed melody — same + arXiv 2404.06393 — medium — version/compat
10. HarmonyRL: MusicXML/MIDI → chords, HookTheory, RL fine-tuned, CPU, 32-bar windows, splits at time-sig changes, selected-bar redraw; code MIT, weights CC BY-NC-SA 3.0; created 2026-11-16 — github.com/HarmonyRL/HarmonyRL — high (facts), quality unknown — licence/compat
11. NeuraLLMuse hosts SplitEncoder, GridMLMelHarm, LatentTraceGuidance (ISMIR 2026), GraphGuidance, dataset; Apache-2.0 — api.github.com/orgs/NeuraLLMuse/repos — high — landscape
12. ISMIR 2025 Function Alignment: melody→chord + chord recognition, code claimed, no URL — ismir2025program.ismir.net/poster_25.html — medium — landscape
13. RL-Chord (TNNLS 2024) zero-shot Chinese folk harmonization — scholar.xjtu.edu.cn listing (snippet) — medium — landscape
14. CPFG-Net code MIT at huang0251/CPFG_model (2025-11-20) — high — licence
15. asigalov61 HF harmonizers Apache-2.0 card metadata — huggingface.co/asigalov61/Melody-Harmonizer-Transformer — high (licence) — licence

## Leads
HarmonyRL gated cards + 3/4 test; ask NeuraLLMuse for checkpoints; Function Alignment URL; RL-Chord code; Hookpad Aria weights; asigalov61 models.

## Not found
B*/BART weights; AIMC listing; MuPT harmonization eval; EMO metrics; Mac-runnable 2025–26 weights other than HarmonyRL and asigalov61; models evaluated on 3/4, 2/4 or pentatonic melodies (except RL-Chord claim).
