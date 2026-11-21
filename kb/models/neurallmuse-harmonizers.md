---
id: neurallmuse-harmonizers
type: model
task: '配和聲（旋律 → 和弦）'
status: '觀察中（沒有權重）'
updated: '2026-11-21'
---

# NeuraLLMuse 配和聲系列（SplitEncoder、GridMLMelHarm 等）

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲（旋律 → 和弦） |
| 連結 | [GitHub NeuraLLMuse](https://github.com/NeuraLLMuse) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | 沒有公開（SplitEncoder README 說會釋出） |
| 大小 | — |
| 輸入 | 旋律＋遮罩的和聲格 |
| 輸出 | 和聲 |
| Mac（M3 Pro 18GB） | — |
| 我們的使用狀態 | 觀察中（沒有權重） |
| 實測效能 | — |

## 重點與坑

- SplitEncoder（2026-11，R3「單編碼器遮罩式配和聲」的後繼）、GridMLMelHarm（Applied Sciences 2025，16 分音符格、遮罩式）、LatentTraceGuidance（ISMIR 2026）、GraphGuidanceMelodicHarmonization（2026）、MelodicHarmonizationDataset（2026-10）。
- 是目前最活躍的開源配和聲團隊；權重一釋出就值得試。

## 文獻

—

## 出處

[R4 [13]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
