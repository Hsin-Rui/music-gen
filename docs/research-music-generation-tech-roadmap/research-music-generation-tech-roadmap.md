---
title: '技術研究：音樂生成專案的技術起點與路線圖'
type: 'technical'
topic: '音樂生成專案的技術起點與路線圖'
decision: '決定技術起點與路線圖：樂譜↔音樂雙向轉換（採譜、看譜表情演奏）與可控、跨文化研究素材生成——哪些用現成、哪些自訓、用哪些資料、單旋律 MIDI 之後的下一步'
source: 'native run'
status: complete
preset: 'standard'
validation: 'normal + red-team'
created: '2026-11-19'
updated: '2026-11-20'
claims_verified: 13
claims_unverified: 8
---

# 技術研究：音樂生成專案的技術起點與路線圖

**這份研究服務的決定：** 樂譜↔音樂雙向轉換，以及可控、跨文化的研究素材生成，該從哪裡開始？哪些部分用現成的、哪些自己訓練、用哪些資料、單旋律 MIDI 之後的下一步是什麼？

## 執行摘要

**建議：不要從頭訓練。先用現成的開源模型拼出一條「採譜→樂譜層→表情演奏」的流程，把力氣花在整合、控制和評估上。研究的切入點選在「神經網路生成的測驗題目＋IRT 難度校準」。**

支撐這個建議的三個發現：

1. **每一段都有可以直接拿來用的零件，但沒有人把它們串起來。**
   - 採譜：MuScriptor、YourMT3+、Basic Pitch [1][3][4][5]
   - 給旋律生伴奏：AMT [12]
   - 作曲家和時期控制：NotaGen [19]
   - 鋼琴表情演奏：SyMuPe、Aria [8][18]

   找不到任何整合這些功能的開源工具鏈，而這正是你想做的「轉換工具箱」。
2. **你的研究問題有一個經過反方審查仍然成立的空白。**
   - 音樂能力測驗早就在用自動出題加 IRT，但用的是馬可夫鏈，只控制 3 個因子 [53]。
   - 針對性搜尋後，沒有找到任何研究用神經網路生成題目、再用 IRT 校準難度。
   - 西方中心的問題有實證支持 [58]，所以「跨文化、可控的生成題目」是有根據的研究貢獻。
3. **雙層架構方向對，但要修正說法。**
   - 有顯式的樂譜或規劃層，確實有助於控制。YuE2 的專家評分是 49.3% 對 34.6% [70]（預印本，只讀摘要）。
   - 對歌仔戲、京劇這類以滑音為主的傳統，控制點可能應該放在「音高曲線」或該文化專屬的符號，而不是西方的音符。這是從印度聲樂的研究推論出來的 [50]，京劇另有只用音符就合成歌聲的反例 [76]。
   - 兩層要分開訓練還是合成一個模型，目前還沒有定論。2026 年的證據比較偏向合成一個 [70]。

**最大的限制：資料和授權。**
- 可以商用的大型符號資料，只找到 PDMX [27]。主要的演奏資料、非西方資料和多數模型權重都限非商用 [2][8][17][28][34][35][36]。
- 歌仔戲幾乎沒有可以用的公開資料 [37][38]。
- 2026 年 7 月德國法院在 GEMA 對 Suno 案認定「模型本身侵權」[41]，判決尚未定讞，也只有單一來源。
- 結論：**做學術研究可行，但將來要做訂閱產品，就得重新挑選資料和權重。**

---

## D1　現況：採譜、表情演奏、可控生成

**採譜（音訊→樂譜）大致可以直接用現成的，但輸出是 MIDI，不是樂譜。**
- 最新的開源多樂器採譜模型是 **MuScriptor**（2026-08，預印本）。在作者自己的測試集上，多樂器 F1 是 48.2，YourMT3+ 是 21.9。不過在 Bach10、合唱和古典樂資料集上，YourMT3+ 的起音 F1 比較高，而且兩者唱合唱都很弱 [1]（中信心：數字是單一來源，而且來自競爭者自己的表格）。
- MuScriptor 的程式碼是 MIT，**權重是 CC BY-NC 4.0（非商用）** [2]。
- YourMT3+ 的程式碼是 GPL-3.0，HF 上的權重是 Apache-2.0 [3][4]。
- Basic Pitch 是 Apache-2.0，可以商用 [5]。
- 鋼琴採譜：最新的頂尖結果仍是 2024 年的 Transkun [6]，沒找到 2025–26 年的後繼者。
- **音訊→可編輯樂譜（MusicXML）**目前仍要分兩步：先轉 MIDI，再轉樂譜。已發表的系統只有鋼琴 [7]，沒有找到通用的多樂器音訊轉樂譜模型。

**看譜表情演奏（樂譜→有表情的演奏）研究很活躍，但幾乎全部只做鋼琴。**
- 最實用的開源工具是 **SyMuPe/PianoFlow**（README 標示 ACM MM'25，未獨立確認），可以用情緒文字引導。它的程式碼是 Apache-2.0，**權重和訓練資料是 CC BY-NC-SA 4.0**，論文自己也說還不能即時互動 [8]。
- 唯一找到的多樂器版本是 RenderBox（預印本，開放程度未確認）[9]（低信心）。

