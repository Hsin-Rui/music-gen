# Digest: Aria for expressive rendering, and alternatives (r1-1)

Decision served: can the prototype (melody MIDI -> accompaniment -> expressive piano rendering, local on M3 Pro 18GB) use Aria to render expressively, or does it need an alternative?
Accessed: 2026-11-21. Sources were fetched with a summarising web fetcher, so "not stated" means the fetched page did not say it, not that it was proven absent.

## Findings

1. **Claim:** Aria (base / gen / embedding checkpoints) supports prompt continuation of MIDI, MIDI embeddings and a real-time continuation demo. Its README documents no score-to-performance or "humanize" mode that keeps the given notes.
   - Source: https://github.com/EleutherAI/aria (README) · EleutherAI · undated (132 commits) · accessed 2026-11-21 · confidence: high · class: capability
2. **Claim:** The official checkpoints are `loubb/aria-medium-base`, `loubb/aria-medium-gen` (finetuned for generation) and `loubb/aria-medium-embedding`, plus a demo checkpoint with sustain-pedal control (`model-demo.safetensors`). None is described as a renderer.
   - Sources: https://github.com/EleutherAI/aria ; https://huggingface.co/loubb/aria-medium · EleutherAI / loubb · accessed 2026-11-21 · confidence: high · class: capability
3. **Claim:** Aria ships an MLX implementation for Apple Silicon (demo/demo_mlx.py) alongside PyTorch CUDA. The CLI generate example uses `--backend torch_cuda`.
   - Source: https://github.com/EleutherAI/aria · EleutherAI · accessed 2026-11-21 · confidence: high · class: compat
4. **Claim:** Aria's code and models are Apache-2.0. The HF cards say they were trained on the loubb/aria-midi dataset.
   - Sources: https://github.com/EleutherAI/aria ; https://huggingface.co/loubb/aria-medium · accessed 2026-11-21 · confidence: high · class: licence
5. **Claim:** The Aria paper ("Scaling Self-Supervised Representation Learning for Symbolic Piano Performance", arXiv 2506.23869, ISMIR 2025) evaluates continuations and linear-probe classification, not score rendering. This comes from search snippets only; the full paper was not read.
   - Source: https://arxiv.org/abs/2506.23869 · Bradshaw et al. · 2025-06 · accessed 2026-11-21 · confidence: med · class: capability
6. **Claim:** A GitHub issue search on EleutherAI/aria for "performance OR humanize OR render" returned 0 results. There is no visible community request or fork for rendering in the tracker.
   - Source: https://github.com/EleutherAI/aria/issues · accessed 2026-11-21 · confidence: med · class: ecosystem
7. **Claim:** MAJEPPA (`anusfoil/majeppa`) is a LoRA fine-tune of `loubb/aria-medium`. Its generation mode takes a score MIDI and produces a performance MIDI, conditioned on performer type and recording context. The HF card says Apache-2.0, intended for non-commercial research. The code repo is MIT. Examples use `device="cuda"`, the README says "training code assumes a CUDA GPU", and the repo has 8 commits. The card, README and abstract do not say whether the score notes stay fixed, or whether pedal is output.
   - Sources: https://huggingface.co/anusfoil/majeppa ; https://github.com/anusfoil/majeppa ; https://arxiv.org/abs/2608.11026 (Zhou, Zhang, ..., Dixon; submitted 2026-08-11; ISMIR 2026) · accessed 2026-11-21 · confidence: med (the capability is claimed, but note fidelity and Mac support are unverified) · class: capability / compat / licence
8. **Claim:** Pianist Transformer (yhj137/PianistTransformer, ICML 2026) renders expressive performances from score **MIDI**, with no MusicXML. It is 135M parameters (about 270 MB) and its weights are on HF as `yhj137/pianist-transformer-base` and `yhj137/pianist-transformer-rendering` (also on ModelScope). It outputs pedal (4 pedal points per note) and has a PyQt GUI. The README says a standard CPU is enough for inference and gives a "macOS or CPU-only" install path; MPS is not mentioned. It uses Python 3.11, PyTorch 2.7.1 and Transformers 4.54.0. The code is Apache-2.0; the weights licence is not stated. The repo has 12 commits.
   - Sources: https://github.com/yhj137/PianistTransformer ; https://arxiv.org/abs/2512.02652 (You et al.; v1 2025-12-02, v2 2026-06-25) · accessed 2026-11-21 · confidence: high for format, weights and CPU; low for strict note preservation (the per-note pedal points suggest note-level output, but this is unconfirmed) · class: capability / compat / licence
