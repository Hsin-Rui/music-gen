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
