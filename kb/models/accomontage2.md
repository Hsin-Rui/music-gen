---
id: accomontage2
type: model
task: '配和聲＋伴奏（只給旋律）'
status: '原型 02 候選'
updated: '2026-11-21'
---

# AccoMontage2

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲＋伴奏（只給旋律） |
| 連結 | [GitHub](https://github.com/billyblu2000/AccoMontage2) |
| 程式碼授權 | MIT |
| 權重授權 | 資料檔在 Google Drive |
| 大小 | 檢索＋動態規劃 |
| 輸入 | MIDI 旋律＋主音＋樂句切分 |
| 輸出 | 和弦 MIDI＋伴奏 MIDI |
| Mac（M3 Pro 18GB） | README 沒提 GPU；有網頁介面 |
| 我們的使用狀態 | 原型 02 候選 |
| 實測效能 | — |

## 重點與坑

- ISMIR 2022。**只支援 4/4**，樂句 4 或 8 小節。
- 和弦風格：pop_standard、pop_complex、dark、r&b。

## 文獻

[arxiv-2209.00353](../literature/arxiv-2209.00353.md)

## 出處

[R3 [3][4]](../../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)

## 更新紀錄

- **原型 02（2026-11-21）：** 在 Mac CPU 上跑成功；只配和聲的路徑上游會當掉（`__add_textures()` 缺 `log`），加了小補丁。綠袖子（3/4）不支援。