9. **Claim:** VirtuosoNet (jdasam) reads a **MusicXML** score and outputs a performance MIDI. The HAN+GRU checkpoint is on HF at `dasaem/virtuosonet`. Install is via uv / pip with Python 3.10, plus a `download_and_test.py` quick test. CUDA 11.8 is named only for GPU use. The repo About section shows no licence.
   - Source: https://github.com/jdasam/virtuosoNet · Dasaem Jeong · undated (702 commits) · accessed 2026-11-21 · confidence: high (format, weights); med (CPU viability inferred) · class: capability / compat / licence
10. **Claim:** ScorePerformer (ilya16) is CC BY-NC-SA 4.0. The README offers a Colab demo but no clear downloadable weights. Score/performance alignment and preprocessing code is "deliberately not made available". The input format is not stated. The repo has 4 commits.
    - Source: https://github.com/ilya16/ScorePerformer · accessed 2026-11-21 · confidence: med · class: licence / capability
11. **Claim:** DExter (anusfoil) is a diffusion renderer that takes MusicXML input and is MIT licensed. No pretrained weights are linked (the checkpoint comes from your own training), and the old codec data link is dead. A Colab is offered.
    - Source: https://github.com/anusfoil/DExter · accessed 2026-11-21 · confidence: med · class: capability / licence
12. **Claim:** Newer 2025-2026 rendering works exist without code verified this run: PianoKontext (arXiv 2606.12282, ICML 2026, flow matching in Music2Latent space), "Disentangling Score Content and Performance Style" (arXiv 2509.23878, ICLR 2026), RenderBox (arXiv 2502.07711, text control) and the PianoCoRe dataset (arXiv 2605.06627, github.com/ilya16/PianoCoRe).
    - Source: WebSearch results listing for "expressive performance rendering piano 2026 github" · accessed 2026-11-21 · confidence: low (search snippets only) · class: ecosystem

## Verdict (for the decision)
- **Aria itself:** not usable as a note-preserving renderer. Officially it only continues or generates. Feeding a score as a prompt would continue it, not render it.
- **Aria-derived route:** MAJEPPA adds score-to-performance on an Aria backbone. It is research-only, CUDA-oriented, and unverified for note fidelity or Mac use.
- **Best-evidenced Mac-local alternative:** Pianist Transformer. It takes MIDI in, has downloadable weights, runs inference on CPU (with an explicit macOS install), outputs pedal and is small (135M). Next is VirtuosoNet, which needs MusicXML, so MIDI would have to be converted to MusicXML first.

## Leads worth chasing
- Pianist Transformer: read the paper (method section) and code to confirm that output notes map 1:1 to score notes and pitches are unchanged. Check the HF card licence for the weights. Test whether MPS works by setting the device.
- MAJEPPA: read the `generate()` code or paper for note alignment and pedal tokens. Check whether loading with `device="mps"`/cpu works, and whether an MLX port via Aria's MLX code is feasible.
- VirtuosoNet: check the LICENSE file directly (the About section shows none) and the HF card `dasaem/virtuosonet`. Test CPU inference.
- PianoKontext and the Disentangling (ICLR 2026) paper: find out whether code or weights are released.
- ScorePerformer: check whether the Colab pulls downloadable weights.

## Looked for, could not find
- Any official Aria "humanize" or score-to-performance mode, checkpoint or CLI flag (none in the README or HF listings).
- Aria GitHub issues about rendering, humanizing or performance (0 results).
- Last-commit dates for any repo (the fetched pages showed commit counts only).
- Explicit MPS or MLX support in any renderer other than Aria's continuation demo.
- Weights licence for Pianist Transformer, and code licence for VirtuosoNet.
- Magenta or other maintained "humanize MIDI" tools (not searched, because the tool-call budget ran out).
