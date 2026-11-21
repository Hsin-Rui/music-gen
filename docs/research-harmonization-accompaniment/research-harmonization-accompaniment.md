---
title: '技術研究：配和聲模型與和弦條件伴奏生成'
type: 'technical'
topic: '配和聲模型、伴奏生成模型、語言模型配和聲能力、附和弦標記的旋律資料'
decision: '原型 02「先定和聲，再生伴奏」用哪些模型與資料；累積進知識庫'
source: 'native run'
status: complete
preset: 'standard'
validation: 'normal'
created: '2026-11-21'
updated: '2026-11-21'
claims_verified: 7
claims_unverified: 1
builds_on:
  - docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md
  - docs/research-prototype-model-check/research-prototype-model-check.md
---

# 技術研究：配和聲模型與和弦條件伴奏生成

**這份研究服務的決定：** 原型 02「先定和聲，再生伴奏」要用哪些模型和資料，並把結果累積進 `kb/`。

## 執行摘要

**建議：原型 02 拆成兩段分開比較。先比「誰來配和聲」，再比「誰來把和聲彈成伴奏」。**
- 配和聲比三個：MelodyT5、AccoMontage2、語言模型。用你親手配的和弦當標準答案。
- 伴奏比三個：AMT 加上和弦條件、AccoMontage、Polyffusion。
- 每段多生幾份，用和聲指標挑最好的。
- 前提是和聲要正確，而你本身就是最可靠的裁判。

推出這個建議的三個發現：

1. **「配和聲」和「吃和弦生伴奏」都有開源、MIT 授權、有權重的模型**，而且都是為了我們這種任務設計的。這是前一輪沒查到的。
   - **MelodyT5**（ISMIR 2024）：用 ABC 記譜替旋律配和弦，支援七和弦和轉位。程式碼和 HF 權重都是 MIT，1.13 億參數 [1][2]。
   - **AccoMontage2**（ISMIR 2022）：只給旋律，就能同時配和聲、生伴奏，但**只支援 4/4 拍** [3][4]。
   - **AccoMontage、Polyffusion**：吃「旋律＋和弦」生鋼琴伴奏 [11][10]。
   - 這些模型多半用 **POP909** 訓練，它是「旋律＋和弦＋鋼琴伴奏」的資料集 [21]。原型 01 用的 AMT 主要學的是流行歌轉成的多樂器 MIDI，不是為「單旋律配鋼琴伴奏」設計的（[R1 來源 10–12](../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)）。
2. **「和弦正確」不等於「聽起來和諧」。** D3PIA 的聽覺測試發現：和弦正確率最高的模型（WSG，87.6%），聽者反而覺得比較不和諧，因為裡面有不協和的音 [8]。所以挑選伴奏時，要同時看和弦正確率、調外音比例和協和度，最後還是要靠耳朵 [12]。這呼應前一輪的發現：客觀指標和聽者評分相關很弱（[R1 來源 60](../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)）。
3. **讓語言模型決定和聲，目前沒有嚴謹證據，只有零星跡象。**
   - 沒有任何正式評測拿一般語言模型配和聲，和專門的配和聲模型比較 [20]。
   - 有利的跡象：用文字格式（MIDI、LilyPond、MEI）把音符餵給語言模型時，和聲分析的表現接近滿分或不錯 [15][16][17]。
   - 不利的跡象：遇到半音和聲多的曲子就會出錯 [17]；也很難定位到特定小節 [18]，這和前一輪 ABC-Eval 的發現一致（[R1 來源 22](../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)）。
   - 原型 01 的三段旋律都是自然音階為主的民謠，正好是語言模型表現較好的情況。

**最大的限制：** 東亞、中國音樂的配和聲資料和模型都沒找到。附和弦標記的中國民歌語料完全沒有；最接近的是 OpenGufeng（古風流行）和中國合唱資料集 [26][27]。這和前一輪「非西方資料稀少」的結論一致（[R1 D2](../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)）。茉莉花這類旋律，現有的配和聲模型都是用西方資料訓練的。

