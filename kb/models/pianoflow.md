---
id: pianoflow
type: model
task: '表情演奏：樂譜 MIDI → 演奏 MIDI'
status: '已用於 prototype-01'
updated: '2026-11-21'
---

# SyMuPe / PianoFlow

| 項目 | 內容 |
|---|---|
| 做什麼 | 表情演奏：樂譜 MIDI → 演奏 MIDI |
| 連結 | [GitHub](https://github.com/ilya16/SyMuPe)、[HF PianoFlow-base](https://huggingface.co/SyMuPe/PianoFlow-base) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | CC BY-NC-SA 4.0 |
| 大小 | 約 2,400 萬參數 |
| 輸入 | 量化的單軌樂譜 MIDI |
| 輸出 | 演奏 MIDI（套用延音踏板） |
| Mac（M3 Pro 18GB） | ✅ CPU；MPS 需小修補（float64→float32） |
| 我們的使用狀態 | 已用於 prototype-01 |
| 實測效能 | 一段旋律數秒；記憶體約 0.5–0.6GB |

## 重點與坑

- 開源版沒有論文裡的情緒文字引導。
- 安裝要手動補 `numba`（issue #9）。
- **自己決定速度，不看譜上速度**：快樂頌被彈慢 1.6–3.6 倍。
- 音符全部保留（prototype-01 實測）。
- 使用者評：差強人意，可用。

## 文獻

[arxiv-2511.03425](../literature/arxiv-2511.03425.md)

## 出處

[R1 [8]](../../docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)、[R2 [10]–[13]](../../docs/research-prototype-model-check/research-prototype-model-check.md)、[prototype-01](../experiments/prototype-01-melody-to-performance.md)
