---
id: accomontage
type: model
task: '伴奏（旋律＋和弦 → 鋼琴）'
status: '原型 02 候選'
updated: '2026-11-21'
---

# AccoMontage

| 項目 | 內容 |
|---|---|
| 做什麼 | 伴奏（旋律＋和弦 → 鋼琴） |
| 連結 | [GitHub](https://github.com/zhaojw1998/AccoMontage) |
| 程式碼授權 | MIT |
| 權重授權 | 資料與權重在 Google Drive（授權未標） |
| 大小 | 檢索＋小型 VAE |
| 輸入 | MIDI 旋律＋和弦（拍為單位，可到九和弦） |
| 輸出 | 鋼琴 MIDI（含力度、踏板） |
| Mac（M3 Pro 18GB） | README 沒提 CUDA（未驗證） |
| 我們的使用狀態 | 原型 02 候選 |
| 實測效能 | — |

## 重點與坑

- ISMIR 2021。從 POP909 樂句庫檢索再做風格轉換。

## 文獻

—

## 出處

[R3 [11]](../../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)

## 更新紀錄

- **原型 02（2026-11-21）：** 在 Mac CPU 上跑成功（加了 map_location、Tensor.cuda 空操作兩個小補丁）。**只支援 4/4**：綠袖子（3/4）、茉莉花（2/4）要重新分成 4 拍一小節。8 份要不同，需要把樂句選擇隨機度設為 0.1。伴奏密度高（每段 100–350 個音），和弦音比例 0.91–0.99。