---

## 一、配和聲模型（旋律 → 和弦）

| 模型 | 年份／會議 | 授權（程式碼／權重） | 權重 | 輸入→輸出 | 訓練資料 | Mac | 備註 |
|---|---|---|---|---|---|---|---|
| **MelodyT5** | ISMIR 2024 | MIT／MIT（HF 標籤） | ✅ HF | ABC 旋律 → 帶和弦記號的 ABC | 民謠、巴哈聖詠、Nottingham（西方） | 1.13 億參數，應可用 CPU；環境寫死 Python 3.7、CUDA 11.6，要改（未驗證） | 在 2 of 3 項指標上贏 STHarm，聽覺測試也較受偏好 [1][2] |
| **AccoMontage2** | ISMIR 2022 | MIT | 資料檔在 Google Drive | MIDI 旋律＋主音＋樂句切分 → 和弦＋伴奏 | Niko 和弦庫（5,000＋進行）、POP909 | README 沒提 GPU；有網頁介面 | **只支援 4/4**；樂句限 4 或 8 小節；四種和弦風格 [3][4] |
| 單編碼器遮罩式配和聲 | arXiv 2026-01 | Apache-2.0 | ❌ | 音級鋼琴卷 → 和聲 | HookTheory | 未知 | 摘要說幾乎所有指標都贏，跨領域進步最大 [5] |
| EMO_Harmonizer | arXiv 2024 | 無授權 | ✅ Google Drive | 事件序列 → MIDI | HookTheory＋EMOPIA | 依賴 CUDA 專用套件，可能不行 | 可以依情緒配和聲 [6] |
| STHarm／VTHarm | IEEE Access 2022 | 無授權 | ❌ 要自己訓練 | — | CMD、HookTheory | 假設 CUDA | 附 9 種評估指標的程式 [7] |
| B* 限制解碼 | AIMC 2025 | 論文 CC BY 4.0 | ？ | 旋律＋指定和弦 → 和弦 | — | 搜尋演算法 | 可以強制某些小節用你指定的和弦 [9] |

**評估的標準：** Yeh 等人（JNMR 2021）比較了模板比對、HMM、基因演算法和兩個深度模型，用了 6 項指標和 202 位聽者，是這個領域常用的比較基準 [13]。常用指標有 CTnCTR（和弦音比例）、PCS（音高協和分數）、MCTD（旋律與和弦的調性距離）[1][13]。

**沒查到：** music21 有沒有現成的規則式配和聲工具（預算用完沒查）；BART harmonization、MuPT、CoCoMulla。

## 二、吃和弦條件的伴奏模型（旋律＋和弦 → 鋼琴伴奏）

| 模型 | 年份／會議 | 授權 | 權重 | 輸入 | 訓練資料 | Mac | 備註 |
|---|---|---|---|---|---|---|---|
| **AccoMontage** | ISMIR 2021 | MIT | ✅ Google Drive | MIDI 旋律＋和弦（以拍為單位，可到九和弦） | POP909 樂句庫 | 檢索＋小型 VAE，README 沒提 CUDA（未驗證） | 輸出有力度和踏板，1–16 小節樂句 [11] |
| **Polyffusion** | ISMIR 2023 | MIT | ✅ SharePoint | 和弦條件、織體條件、旋律補寫 | POP909 | README 沒提裝置 | D3PIA 測得和弦正確率 37.5%，調外音 0% [10][8] |
| **Compose & Embellish** | ICASSP 2023 | MIT | ✅ HF | 旋律＋和弦（Embellish 階段） | Pop1K7 | 建議 CUDA 10.2 | 調外音 14.8%、和弦正確率 58.1% [14][8] |
| **D3PIA** | ICASSP 2026 | 未知 | ❌ 沒找到 | 旋律＋和弦的鋼琴卷 | POP909 | 只有 220 萬參數，8 小節約 1.7 秒 | **聽者評分最好**；和弦正確率 80.1%，調外音 0% [8] |
| FGG | ICML 2025（依 README） | **沒看到授權** | ✅ | 和弦（必要）＋旋律 | POP909 | 未驗證 | 取樣時硬性擋掉調外音，這個技巧可以套用到其他模型 [19] |
| Whole-Song Gen | ICLR 2024 | MIT | 部分 | 曲式＋調 | POP909 | 慢（GPU 上 8 小節 79 秒） | 和弦正確率 87.6%，但聽起來較不和諧 [8] |
| AccoMontage-3 | NeurIPS 2024 | MIT | ✅ | 旋律＋和弦 → 鋼琴 → 多軌 | LMD、Slakh2100 | 舊版 PyTorch、Python ≤ 3.9 | [24] |
| GETMusic | 2023 | — | README 沒寫 | 多軌 | 未公開 | — | 所屬的 muzic repo 已於 2026-10-01 封存 [25] |