**可控的符號生成：有可以拿來改的基礎模型，各自控制的面向不同。**
- **Anticipatory Music Transformer（AMT）**：可以補寫缺段，也能「給旋律、生伴奏」。README 裡直接示範了 `controls=` 的用法 [10][12]。程式碼和權重都是 Apache-2.0，但大型模型的訓練資料包含「約 45 萬張商業唱片的轉譜」[11]。
- **NotaGen**（IJCAI 2025）：以「時期－作曲家－編制」作為提示生成 ABC 記譜，程式碼是 MIT [19]。這是本研究唯一找到、**有現成作曲家和時期控制**的開源模型。不過只有微調後的權重支援這種控制，而且本研究沒有系統性地搜尋其他有作曲家條件的模型。
- **Text2midi**（AAAI 2025，權重 Apache-2.0）[13] 和 **MIDI-LLM**（Llama 3.2 授權）[14]：用文字描述風格、調性、速度和樂器。
- **MIDI-GPT**：多軌補寫，加上密度、複音數、風格等屬性控制。權重是 Open RAIL-M，有使用限制 [20]。

**音訊生成：控制力進步很快，但產出不是樂譜。**
- ACE-Step 1.5（2026-02，MIT）支援風格控制、翻唱、局部重繪、給人聲生伴奏和 LoRA 微調；摘要沒有提到 MIDI 或樂譜輸出 [15][16]。
- MusicGen 的權重是 CC BY-NC [17]。

**整合工具鏈：** 沒有找到任何開源工具同時涵蓋採譜、生成和演奏（低信心：這是「沒找到」，不是「確定不存在」）。

## D2　資料集與授權

**可以商用又乾淨的大型符號資料，只找到 PDMX。**
- PDMX 收錄超過 25 萬份 MusicXML 樂譜，授權 CC BY 4.0。有 12.29% 的曲目授權資訊互相矛盾，作者建議使用 `no_license_conflict` 子集（222,856 首）[27]。

**其他主要資料集都只能非商用，或底層版權有疑慮：**
| 資料集 | 內容 | 授權 |
|---|---|---|
| MAESTRO v3 | 198.7 小時，鋼琴 MIDI＋音訊 | CC BY-NC-SA [28] |
| ASAP | 222 份樂譜對 1,067 次演奏（README 內的數字不一致：222／236、1,067／1,068） | CC BY-NC-SA [31] |
| Aria-MIDI | 從網路音訊轉錄的鋼琴 MIDI [81] | CC BY-NC-SA，另有免責聲明 [30] |
| Lakh MIDI | 17.6 萬個 MIDI | 資料集本身 CC BY 4.0，但內容是抓下來的流行歌轉譜，底層作品的版權並未因此授權（推論）[29] |
| Opencpop | 中文歌聲加樂譜 | 官方頁面是 CC BY-NC-ND 4.0，商用需另外寫信洽談。來源原本互相矛盾，已依官方頁面釐清 [32] |
| M4Singer | 中文多風格歌聲 | CC BY-NC-SA，另附賠償條款 [33] |

**非西方和傳統音樂：資料大多限非商用、以音訊為主，有些要申請才能取得。**
- 京劇（CompMusic）：不同紀錄的授權不同，有 CC BY-NC-ND、CC BY-NC 和 CC BY [35]。其中有 120 段唱腔、1,265 句的清唱資料，附 pYIN 音高曲線和音符標註 [49]。
- 土耳其 makam 的 SymbTr：約 3,000 首，CC BY-NC-SA [36]。
- 印度音樂的 Saraga：CC BY-NC-SA [34]。
- **歌仔戲**：
  - 中研院團隊有一份「人聲片段＋歌詞」資料（ISMIR 2025 初步發表），沒有音高或樂譜層，發布狀態也不明 [37]。
  - FT-GAN 的 GOAT 歌仔戲資料要申請才能取得，授權是 CC BY-NC-SA，並附賠償條款 [38]。
- **日本傳統音樂**：在英文搜尋中，唯一能拿來做研究的只有 9 段民謠錄音（VocalNotes，CC BY-NC-SA），而且要填申請表才能取得。整份資料集含有敏感的儀式內容，作者要求不要重新彙整後公開 [64]（中信心：來自搜尋摘要）。
- **台灣原住民音樂**：中研院民族所的祭儀歌舞檔案有 7 族、309 個影音檔，可以在線上取得，但**頁面沒有寫重用條款** [65]。

**法律現況：風險在模型背下並吐出訓練資料，不只是「訓練」這個行為本身。**
- GEMA 對 OpenAI 案（慕尼黑，2025-11）：法院判定模型背下歌詞並在輸出中重現屬於侵權，而且文字與資料探勘（TDM）的例外不適用 [40]。截至 2026-07 仍在上訴中 [41]。
- **GEMA 對 Suno 案（慕尼黑，2026-07-31）**：法院認為「模型本身侵權」，責任在提供模型的業者，符合 EU AI Act 也不能當作抗辯。判決尚未定讞 [41]（中信心：只有一個法律事務所的來源）。
- 美國：2025 年 10 到 11 月，UMG 和 WMG 分別與 Udio 和解，WMG 也與 Suno 和解 [42]。

## D3　非十二平均律的表示法

**記譜格式在規格上做得到，實際上很少軟體支援。**
- MIDI 2.0 有逐音音高和 32 位元的滑音（pitch bend）[43]。
- MusicXML 原生支援四分之一音，也可以用小數 `<alter>` 表示更細的音高 [44]。
- MEI 能區分「寫的」和「實際發聲的」臨時記號 [46]。
- 但實務上：沒找到確認支援 MIDI 2.0 逐音音高的合成器清單 [77]；Dorico 匯出時會丟掉微分音記號 [45]，OpenMusic 匯入時也會忽略它們 [78]（中低信心：都來自論壇）。
- 滑音和裝飾音在這些格式中，多半只能當作音符或裝飾記號處理。有研究者因此質疑「音符」是不是適合許多傳統的基本單位 [83]（低信心）。

