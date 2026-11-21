---
id: amt
type: model
task: '符號生成：補寫、給旋律生伴奏'
status: '已用於 prototype-01'
updated: '2026-11-21'
---

# Anticipatory Music Transformer (AMT)

| 項目 | 內容 |
|---|---|
| 做什麼 | 符號生成：補寫、給旋律生伴奏 |
| 連結 | [GitHub](https://github.com/jthickstun/anticipation)、[HF music-medium-800k](https://huggingface.co/stanford-crfm/music-medium-800k) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | Apache-2.0（訓練資料含約 45 萬張商業唱片轉譜，作者提醒輸出推定有侵權風險） |
| 大小 | small／medium 約 3.6 億參數／large |
| 輸入 | MIDI 事件（time, dur, note）；`controls=` 當條件 |
| 輸出 | 多樂器 MIDI |
| Mac（M3 Pro 18GB） | ✅ CPU、MPS 都能跑（prototype-01 實測） |
| 我們的使用狀態 | 已用於 prototype-01 |
| 實測效能 | medium 在 M3 Pro CPU：一段 25–30 秒旋律 30–250 秒，記憶體約 3.4GB；MPS 每音較快 |

## 重點與坑

- 主分支沒有 KV 快取，很慢；`transformers==4.29.2` 在 Python 3.12 裝不起來，用 3.10。
- 輔助腳本寫死 `.cuda()`，直接呼叫 `generate()`。
- 沒有伴奏開頭時品質會掉（issue #18）；控制音在前 50 毫秒會被丟掉。
- 不能指定樂器；prototype-01 用 logit 遮罩限定只寫鋼琴，可行但「不給開頭」時易重複單音。
- **沒有和聲概念**，使用者評：和弦怪、對不上、進行難聽。

## 文獻

[arxiv-2306.08620](../literature/arxiv-2306.08620.md)

## 出處

[R1 [10][11][12]](../../docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)、[R2 [14]–[20]](../../docs/research-prototype-model-check/research-prototype-model-check.md)、[prototype-01](../experiments/prototype-01-melody-to-performance.md)