**「多生幾份挑最好的」：** 沒有找到任何論文對鋼琴伴奏這樣做 [12]。最接近的是 2026 年一篇檢索式論文：用一個綜合分數（和聲吻合、聲部進行、風格、重複度）挑選 POP909 的伴奏樂句，但沒有程式碼，也沒有聽覺測試 [23]。**這是一個可以自己做的空白。**

**可以拿來挑選的指標：** 和弦正確率、調外音比例（OOK）、和弦嵌入相似度、和弦音比例（CTnCTR）、音高協和分數（PCS）、旋律與伴奏的協和／不協和重疊比例 [12]。

## 三、語言模型配和聲的證據

| 研究 | 模型 | 發現 | 可信度 |
|---|---|---|---|
| Carone 等人（PMLR 2026） | Gemini 2.5 Pro／Flash、Qwen2.5-Omni | 用 MIDI 文字輸入時，和弦性質辨識接近滿分；改成音訊就大幅下降。提示技巧幫助不大 [15] | 中（只讀摘要） |
| Pond 與 Fujinaga（CSME 2025） | ChatGPT、Claude、Gemini | 樂理考試：用 MEI 格式最好，Claude 加上情境教學達 75%；和弦分析的進步最少 [16] | 中 |
| Augmented Fifth 部落格（2026-08） | Claude Opus 5、Gemini 3.1 Pro、Grok 4.5 | 羅馬數字分析：巴哈、蕭邦表現不錯，史克里亞賓全部出錯（漏掉掛留音、副屬和弦）；用 LilyPond 文字可以，用樂譜圖片不行 [17] | 低（只有 3 段、單一評分者） |
| MSU-Bench（ACL 2026） | 15 個以上模型 | 很難定位到特定小節，連帶影響和聲題 [18] | 中 |
| ComposerX（2024） | GPT-4 多代理人 | 有一個「和聲代理人」負責加和弦，並檢查和弦與旋律的調性是否相符，是最接近「語言模型指揮」的設計 [19b] | 低中 |

**解讀：** 「語言模型先寫和弦、程式負責檢查和執行」這個混合設計有前例，例如 Carone 等人用的 LogicLM 作法 [15]、ComposerX [19b]、Libretto [20b]。但沒有人量過它配出來的和聲好不好。這正好可以在原型 02 裡，用你配的和弦當標準答案來量。

## 四、附和弦標記的旋律資料（新增到資料目錄）