**目前研究的做法：把「連續音高曲線」放在中間層。**
- 印度聲樂的 GaMaDHaNi（ISMIR 2024）是「音高曲線→音訊」的兩階段生成。作者明確反對用「粗糙的離散符號」來表示旋律 [50]。
- 京劇的資料集同時提供 f0 曲線和音符標註 [49]。
- 2026 年有一篇預印本用 VQ-VAE 把韓國傳統音樂的裝飾音曲線「學成」離散符號 [51]。
- 計算民族音樂學早就主張：把音高切成離散的音，本身就是一種文化慣例 [52]。

**在地資料的缺口：**
- 工尺譜的光學辨譜研究只在 39 張圖上做過評估，沒有公開資料集 [47]。
- 簡譜沒有標準的評測資料，2025 年的系統改用不需要大量訓練資料的傳統電腦視覺方法 [48]。

## D4　音樂心理學裡的生成刺激

**已經有測驗用程式自動生成題目，但都不是深度學習。**
- 旋律辨別測驗（MDT，Sci Rep 2017）的做法 [53]：
  - 用馬可夫鏈，從愛爾蘭民謠（Essen 資料庫）生成旋律。
  - 只控制 3 個「難度因子」：旋律長度、輪廓違反、調性違反。
  - 用解釋型 IRT 校準難度，這 3 個因子能解釋難度變異的 **adj. R² = 0.869**。
  - 共校準 1,200 題，受試者是 158 位成人和 266 位兒童。
- CA-BAT（節拍）和 MPT（音準）沿用同樣的「自動出題＋IRT＋適性化測驗」做法 [54][55]。
- PROMS 標榜自己「文化公平」[56]。

**近年用 AI 音樂當刺激的研究，大多在問別的問題。** 它們多半測的是「標示為人做的還是 AI 做的，會不會改變聽者反應」，沒有拿模型來精確操弄變因，自然度的驗證也只做到操弄檢核 [57]。

**缺口還在，經過反方審查仍然成立。** 在 2017–2026 年的文獻中做了針對性搜尋，**沒有找到**任何研究用神經網路生成音樂能力測驗的題目，再用 IRT 或適性化測驗校準難度。最接近的有三個：
- 一篇用 VAE 生成相似度刺激、但沒有用 IRT 的研究（ICMPC 2023）[61]
- 一篇因為生成模型失敗、改用 Suno 的學士論文 [62]
- 一篇「依目標難度生成鋼琴視奏譜」的預印本（教育用途，不是測驗）[63]

**西方中心的批評有實證支持。**
- MDT 的作者自己承認只用了單一曲風 [53]。
- Jacoby 等人在 2024 年的 15 國研究發現，不同族群偏好的節奏比例不同，而學生和網路樣本的反應都很接近美國聽者 [58]。
- 音樂聽力測驗（MET）在中國樣本上，之前並沒有做過跨文化的信效度檢驗 [68]。

**評估生成品質的方法還沒有標準。** 評估方法的分類可以參考 ACM CSUR 的綜述 [59]。主觀的聽覺測驗沒有統一的實驗程序 [79]（預印本，中信心），客觀指標和聽者評分的相關也很弱：IS 是 0.25 到 0.37，FAD 是 −0.01 到 −0.16 [60]。

## D5　單旋律 MIDI 之後的路線

**現在的標準做法：**
- 用 MidiTok 把 MIDI 轉成模型能讀的符號序列，目前版本 3.1.0（2026-09，MIT），支援 REMI、CPWord、Octuple、MMM 等格式 [21]。
- 再接一個只有解碼器的 Transformer，或改用 ABC 記譜的文字模型。
- 三個目標都有開源的預訓練模型可以拿來改：
  - 伴奏：AMT [12]
  - 鋼琴表情演奏：Aria，Apache-2.0，ISMIR 2025（依 README，BibTeX 仍標為預印本，未確認）[18]
  - 作曲家和時期控制：NotaGen [19]

**算力：**
- NotaGen-large 的訓練、微調和推論都**至少**需要 24GB 顯示記憶體。NotaGen-X 在本機推論大約 8GB。較小的版本（110M、244M）需求更低 [19]。
- Aria 可以在 Apple Silicon 上用 MLX 推論 [18]。
- 參考值：MIDI-GPT 這種小型多軌模型從頭訓練，大約要 4 張 V100 跑 2 到 3 天 [20]。
- AMT、Aria 和 NotaGen 都沒有公布訓練所需的 GPU 時數。AMT 和 Aria 也**沒有附微調說明**，AMT 的作者把訓練導向另一套框架 Levanter [12][18]。

**一般 LLM 不適合當核心生成器。**
- 在 ABC-Eval（2025-09，預印本）上，GPT-5 的平均分數約 55%。所有模型在小節層級的任務上都失敗，辨認作曲家和曲風也接近用猜的 [22]。
- 用 ABC 微調 LLM 可以提升理解力，但會犧牲一般能力 [23]。
- 比較適合的用途是「自然語言介面」，而不是生成音樂本身。

**常見的坑：**
- 直接微調新的細部控制，模型常常學不會遵守。MuseBarControl 加了一個預訓練階段後，和弦正確率從 65.3% 提升到 78.3% [24]（中低信心）。
- 模型抄襲訓練資料，多半來自短動機重複出現 [26]。檢查方法也有限：旋律式的抄襲檢測在多聲部音樂上會失效，要改用 SSIMuse 這類專門方法 [25]。
- FMD 不是可靠的品質指標 [23]。訓練損失也不可靠：有研究發現，過擬合的模型聽起來反而更連貫，驗證損失卻變差 [80]（中低信心）。聽覺測驗仍然是基準。

