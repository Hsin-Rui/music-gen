# Digest: SyMuPe/PianoFlow + Anticipatory Music Transformer on Mac M3 Pro (18GB). Round 1, researcher 1

Accessed: 2026-11-21 for every source. Code evidence comes from shallow clones of the default branches, grepped without running anything:
SyMuPe HEAD 13cc57d (2026-04-30, v1.1.0); anticipation HEAD af37397 (2024-03-18).

## Findings

### SyMuPe / PianoFlow

1. **Claim:** The released inference API takes a quantized score MIDI file (`generator.perform_score("score.mid", ...)`), a `symusic.Score` or a TokSequence. MusicXML is converted to MIDI first with `partitura_score_to_midi`. It needs no aligned performance; alignment (RAScoP/Parangonar) is only for building datasets. A plain melody+accompaniment MIDI is a valid input type. Single-track is assumed (the alignment tools merge tracks by default).
   - Source: https://github.com/ilya16/SyMuPe (README); https://github.com/ilya16/SyMuPe/blob/main/symupe/inference/performance.py (perform_score docstring, L124-160)
   - Publisher: Ilya Borovik (GitHub) · pub_date: 2026-04-30 (v1.1.0 commit) · confidence: high · class: capability

2. **Claim:** Inference has no CUDA-only dependency. pyproject has no flash-attn, triton, xformers or custom kernels; it needs torch>=2.4.1, accelerate, transformers, miditok, symusic, partitura, parangonar; Python >=3.10. Grepping the source for `.cuda(` finds nothing. The device is a parameter (`AutoGenerator.from_pretrained(..., device=device)`). The examples default to `"cuda" if available else "cpu"`. The only other CUDA references are `torch.autocast("cuda", enabled=False)` in embeddings.py (L668, L732), which only disables autocast, and a guard in trainer.py.
   - Source: https://github.com/ilya16/SyMuPe/blob/main/pyproject.toml; grep of repo source
   - Publisher: Ilya Borovik · pub_date: 2026-04-30 · confidence: high (CPU), med (MPS: plausible, but nothing in the docs, tests or issues mentions MPS) · class: compat

3. **Claim:** PianoFlow is small, about 24M parameters (8 layers, dim 512). Default sampling is 10 CFM ODE steps (step factor 0.75), in windows (`max_seq_len=256`, `max_new_notes=64`, `num_samples=8` by default). The paper reports "up to 355 notes per second on a V100 GPU", faster than real time on GPU and "near real time on CPU" (CPU not named). Memory is not reported, but 24M parameters is trivial for 18GB.
   - Source: https://arxiv.org/html/2511.03425v1 ; performance.py signature
   - Publisher: Borovik et al., arXiv / ACM MM'25 · pub_date: 2025-11 · confidence: med (CPU speed is the authors' qualitative claim) · class: performance

4. **Claim:** In the paper, emotion guidance works like this. An MLM-pretrained emotion classifier soft-labels each bar over 33 emotions. A bar's text embedding is a probability-weighted mix of Flan-T5-base embeddings of 16 emotion templates. That embedding, plus tempo and velocity controls, is added before the middle transformer layer, and training uses classifier-free guidance (20% dropout). Only a fine-tuned "control" PianoFlow variant has this.
   - Source: https://arxiv.org/html/2511.03425v1
   - Publisher: Borovik et al. · pub_date: 2025-11 · confidence: high (that this is what the paper describes) · class: capability

5. **Claim:** The released v1.1.0 inference code and the PianoFlow-base model card expose no emotion or text interface. Grepping inference/ and the models for T5/Flan/text_embed/guidance finds nothing. The only controls are `cond_seq_control` (score-token values such as Tempo/Velocity) and `emotion_embeddings` hooks inside the model code (no released emotion encoder found). Emotion-text guidance therefore looks unreleased or not usable out of the box.
   - Source: https://huggingface.co/SyMuPe/PianoFlow-base/blob/main/README.md ; repo grep (performance.py L240-253, music_transformer/inference.py L355, L515)
   - Publisher: SyMuPe (HF) / Ilya Borovik · pub_date: 2026-04 · confidence: med · class: capability