| 資料集 | 規模 | 內容 | 授權 | 風格 |
|---|---|---|---|---|
| **POP909** | 909 首 | 旋律＋副旋律＋鋼琴伴奏＋和弦／調／拍（演算法標記） | MIT（repo 標籤） | 流行（是否為華語未在本輪確認）[21] |
| **Hooktheory** | 約 50 小時 | 旋律＋和聲標記 | CC BY-NC-SA 3.0 | 西方流行 [22] |
| **Chordonomicon** | 約 68 萬條和弦進行 | 只有和弦，沒有旋律 | CC BY-NC 4.0 | 西方流行／搖滾 [28] |
| **When-in-Rome** | 約 2,000 份羅馬數字分析 | 含 371 首巴哈聖詠、貝多芬四重奏等 | 新內容 CC BY-SA 4.0 | 西方古典 [29] |
| **Chord Melody Dataset** | 少於 650 首 | 爵士標準曲旋律＋和弦 | MIT（但原曲可能有版權） | 爵士 [30] |
| **OpenGufeng** | 未標示 | 旋律＋三和弦 | MIT | 中國風流行 [26] |
| **中國合唱資料集** | 125 首、441 段 | 含和弦標記 | 未讀 | 中國合唱 [27] |
| **Essen 中國民歌調式標記** | 219 首 | 調式標記（不是和弦） | CC BY 4.0，限制存取 | 中國民歌 [31] |
| MelodyHub | 26.19 萬首 ABC | 配和聲是七種任務之一 | 未讀 | 民謠、西方為主 [1] |

**沒查證：** Wikifonia、Nottingham、McGill Billboard、Rock Corpus、DCML。

## 跨面向洞察

- **我們做的任務，正好是 POP909 這一支研究在做的。** 「旋律＋和弦 → 鋼琴伴奏」是 POP909 系列模型的標準任務（AccoMontage、Polyffusion、D3PIA、FGG），AMT 不是。原型 01 的伴奏不好，很可能是選錯了工具，而不只是少了和聲控制。不過這些模型學的都是流行歌，配古典或民謠旋律時，風格可能會不對（推論）。
- **評估方法又一次成為空白。** 「多生幾份挑最好的」沒有人做過；「和弦正確」和「聽起來和諧」又會分歧。這呼應前一輪的洞察：評估方法本身就可以是研究貢獻（[R1 跨面向洞察](../research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)）。你擅長心理計量和聽覺實驗，正好派得上用場。
- **非西方資料仍是最大缺口。** 配和聲、伴奏兩邊都沒有用中國或東亞語料訓練的模型。這和前一輪的 D2、D3 一致：跨文化這條路必須從自己整理資料開始。

## 建議

1. **原型 02 的配和聲段：比較三種配和聲方法，用你配的和弦當標準答案。** 信心：中高。
   - 三種方法：MelodyT5、AccoMontage2、語言模型。
   - 你替三段旋律親手配一份和弦，量每個方法和標準答案的一致程度。
   - 這正好回應你說的前提「和聲標記要正確」。
   - 注意：AccoMontage2 只支援 4/4，綠袖子（3/4）不能用；茉莉花（2/4）可以兩小節併成一小節。
   - **對應原型 02 計畫的〈要比較的選項〉。**
2. **伴奏段：比較三種生伴奏方法，和弦都用同一份。** 信心：中。
   - 三種方法：AMT 加上和弦條件、AccoMontage、Polyffusion。
   - AMT 是現成流程，加上和弦條件的改動最小；另外兩個是為這個任務設計的 MIT 模型。
   - 它們在 Mac 上能不能跑，只看了 README，要先做簡單的試跑。
   - D3PIA 評價最好，但找不到程式碼，先記在知識庫裡，持續觀察。
3. **每種組合生 8 份，用和聲指標挑最好的，最後用耳朵確認。** 信心：中。指標用 CTnCTR、PCS、調外音比例，加上旋律與伴奏的不協和重疊比例。D3PIA 的研究顯示，單看和弦正確率會挑錯 [8]。
4. **知識庫：** 這一輪新增的模型、資料集、文獻都已經放進 `kb/`。POP909 和 When-in-Rome 是之後自己訓練時最值得先拿到的兩個資料集（授權寬鬆、標記完整）。
5. **暫不微調**，這是你已經做的決定。之後要做跨文化，需要自己整理附和弦標記的中國民歌資料。

## 待解問題

- MelodyT5、AccoMontage、Polyffusion 在 Mac 上跑不跑得動：要實際試跑。
- D3PIA 的程式碼到底有沒有公開：專案頁沒有連結。
- FGG 的授權：README 沒有授權檔。
- POP909 的曲目是不是華語流行：本輪沒確認。
- music21 有沒有規則式的配和聲工具，可以當最簡單的基準：本輪沒查。
- 語言模型配和聲的品質：沒有正式評測，原型 02 會自己量。

