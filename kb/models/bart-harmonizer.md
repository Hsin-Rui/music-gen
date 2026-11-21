---
id: bart-harmonizer
type: model
task: '配和聲（旋律 → 和弦）'
status: '觀察中（沒有權重）'
updated: '2026-11-21'
---

# BART 配和聲與 B* 限制解碼（NeuraLLMuse）

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲（旋律 → 和弦） |
| 連結 | [GitHub BStarConstraintHarmonization](https://github.com/NeuraLLMuse/BStarConstraintHarmonization) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | 沒有公開 |
| 大小 | 約 5,000 萬參數（8 層、d=512） |
| 輸入 | MusicXML 旋律 token（可加「某小節必須用某和弦」的限制） |
| 輸出 | 348 種和弦記號（或 12 個音級） |
| Mac（M3 Pro 18GB） | 應可用 CPU（未驗證） |
| 我們的使用狀態 | 觀察中（沒有權重） |
| 實測效能 | — |

## 重點與坑

- 希臘 Kaliakatsos-Papakostas 團隊；HookTheory 17,476 首（轉到 C 大調／A 小調）。
- 拍號 token 分子 1–10、分母 4/8，可表示 2/4、3/4。
- B*：beam search＋A* 回溯，限制達成率 0.91–0.99（不限制 0.20–0.27、軟提示 0.53–0.63）。
- R3 稱「B* 限制解碼（AIMC 2025）」；R4 無法確認會議。

## 文獻

[arXiv 2512.07627](../literature/arxiv-2512.07627.md)

## 出處

[R4 [11][12]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