6. **Claim:** Pretrained weights can be downloaded from Hugging Face (safetensors): SyMuPe/PianoFlow-base, EncDec-base, MLM-base and MIDI-Quality-Classifier, all in the "SyMuPe (ACM MM'25)" collection. Install with `pip install -U symupe`. Weights and data are CC BY-NC-SA 4.0; code is Apache-2.0.
   - Source: https://github.com/ilya16/SyMuPe ; https://huggingface.co/SyMuPe/PianoFlow-base
   - Publisher: Ilya Borovik / SyMuPe · pub_date: 2026-04 · confidence: high · class: licence

7. **Claim:** Known install snags, open since 2026-07-20 (issue #9, still open). `import symupe` fails because `numba` is not declared as a dependency. scipy needs upgrading. parangonar's DTW modules raise typing errors. These are workable with a manual `pip install numba scipy -U`.
   - Source: https://github.com/ilya16/SyMuPe/issues/9
   - Publisher: GitHub user report · pub_date: 2026-07-20 · confidence: high · class: compat

8. **Claim:** The project is young and thinly maintained: 31 stars, 1 fork, no GitHub Releases. The last commit was 2026-04-30, nearly 7 months before access.
   - Source: https://github.com/ilya16/SyMuPe
   - Publisher: GitHub · pub_date: 2026-04-30 · confidence: high · class: compat

### Anticipatory Music Transformer (AMT)

9. **Claim:** Core sampling is device-agnostic: `anticipation/sample.py` moves tensors with `.to(model.device)`, and the `anticipation/` package has no `.cuda()`. Hard-coded `.cuda()` appears only in the auxiliary scripts `humaneval/accompany.py`, `humaneval/prompt*.py` and `scripts/eval-loss.py`. Those need editing (or just call `generate()` directly) to run on CPU or MPS.
   - Source: https://github.com/jthickstun/anticipation/blob/main/anticipation/sample.py (L88); grep of repo
   - Publisher: John Thickstun (GitHub) · pub_date: 2024-03-18 · confidence: high (CPU), med (MPS: no MPS-specific evidence found either way) · class: compat

10. **Claim:** requirements.txt pins `transformers==4.29.2` (and torch>=2.0.1, mido==1.2.10). Users report that installing transformers 4.29.2 gets stuck on tokenizers 0.13.1 under Python 3.12, and that Python 3.9 fixes it. On Apple Silicon, an old Python or a looser transformers pin is likely needed (the newer pin is untested).
    - Source: https://github.com/jthickstun/anticipation/blob/main/requirements.txt ; https://github.com/jthickstun/anticipation/issues/19
    - Publisher: J. Thickstun; GitHub user · pub_date: 2025-09-12 (issue) · confidence: high · class: compat

11. **Claim:** music-medium-800k has about 360M parameters, a GPT-2 architecture and an Apache-2.0 licence. In fp32 that is about 1.4GB of weights (computed from the parameter count, not measured), which fits easily in 18GB.
    - Source: https://huggingface.co/stanford-crfm/music-medium-800k
    - Publisher: Stanford CRFM (HF) · pub_date: 2023 · confidence: high (params, licence), med (memory estimate) · class: licence / performance

12. **Claim:** Generation is slow by design in main. `add_token` re-runs the full context (up to 1024 tokens) with no KV cache, for each of the 3 tokens per note event. The author has a KV-caching branch (`caching`) that is not merged ("there could be bugs"). Main is still unmerged as of the 2024-03-18 HEAD. No CPU or MPS speed numbers were found.
    - Source: sample.py L76-108; https://github.com/jthickstun/anticipation/issues/15
    - Publisher: J. Thickstun · pub_date: 2024-03-22 · confidence: high (mechanism), low (actual speed on M3) · class: performance

13. **Claim:** Melody-conditioned accompaniment is a documented, first-class use. The steps: `events, melody = extract_instruments(events, [instr])`, then `generate(model, start, end, inputs=history, controls=melody, top_p=.98)`, then `ops.combine(accompaniment, melody)`. The melody must be on its own MIDI program (instrument) so it can be extracted as controls. The README example and humaneval/accompany.py both use a prompt (history), i.e. the first 5 s of real accompaniment.
    - Source: https://github.com/jthickstun/anticipation (README L63-83); humaneval/accompany.py
    - Publisher: J. Thickstun · pub_date: 2024-03 · confidence: high · class: capability

14. **Claim:** Quality drops without that prompt. A user reports that without a 5-second reference accompaniment "it could barely generate good accompaniment" (issue #18, open, no reply). For a melody-only input, this is a real risk to the pipeline.
    - Source: https://github.com/jthickstun/anticipation/issues/18
    - Publisher: GitHub user · pub_date: 2025-04-16 · confidence: med (single report) · class: capability

15. **Claim:** You cannot choose the accompaniment's instrument (e.g. force piano). The model picks instruments freely (capped at 16). The author calls instrument conditioning "the most requested feature" and offered a logit-masking hack on an experimental branch. A user reports that the hack gets stuck in repeated notes and zero-duration notes, and the author agreed it is "a bit out of scope for the current models". The issue is still open. For a piano-only accompaniment feeding PianoFlow, expect to post-filter or remap to piano.
    - Source: https://github.com/jthickstun/anticipation/issues/9 ; sample.py `instr_logits` L63-71
    - Publisher: J. Thickstun / GitHub users · pub_date: 2023-12-14 (last comment) · confidence: med · class: capability

16. **Claim:** Context and length limits: a 1024-token context (341 events, 3 tokens each) with a sliding "Markov window" (lookback 1017). Training excluded sequences over 100 s, and maximum note duration is 10 s. Long pieces are generated with a sliding window, which limits long-range coherence.
    - Source: https://github.com/jthickstun/anticipation/blob/main/anticipation/config.py ; sample.py L80
    - Publisher: J. Thickstun · pub_date: 2024-03 · confidence: high · class: capability

17. **Claim:** The repo has been dormant on main since 2024-03-18. Activity in 2026 (PRs #20-#26: "Nanochat Changes", "Span Anticipation", "Symusic Conversion", "Vocab adjustment") suggests next-generation work, but none of it is on main.
    - Source: https://api.github.com/repos/jthickstun/anticipation/issues?state=all
    - Publisher: GitHub · pub_date: 2026-03-16 · confidence: med · class: compat

## Leads worth chasing
- AMT `caching` branch (KV cache) for a practical speed-up on CPU/MPS; check whether it is stable.
- AMT 2026 PRs #24/#25 "Span Anticipation" and #21 "Symusic Conversion": possibly a newer model or vocabulary with instrument conditioning.
- AMT experimental branch commit 84c4374 (`masked_instrs`) to force piano-only accompaniment; test whether degeneration still happens.
- SyMuPe: inspect `music_transformer/inference.py` `emotion_embeddings` and check whether any HF repo (beyond -base) ships a control/emotion PianoFlow variant.
- Hands-on smoke test on the M3 is the only way to confirm MPS: `device=torch.device("mps")` for both, with `PYTORCH_ENABLE_MPS_FALLBACK=1`.
- The AMT Colab notebook (linked in the README) for the full accompaniment recipe and the instrument codes it uses.

## Looked for, could not find
- Any MPS / Apple Silicon report (success or failure) for either SyMuPe or AMT.
- Measured AMT generation speed on CPU or MPS; measured PianoFlow CPU throughput or memory use.
- A released emotion-text-guided PianoFlow checkpoint or a text-prompt API in symupe v1.1.0.
- Explicit documentation that PianoFlow input must be single-track piano; only implied by the piano pitch range 21-108 and the merge-tracks default.
- Systematic quality evaluation of AMT accompaniment for melody-only input with no accompaniment prompt (the paper's human eval used prompts; this was not checked in the paper this run).