## 跨面向洞察

- **授權決定了「研究版」和「產品版」是兩條不同的路。** 把 D1 的權重授權和 D2 的資料授權放在一起看：
  - 研究版可以用 MuScriptor、SyMuPe、MAESTRO、京劇資料。
  - 產品版只剩 Basic Pitch、YourMT3+（附 GPL 義務）、ACE-Step、PDMX，再加上自己錄製或取得授權的資料 [2][4][5][8][16][27]。其中 ACE-Step 和 YourMT3+ 的訓練資料來源還沒查證，商用前需要先確認。
  - AMT 雖然是 Apache 授權，作者自己也提醒輸出「應推定有侵權風險」[10]。在 GEMA 對 Suno 案之後，「寬鬆的授權不等於可以安全商用」這點更明確了 [41]。
- **最缺資料的文化，剛好也是最需要曲線表示的文化。** 歌仔戲和京劇的公開資料最少（D2），而它們偏偏最依賴滑音和裝飾音，西方記譜表達不了（D3）[37][49][50]。所以跨文化這一段，要從**自己採集資料**和**設計表示法**開始，不能指望直接微調現成模型。這也呼應了你想做田野調查的願望。
- **評估方法本身就可以是研究貢獻。**
  - 客觀指標不可靠，聽覺測驗又沒有標準程序（D4）[60][79]。
  - 但你的專業恰好有 IRT 和心理計量的方法（D4）[53]。
  - 加上模型會抄襲訓練資料，需要專門的檢查（D5）[25][26]。
  - 三者合在一起，「用心理計量方法驗證生成刺激的可控度、自然度和原創性」本身就是一個方法學貢獻。

## 反證（反方審查）

| 結論 | 判定 | 最強的反方論點 |
|---|---|---|
| 神經網路生成＋IRT 是研究空白 | **成立**，措辭改為「沒有找到」 | 馬可夫鏈出題已經能解釋約 87% 的難度變異；神經網路生成器沒有可以解釋的難度因子，可能反而削弱構念效度。所以必須說清楚神經網路生成「多帶來了什麼」，例如風格廣度和生態效度 [53]。最接近的既有研究見 [61][62][63]。這是審查員自己的推論，不是文獻結論。 |
| 雙層架構優於直接生成音訊 | **被削弱** | YuE2 中，專家較偏好「一個模型同時寫譜和生成音訊」，勝過分段串接 [70]。音訊轉接器已經能在沒有符號層的情況下控制節拍和音高 [71]。JASCO 則直接把符號形式的和弦和旋律當作條件，而不另外生成符號層 [72]。阿拉伯 maqam 有直接用提示詞引導音訊模型的例子 [73]。民族音樂學批評音符類別帶有歐洲的預設 [82]，採譜研究也普遍預設五線譜是目標格式 [75]。京劇歌聲也有只用音符、不用曲線就合成出來的研究 [76]。但目前沒有找到任何正面比較兩種做法的研究。 |
| 採用現成模型並微調，優於從頭訓練 | **被削弱**，核心仍然成立 | 24GB 只是 NotaGen-large 的下限，實際上要改用中小型版本 [19]。NotaGen 的預訓練資料來源沒有公開 [19]。西方偏誤主要在音訊模型上有實證，非西方資料只占 5.7% [74]。用很小的資料集微調容易背下訓練資料。替代方案「針對特定傳統自訂表示法、從頭訓練小模型」說得通，但沒有找到實證。 |

## 建議

1. **第一步，用 2 到 4 週做一個研究版原型，涵蓋「旋律→伴奏→演奏」。**
   - 用 AMT 從旋律生伴奏 [12]，再用 SyMuPe/PianoFlow 或 Aria 做鋼琴表情演奏 [8][18]。全部在研究授權下進行。
   - 這條路直接接著你做過的單旋律 MIDI，回答「下一步」的問題。
   - 信心：中高。授權都已到第一手來源查證，但能力只有部分查證：SyMuPe 的能力來自搜尋摘要，AMT 和 Aria 也沒有微調說明。「2 到 4 週」是我的估計，沒有來源。
   - **對應 brief 的「可行性」一節。**
2. **第二步，在西方曲風上建立可控的題目庫，再用 IRT 校準難度，做出第一篇論文的雛型。**
   - 仿照 MDT 的方法 [53]，把「難度因子」換成 NotaGen 的作曲家和時期條件 [19]，或 MIDI-GPT 的屬性控制 [20]。
   - 一開始就設計好「因子→難度」的解釋模型，回應反方審查的效度疑慮。
   - 信心：中。目前沒有先例，這同時是機會也是風險。
   - **對應研究計畫的「研究目標」和「構想方法」。**
3. **第三步，把跨文化視為獨立的資料和表示法工程，不要期待微調就能解決。**
   - 先挑一個傳統，京劇的資料最完整 [49]。用「音符骨架＋音高曲線」的表示法 [50][51]，並評估合一模型這條路 [70]。
   - 歌仔戲要先和中研院團隊 [37] 或 FT-GAN 團隊 [38] 洽談取得資料，或自己做田野採集。
   - 歌聲合成的部分，改用 openvpi/DiffSinger 作為基礎：它的程式碼是 Apache-2.0，但預訓練模型和聲庫的條款還沒查證 [39]。不要用沒有授權的 FT-GAN 程式碼 [38]。
   - 信心：中低。關於表示法的結論已被反方審查削弱，在地資料也極少。
   - **對應研究計畫的「跨文化變因框架」和「風險」。**