## 來源附錄

| # | 支撐的說法 | 發布者 | 發布日期 | 查閱日期 | 信心 |
|---|---|---|---|---|---|
| [1] | MelodyT5：ABC 配和聲、七和弦與轉位、1.13 億參數、訓練資料、指標比較 | [arXiv 2407.02277](https://arxiv.org/html/2407.02277) | 2024-07 | 2026-11-21 | 高 |
| [2] | MelodyT5 程式碼 MIT、HF 權重 MIT 標籤、環境寫死 CUDA 11.6 | [GitHub](https://github.com/sanderwood/melodyt5)、[HF](https://huggingface.co/sander-wood/melodyt5) | 2024 | 2026-11-21 | 高 |
| [3] | AccoMontage2：MIT、只支援 4/4、4／8 小節樂句、CLI 與 GUI | [GitHub AccoMontage2](https://github.com/billyblu2000/AccoMontage2) | 2022 | 2026-11-21 | 高 |
| [4] | AccoMontage2 聽覺測試：和聲性顯著優於 BLSTM | [arXiv 2209.00353](https://arxiv.org/pdf/2209.00353) | 2022 | 2026-11-21 | 中 |
| [5] | 單編碼器遮罩式配和聲（Apache-2.0、無權重） | [arXiv 2601.16150](https://arxiv.org/abs/2601.16150)、[GitHub](https://github.com/NeuraLLMuse/SingleEncoderMHCrossAttention) | 2026-01 | 2026-11-21 | 高 |
| [6] | EMO_Harmonizer：無授權、依賴 CUDA 套件 | [GitHub](https://github.com/Yuer867/EMO_Harmonizer)、[arXiv 2407.20176](https://arxiv.org/html/2407.20176) | 2024-07 | 2026-11-21 | 中 |
| [7] | STHarm／VTHarm：無授權、無權重 | [GitHub](https://github.com/rsy1026/harmonizers_transformer) | 2022 | 2026-11-21 | 高 |
| [8] | D3PIA：220 萬參數、POP909 比較表、13 位專家聽覺測試；和弦正確率不等於聽感和諧 | [arXiv 2602.03523](https://arxiv.org/html/2602.03523)、[專案頁](https://jech2.github.io/D3PIA/) | 2026-02 | 2026-11-21 | 高 |
| [9] | B* 限制解碼 | [arXiv 2512.07627](https://arxiv.org/abs/2512.07627) | 2025-12 | 2026-11-21 | 中 |
| [10] | Polyffusion：MIT、和弦與織體條件、旋律補寫 | [GitHub](https://github.com/aik2mlj/polyffusion) | 2023 | 2026-11-21 | 高 |
| [11] | AccoMontage：MIT、旋律＋和弦 → 鋼琴伴奏、POP909 樂句庫 | [GitHub](https://github.com/zhaojw1998/AccoMontage) | 2024-02 | 2026-11-21 | 高 |
| [12] | 和聲一致性指標彙整；沒有「多生幾份再挑」的伴奏論文 | [arXiv 2001.02360](https://arxiv.org/pdf/2001.02360)、[arXiv 2506.14723](https://arxiv.org/pdf/2506.14723)、[arXiv 2606.11886](https://arxiv.org/pdf/2606.11886) | 2020–2026 | 2026-11-21 | 中 |
| [13] | Yeh 等人配和聲比較研究（JNMR） | [arXiv 2001.02360](https://arxiv.org/abs/2001.02360) | 2020-01 | 2026-11-21 | 高 |
| [14] | Compose & Embellish：MIT、HF 權重 | [GitHub](https://github.com/slSeanWU/Compose_and_Embellish) | 2024-07 | 2026-11-21 | 高 |
| [15] | 語言模型在符號輸入接近滿分、音訊下降；LogicLM | [PMLR v303](https://proceedings.mlr.press/v303/carone26a.html) | 2026-01 | 2026-11-21 | 中 |
| [16] | 樂理考試各編碼格式比較 | [arXiv 2503.22853](https://arxiv.org/abs/2503.22853) | 2025-03 | 2026-11-21 | 中 |
| [17] | 前沿語言模型的羅馬數字分析（非正式） | [Augmented Fifth](https://aug5th.substack.com/p/llms-vs-harmonic-analysis) | 2026-08 | 2026-11-21 | 低 |
| [18] | MSU-Bench（ACL 2026） | [arXiv 2511.20697](https://arxiv.org/abs/2511.20697) | 2025-11 | 2026-11-21 | 中 |
| [19] | FGG：取樣時擋掉調外音；沒看到授權 | [arXiv 2410.08435](https://arxiv.org/html/2410.08435)、[GitHub](https://github.com/huajianduzhuo-code/FGG-music-code) | 2025-06 | 2026-11-21 | 高／中 |
| [19b] | ComposerX 多代理人 | [QMUL](https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/98627/) | 2024 | 2026-11-21 | 低中 |
| [20] | 找不到語言模型配和聲的正式評測 | [HN](https://news.ycombinator.com/item?id=36497414)、[AudioCipher](https://www.audiocipher.com/post/chatgpt-music) | 2023 | 2026-11-21 | 中 |
| [20b] | Libretto：給語言模型代理人的文法與評分空間 | [arXiv 2606.22708](https://arxiv.org/abs/2606.22708) | 2026-06 | 2026-11-21 | 低 |
| [21] | POP909 內容與授權 | [GitHub](https://github.com/music-x-lab/POP909-Dataset)、[arXiv 2008.07142](https://arxiv.org/pdf/2008.07142) | 2020 | 2026-11-21 | 高／中 |
| [22] | Hooktheory 資料 CC BY-NC-SA 3.0 | [Sheet Sage](https://github.com/chrisdonahue/sheetsage) | 2022 | 2026-11-21 | 高 |
| [23] | 風格規劃＋樂句檢索，以綜合分數挑選 | [arXiv 2602.15074](https://arxiv.org/html/2602.15074v1) | 2026-02 | 2026-11-21 | 高 |
| [24] | AccoMontage-3：MIT、舊版 PyTorch | [GitHub](https://github.com/zhaojw1998/AccoMontage-3) | 2024-10 | 2026-11-21 | 高 |
| [25] | GETMusic 所屬 repo 封存 | [GitHub muzic](https://github.com/microsoft/muzic/tree/main/getmusic) | 2026-10 | 2026-11-21 | 高 |
| [26] | OpenGufeng 古風流行旋律＋和弦，MIT | [GitHub](https://github.com/yongyizang/OpenGufeng) | — | 2026-11-21 | 中 |
| [27] | 中國合唱資料集 | [Springer](https://www.springerprofessional.de/en/chinese-chorales-dataset-a-high-quality-music-dataset-for-score-/26698008) | 約 2024 | 2026-11-21 | 低 |
| [28] | Chordonomicon，CC BY-NC 4.0 | [HF](https://huggingface.co/datasets/ailsntua/Chordonomicon) | 2024 | 2026-11-21 | 高 |
| [29] | When-in-Rome，CC BY-SA 4.0 | [GitHub](https://github.com/MarkGotham/When-in-Rome) | 持續更新 | 2026-11-21 | 高 |
| [30] | Chord Melody Dataset | [GitHub](https://github.com/shiehn/chord-melody-dataset) | — | 2026-11-21 | 中 |
| [31] | Essen 中國民歌調式標記 | [Zenodo 14607710](https://zenodo.org/records/14607710) | 2025 | 2026-11-21 | 中 |

## 過期地圖

全部在 2026-11-21 查閱。模型的相容性和授權每月可能變動，原型 02 開工前要重查：MelodyT5、AccoMontage、AccoMontage2、Polyffusion 的安裝相依，以及 D3PIA 是否公開程式碼。能力和評估類的說法，2027-02 前重查。
