---
id: openscore-lieder
type: dataset
updated: '2026-11-22'
---

# OpenScore Lieder Corpus

| 項目 | 內容 |
|---|---|
| 類型 | 藝術歌曲樂譜（人聲＋鋼琴，MusicXML／MuseScore） |
| 規模 | 約 1,300 首 |
| 授權 | CC0（專案方說明；HF 衍生版標 CC BY-SA 4.0） |
| 文化／風格 | 19 世紀西方藝術歌曲（Schubert、Schumann、Brahms 等） |
| 取得 | [GitHub](https://github.com/OpenScore/Lieder) |
| 我們的使用狀態 | 未取得；候選的「像真人」參考範圍語料（待試驗） |

## 筆記

- 人聲和鋼琴分在不同譜表，結構和我們的任務相同：給旋律、寫鋼琴伴奏。
- 專案方請使用者註明 OpenScore Lieder 並附連結。少數曲子的公有領域狀態可能有誤。
- 用作參考範圍前要處理三件事：
  - 篩選民謠風的分節歌，因為很多伴奏比我們的目標繁複；
  - 只算人聲在唱的小節，排除前奏和間奏；
  - 驗證照抄柱式和弦的候選會落在範圍外。
- 2026-11-22 決定：原型 02 的下一輪先不用，之後再做小規模試驗。

## 出處

[R5 [29]](../../docs/research-accompaniment-metrics-r5/research-accompaniment-metrics-r5.md)
