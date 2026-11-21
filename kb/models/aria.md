---
id: aria
type: model
task: '鋼琴續寫、MIDI 嵌入'
status: '已排除'
updated: '2026-11-21'
---

# Aria (EleutherAI)

| 項目 | 內容 |
|---|---|
| 做什麼 | 鋼琴續寫、MIDI 嵌入 |
| 連結 | [GitHub](https://github.com/EleutherAI/aria)、[HF](https://huggingface.co/loubb/aria-medium) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | Apache-2.0 |
| 大小 | medium |
| 輸入 | MIDI 提示 |
| 輸出 | 續寫的鋼琴 MIDI |
| Mac（M3 Pro 18GB） | ✅ 有 MLX 推論 |
| 我們的使用狀態 | 已排除 |
| 實測效能 | — |

## 重點與坑

- **不能照譜演奏，只會續寫**，所以從 prototype-01 排除。
- 訓練資料 Aria-MIDI（約 6 萬小時轉譜鋼琴）。

## 文獻

[arxiv-2506.23869](../literature/arxiv-2506.23869.md)

## 出處

[R1 [18]](../../docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)、[R2 [1]–[3]](../../docs/research-prototype-model-check/research-prototype-model-check.md)
