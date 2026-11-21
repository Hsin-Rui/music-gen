---
title: '技術研究 R4：原型 02 還能加哪些模型（配和聲、生伴奏）'
type: 'technical'
topic: 'accompaniment and harmonization candidates R4'
decision: '原型 02 下一步要加哪 1 到 2 個模型（配和聲一個名額、生伴奏一個名額）'
source: 'native run'
status: complete
preset: 'standard'
validation: 'normal'
created: '2026-11-21'
updated: '2026-11-21'
claims_verified: 12
claims_unverified: 1
prior_runs:
  - ../research-harmonization-accompaniment/research-harmonization-accompaniment.md
  - ../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md
---

# 技術研究 R4：原型 02 還能加哪些模型

**這份研究要支援的決定：** 原型 02 下一步要加哪 1 到 2 個模型，配和聲、生伴奏各一個名額。

**規則（使用者指定）：** 蒐集時每個候選都記錄，不管能不能跑；決策時只選跑得動的。不再追 Polyffusion。

## 摘要

**建議：配和聲加 HarmonyRL，生伴奏這一輪不加新模型。**

1. **配和聲：HarmonyRL 是唯一同時滿足「有公開權重、能用 CPU、吃得進我們的旋律、支援 2/4 和 3/4」的新模型** [16]。它 2026-11-16 才發布，評估很弱：聽覺測試只有 1 位聽者 [17]。所以它值得放進來讓你用耳朵比，但不代表它比較好。規則式的 VeeHarmGen 可以當成成本很低的「基準線」[26]。
2. **生伴奏：2025–2026 年有新論文，但沒有一個公開了可用的程式碼和權重** [6][7]。
   - 唯一拿得到的 **AccoMontage-3**，第一段「旋律＋和弦 → 鋼琴」用的就是我們已經試過的 AccoMontage [1]。它多出來的是第二段，把鋼琴編成樂團，不在這次範圍內。
   - **Compose & Embellish** 只能在 CUDA 上推論，README 提到、可以不靠 fast-transformers 套件的 GPT-2 推論檔也不存在 [3]。
   - 結論是：伴奏這邊與其接新模型，不如先把現有模型的參數調好，再和「Claude 寫伴奏」比。
3. **語言模型配和聲：沒有任何研究評估過 GPT-4o、GPT-5、Claude、Gemini 替給定的旋律配和弦。** 最接近的是 2024 年的研究，專家給 GPT-4 的評分是 5.5 到 6.5 分（滿分 10）[23]。你用耳朵比較 Claude 的和弦，是現有文獻沒有的資料。如果再加一個語言模型（例如 GPT 或 Gemini）一起比，會是新的證據。

**最大的保留：** HarmonyRL 太新（5 天、約 40 次下載），權重授權是非商用（CC BY-NC-SA），模型卡要登入同意條款才能下載 [16][17]。

## Table of Contents

