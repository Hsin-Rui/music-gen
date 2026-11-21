---
id: asigalov61-harmonizer
type: model
task: '配和聲（每個音配一個和弦）'
status: '不建議'
updated: '2026-11-21'
---

# asigalov61 Melody-Harmonizer-Transformer

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲（每個音配一個和弦） |
| 連結 | [HF Space](https://huggingface.co/spaces/asigalov61/Melody-Harmonizer-Transformer) |
| 程式碼授權 | — |
| 權重授權 | Apache-2.0（卡片欄位） |
| 大小 | dim 1024、8 層 |
| 輸入 | 旋律前 64 個音的音名（不看節奏、拍子） |
| 輸出 | 每個音一個和弦，輸出 MIDI（含低音） |
| Mac（M3 Pro 18GB） | 可用 CPU |
| 我們的使用狀態 | 不建議 |
| 實測效能 | — |

## 重點與坑

- 模型卡沒有內容；訓練資料只連到 Monster MIDI Dataset。
- 不看節奏和拍子，不適合我們的比較。

## 文獻

—

## 出處

[R4 [21]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
