---
id: accomontage3
type: model
task: '伴奏＋多軌編曲'
status: '未試'
updated: '2026-11-21'
---

# AccoMontage-3（Structured Arrangement）

| 項目 | 內容 |
|---|---|
| 做什麼 | 伴奏＋多軌編曲 |
| 連結 | [GitHub](https://github.com/zhaojw1998/AccoMontage-3) |
| 程式碼授權 | MIT |
| 權重授權 | Google Drive |
| 大小 | — |
| 輸入 | 旋律＋和弦 |
| 輸出 | 鋼琴 → 多軌 |
| Mac（M3 Pro 18GB） | 舊版 PyTorch 1.10、Python ≤ 3.9 |
| 我們的使用狀態 | 未試 |
| 實測效能 | — |

## 重點與坑

- NeurIPS 2024。先驗用 LMD、自編碼器用 Slakh2100。

## 文獻

—

## 出處

[R3 [24]](../../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)

## 更新紀錄

- **R4（2026-11-21）：** repo 改名為 [Structured-Arrangement-Code](https://github.com/zhaojw1998/Structured-Arrangement-Code)。第一段（樂譜 → 鋼琴）就是 AccoMontage；和弦要寫成 MIDI 音符、由程式重新辨認；第一段有寫死的 `.cuda()`；只支援 4/4。聽測 23 人勝過 AMT 等對照組。R4 結論：對「只要鋼琴伴奏」的原型 02 幫助不大。[R4 [1][2]]
