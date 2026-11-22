---
id: compose-embellish
type: model
task: '伴奏（旋律＋和弦 → 鋼琴演奏）'
status: '原型 02 使用中（第三輪加入）'
updated: '2026-11-22'
---

# Compose & Embellish

| 項目 | 內容 |
|---|---|
| 做什麼 | 伴奏（旋律＋和弦 → 鋼琴演奏） |
| 連結 | [GitHub](https://github.com/slSeanWU/Compose_and_Embellish) |
| 程式碼授權 | MIT |
| 權重授權 | MIT（HF） |
| 大小 | GPT-2 規模 |
| 輸入 | 旋律＋和弦 |
| 輸出 | 鋼琴演奏 MIDI |
| Mac（M3 Pro 18GB） | 可以跑：MPS，PyTorch 2.15、transformers 4.49，只用第二階段 GPT-2 版 |
| 我們的使用狀態 | 原型 02 第三輪加入（`steps/accomp_compose_embellish.py`） |
| 實測效能 | 每份 7–29 秒（16–17 小節），載入約 1 秒，常駐記憶體約 0.9GB |

## 重點與坑

- ICASSP 2023。Pop1K7 訓練。調外音 14.8%、和弦正確率 58.1%。

## 文獻

—

## 出處

[R3 [14]](../../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)

## 更新紀錄

- **R4（2026-11-21）：** Embellish 推論只寫了 CUDA；README 說的 `inference_gpt2.py` 不存在（404）；輸入是 REMI 事件文字檔，要自己寫轉換。R4 結論：在 Mac 上要改的地方太多，這輪不加。[R4 [3]]
- **原型 02 第三輪（2026-11-22）：** 實際裝起來了。
  - 只用第二階段 Embellish（GPT-2 版，權重 379MB）；第一階段「自己寫旋律＋和弦」換成我們的旋律與和弦表。
  - 自己寫了 lead sheet 轉換（Bar／Beat／Chord／Note 事件，每小節 16 格，照訓練資料的順序）和取樣迴圈（上游 `inference.py` 一載入就呼叫 CUDA，不能直接用）。
  - 載入權重要：詞彙表多算一個 PAD（367），並丟掉舊版 transformers 的注意力遮罩 buffer。
  - 模型會把旋律一起彈出來，而且幾乎一音不差（快樂頌 62/62、綠袖子 38/38）；轉換時把旋律音拿掉，只留伴奏。
  - 和弦只有 11 種性質，其他和弦就近對應，轉位的低音被丟掉。只吃 4/4，綠袖子（3/4）重新併成 4 拍一小節。
  - 第三輪 4 格共 32 份，全部通過新指標的五道門檻；伴奏偏稀疏（中位數約 72 個音），還沒聽過。
- **論文精讀（2026-11-22）：** Pop1K7 約 1,700 首西方、日、韓流行鋼琴翻奏，由音檔自動採譜（Kong 等人的模型）；清理後 1,591 首。樂譜由 skyline 抽旋律（約八成準確）加上自動分析的和弦與樂句。第一階段另用 Lakh MIDI 14,934 首預訓練（我們沒用）。第二階段一小節樂譜、一小節演奏交錯，12 層、38M 參數，截 3,072 符號訓練，約 3 天。論文版是 Performer；GPT-2 版同資料、同大小。**作者給第二階段的取樣值是溫度 1.1、top_p 0.99**（1.2／0.97 是第一階段的值）。旋律符合率超過 98%。評估：15 人、整首從零寫，整體 3.18 分，真人 4.40 分。[模型來歷報告](../../docs/prototype-plan-harmony-first/model-background.html)
