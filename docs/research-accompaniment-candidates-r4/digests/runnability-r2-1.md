# Round 2: can we feed our own melody + chords? (accessed 2026-11-21)

Researcher assistant; 20 tool calls; read repo code, READMEs, model cards; ran nothing.

## Verdicts
| Candidate | Our melody + chords in? | Mac / CPU |
|---|---|---|
| HarmonyRL | easy (melody in, chords out; MusicXML chords can be kept, selected bars redrawn) | README: CPU supported |
| AccoMontage-3 (repo renamed zhaojw1998/Structured-Arrangement-Code) | easy-ish: "lead sheet.mid" = melody track + chord track as notes; chords re-detected by rule-based recognizer; hand-written segmentation string + pickup count; 4/4 only | small patch: hard .cuda() in stage 1 |
| Compose & Embellish (Embellish) | needs a converter: REMI-style .txt events; vocabulary in pickled vocab file | hard: CUDA-only inference; README's GPT-2 inference file missing (404) |
| asigalov61 Melody-Harmonizer / Seq2Seq | melody only, lossy: pitch classes of first 64 notes, no rhythm/meter; one chord per note | yes (CPU Space) |
| Florence Price generator | unknown; melody → accompaniment, chord input not evidenced | unknown |
| Function Alignment (music-x-lab) | unknown: has mel_to_chord and chord_to_mel adapters; no melody+chords → accompaniment | unknown; install uses torch cu126 |

## Claims
1. AccoMontage-3 repo renamed Structured-Arrangement-Code (MIT); two stages; Drive checkpoints; torch 1.10.1+cu111, Py ≤3.9 — github.com/zhaojw1998/Structured-Arrangement-Code (README Oct 2024; push 2026-01-17) — high
2. User lead sheet: "lead sheet.mid" in ./demo/<SONG>/, set SEGMENTATION ('A8A8B8B8'), NOTE_SHIFT, TEMPO; DEVICE='cuda:0' — inference_arrangement.ipynb — high
3. Stage 1 `piano_arrangement(...)` is called separately before `orchestration(...)`; whether orchestrator load can be skipped unverified — arrangement_utils.py — medium
4. `leadsheet2matrix`: melody track 0; chords via `transcribe_cb1000_midi` recognizer (mir_eval encoding); 4 steps/beat, 16 steps/bar → 4/4 — piano_arranger/format_converter.py — high
5. Hard CUDA: AccoMontage.py lines 291/293 `.cuda()`; line 32 `DisentangleVAE.init_model(torch.device('cuda')).cuda()`; torch.load without map_location — piano_arranger/AccoMontage.py; arrangement_utils.py — high
6. C&E README names stage02_embellish/inference_gpt2.py, which 404s; only Performer inference.py (needs fast-transformers) — github.com/slSeanWU/Compose_and_Embellish (push 2024-09-16) — high
7. Embellish inference.py: torch.cuda.set_device, .cuda(); map_location='cpu' commented out — stage02_embellish/inference.py — high
8. Embellish input: folder of .txt, one event per line: Tempo_n, Bar_None, Beat_pos, Chord_<root>_<quality>, Note_Pitch_n, Note_Duration_n; BAR_RESOL 480*4, 16 positions/bar (4/4 implied); vocab in skyline2midi_vocab.pkl (not opened) — inference.py, convert2midi.py — medium-high
9. HarmonyRL: pip harmonyrl v1.0.0, Py ≥3.12, torch, music21, pretty-midi; API from_pretrained / read_lead_sheet / harmonize_sheet(candidates, bars, seed, temperature) / write_lead_sheet; "models also run on the CPU" — github.com/HarmonyRL/HarmonyRL; pypi.org/project/harmonyrl (2026-11-17) — high
10. HarmonyRL I/O: MusicXML melody+chords in/out; MIDI melody in, melody+chord notes out; ≤32 bars per call with overlapping windows; one key per piece; splits at time-signature changes — README — high
11. HarmonyRL meters: denominator 4 or 8; strong beats tabulated for 2/4, 3/4, 3/8, 4/4, 5/4, 6/4, 6/8, 8/4, 9/4, 9/8, 12/4, 12/8 — src/harmonyrl/schema/meter.py — high
12. HarmonyRL eval on Hooktheory/Sheet Sage test (2,473 segments × 8): out-of-key chord time Human 9.6%, Base 6.9%, Smooth 5.5%, Chromatic 12.9%; chord held >2 bars 3.2/4.1/5.3/1.4%; listening = blind rankings by 1 listener; 18.4M params; weights CC BY-NC-SA 3.0, gated click-through — huggingface.co/CloudHolic/harmonyrl-chromatic (2026-11-16) — high as reported, weak evaluation
13. asigalov61 Space loads Seq2Seq checkpoint (x-transformers, dim 1024, depth 8), map_location cpu; prompt = pitch classes of first 64 melody notes; one chord per note; MIDI output with chords + bass; cards empty; Monster MIDI Dataset link — huggingface.co/spaces/asigalov61/Melody-Harmonizer-Transformer (2025-03-31) — high
14. asigalov61 Monophonic-MIDI-Melody-Harmonizer is retrieval-based — huggingface.co/spaces/asigalov61/Monophonic-MIDI-Melody-Harmonizer — medium
15. Florence Price: 112-work dataset; generator released; links github.com/TT515/Florence_Price_Art_Song_Dataset, github.com/m-malandro/Florence-Price-listening-examples; base model unconfirmed — arxiv.org/abs/2506.23130 (2025-06-29) — high (links)
16. Function Alignment code github.com/music-x-lab/midi-function-alignment (no licence field); Drive weights; Roformer + adapters mel_to_chord, chord_to_mel, drum, analysis; Py 3.13, torch 2.7.1 cu126 — repo + arxiv.org/abs/2506.15548 (2025-06-18) — high

## Leads
AccoMontage-3 Mac patch (.to(DEVICE), map_location; torch 1.10 / Py ≤3.9 vs Apple Silicon wheels unverified); C&E vocab; HarmonyRL fits melody→chords best; Florence Price TT515 README; Function Alignment inference script.

## Not found
Embellish exact vocabulary; hidden .cuda() elsewhere in AccoMontage-3; fast-transformers without CUDA; asigalov61 training/eval; Florence Price base model and chord input; Function Alignment licence/CPU.
