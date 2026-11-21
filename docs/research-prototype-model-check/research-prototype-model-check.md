---
title: '技術查證：原型的三個模型能不能用'
type: 'technical'
topic: '原型模型查證：Aria、SyMuPe、AMT 在 Mac 上的可用性'
decision: '原型計畫〈要比較的選項〉與〈平台與技術〉要不要改'
source: 'native run'
status: complete
preset: 'quick'
validation: 'normal'
created: '2026-11-21'
updated: '2026-11-21'
claims_verified: 9
claims_unverified: 2
---

# 技術查證：原型的三個模型能不能用

**這份研究服務的決定：** docs/prototype-plan-melody-to-performance/ 的〈要比較的選項〉與〈平台與技術〉要不要改。

## 執行摘要

**建議：表情演奏的兩個候選換成 SyMuPe/PianoFlow 對 Pianist Transformer，拿掉 Aria。真正的風險不在演奏端，而在 AMT 生伴奏這一段。**

1. **Aria 只能續寫，不能照譜演奏** [1][2][3]。它的 README、模型卡和 issue 都沒有「樂譜→演奏」的模式。有一個用 Aria 微調的研究版 MAJEPPA 能做到 [4][5]，但它以 CUDA 為主，也還不確定會不會改動音符。
2. **兩個演奏模型都能在 Mac 的 CPU 上跑，也都直接吃樂譜 MIDI。**
   - SyMuPe/PianoFlow：約 2,400 萬參數，沒有只能用 CUDA 的套件，裝置可以自己指定 [10][12]。
   - Pianist Transformer（ICML 2026）：1.35 億參數，README 明寫一般 CPU 就夠，附 macOS 安裝步驟，權重是 Apache-2.0 [6][7]。
   - **但 SyMuPe 開源版沒有「情緒文字引導」**，原型計畫列的這個優點要拿掉 [10][11]。
3. **AMT 能跑，但有三個坑：**
   - 沒有前 5 秒的伴奏當開頭，生出來的伴奏品質會掉；這是使用者回報，作者沒有回應 [18]。
   - 不能指定只用鋼琴伴奏 [19]。
   - 舊版相依套件在 Python 3.12 上裝不起來 [16]；生成很慢，主分支沒有 KV 快取 [17]。

**最大的限制：** 沒有人回報過這三個模型在 Apple MPS 上的成敗，只能確定 CPU 可行。速度要實際跑過才知道。

## 一、表情演奏：Aria 與替代方案

**Aria 不合用。** 官方只提供續寫、MIDI 嵌入向量和即時續寫的展示 [1][2]。論文評估的也是續寫和分類，不是演奏渲染（只讀了搜尋摘要，中信心）[3]。在 issue 裡搜尋 render、humanize、performance，都沒有結果 [1]。把樂譜當提示詞丟給 Aria，它只會往下接著寫。

**MAJEPPA** 是 Aria 的 LoRA 微調版（ISMIR 2026），可以輸入樂譜 MIDI、輸出演奏 MIDI [4][5]。不過範例寫死 `device="cuda"`，也沒說會不會保留原本的音符、有沒有輸出踏板（中信心）。

**Pianist Transformer** 最適合在 Mac 上跑 [6][7]：
- 輸入是樂譜 MIDI，不用轉 MusicXML。
- README 寫明「一般 CPU 就夠，有 GPU 會比較快」，附 macOS 安裝步驟（Python 3.11、PyTorch 2.7.1）。
- 輸出可編輯的 MIDI，包含力度、運音和踏板；速度表情用「動態速度曲線」表示。
- 有指令列，也有圖形介面。程式碼和權重都是 Apache-2.0。
- **沒有明講會保留每一個原本的音符**。用速度曲線表示速度表情，暗示音符本身不動，但這是推論（中信心）。

**其他候選比較不適合：**
- VirtuosoNet 一定要 MusicXML，權重在 HF，授權沒標 [8]。
- ScorePerformer 是非商用授權，沒有明確可下載的權重 [9]。
- DExter 沒有預訓練權重 [14]。

## 二、SyMuPe/PianoFlow 在 Mac 上

- **能在 CPU 上跑。** 相依套件裡沒有 flash-attn、triton 這類只能用 CUDA 的東西，原始碼也沒有寫死 `.cuda()`，裝置是傳進去的參數 [10]。MPS 應該也可以，但沒有人回報過（中信心）。
- **輸入是量化過的樂譜 MIDI**（`perform_score("score.mid")`），不需要對齊好的演奏資料。程式預設把多軌合併成一軌 [10]。
- **很小，速度夠用。** 約 2,400 萬參數；作者說在 CPU 上「接近即時」，但沒有說是哪顆 CPU（中信心）[12]。
- **沒有情緒文字引導。** 論文裡有，但開源的 v1.1.0 和 PianoFlow-base 模型卡都沒有提供 [10][11][12]。
- **安裝要手動補 `numba`**（issue #9，仍未修）[13]。權重是 CC BY-NC-SA，研究用沒問題 [11]。專案很新、維護者少，最後一次提交是 2026-04-30 [10]。