4. **一開始就決定是做研究還是做產品。**
   - 產品版從 PDMX、Basic Pitch、ACE-Step 這類可以商用的組合出發 [5][16][27]。
   - 所有生成內容都要做抄襲檢查，例如 SSIMuse [25]。
   - 信心：中。法律判決還在變動 [41]。
   - **對應 brief 的「限制與風險」。**
5. **不要拿一般的 LLM 當音樂生成器，只用它做自然語言介面** [22][23]。信心：中，因為只有單一評測來源。

## 待解問題

- **NotaGen 和 AMT 能不能在少量非西方資料上微調成功？** 目前沒有任何實作報告。需要自己做一個小實驗，例如拿京劇的樂譜 [49] 試微調 NotaGen-small。
- **雙層分開訓練和合一模型，哪個比較好？** 沒有找到正面比較的研究 [70]。要等 YuE2 的論文經過同儕審查，或自己做消融實驗。
- **歌仔戲和原住民音樂的資料能不能取得、怎麼取得？** 需要寫信洽談中研院民族所 [65]、Li Su 團隊 [37] 和 FT-GAN 作者 [38]，並遵循原住民同意相關的規範。
- **還沒查到的部分：**
  - 日文文獻裡的日本傳統音樂資料（英文搜尋幾乎沒有結果）
  - 中國少數民族音樂的資料庫
  - 美國著作權局的 AI 訓練報告
  - 可以用 Deepen 繼續查，或改用你自己的研究工具。
- **只有單一來源、尚待確認的說法：** GEMA 對 Suno 判決 [41]，以及 MAESTRO、M4Singer 和 Saraga 的授權 [28][33][34]。

## 過期地圖

大部分授權條款是在 2026-11-19 當天到第一手來源查證的，但 SymbTr、Saraga 和 Aria-MIDI 仍只有單一來源或搜尋摘要。授權最容易變動，建議每個月重查。依各類說法的有效期限，建議重查的時間如下：

| 類別 | 代表說法 | 建議重查 |
|---|---|---|
| 授權 | MuScriptor、SyMuPe、ACE-Step、MusicGen、AMT、PDMX、Opencpop、MAESTRO [2][8][11][16][17][27][28][32] | **2026-12-19** |
| 法律 | GEMA 對 OpenAI 上訴、GEMA 對 Suno [40][41] | 2027-02 |
| 評測和能力 | MuScriptor F1、ABC-Eval、YuE2、AMT 和 NotaGen 能力 [1][12][19][22][70] | 2027-05 |
| 資料集 | 工尺譜和簡譜辨譜資料、歌仔戲資料 [37][47][48] | 2027-11 |
| 方法 | GaMaDHaNi、MDT、民族音樂學 [50][52][53] | 2028-11 |

`recon_kit staleness` 依照「發表日期」計算，把 16 條說法標成過期，其中大多是授權類。不過授權本身是今天到第一手來源確認的，所以上表以存取日起算。**最早的重查日是 2026-12-19（授權類）。**

---

## 來源附錄