- [一、生伴奏模型](#一生伴奏模型旋律和弦--鋼琴)：AccoMontage-3、Compose & Embellish、CoCoMulla、2026 新論文
- [二、配和聲模型](#二配和聲模型旋律--和弦)：HarmonyRL、BART／B\*、NeuraLLMuse 系列、EMO_Harmonizer、MuPT、其他
- [三、語言模型配和聲的證據與規則式基準](#三語言模型配和聲的證據與規則式基準)：ChatMusician、GPT-4 專家評分、ABC-Eval、VeeHarmGen
- [跨面向洞察](#跨面向洞察)
- [決策矩陣](#決策矩陣)：只看跑得動的候選
- [建議](#建議)
- [待解問題](#待解問題)
- [來源附錄](#來源附錄)
- [過期地圖](#過期地圖)

## 一、生伴奏模型（旋律＋和弦 → 鋼琴）

R3 已經查過、這次不重查：AMT、AccoMontage、AccoMontage2、Polyffusion、D3PIA、FGG、Whole-Song Gen、GETMusic。

| 模型 | 年份／會議 | 程式碼／權重 | 授權 | 輸入 → 輸出 | Mac | 品質證據 | 拍子 |
|---|---|---|---|---|---|---|---|
| **AccoMontage-3** | NeurIPS 2024 | ✅／✅ Google Drive（repo 已改名 Structured-Arrangement-Code） | 程式碼 MIT；權重沒寫 | 旋律軌＋和弦軌（MIDI 音符）→ ① 鋼琴 → ② 多樂器 | 第一段有寫死的 `.cuda()`，要小改；和弦要寫成 MIDI 音符，由程式重新辨認；環境釘在 torch 1.10、Python ≤ 3.9 [2] | 和弦正確率 0.567（AMT 0.446）；23 人聽覺測試全部勝過對照組 [1] | **只支援四拍子（不支援 3/4）** |
| **Compose & Embellish** | ICASSP 2023 | ✅／✅ HF | MIT | REMI 事件文字檔 → 鋼琴演奏 MIDI | 推論只寫了 CUDA；程式碼寫死 CUDA；README 說的 GPT-2 推論檔不存在（404）[3] | 論文說縮小了和真人演奏的結構差距（沒拿到數字）[4] | 程式碼暗示 4/4 |
| CoCoMulla | ISMIR 2024 | ✅／✅ | **沒有授權** | 音訊＋MIDI＋和弦 → **音訊** | — | 審稿人說評估不嚴謹 [5] | — |
| 結構化鋼琴伴奏（Zang 等人） | arXiv 2026-02 | ❌／❌ | — | 功能和聲樂譜＋段落標記 → 鋼琴 MIDI（規劃器＋POP909 檢索） | — | 沒有聽覺測試；有 60 首試聽 MIDI [6] | POP909 多為 4/4 |
| 無配對鋼琴伴奏風格轉換 | APSIPA 2025 | 未知 | 未知 | 樂譜 → 換風格的伴奏 | — | PDF 讀不到內容 [7] | — |
| Florence Price 伴奏生成 | ISMIR 2025 | 說有釋出，找不到權重 | 論文 CC BY 4.0 | **只吃旋律** → 藝術歌曲風格伴奏 | 未知 | 盲聽比基準更像 Price [8] | 未知 |
| STAGE | ISMIR 2025 | — | — | 音訊 → 音訊 | — | [9] | — |
| LeadsheetArrangement | 約 2018 | ✅／未知 | 未知 | 樂譜 → 5 軌鋼琴卷 | — | — | — |

**MIREX 2024 的符號生成項目就是「樂譜 → 鋼琴伴奏，8 小節，4/4」** [10]。這說明這是社群公認的任務，但幾乎所有系統都綁在 4/4。

**這個面向的結論：** 停在「新穎性耗盡」。兩輪下來，沒有找到 2025–2026 年公開權重、又吃旋律＋和弦的鋼琴伴奏模型。

## 二、配和聲模型（旋律 → 和弦）

R3 已經查過：MelodyT5、AccoMontage2、STHarm／VTHarm、2026 單編碼器遮罩模型、Yeh 等人的比較研究。

| 模型 | 年份 | 權重 | 授權 | 輸入 → 輸出 | Mac | 品質證據 | 拍子 |
|---|---|---|---|---|---|---|---|
| **HarmonyRL** | 2026-11 | ✅ HF（要登入同意條款） | 程式碼 MIT；權重 **CC BY-NC-SA 3.0** | MusicXML／MIDI 旋律 → 和弦記號；可以只重配指定小節；有 temperature、seed 參數 | README 說可用 CPU；需要 Python ≥ 3.12 [16] | 調外和弦時間 5.5–12.9%（人類 9.6%）；聽覺測試只有 1 人 [17] | **2/4、3/4、6/8 等都有支援**（見程式碼 `meter.py`，README 沒寫）[16] |
| BART 配和聲（希臘 NeuraLLMuse 團隊） | 2025 | ❌ 沒找到 | 程式碼 Apache-2.0 | MusicXML 旋律 → 348 種和弦記號 | 約 5,000 萬參數，應該跑得動 | 驗證集 token 正確率約 80%；論文報告多項和聲指標 [11] | 拍號分子 1–10 |
| B\* 限制解碼 | 2025 | ❌ | Apache-2.0 | 同上，加上「這幾小節一定要用某和弦」 | — | 限制達成率 0.91–0.99（不限制時 0.20–0.27）[11][12] | 同上 |
| NeuraLLMuse 其他：SplitEncoder、GridMLMelHarm、LatentTraceGuidance（ISMIR 2026）、GraphGuidance、配和聲資料集 | 2025–2026 | ❌（SplitEncoder 說會釋出） | Apache-2.0 | — | — | GridMLMelHarm 有和 BART、GPT-2 比較（數字沒拿到）[13] | — |
| EMO_Harmonizer | 2024–25 | ✅ Google Drive | **沒有授權檔** | MIDI → 和弦／伴奏（可依情緒） | 要 CUDA 10.2 和 fast-transformers [14] | 沒查到 | 沒查到 |
| MuPT | ICLR 2025 | ✅ HF | Apache-2.0（190M 版） | ABC **續寫**，不是替固定旋律配和聲 | 小版本應可用 CPU | 沒有配和聲評估 [15] | 任何拍子 |
| CPFG-Net | arXiv 2025-11 | 沒查 | MIT | 旋律 → 和弦，可控制緊張度 | — | — [18] | — |
| Function Alignment（music-x-lab） | ISMIR 2025 | ✅ Google Drive | **沒有授權欄位** | 有「旋律→和弦」和「和弦→旋律」兩個轉接器 | 安裝指令用 CUDA 版 torch | 論文報 CTnCTR 等（沒拿到數字）[19] | — |
| RL-Chord | IEEE TNNLS 2024 | ❌ | — | 旋律 → 和弦，**可零樣本配中國民歌** | — | DQN 版最好 [20] | — |
| asigalov61 配和聲 Transformer | HF 2024–25 | ✅ | Apache-2.0 | **只看前 64 個音的音名**，不看節奏和拍子；每個音配一個和弦 | 可用 CPU | 沒有評估 [21] | 不看拍子 |
| 規則式：Fernandes Harmonizer、可解釋配和聲器 | 2025–2026 | 不需要 | — | 旋律 → 和弦 | CPU | — [32] | — |

**這個面向的結論：** 停在「涵蓋完成」。新的配和聲研究很活躍（尤其是 NeuraLLMuse 團隊），但只有 HarmonyRL 公開了能直接用的權重。RL-Chord 是唯一明說能配中國民歌的，可惜沒有程式碼。

## 三、語言模型配和聲的證據與規則式基準

| 研究 | 年份 | 模型 | 怎麼評 | 結果 |
|---|---|---|---|---|
| ChatMusician／MusicTheoryBench | 2024 | ChatMusician、GPT-4、GPT-3.5 | 用「生成結果和提示旋律的編輯距離」打分，**量的是旋律有沒有被保留，不是和聲好不好** [22] | 有效 ABC 比例：ChatMusician 99.6%、GPT-4 94.6%；一般音樂性聽測 ChatMusician 勝 GPT-4 76% |
| 語言模型會「推理」音樂嗎？ | ISMIR 2024 | GPT-4、Gemma、Llama2、Qwen | 從 355 題 ABC 配和聲資料中抽題，作者與兩位職業音樂家設計提示，專家打 0–10 分 [23] | GPT-4 遵循指示 6.5、符合條件 5.5。論文整體（各生成任務共通）觀察到的錯誤：調外音、和聲重複沒有結構、照抄動機、格式對但沒照條件 |
| ABC-Eval | 2025 | GPT-5、Gemini 2.5、DeepSeek | 10 項 ABC 理解題，**沒有和聲題** [24] | 數小節：GPT-5 家族 93–99%、Gemini pro 66%、DeepSeek-chat 30%（DeepSeek-reasoner 91%） |
| 和聲推理（Kruspe） | 2024 | GPT-3.5、GPT-4o | 音程、和弦、音階題 | 簡單音程接近全對，辨認和弦和音階較弱（只看到摘要）[25] |
| MusiChat、Libretto | 2026 | 未說明 | 語言模型＋符號引擎 | 摘要沒有配和聲數字 [31] |

**規則式和其他基準工具：**

| 工具 | 授權 | 狀態 | 方法 | 適合度 |
|---|---|---|---|---|
| **VeeHarmGen** | 有授權檔（沒讀內容） | v3.1.0（2025），music21 9.1 | 依風格（流行、爵士、古典、藍調）把每段旋律的音級集合對應到和弦；MusicXML 進出 [26] | **最便宜的基準線** |
| AutoHarmonizer | MIT | Python 3.7、TF 2.2（舊） | 神經網路（Wikifonia），可調和聲密度 [27] | 環境難裝 |
| meagtan/harmonizer | MIT | 小型 | 動態貝氏網路＋Viterbi（類 HMM）[28] | 傳統基準 |
| Impro-Visor | GPLv2 | 仍可下載 | Java，依和弦表生成爵士風格伴奏 [29] | 偏爵士 |
| music21 本身 | — | — | 有調性分析、和弦化、羅馬數字，但**沒有找到內建的配和聲功能**（未證實） | 只能當零件 |

Yeh 等人（202 位聽者）指出：和弦正確率不適合評配和聲，因為同一段旋律有很多種合理的配法，應該用 CTnCTR、PCS、MCTD 等指標加上聽者評分 [30]。

**這個面向的結論：** 停在「新穎性耗盡」。**沒有證據的地方本身就是發現。**

## 跨面向洞察

1. **「拿得到、跑得動、又有好評估」三者不可兼得。** 有聽覺測試的模型（AccoMontage-3、D3PIA）不是綁 4/4、要 CUDA，就是沒公開；跑得動的新模型（HarmonyRL、asigalov61）評估都很弱。原型 02 的盲聽本身，就是在補這塊缺口。
2. **幾乎所有工具都假設 4/4 和西方流行和聲。** 伴奏模型全都綁 4/4（AccoMontage 系列、C&E、MIREX 項目）[1][3][10]；配和聲模型多用 HookTheory 流行歌訓練。綠袖子（3/4）和茉莉花（五聲音階）會一直是弱點。HarmonyRL 是少數在程式碼裡明確處理 3/4、2/4 的 [16]。
3. **語言模型的長處剛好落在現有模型的弱點上。** 語言模型不受拍子限制，也能依照文字說明（例如「五聲音階、避免功能進行」）調整。但文獻記錄的弱點是數小節錯誤（部分模型）和調外音 [23][24]。這可以解釋為什麼 Claude 的和弦在你耳中最好：它是逐小節寫、附理由、每一份都由人看過，而不是一次產生整份 ABC。這是推論，還沒驗證。
4. **伴奏的瓶頸已經從「找模型」轉成「控制與挑選」。** 新的伴奏模型拿不到，現有模型的問題（AMT 抄旋律、AccoMontage 綁 4/4）要靠參數、挑選規則，或是「Claude 規劃＋規則展開」這類混合做法來處理。

## 決策矩陣

只列通過硬性門檻（公開權重、只需推論、Mac 可跑或小改可跑、研究用授權、輸入輸出符合）的候選。分數 1–5，權重可以重調。

**配和聲名額**

| 候選 | 聽覺／品質證據（30%） | 支援 3/4、2/4（25%） | 安裝成本低（25%） | 和已試方法不同（20%） | 加權 |
|---|---|---|---|---|---|
| **HarmonyRL** | 2（1 位聽者；有調外和弦統計）| 5 | 4（pip，Python 3.12 新環境） | 4（強化學習微調，可只重配指定小節） | **3.65** |
| VeeHarmGen（規則基準） | 1（沒有量化評估） | 4（music21，看音級，不綁拍子） | 5 | 5（規則式） | 3.45 |
| 另一個語言模型（GPT／Gemini） | 2（只有 GPT-4 的舊證據） | 5 | 4（需要 API 金鑰或手動貼上） | 3（和 Claude 同類） | 3.40 |
| asigalov61 Transformer | 1 | 1（不看節奏、拍子） | 4 | 3 | 2.15 |

**生伴奏名額**

| 候選 | 聽覺／品質證據（30%） | 支援 3/4、2/4（25%） | 安裝成本低（25%） | 和已試方法不同（20%） | 加權 |
|---|---|---|---|---|---|
| AccoMontage-3 第一段 | 4 | 1 | 2（要改 CUDA，torch 1.10 在 Apple Silicon 可能裝不起來） | **1（第一段就是 AccoMontage）** | 2.15 |
| Compose & Embellish | 3 | 1 | 1（推論只寫 CUDA，要自己寫格式轉換） | 4 | 2.20 |

伴奏名額沒有候選超過 2.5 分。

## 建議

1. **把 HarmonyRL 加進原型 02 當第四個配和聲方法。** 信心：中。它是唯一跑得動、又支援三種拍子的新模型 [16]，但品質證據很弱 [17]。另外，它的 temperature、seed 參數剛好可以用在下一輪的系統性調參數。
2. **加入 VeeHarmGen 當規則式基準線。** 信心：中。成本最低 [26]。它能回答：「模型配和聲有沒有比查表好？」
3. **（可選）再加一個語言模型配和聲。** 信心：中。文獻完全沒有比較過現代語言模型配和聲 [22][23][24]，所以這會是新的證據，也能檢驗「是 Claude 特別好，還是語言模型都行」。需要決定用哪一家、要不要 API 金鑰。
4. **生伴奏這一輪不加新模型。** 信心：中高。AccoMontage-3 的第一段就是 AccoMontage [1]；C&E 在 Mac 上要改的地方太多 [3]。把力氣放在現有模型的系統性調參數，以及「Claude 寫伴奏」。
5. **持續觀察：** NeuraLLMuse 的 SplitEncoder（說會釋出權重）、RL-Chord（中國民歌）、Function Alignment（有權重，沒有授權）、Florence Price 生成器（找到權重後）。都記進知識庫。

**下一步：** 交給 John 更新原型計畫 02：加入 HarmonyRL、VeeHarmGen（以及可選的另一個語言模型），並寫進系統性調參數的設計。

## 待解問題

- **HarmonyRL 在 3/4、2/4 和五聲音階旋律上的實際品質**：只能自己跑過才知道。
- **music21 有沒有內建配和聲功能**：沒查到，目前相信沒有。
- **AccoMontage-3 第一段能不能在 Apple Silicon 上跑**：torch 1.10 有沒有可用的版本、有沒有其他隱藏的 `.cuda()`，都沒有確認。
- **Function Alignment 的授權和 CPU 可行性**：要讀它的推論程式並詢問作者。
- **Florence Price 生成器的權重位置和基礎模型**：要讀 TT515 資料集 repo。
- **APSIPA 2025 那篇的內容、MIREX 2024 的參賽系統**：網頁或 PDF 讀不到。

## 來源附錄

| # | 支持的發現 | 出處 | 發表 | 存取 | 信心 |
|---|---|---|---|---|---|
| [1] | AccoMontage-3 架構、指標、聽測、只支援 4/4、第一段沿用 AccoMontage | [arXiv 2310.16334v4](https://arxiv.org/html/2310.16334v4) | 2024-11 | 2026-11-21 | 高 |
| [2] | AccoMontage-3 改名、輸入格式、寫死的 CUDA | [GitHub Structured-Arrangement-Code](https://github.com/zhaojw1998/Structured-Arrangement-Code) | 2024-10／2026-01 | 2026-11-21 | 高 |
| [3] | C&E 推論只有 CUDA、GPT-2 推論檔不存在、REMI 輸入 | [GitHub Compose_and_Embellish](https://github.com/slSeanWU/Compose_and_Embellish) | 2024-09 | 2026-11-21 | 高 |
| [4] | C&E 權重、MIT、3,820 萬參數 | [HF slseanwu/compose-and-embellish-pop1k7](https://huggingface.co/slseanwu/compose-and-embellish-pop1k7) | 2023–24 | 2026-11-21 | 高 |
| [5] | CoCoMulla 輸出音訊、沒有授權 | [arXiv 2310.17162](https://arxiv.org/abs/2310.17162)、[GitHub coco-mulla-repo](https://github.com/kikyo-16/coco-mulla-repo) | 2023／2024 | 2026-11-21 | 高 |
| [6] | Zang 等人：規劃＋檢索、沒有程式碼、沒有聽測 | [arXiv 2602.15074](https://arxiv.org/html/2602.15074) | 2026-02 | 2026-11-21 | 高 |
| [7] | 無配對鋼琴伴奏風格轉換 | [APSIPA 2025 P424](https://www.apsipa.org/proceedings/2025/papers/APSIPA2025_P424.pdf) | 2025-08 | 2026-11-21 | 低 |
| [8] | Florence Price 伴奏生成 | [arXiv 2506.23130](https://arxiv.org/abs/2506.23130) | 2025-06 | 2026-11-21 | 中 |
| [9] | STAGE 是音訊模型 | [arXiv 2504.05690](https://arxiv.org/html/2504.05690v2) | 2025 | 2026-11-21 | 高 |
| [10] | MIREX 2024 符號生成項目 | [MIREX wiki](https://www.music-ir.org/mirex/wiki/2024:Symbolic_Music_Generation)（只有搜尋摘要） | 2024 | 2026-11-21 | 中 |
| [11] | BART 配和聲規格、B\* 限制達成率 | [arXiv 2512.07627](https://arxiv.org/html/2512.07627v1) | 2025-12 | 2026-11-21 | 高 |
| [12] | B\* repo、Apache-2.0、沒有權重 | [GitHub BStarConstraintHarmonization](https://github.com/NeuraLLMuse/BStarConstraintHarmonization) | 2025-07 | 2026-11-21 | 高 |
| [13] | NeuraLLMuse 系列 repo；GridMLMelHarm | [GitHub NeuraLLMuse](https://github.com/NeuraLLMuse)、[MDPI 9513](https://www.mdpi.com/2076-3417/15/17/9513)（只有摘要） | 2025–2026 | 2026-11-21 | 高／中 |
| [14] | EMO_Harmonizer 沒有授權、要 CUDA | [GitHub EMO_Harmonizer](https://github.com/Yuer867/EMO_Harmonizer) | 2025-12 | 2026-11-21 | 高 |
| [15] | MuPT 權重、授權、只會續寫 | [HF MuPT-v1-8192-190M](https://huggingface.co/m-a-p/MuPT-v1-8192-190M)、[arXiv 2404.06393](https://arxiv.org/abs/2404.06393) | 2024 | 2026-11-21 | 高／中 |
| [16] | HarmonyRL 安裝、輸入輸出、拍子、CPU、授權 | [GitHub HarmonyRL](https://github.com/HarmonyRL/HarmonyRL)、[PyPI harmonyrl](https://pypi.org/project/harmonyrl/) | 2026-11 | 2026-11-21 | 高 |
| [17] | HarmonyRL 評估數字、1 位聽者 | [HF CloudHolic/harmonyrl-chromatic](https://huggingface.co/CloudHolic/harmonyrl-chromatic) | 2026-11 | 2026-11-21 | 中（自報、評估弱） |
| [18] | CPFG-Net | [GitHub CPFG_model](https://github.com/huang0251/CPFG_model)、[arXiv 2511.14600](https://arxiv.org/abs/2511.14600) | 2025-11 | 2026-11-21 | 高 |
| [19] | Function Alignment | [ISMIR 2025 poster 25](https://ismir2025program.ismir.net/poster_25.html)、[GitHub midi-function-alignment](https://github.com/music-x-lab/midi-function-alignment) | 2025 | 2026-11-21 | 高／中 |
| [20] | RL-Chord 中國民歌 | [XJTU scholar](https://scholar.xjtu.edu.cn/en/publications/rl-chord-clstm-based-melody-harmonization-using-deep-reinforcemen/)（只有摘要） | 2024 | 2026-11-21 | 中 |
| [21] | asigalov61 配和聲只看音名 | [HF Space Melody-Harmonizer-Transformer](https://huggingface.co/spaces/asigalov61/Melody-Harmonizer-Transformer) | 2025-03 | 2026-11-21 | 高 |
| [22] | ChatMusician 評估方式與數字 | [arXiv 2402.16153](https://arxiv.org/html/2402.16153v1) | 2024-02 | 2026-11-21 | 高 |
| [23] | GPT-4 配和聲專家評分與錯誤類型 | [arXiv 2407.21531](https://arxiv.org/html/2407.21531v1)、[GitHub LLMs_music_reasoning](https://github.com/SylviaZiyaZhou/LLMs_music_reasoning) | 2024-07 | 2026-11-21 | 高 |
| [24] | ABC-Eval 沒有和聲題、數小節正確率 | [arXiv 2509.23350](https://arxiv.org/html/2509.23350v1) | 2025-09 | 2026-11-21 | 高 |
| [25] | GPT-4o 和聲推理 | [arXiv 2409.05521](https://arxiv.org/html/2409.05521v1)（只有摘要） | 2024-09 | 2026-11-21 | 低 |
| [26] | VeeHarmGen | [GitHub VeeHarmGen](https://github.com/RedFerret61/VeeHarmGen) | 2025 | 2026-11-21 | 高 |
| [27] | AutoHarmonizer | [GitHub autoharmonizer](https://github.com/sander-wood/autoharmonizer) | — | 2026-11-21 | 高 |
| [28] | meagtan/harmonizer | [GitHub harmonizer](https://github.com/meagtan/harmonizer) | — | 2026-11-21 | 中 |
| [29] | Impro-Visor GPLv2 | [SourceForge Impro-Visor](https://sourceforge.net/projects/impro-visor/) | — | 2026-11-21 | 中 |
| [30] | Yeh 等人：和弦正確率不適合評配和聲 | [arXiv 2001.02360](https://arxiv.org/pdf/2001.02360) | 2020-01 | 2026-11-21 | 中 |
| [31] | MusiChat、Libretto | [arXiv 2607.24873](https://arxiv.org/abs/2607.24873)、[arXiv 2606.22708](https://arxiv.org/abs/2606.22708) | 2026 | 2026-11-21 | 低 |
| [32] | 規則式配和聲論文 | [arXiv 2501.02642](https://arxiv.org/abs/2501.02642)、[arXiv 2610.22416](https://arxiv.org/pdf/2610.22416) | 2025–2026 | 2026-11-21 | 中 |

## 過期地圖

| 主張 | 類別 | 依據日期 | 建議重查 |
|---|---|---|---|
| HarmonyRL 的安裝、格式、拍子、授權 [16] | 版本 | 2026-11 | **2026-12-01**（新專案，變動快） |
| AccoMontage-3 的 CUDA 寫法和輸入格式 [2] | 版本 | 2026-01（本次讀的是目前的 repo） | 動手前重看 |
| C&E 只能用 CUDA 推論 [3] | 版本 | 2024-09（本次讀的是目前的 repo） | 動手前重看 |
| 2025–2026 沒有公開權重的新伴奏模型 [6] | 生態 | 2026-02 | 已過 3 個月窗口；建議 2027-02 前再掃一次 |
| VeeHarmGen 現況 [26] | 生態 | 2025 | 已過窗口；採用前看最新版本 |
| GPT-4 配和聲評分 [23] | 效能 | 2024-07 | 2026-07（已過；也代表需要新研究） |
| AccoMontage-3 指標與聽測 [1] | 效能 | 2024-11 | 2026-11（已到期，但論文數字不會變） |
| ABC-Eval 數小節 [24] | 效能 | 2025-09 | 2027-09 |
| HarmonyRL 評估數字 [17] | 效能 | 2026-11 | 2028-11 |

由 `recon_kit.py staleness` 計算（版本 1 個月、生態 3 個月、效能 24 個月）。「版本」類主張的發表日期是 repo 最後更新日，但內容都是本次（2026-11-21）直接讀取的。最早的重查日是 HarmonyRL：**2026-12-01**。

這是一份「挑選」研究：超過兩季（約 2027-05）要先更新再拿來做決定。HarmonyRL 這類剛發布的模型變動很快，一個月內就該重看。