## 三、AMT 在 Mac 上生伴奏

- **能在 CPU 上跑。** 核心的取樣程式不綁定裝置，只有幾支評估用的輔助腳本寫死 `.cuda()`，直接呼叫 `generate()` 就能避開 [15]。中型模型約 3.6 億參數，fp32 大約 1.4GB，18GB 記憶體綽綽有餘 [20]。
- **環境要用舊版 Python。** `transformers==4.29.2` 在 Python 3.12 上裝不起來，有人改用 3.9 解決 [16]。
- **很慢。** 主分支沒有 KV 快取，每加一個 token 都要重算整段上下文；作者另一個有快取的分支還沒合併 [17]。查不到 CPU 或 MPS 的速度數字。
- **給旋律生伴奏是官方支援的用法**，但有前提 [14]：
  - 旋律要放在獨立的樂器（MIDI program）上，才能抽出來當條件。
  - 官方範例都附了前 5 秒的真實伴奏當開頭。有使用者回報，沒有這段開頭，「幾乎生不出好的伴奏」[18]（單一回報，已親自核對）。
- **不能指定只用鋼琴伴奏** [19]。模型會自己挑樂器；作者給的遮罩作法會卡在重複音和零長度音符上。要接到鋼琴演奏模型，就得事後把所有伴奏軌改成鋼琴。
- 上下文是 1,024 個 token，長曲子用滑動視窗生成，整首的連貫性有限 [14]。

## 跨面向洞察

- **風險從演奏端移到了伴奏端。** 原本最擔心的是 Aria 和 SyMuPe 跑不跑得動，結果演奏端有兩個能在 CPU 上跑、直接吃 MIDI 的選項。反而是 AMT 有三個問題疊在一起：需要伴奏開頭、不能指定鋼琴、速度慢。原型計畫的放棄條件之一是「沒有一段伴奏和旋律搭得起來」，最可能觸發它的就是這一段。
- **兩端的格式要對上。** AMT 輸出多種樂器，兩個演奏模型都預期單軌鋼琴。中間要有一步把所有軌改成鋼琴、合併成一軌。

## 建議

1. **〈要比較的選項〉改成 SyMuPe/PianoFlow 對 Pianist Transformer，Aria 拿掉。** MAJEPPA 列為備案，只在 Colab 上試。信心：高。CPU 可行和輸入格式都有第一手來源。音符會不會被改動要實測。**對應原型計畫〈要比較的選項〉。**
2. **SyMuPe 的優點拿掉「情緒文字引導」。** 信心：中高（程式碼搜尋加模型卡）。**對應〈平台與技術〉和〈要比較的選項〉。**
3. **AMT 用獨立的 Python 3.10 虛擬環境**，直接呼叫 `generate()`，不用官方的輔助腳本。先跑 CPU，再試 MPS。信心：高。**對應〈平台與技術〉。**
4. **把「沒有伴奏開頭」當成這次要測的事。** 每段旋律試兩種開頭：完全沒有，以及幾小節簡單的柱式和弦。生成後把所有伴奏軌改成鋼琴。信心：中（品質問題只有單一回報）。**對應〈建置〉。**
5. **建置的第一步先做煙霧測試**：三個模型各在 CPU 上跑一小段，記下速度，再試 `device="mps"`。信心：高。**對應〈建置〉。**

## 待解問題

- **三個模型在 MPS 上的表現**：沒有任何回報，要實機測試。
- **Pianist Transformer 和 PianoFlow 會不會改動音符**：要讀原始碼，或比較輸入和輸出的音高序列。
- **AMT 沒有伴奏開頭時的品質**：只有一則使用者回報，要實際聽。
- **AMT 2026 年的新 PR**（Span Anticipation、Symusic Conversion）會不會帶來能指定樂器的新模型：還沒合併到主分支，要繼續觀察 [14]。
- **沒有查的部分**：Magenta 之類的「MIDI 人性化」工具，因為助理的查詢額度用完了。

## 來源附錄