| # | 支持的發現 | 發表者 | 發表日期 | 存取日期 | 信心 |
|---|---|---|---|---|---|
| [1] | MuScriptor 架構與評測（預印本，ISMIR 2026 投稿） | [arXiv 2607.08168](https://arxiv.org/abs/2607.08168) | 2026-08 | 2026-11-19 | 中 |
| [2] | MuScriptor 程式碼 MIT／權重 CC BY-NC | [GitHub muscriptor](https://github.com/muscriptor/muscriptor)、[HF](https://huggingface.co/MuScriptor/muscriptor-large) | 2026-11 | 2026-11-19 | 高 |
| [3] | YourMT3+（IEEE MLSP 2024） | [arXiv 2407.04822](https://arxiv.org/html/2407.04822v3) | 2024-07 | 2026-11-19 | 中 |
| [4] | YourMT3 程式碼 GPL-3.0／權重 Apache-2.0 | [GitHub](https://github.com/mimbres/YourMT3)、[HF](https://huggingface.co/mimbres/YourMT3) | 2025-06 | 2026-11-19 | 高 |
| [5] | Basic Pitch Apache-2.0 | [Spotify GitHub](https://github.com/spotify/basic-pitch) | 2022 | 2026-11-19 | 高 |
| [6] | Transkun 鋼琴採譜（ISMIR 2024） | [arXiv 2404.09466](https://arxiv.org/html/2404.09466v6) | 2024 | 2026-11-19 | 中 |
| [7] | 鋼琴 MIDI→MusicXML（ISMIR 2024）；音訊→樂譜（IJCAI 2024） | [arXiv 2410.00210](https://arxiv.org/html/2410.00210v1)、[IJCAI](https://ijcai.org/proceedings/2024/862) | 2024 | 2026-11-19 | 中 |
| [8] | SyMuPe/PianoFlow 能力與授權 | [arXiv 2511.03425](https://arxiv.org/html/2511.03425v1)、[GitHub](https://github.com/ilya16/SyMuPe)、[HF](https://huggingface.co/SyMuPe/PianoFlow-base) | 2025-11 / 2026-05 | 2026-11-19 | 高（授權）／中（能力） |
| [9] | RenderBox 多樂器演奏（預印本） | [arXiv 2502.07711](https://arxiv.org/html/2502.07711v1) | 2025-02 | 2026-11-19 | 低 |
| [10] | AMT 補寫與伴奏能力（TMLR） | [arXiv 2306.08620](https://arxiv.org/abs/2306.08620) | 2023-06 | 2026-11-19 | 高 |
| [11] | AMT 權重 Apache-2.0；訓練資料含 45 萬張商業唱片轉譜 | [HF music-large-800k](https://huggingface.co/stanford-crfm/music-large-800k) | 2024-03 | 2026-11-19 | 高 |
| [12] | AMT `controls=` 伴奏示範；無訓練／微調程式碼 | [GitHub anticipation](https://github.com/jthickstun/anticipation) | 2026-07 | 2026-11-19 | 高 |
| [13] | Text2midi（AAAI 2025）MIT／Apache-2.0 | [HF](https://huggingface.co/amaai-lab/text2midi)、[GitHub](https://github.com/AMAAI-Lab/Text2midi) | 2025-01 | 2026-11-19 | 高 |
| [14] | MIDI-LLM，Llama 3.2 授權 | [arXiv 2511.03942](https://arxiv.org/abs/2511.03942v1)、[GitHub](https://github.com/slSeanWU/MIDI-LLM) | 2025-11 | 2026-11-19 | 高 |
| [15] | ACE-Step 1.5 能力（預印本） | [arXiv 2602.00744](https://arxiv.org/abs/2602.00744v2) | 2026-02 | 2026-11-19 | 高 |
| [16] | ACE-Step 1.5 程式碼與權重 MIT | [GitHub](https://github.com/ace-step/ACE-Step-1.5)、[HF](https://huggingface.co/ACE-Step/Ace-Step1.5) | 2026-02 | 2026-11-19 | 高 |
| [17] | MusicGen 權重 CC BY-NC | [AudioCraft GitHub](https://github.com/facebookresearch/audiocraft) | 2026-03 | 2026-11-19 | 高 |
| [18] | Aria：Apache-2.0、約 6 萬小時鋼琴、MLX 推論；無微調說明（README 標 ISMIR 2025，BibTeX 標預印本） | [GitHub EleutherAI/aria](https://github.com/EleutherAI/aria) | 2026-05 | 2026-11-19 | 高 |
| [19] | NotaGen：MIT、時期－作曲家－編制提示、24GB 微調（IJCAI 2025） | [GitHub](https://github.com/ElectricAlexis/NotaGen)、[arXiv 2502.18008](https://arxiv.org/abs/2502.18008) | 2025-02 | 2026-11-19 | 高（權重授權未載明） |
| [20] | MIDI-GPT 屬性控制、Open RAIL-M、4×V100 2–3 天（預印本） | [arXiv 2501.17011](https://arxiv.org/html/2501.17011v2) | 2025-02 | 2026-11-19 | 高 |
| [21] | MidiTok 3.1.0（MIT） | [PyPI](https://pypi.org/project/miditok/) | 2026-09 | 2026-11-19 | 高 |
| [22] | ABC-Eval：LLM 小節層級失敗（預印本） | [arXiv 2509.23350](https://arxiv.org/html/2509.23350v1) | 2025-09 | 2026-11-19 | 高（單一來源） |
| [23] | 在 ABC 上微調 LLM 的取捨；FMD 不可靠（預印本） | [arXiv 2601.22764](https://arxiv.org/html/2601.22764v1) | 2026-01 | 2026-11-19 | 中 |
| [24] | MuseBarControl：直接微調不服從控制（預印本） | [arXiv 2407.04331](https://arxiv.org/abs/2407.04331) | 2024-07 | 2026-11-19 | 中低 |
| [25] | SSIMuse 多聲部抄襲檢測（預印本） | [arXiv 2509.13658](https://arxiv.org/abs/2509.13658) | 2025-09 | 2026-11-19 | 中 |
| [26] | 短動機導致抄襲（NeurIPS 2025 workshop） | [NeurIPS](https://neurips.cc/virtual/2025/123788) | 2025 | 2026-11-19 | 中 |
| [27] | PDMX CC BY 4.0、no_license_conflict 222,856 首 | [Zenodo 15571083](https://zenodo.org/records/15571083) | 2025-06 | 2026-11-19 | 高 |
| [28] | MAESTRO v3 規模與 CC BY-NC-SA | [Magenta](https://magenta.tensorflow.org/datasets/maestro) | 即時頁面 | 2026-11-19 | 高 |
| [29] | Lakh MIDI 規模與 CC BY 4.0 | [Colin Raffel](https://colinraffel.com/projects/lmd/) | 即時頁面 | 2026-11-19 | 高／推論為中 |
| [30] | Aria-MIDI CC BY-NC-SA＋免責聲明 | [GitHub aria-midi](https://github.com/loubbrad/aria-midi) | 2025-06 | 2026-11-19 | 中高 |
| [31] | ASAP 規模與 CC BY-NC-SA | [GitHub asap-dataset](https://github.com/fosfrancesco/asap-dataset) | 即時頁面 | 2026-11-19 | 高 |
| [32] | Opencpop CC BY-NC-ND 4.0（官方頁面） | [Opencpop](https://wenet-e2e.github.io/opencpop/liscense/) | 2022 | 2026-11-19 | 高 |
| [33] | M4Singer CC BY-NC-SA＋賠償條款 | [GitHub](https://github.com/M4Singer/M4Singer/blob/master/dataset_license.md) | — | 2026-11-19 | 高 |
| [34] | Saraga CC BY-NC-SA | [Zenodo 4301737](https://zenodo.org/records/4301737) | 2018-05 | 2026-11-19 | 中 |
| [35] | CompMusic 京劇各紀錄授權 | [Zenodo 1285647 等](https://zenodo.org/records/1285647) | 2017–2024 | 2026-11-19 | 中 |
| [36] | SymbTr 約 3,000 首、CC BY-NC-SA | [GitHub MTG/symbtr](https://github.com/MTG/symbtr) | 2016 | 2026-11-19 | 中 |
| [37] | 歌仔戲人聲＋歌詞資料（ISMIR 2025 LBD） | [arXiv 2601.00299](https://arxiv.org/abs/2601.00299v1) | 2026-01 | 2026-11-19 | 高（存在）／低（取得） |
| [38] | FT-GAN（AAAI 2024）：程式碼無授權；GOAT CC BY-NC-SA 需申請 | [GitHub](https://github.com/zhengmidon/Gezi-Opera-Synthesis)、[專案頁](https://zhengmidon.github.io/FTGAN.github.io/) | 2024-02 | 2026-11-19 | 高 |
| [39] | openvpi/DiffSinger Apache-2.0 | [GitHub](https://github.com/openvpi/DiffSinger) | 即時頁面 | 2026-11-19 | 高 |
| [40] | GEMA 對 OpenAI 一審判決 | [Taylor Wessing](https://www.taylorwessing.com/de/insights-and-events/insights/2025/11/gema-v-openai)、[GEMA](https://www.gema.de/en/w/landmark-ruling-gema-against-openai) | 2025-11 | 2026-11-19 | 中高 |
| [41] | OpenAI 案上訴中；GEMA 對 Suno 判決 | [Reed Smith](https://www.reedsmith.com/our-insights/blogs/viewpoints/102nfis/gema-notches-a-second-transatlantic-ai-copyright-win-in-germany/) | 2026-07 | 2026-11-19 | 中（單一來源） |
| [42] | UMG／WMG 與 Udio、Suno 和解 | [MBW](https://www.musicbusinessworldwide.com/universal-music-settles-udio-lawsuit-strikes-deal-for-licensed-ai-music-platform)、[Bloomberg Law](https://news.bloomberglaw.com/ip-law/warner-music-settles-lawsuit-with-ai-music-startup-suno) | 2025-10/11 | 2026-11-19 | 中高 |
| [43] | MIDI 2.0 逐音音高 | [MIDI Association](https://midi.org/the-state-of-midi-2-0-high-resolution-performance-and-the-rise-of-profiles-update-feb-2026) | 2026-02 | 2026-11-19 | 中 |
| [44] | MusicXML 四分之一音、小數 alter | [W3C 郵件列表](https://lists.w3.org/Archives/Public/public-music-notation-contrib/2016Jul/0007.html) | 2016 / 2020 | 2026-11-19 | 中 |
| [45] | 微分音匯出遺失（Dorico／OpenMusic） | [Steinberg 論壇](https://forums.steinberg.net/t/microtonality-and-musicxml/863784) | — | 2026-11-19 | 中低 |
| [46] | MEI accid／accid.ges | [MEI v5](https://music-encoding.org/guidelines/v5/elements/accid.html) | v5 | 2026-11-19 | 中 |
| [47] | 工尺譜光學辨譜，39 張圖評估 | [EURASIP JASMP 2014](https://asmp-eurasipjournals.springeropen.com/articles/10.1186/1687-4722-2014-7) | 2014 | 2026-11-19 | 中 |
| [48] | 簡譜光學辨譜（預印本） | [arXiv 2512.14758](https://arxiv.org/abs/2512.14758v1) | 2025-12 | 2026-11-19 | 中 |
| [49] | 京劇清唱資料，f0＋音符（ISMIR 2017） | [ISMIR 2017](https://archives.ismir.net/ismir2017/paper/000119.pdf)、[Zenodo 832736](https://zenodo.org/records/832736) | 2017 | 2026-11-19 | 中高 |
| [50] | GaMaDHaNi 音高曲線階層生成（ISMIR 2024） | [arXiv 2408.12658](https://arxiv.org/abs/2408.12658v2) | 2024-08 | 2026-11-19 | 高 |
| [51] | VQ-VAE 曲線符號化（韓國傳統音樂，預印本） | [arXiv 2608.10979](https://arxiv.org/pdf/2608.10979) | 2026-08 | 2026-11-19 | 中 |
| [52] | 計算民族音樂學：離散化是文化慣例 | [ICMC-SMC 2014](https://speech.di.uoa.gr/ICMC-SMC-2014/images/VOL_1/0069.pdf) | 2014 | 2026-11-19 | 中 |
| [53] | MDT：馬可夫鏈出題、3 個難度因子、R² 0.869（Sci Rep） | [PMC5472621](https://pmc.ncbi.nlm.nih.gov/articles/PMC5472621) | 2017-06 | 2026-11-19 | 高 |
| [54] | CA-BAT（IRT＋CAT＋AIG） | [PMC6097996](https://pmc.ncbi.nlm.nih.gov/articles/PMC6097996) | 2018 | 2026-11-19 | 中 |
| [55] | Mistuning Perception Test（BRM 2019） | [Springer](https://link.springer.com/article/10.3758/s13428-019-01225-1) | 2019 | 2026-11-19 | 中 |
| [56] | PROMS（PLoS One 2012） | [PMC3532219](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3532219/) | 2012 | 2026-11-19 | 中 |
| [57] | AI 音樂刺激研究以標示偏誤為主 | [PMC12194076](https://pmc.ncbi.nlm.nih.gov/articles/PMC12194076/)、[arXiv 2512.02785](https://arxiv.org/html/2512.02785) | 2025–2026 | 2026-11-19 | 中 |
| [58] | Jacoby 等人 15 國節奏先驗（NHB 2024） | [MPI 新聞稿](https://www.aesthetics.mpg.de/en/research/former-departments-and-research-groups/research-group-computational-auditory-perception/news/news-rg-cap-detail/article/rhythm-diversity-different-cultures-prefer-different-beat-patterns-1.html) | 2024-03 | 2026-11-19 | 中 |
| [59] | 生成音樂評估綜述（ACM CSUR） | [arXiv 2506.05104](https://arxiv.org/abs/2506.05104) | 2025-06 | 2026-11-19 | 高 |
| [60] | IS／FAD 與主觀評分相關弱 | [arXiv 2108.01576](https://arxiv.org/pdf/2108.01576) | 2021-08 | 2026-11-19 | 中 |
| [61] | VAE 旋律作為相似度刺激（ICMPC 2023） | [KAIST](https://mac.kaist.ac.kr/pubs/kim-icmpc2023.pdf) | 2023 | 2026-11-19 | 中 |
| [62] | UAB 學士論文：AI 音樂刺激資料集 | [UAB](https://ddd.uab.cat/record/317789/?ln=en) | 2025 | 2026-11-19 | 低 |
| [63] | 依目標難度生成視奏譜（預印本） | [arXiv 2509.16913](https://arxiv.org/pdf/2509.16913) | 2025-09 | 2026-11-19 | 中 |
| [64] | VocalNotes（ISMIR 2023 LBD），日本民謠 9 段 | [ISMIR 2023](https://ismir2023program.ismir.net/lbd_354.html) | 2023-11 | 2026-11-19 | 中 |
| [65] | 中研院台灣原住民祭儀歌舞檔案 | [中研院民族所](https://www.ethno.sinica.edu.tw/page2-1_e.php) | — | 2026-11-19 | 高 |
| [68] | MET 中國樣本驗證 | [PMC10849222](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10849222/) | 2024 | 2026-11-19 | 中 |
| [70] | YuE2：合一模型優於分段串接；顯式樂譜規劃有幫助（預印本，只讀摘要） | [arXiv 2609.33757](https://arxiv.org/abs/2609.33757) | 2026-09 | 2026-11-19 | 中 |
| [71] | DiffSynth-Music：音訊轉接器控制節拍和音高（預印本） | [HF Papers 2609.12774](https://huggingface.co/papers/2609.12774.md) | 2026-09 | 2026-11-19 | 中 |
| [72] | JASCO：音訊模型直接吃和弦和旋律條件 | [arXiv 2406.10970](https://arxiv.org/abs/2406.10970) | 2024-06 | 2026-11-19 | 中 |
| [73] | MazzikaAI：用提示詞引導音訊模型增加 maqam 微分音（預印本） | [arXiv 2608.10360](https://arxiv.org/abs/2608.10360) | 2026-08 | 2026-11-19 | 中低 |
| [74] | Music for All：非西方資料只占 5.7%（NAACL 2025） | [arXiv 2502.07328](https://arxiv.org/abs/2502.07328) | 2025-02 | 2026-11-19 | 中 |
| [75] | 採譜研究預設西方五線譜的問題（DSH 2022） | [SOAS](https://library.soas.ac.uk/Record/eprints-35331) | 2022 | 2026-11-19 | 中 |
| [76] | 京劇歌聲只用音符合成（DurIAN，預印本） | [arXiv 1912.12010](https://arxiv.org/abs/1912.12010) | 2019-12 | 2026-11-19 | 中低 |
| [77] | 找不到支援 MIDI 2.0 逐音音高的合成器清單 | [KVR Audio 論壇](https://www.kvraudio.com/forum/viewtopic.php?p=8160672) | — | 2026-11-19 | 低 |
| [78] | OpenMusic 8 匯入時忽略四分之一音記號 | [IRCAM 論壇](https://discussion.forum.ircam.fr/t/musicxml-import-still-ignores-quarter-tone-accidentals-in-openmusic-8-0/183126) | — | 2026-11-19 | 低 |
| [79] | 主觀評估沒有標準化程序（預印本，搜尋摘要） | [arXiv 2308.13736](https://arxiv.org/pdf/2308.13736) | 2023-08 | 2026-11-19 | 中 |
| [80] | 過擬合的模型聽起來更連貫、驗證損失卻變差（預印本） | [arXiv 2511.07268](https://arxiv.org/pdf/2511.07268v2) | 2025-11 | 2026-11-19 | 中低 |
| [81] | Aria-MIDI 從網路音訊轉錄（ICLR 2025） | [arXiv 2504.15071](https://arxiv.org/abs/2504.15071) | 2025-04 | 2026-11-19 | 高 |
| [82] | 民族音樂學：五線譜帶有歐洲的類別預設 | [JRMA, Notating Deconstruction](https://resolve.cambridge.org/core/journals/journal-of-the-royal-musical-association/article/notating-deconstruction-what-can-ethnomusicological-transcription-learn-from-the-notational-practices-of-contemporary-composers/77AAD1B39327C096678012C3FF848403) | 未確認 | 2026-11-19 | 中 |
| [83] | VocalNotes：「音符」是否適合許多傳統的基本單位 | [IFTAWM journal](https://journal.iftawm.org/?p=4218) | 未確認 | 2026-11-19 | 低 |
