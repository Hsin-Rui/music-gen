---
id: function-alignment
type: model
task: '旋律→和弦、和弦→旋律等多任務'
status: '觀察中'
updated: '2026-11-21'
---

# Function Alignment（music-x-lab）

| 項目 | 內容 |
|---|---|
| 做什麼 | 旋律→和弦、和弦→旋律等多任務 |
| 連結 | [GitHub midi-function-alignment](https://github.com/music-x-lab/midi-function-alignment) |
| 程式碼授權 | 沒有授權欄位 |
| 權重授權 | Google Drive |
| 大小 | Roformer 基礎模型＋轉接器 |
| 輸入 | 16 分音符量化 MIDI |
| 輸出 | 和弦／旋律／分析 |
| Mac（M3 Pro 18GB） | 安裝用 CUDA 版 torch 2.7.1（未驗證 CPU） |
| 我們的使用狀態 | 觀察中 |
| 實測效能 | — |

## 重點與坑

- ISMIR 2025（Jiang、Chin、Lin、Liu、Xia）。
- 轉接器：mel_to_chord、chord_to_mel、drum、midi_analysis。可當配和聲候選，但授權不明。

## 文獻

[arXiv 2506.15548](../literature/arxiv-2506.15548.md)

## 出處

[R4 [19]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