| # | 支撐的說法 | 發布者 | 發布日期 | 查閱日期 | 信心 |
|---|---|---|---|---|---|
| [1] | Aria 只提供續寫、嵌入、MLX 即時展示；issue 無渲染需求 | [EleutherAI/aria (GitHub)](https://github.com/EleutherAI/aria) | 未標 | 2026-11-21 | 高 |
| [2] | Aria 官方檢查點皆非渲染器；Apache-2.0 | [loubb/aria-medium (HF)](https://huggingface.co/loubb/aria-medium) | 未標 | 2026-11-21 | 高 |
| [3] | Aria 論文評估續寫與分類 | [Bradshaw et al., arXiv 2506.23869](https://arxiv.org/abs/2506.23869) | 2025-06 | 2026-11-21 | 中 |
| [4] | MAJEPPA：Aria LoRA，樂譜 MIDI→演奏；範例用 CUDA | [anusfoil/majeppa (GitHub)](https://github.com/anusfoil/majeppa) | 2026 | 2026-11-21 | 中 |
| [5] | MAJEPPA 論文，ISMIR 2026 | [Zhou et al., arXiv 2608.11026](https://arxiv.org/abs/2608.11026) | 2026-08 | 2026-11-21 | 中 |
| [6] | Pianist Transformer：吃樂譜 MIDI、CPU 可推論、macOS 安裝、輸出速度曲線與踏板 | [yhj137/PianistTransformer (GitHub)](https://github.com/yhj137/PianistTransformer) | 2026-06（論文 v2） | 2026-11-21 | 高 |
| [7] | Pianist Transformer 權重 Apache-2.0 | [yhj137/pianist-transformer-rendering (HF)](https://huggingface.co/yhj137/pianist-transformer-rendering) | 未標 | 2026-11-21 | 高 |
| [8] | VirtuosoNet 需 MusicXML；權重在 HF | [jdasam/virtuosoNet (GitHub)](https://github.com/jdasam/virtuosoNet) | 未標 | 2026-11-21 | 高 |
| [9] | ScorePerformer 非商用、無明確權重 | [ilya16/ScorePerformer (GitHub)](https://github.com/ilya16/ScorePerformer) | 未標 | 2026-11-21 | 中 |
| [10] | SyMuPe 無 CUDA 專屬相依、裝置可設、吃樂譜 MIDI；開源版無情緒文字介面 | [ilya16/SyMuPe (GitHub)](https://github.com/ilya16/SyMuPe) | 2026-04 | 2026-11-21 | 高 |
| [11] | PianoFlow-base 權重 CC BY-NC-SA；模型卡無文字介面 | [SyMuPe/PianoFlow-base (HF)](https://huggingface.co/SyMuPe/PianoFlow-base) | 2026-04 | 2026-11-21 | 高 |
| [12] | PianoFlow 約 24M 參數、CPU 接近即時；論文的情緒引導機制 | [Borovik et al., arXiv 2511.03425](https://arxiv.org/html/2511.03425v1) | 2025-11 | 2026-11-21 | 中 |
| [13] | symupe 安裝需手動補 numba | [SyMuPe issue #9](https://github.com/ilya16/SyMuPe/issues/9) | 2026-07 | 2026-11-21 | 高 |
| [14] | AMT 旋律條件伴奏用法、上下文長度、2026 PR | [jthickstun/anticipation (GitHub)](https://github.com/jthickstun/anticipation) | 2024-03 | 2026-11-21 | 高 |
| [15] | AMT 核心取樣不綁裝置，輔助腳本寫死 .cuda() | [anticipation/sample.py](https://github.com/jthickstun/anticipation/blob/main/anticipation/sample.py) | 2024-03 | 2026-11-21 | 高 |
| [16] | transformers 4.29.2 在 Python 3.12 安裝失敗 | [anticipation issue #19](https://github.com/jthickstun/anticipation/issues/19) | 2025-09 | 2026-11-21 | 高 |
| [17] | 主分支無 KV 快取，快取分支未合併 | [anticipation issue #15](https://github.com/jthickstun/anticipation/issues/15) | 2024-03 | 2026-11-21 | 高 |
| [18] | 沒有 5 秒伴奏開頭時品質差 | [anticipation issue #18](https://github.com/jthickstun/anticipation/issues/18) | 2025-04 | 2026-11-21 | 中 |
| [19] | 無法指定只用鋼琴伴奏；遮罩作法會退化 | [anticipation issue #9](https://github.com/jthickstun/anticipation/issues/9) | 2023-12 | 2026-11-21 | 中 |
| [20] | music-medium-800k 約 360M 參數，Apache-2.0 | [stanford-crfm/music-medium-800k (HF)](https://huggingface.co/stanford-crfm/music-medium-800k) | 2023 | 2026-11-21 | 高 |

## 過期地圖

以下全都在 2026-11-21 對照各專案的最新版本查過。工具腳本依「來源發布日期」計算，九項裡有八項顯示為過期。這只代表 README 和 issue 本身是舊的，不代表結論過時。版本相容性的有效期限是一個月，所以**最晚 2026-12-21 前要開工，否則開工前重查一次**：

| 說法 | 類別 | 重查時機 |
|---|---|---|
| AMT 的 transformers 鎖定版本、沒有 KV 快取 | 相容性／效能 | 開工時；留意 2026 年的新 PR 是否合併 |
| symupe 安裝要補 numba（issue #9） | 相容性 | 開工時 |
| Pianist Transformer 能在 CPU／macOS 上跑 | 相容性 | 開工時 |
| SyMuPe 沒有開源情緒文字引導 | 能力 | 2027-02 前 |
| Aria 只能續寫 | 能力 | 2027-02 |
