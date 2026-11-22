---
id: accomontage
type: model
task: '伴奏（旋律＋和弦 → 鋼琴）'
status: '原型 02 候選'
updated: '2026-11-22'
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
- **論文精讀（2026-11-22）：** POP909 只留 2/4、4/4 → 857 首、11,032 樂句，並移到 12 個調。挑樂句：每句合不合（節奏 0.5 ＋ 調性區間向量 0.5，規則式）× 0.3 ＋ 上下句接得順不順（對比學習）× 0.7，再用 Viterbi 解；和弦是刻意的弱條件，事後由「和弦與織體拆開」的 VAE（Wang 2020，POP909）改和弦。密度與發聲數只篩第一句（論文分三級）。評估：72 人、14 首 Nottingham 民謠、5 分量表，連貫與結構顯著較好；沒有測可彈性。[模型來歷報告](../../docs/prototype-plan-harmony-first/model-background.html)
