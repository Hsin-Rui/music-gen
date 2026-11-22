# 知識庫

音樂生成專案一路累積的文獻、模型、資料集和實驗。每一筆一個 Markdown 檔，放在 git 裡。

## 怎麼用

- **找東西：** 看下面的目錄，或在 `kb/` 裡搜尋關鍵字（`grep -ri 伴奏 kb/`）。
- **新增：** 每次研究或做原型後，把新的文獻、模型、資料集各加一個檔（格式照同資料夾現有的檔），再執行 `python3 kb/build_index.py` 重建本頁。
- **出處：** 每筆都連回它來自哪份研究報告或實驗。研究報告（`docs/research-*`）是原始證據，這裡是整理後的索引。R1＝技術路線圖、R2＝原型模型查證、R3＝配和聲與伴奏模型、R4＝原型 02 候選模型補查、R5＝伴奏挑選指標。
- **信心：** 文獻的信心欄位沿用研究報告的判定；「尚未精讀」表示只用了報告查證過的那句話。

## 實驗

- [原型 01：旋律 → AMT 伴奏 → 表情鋼琴演奏](experiments/prototype-01-melody-to-performance.md)：結論 `conditional`，2026-11-21

## 模型

| 模型 | 做什麼 | 我們的使用狀態 |
|---|---|---|
| [AccoMontage](models/accomontage.md) | 伴奏（旋律＋和弦 → 鋼琴） | 原型 02 候選 |
| [AccoMontage2](models/accomontage2.md) | 配和聲＋伴奏（只給旋律） | 原型 02 候選 |
| [AccoMontage-3（Structured Arrangement）](models/accomontage3.md) | 伴奏＋多軌編曲 | 未試 |
| [ACE-Step 1.5](models/ace-step.md) | 音訊生成 | 未試 |
| [Anticipatory Music Transformer (AMT)](models/amt.md) | 符號生成：補寫、給旋律生伴奏 | 已用於 prototype-01 |
| [Aria (EleutherAI)](models/aria.md) | 鋼琴續寫、MIDI 嵌入 | 已排除 |
| [asigalov61 Melody-Harmonizer-Transformer](models/asigalov61-harmonizer.md) | 配和聲（每個音配一個和弦） | 不建議 |
| [AutoHarmonizer](models/autoharmonizer.md) | 配和聲（神經網路，可調和聲密度） | 未試 |
| [BART 配和聲與 B* 限制解碼（NeuraLLMuse）](models/bart-harmonizer.md) | 配和聲（旋律 → 和弦） | 觀察中（沒有權重） |
| [Basic Pitch (Spotify)](models/basic-pitch.md) | 採譜：音訊 → MIDI | 未試 |
| [Claude 寫伴奏（本專案）](models/claude-accompaniment.md) | 伴奏（Claude 逐小節規劃織體 → 規則展開） | 原型 02 使用中 |
| [CoCoMulla](models/cocomulla.md) | 音訊生成（MusicGen 加和弦／旋律控制） | 不適用（輸出音訊） |
| [Compose & Embellish](models/compose-embellish.md) | 伴奏（旋律＋和弦 → 鋼琴演奏） | 原型 02 使用中（第三輪加入） |
| [CPFG-Net](models/cpfg-net.md) | 配和聲（可控制緊張度） | 未試 |
| [D3PIA](models/d3pia.md) | 伴奏（離散擴散） | 觀察中（沒找到程式碼） |
| [DExter](models/dexter.md) | 表情演奏（擴散模型） | 未試 |
| [DiffSinger (openvpi)](models/diffsinger.md) | 歌聲合成 | 未試 |
| [EMO_Harmonizer](models/emo-harmonizer.md) | 依情緒配和聲 | 未試 |
| [FGG（Fine-Grained Guidance）](models/fgg.md) | 伴奏（擴散，取樣時擋掉調外音） | 未試 |
| [FIGARO](models/figaro.md) | 描述控制的多軌生成 | 未試 |
| [Florence Price 伴奏生成器](models/florence-price-accompaniment.md) | 伴奏（只吃旋律 → 藝術歌曲風格鋼琴） | 觀察中 |
| [Function Alignment（music-x-lab）](models/function-alignment.md) | 旋律→和弦、和弦→旋律等多任務 | 觀察中 |
| [GETMusic](models/getmusic.md) | 多軌符號生成 | 不考慮 |
| [HarmonyRL](models/harmonyrl.md) | 配和聲（旋律 → 和弦） | R4 建議加入原型 02 |
| [Impro-Visor](models/impro-visor.md) | 和弦表 → 爵士風格伴奏 | 未試 |
| [MAJEPPA](models/majeppa.md) | 表情演奏（Aria 的 LoRA 微調） | 備案（未試） |
| [meagtan/harmonizer](models/meagtan-harmonizer.md) | 配和聲（動態貝氏網路＋Viterbi） | 未試 |
| [MelodyT5](models/melodyt5.md) | 配和聲（ABC 旋律 → 帶和弦的 ABC），也做其他旋律任務 | 原型 02 候選 |
| [MIDI-GPT](models/midi-gpt.md) | 多軌補寫＋屬性控制 | 未試 |
| [MIDI-LLM](models/midi-llm.md) | 文字 → MIDI（LLM） | 未試 |
| [MidiTok（工具）](models/miditok.md) | MIDI ↔ 模型符號（REMI、CPWord 等） | 未用 |
| [MuPT](models/mupt.md) | ABC 記譜續寫（非配和聲） | 不適用 |
| [MuScriptor](models/muscriptor.md) | 採譜：多樂器音訊 → MIDI | 未試 |
| [MusicGen](models/musicgen.md) | 音訊生成 | 未試 |
| [NeuraLLMuse 配和聲系列（SplitEncoder、GridMLMelHarm 等）](models/neurallmuse-harmonizers.md) | 配和聲（旋律 → 和弦） | 觀察中（沒有權重） |
| [NotaGen](models/notagen.md) | 符號生成：時期－作曲家－編制提示 → ABC | 未試 |
| [Pianist Transformer](models/pianist-transformer.md) | 表情演奏：樂譜 MIDI → 演奏 MIDI | 已用於 prototype-01 |
| [SyMuPe / PianoFlow](models/pianoflow.md) | 表情演奏：樂譜 MIDI → 演奏 MIDI | 已用於 prototype-01 |
| [Polyffusion](models/polyffusion.md) | 伴奏（擴散模型，和弦／織體條件、旋律補寫） | 原型 02 候選 |
| [RL-Chord](models/rl-chord.md) | 配和聲（CLSTM＋強化學習） | 觀察中（沒有程式碼） |
| [ScorePerformer](models/scoreperformer.md) | 表情演奏 | 未試 |
| [單編碼器遮罩式配和聲（FF curriculum）](models/single-encoder-harmonizer.md) | 配和聲 | 未試 |
| [STHarm／VTHarm／rVTHarm](models/stharm.md) | 配和聲 | 未試 |
| [Text2midi](models/text2midi.md) | 文字 → MIDI | 未試 |
| [Transkun](models/transkun.md) | 鋼琴採譜 | 未試 |
| [VeeHarmGen](models/veeharmgen.md) | 配和聲（規則／統計查表） | R4 建議當基準線 |
| [VirtuosoNet](models/virtuosonet.md) | 表情演奏 | 未試 |
| [Whole-Song Hierarchical Generation](models/whole-song-gen.md) | 整首歌階層生成 | 未試 |
| [YourMT3+](models/yourmt3.md) | 採譜：多樂器音訊 → MIDI | 未試 |
| [結構化鋼琴伴奏（規劃＋檢索，Zang 等人）](models/zang-2026-piano-accompaniment.md) | 伴奏（樂譜 → 鋼琴） | 觀察中（沒有程式碼） |

## 資料集

| 資料集 | 類型 | 授權 | 文化／風格 |
|---|---|---|---|
| [Aria-MIDI](datasets/aria-midi.md) | 鋼琴 MIDI（從網路音訊轉錄） | CC BY-NC-SA＋免責聲明 | 鋼琴，多風格 |
| [ASAP](datasets/asap.md) | 樂譜對演奏（對齊） | CC BY-NC-SA | 西方古典鋼琴 |
| [中國合唱資料集](datasets/chinese-chorales.md) | 合唱樂譜＋和弦標記 | 未讀 | 中國合唱 |
| [Chord Melody Dataset（CMD）](datasets/chord-melody-dataset.md) | 爵士旋律＋和弦 | MIT（原曲可能有版權） | 爵士標準曲 |
| [Chordonomicon](datasets/chordonomicon.md) | 和弦進行（無旋律） | CC BY-NC 4.0 | 西方流行／搖滾 |
| [CompMusic 京劇](datasets/compmusic-jingju.md) | 音訊＋音高曲線＋音符標註 | 各紀錄不同：CC BY-NC-ND／CC BY-NC／CC BY | 京劇 |
| [Essen 中國民歌調式標記](datasets/essen-chinese-diao.md) | 調式標記（不是和弦） | CC BY 4.0，限制存取 | 中國民歌 |
| [Essen 民謠資料庫](datasets/essen-folksong.md) | 符號旋律 | 未查證 | 歐洲民謠（MDT 用愛爾蘭民謠） |
| [Florence Price 藝術歌曲資料集](datasets/florence-price-art-songs.md) | 藝術歌曲樂譜（MusicXML／MIDI／PDF） | 未標（論文 CC BY 4.0） | 美國藝術歌曲（Florence Price） |
| [歌仔戲人聲＋歌詞（中研院團隊）](datasets/gezi-asas.md) | 人聲片段＋歌詞 | 發布狀態不明 | 歌仔戲 |
| [GOAT 歌仔戲（FT-GAN）](datasets/gezi-goat.md) | 歌聲資料 | CC BY-NC-SA，需申請，附賠償條款 | 歌仔戲 |
| [Hooktheory（Sheet Sage 版）](datasets/hooktheory.md) | 旋律＋和聲標記（對齊音訊，不含音訊） | CC BY-NC-SA 3.0 | 西方流行 |
| [Lakh MIDI](datasets/lakh-midi.md) | 多樂器 MIDI | 資料集 CC BY 4.0，但內容是流行歌轉譜，底層版權未授權（推論） | 西方流行為主 |
| [M4Singer](datasets/m4singer.md) | 中文多風格歌聲 | CC BY-NC-SA＋賠償條款 | 中文 |
| [MAESTRO v3](datasets/maestro-v3.md) | 鋼琴 MIDI＋音訊 | CC BY-NC-SA | 西方古典鋼琴 |
| [MelodyHub](datasets/melodyhub.md) | ABC 旋律（多任務） | 未讀 | 民謠、西方為主 |
| [NeuraLLMuse 配和聲資料集](datasets/neurallmuse-melodic-harmonization.md) | 兩聲部 MIDI（旋律＋和聲） | Apache-2.0 | 未查 |
| [Opencpop](datasets/opencpop.md) | 中文歌聲＋樂譜 | CC BY-NC-ND 4.0；商用需洽談 | 中文流行歌聲 |
| [OpenGufeng](datasets/opengufeng.md) | 旋律＋三和弦 | MIT | 中國風流行（古風） |
| [OpenScore Lieder Corpus](datasets/openscore-lieder.md) | 藝術歌曲樂譜（人聲＋鋼琴，MusicXML／MuseScore） | CC0（專案方說明；HF 衍生版標 CC BY-SA 4.0） | 19 世紀西方藝術歌曲（Schubert、Schumann、Brahms 等） |
| [PDMX](datasets/pdmx.md) | 符號（MusicXML 樂譜） | CC BY 4.0（12.29% 授權資訊互相矛盾） | 西方為主 |
| [Pop1K7](datasets/pop1k7.md) | 流行鋼琴演奏 MIDI（含樂譜標記） | 未查 | 流行鋼琴 |
| [POP909](datasets/pop909.md) | 旋律＋副旋律＋鋼琴伴奏＋和弦／調／拍 | MIT（repo 標籤） | 流行（華語未確認） |
| [prototype-01 範例旋律（自製）](datasets/prototype-examples.md) | 單旋律 MIDI | 公有領域曲目，本專案自行打譜 | 西方古典、英格蘭民謠、中國民歌 |
| [Saraga](datasets/saraga.md) | 印度古典音訊＋標註 | CC BY-NC-SA | 印度（Carnatic／Hindustani） |
| [Schubert Winterreise Dataset](datasets/schubert-winterreise.md) | 多模態：樂譜、錄音與分析標註 | 開放（Zenodo，DOI 10.5281/zenodo.10839767；授權細節未查） | 西方藝術歌曲（Schubert） |
| [中研院台灣原住民祭儀歌舞檔案](datasets/sinica-indigenous.md) | 影音 | 頁面沒有寫重用條款 | 台灣原住民 |
| [Slakh2100](datasets/slakh2100.md) | 多樂器合成音訊＋MIDI | CC BY 4.0（未在 R4 查證） | 流行多軌 |
| [SymbTr](datasets/symbtr.md) | 土耳其 makam 符號樂譜 | CC BY-NC-SA | 土耳其古典 |
| [VocalNotes](datasets/vocalnotes.md) | 日本民謠錄音 | CC BY-NC-SA，需申請；作者要求不重新彙整公開 | 日本民謠 |
| [When-in-Rome](datasets/when-in-rome.md) | 羅馬數字分析＋樂譜 | 新內容 CC BY-SA 4.0 | 西方古典 |

## 文獻

| 文獻（本專案取用的說法） | 發表 | 信心 |
|---|---|---|
| [AI 音樂刺激研究以標示偏誤為主](literature/ai-music-stimuli-labelling-2025.md) | 2025–2026 | 中 |
| [PIG 鋼琴指法資料集與統計指法模型（Nakamura 等人）](literature/arxiv-1904.10237.md) | 2019 | 高 |
| [Bach Doodle／Coconet](literature/arxiv-1907.06637.md) | 2019 | 低 |
| [京劇歌聲只用音符合成（DurIAN，預印本）](literature/arxiv-1912.12010.md) | 2019-12 | 中低 |
| [和聲一致性指標彙整；沒有「多生幾份再挑」的伴奏論文](literature/arxiv-2001.02360.md) | 2020–2026 | 中 |
| [Bach or Mock?（ICML 2020 工作坊）](literature/arxiv-2006.13329.md) | 2020-06 | 中 |
| [Jazz Transformer（Wu & Yang，ISMIR 2020）](literature/arxiv-2008.01307.md) | 2020-08 | 高 |
| [MusPy（ISMIR 2020）](literature/arxiv-2008.01951.md) | 2020 | 高 |
| [IS／FAD 與主觀評分相關弱](literature/arxiv-2108.01576.md) | 2021-08 | 中 |
| [AccoMontage（ISMIR 2021）](literature/arxiv-2108.11213.md) | 2021 | 高 |
| [FIGARO（ICLR 2023）](literature/arxiv-2201.10936.md) | 2023 | 高 |
| [AccoMontage2 聽覺測試：和聲性顯著優於 BLSTM](literature/arxiv-2209.00353.md) | 2022 | 中 |
| [Compose & Embellish：先寫樂譜再潤飾成鋼琴演奏](literature/arxiv-2209.08212.md) | 2022 / ICASSP 2023 | 高 |
| [AMT 補寫與伴奏能力（TMLR）](literature/arxiv-2306.08620.md) | 2023-06 | 高 |
| [主觀評估沒有標準化程序（預印本，搜尋摘要）](literature/arxiv-2308.13736.md) | 2023-08 | 中 |
| [AccoMontage-3：樂譜 → 鋼琴 → 多軌，聽測勝過 AMT](literature/arxiv-2310.16334.md) | 2024-11 | 高 |
| [CoCoMulla：MusicGen 加和弦控制，輸出音訊](literature/arxiv-2310.17162.md) | 2023 / ISMIR 2024 | 高 |
| [ChatMusician：配和聲用編輯距離評，不是評和聲品質](literature/arxiv-2402.16153.md) | 2024-02 | 高 |
| [MuPT：ABC 預訓練模型，只會續寫](literature/arxiv-2404.06393.md) | 2024 | 中 |
| [Transkun 鋼琴採譜（ISMIR 2024）](literature/arxiv-2404.09466.md) | 2024 | 中 |
| [Whole-Song 階層式生成（ICLR 2024）](literature/arxiv-2405.09901.md) | 2024-05 | 高 |
| [JASCO：音訊模型直接吃和弦和旋律條件](literature/arxiv-2406.10970.md) | 2024-06 | 中 |
| [MelodyT5：ABC 配和聲、七和弦與轉位、1.13 億參數、訓練資料、指標比較](literature/arxiv-2407.02277.md) | 2024-07 | 高 |
| [MuseBarControl：直接微調不服從控制（預印本）](literature/arxiv-2407.04331.md) | 2024-07 | 中低 |
| [YourMT3+（IEEE MLSP 2024）](literature/arxiv-2407.04822.md) | 2024-07 | 中 |
| [語言模型配和聲：專家給 GPT-4 5.5–6.5 分](literature/arxiv-2407.21531.md) | 2024-07 | 高 |
| [RubricNet 鋼琴難度](literature/arxiv-2408.00473.md) | 2024-08 | 高 |
| [GaMaDHaNi 音高曲線階層生成（ISMIR 2024）](literature/arxiv-2408.12658.md) | 2024-08 | 高 |
| [GPT-4o 音程好、辨認和弦與音階弱](literature/arxiv-2409.05521.md) | 2024-09 | 低 |
| [鋼琴 MIDI→MusicXML（ISMIR 2024）；音訊→樂譜（IJCAI 2024）](literature/arxiv-2410.00210.md) | 2024 | 中 |
| [FGG：取樣時擋掉調外音；沒看到授權](literature/arxiv-2410.08435.md) | 2025-06 | 高／中 |
| [MIDI-GPT 屬性控制、Open RAIL-M、4×V100 2–3 天（預印本）](literature/arxiv-2501.17011.md) | 2025-02 | 高 |
| [Music for All：非西方資料只占 5.7%（NAACL 2025）](literature/arxiv-2502.07328.md) | 2025-02 | 中 |
| [RenderBox 多樂器演奏（預印本）](literature/arxiv-2502.07711.md) | 2025-02 | 低 |
| [樂理考試各編碼格式比較](literature/arxiv-2503.22853.md) | 2025-03 | 中 |
| [STAGE：音訊分軌生成](literature/arxiv-2504.05690.md) | 2025 | 高 |
| [Aria-MIDI 從網路音訊轉錄（ICLR 2025）](literature/arxiv-2504.15071.md) | 2025-04 | 高 |
| [SMART](literature/arxiv-2504.16839.md) | 2025-04 | 中 |
| [生成音樂評估綜述（ACM CSUR）](literature/arxiv-2506.05104.md) | 2025-06 | 高 |
| [Function Alignment：一個基礎模型加多個音樂轉接器](literature/arxiv-2506.15548.md) | 2025-06 | 中 |
| [Florence Price 藝術歌曲資料集與伴奏生成](literature/arxiv-2506.23130.md) | 2025-06 | 中 |
| [Aria 論文評估續寫與分類](literature/arxiv-2506.23869.md) | 2025-06 | 中 |
| [生成音樂評量指標綜述（Kader & Karmaker，預印本）](literature/arxiv-2509.00051.md) | 2025-08 | 中 |
| [SSIMuse 多聲部抄襲檢測（預印本）](literature/arxiv-2509.13658.md) | 2025-09 | 中 |
| [依目標難度生成視奏譜（預印本）](literature/arxiv-2509.16913.md) | 2025-09 | 中 |
| [ABC-Eval：LLM 小節層級失敗（預印本）](literature/arxiv-2509.23350.md) | 2025-09 | 高（單一來源） |
| [SyMuPe/PianoFlow 能力與授權](literature/arxiv-2511.03425.md) | 2025-11 / 2026-05 | 高（授權）／中（能力） |
| [MIDI-LLM，Llama 3.2 授權](literature/arxiv-2511.03942.md) | 2025-11 | 高 |
| [過擬合的模型聽起來更連貫、驗證損失卻變差（預印本）](literature/arxiv-2511.07268.md) | 2025-11 | 中低 |
| [CPFG-Net：可控制緊張度的配和聲](literature/arxiv-2511.14600.md) | 2025-11 | 中 |
| [MSU-Bench（ACL 2026）](literature/arxiv-2511.20697.md) | 2025-11 | 中 |
| [B* 限制解碼](literature/arxiv-2512.07627.md) | 2025-12 | 中 |
| [簡譜光學辨譜（預印本）](literature/arxiv-2512.14758.md) | 2025-12 | 中 |
| [歌仔戲人聲＋歌詞資料（ISMIR 2025 LBD）](literature/arxiv-2601.00299.md) | 2026-01 | 高（存在）／低（取得） |
| [單編碼器遮罩式配和聲（Apache-2.0、無權重）](literature/arxiv-2601.16150.md) | 2026-01 | 高 |
| [在 ABC 上微調 LLM 的取捨；FMD 不可靠（預印本）](literature/arxiv-2601.22764.md) | 2026-01 | 中 |
| [ACE-Step 1.5 能力（預印本）](literature/arxiv-2602.00744.md) | 2026-02 | 高 |
| [D3PIA：220 萬參數、POP909 比較表、13 位專家聽覺測試；和弦正確率不等於聽感和諧](literature/arxiv-2602.03523.md) | 2026-02 | 高 |
| [風格規劃＋樂句檢索，以綜合分數挑選](literature/arxiv-2602.15074.md) | 2026-02 | 高 |
| [Academic Text-to-Music 挑戰](literature/arxiv-2605.21538.md) | 2026 | 低 |
| [MuScriptor 架構與評測（預印本，ISMIR 2026 投稿）](literature/arxiv-2607.08168.md) | 2026-08 | 中 |
| [鋼琴編曲論文](literature/arxiv-2608.03050.md) | 2026 | 中 |
| [MazzikaAI：用提示詞引導音訊模型增加 maqam 微分音（預印本）](literature/arxiv-2608.10360.md) | 2026-08 | 中低 |
| [VQ-VAE 曲線符號化（韓國傳統音樂，預印本）](literature/arxiv-2608.10979.md) | 2026-08 | 中 |
| [MAJEPPA 論文，ISMIR 2026](literature/arxiv-2608.11026.md) | 2026-08 | 中 |
| [DiffSynth-Music：音訊轉接器控制節拍和音高（預印本）](literature/arxiv-2609.12774.md) | 2026-09 | 中 |
| [YuE2：合一模型優於分段串接；顯式樂譜規劃有幫助（預印本，只讀摘要）](literature/arxiv-2609.33757.md) | 2026-09 | 中 |
| [前沿語言模型的羅馬數字分析（非正式）](literature/augmented-fifth-2026-llm-harmonic-analysis.md) | 2026-08 | 低 |
| [語言模型在符號輸入接近滿分、音訊下降；LogicLM](literature/carone-2026-llm-music-theory-pmlr.md) | 2026-01 | 中 |
| [中國合唱資料集](literature/chinese-chorales-dataset-2024.md) | 約 2024 | 低 |
| [工尺譜光學辨譜，39 張圖評估](literature/gongche-omr-2014.md) | 2014 | 中 |
| [GrooveToolbox](literature/groovetoolbox-2021.md) | 2021 | 低 |
| [MDT：馬可夫鏈出題、3 個難度因子、R² 0.869（Sci Rep）](literature/harrison-2017-mdt-melodic-discrimination.md) | 2017-06 | 高 |
| [CA-BAT（IRT＋CAT＋AIG）](literature/harrison-2018-ca-bat.md) | 2018 | 中 |
| [Harrison & Pearce（Psychological Review 2020）](literature/harrison-pearce-2020-consonance.md) | 2020 | 高 |
| [Herremans & Chew 張力帶（TENOR 2016）](literature/herremans-chew-2016-tension-ribbons.md) | 2016 | 中 |
| [計算民族音樂學：離散化是文化慣例](literature/icmc-smc-2014-discretisation-culture.md) | 2014 | 中 |
| [VocalNotes：「音符」是否適合許多傳統的基本單位](literature/iftawm-vocalnotes-note-as-unit.md) | 未確認 | 低 |
| [京劇清唱資料，f0＋音符（ISMIR 2017）](literature/ismir-2017-jingju-a-cappella-dataset.md) | 2017 | 中高 |
| [VocalNotes（ISMIR 2023 LBD），日本民謠 9 段](literature/ismir-2023-vocalnotes-japanese-folk.md) | 2023-11 | 中 |
| [Jacoby 等人 15 國節奏先驗（NHB 2024）](literature/jacoby-2024-rhythm-priors-15-countries.md) | 2024-03 | 中 |
| [民族音樂學：五線譜帶有歐洲的類別預設](literature/jrma-notating-deconstruction.md) | 未確認 | 中 |
| [VAE 旋律作為相似度刺激（ICMPC 2023）](literature/kim-2023-vae-similarity-stimuli-icmpc.md) | 2023 | 中 |
| [Mistuning Perception Test（BRM 2019）](literature/larrouy-maestri-2019-mistuning-perception-test.md) | 2019 | 中 |
| [PROMS（PLoS One 2012）](literature/law-2012-proms.md) | 2012 | 中 |
| [McLeod & Steedman（JNMR 2016）HMM 聲部分離，有程式碼，巴赫作品測試](literature/mcleod-steedman-2016-voice-separation.md) | 2016 | 中 |
| [Essen 中國民歌調式標記](literature/meng-2025-essen-chinese-diao.md) | 2025 | 中 |
| [MET 中國樣本驗證](literature/met-2024-chinese-sample.md) | 2024 | 中 |
| [mir_eval 音符比對](literature/mir-eval-transcription.md) | 持續更新 | 高 |
| [MIREX 2024 符號生成：樂譜 → 鋼琴伴奏](literature/mirex-2024-symbolic-generation.md) | 2024 | 中 |
| [music21 VoiceLeadingQuartet](literature/music21-voiceleading.md) | 現行 | 高 |
| [短動機導致抄襲（NeurIPS 2025 workshop）](literature/neurips-2025-memorisation-short-motifs.md) | 2025 | 中 |
| [採譜研究預設西方五線譜的問題（DSH 2022）](literature/soas-2022-transcription-staff-notation-bias.md) | 2022 | 中 |
| [UAB 學士論文：AI 音樂刺激資料集](literature/uab-2025-ai-music-stimuli-thesis.md) | 2025 | 低 |
| [Yang & Lerch（Neural Computing and Applications）](literature/yang-lerch-2020-generative-eval.md) | 2020 | 高 |
| [Yin 等人（SN Computer Science）](literature/yin-2022-originality-report.md) | 2022 | 低 |

## 來源研究

- R1 [技術路線圖研究（2026-11-19）](../docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)
- R2 [原型模型查證（2026-11-21）](../docs/research-prototype-model-check/research-prototype-model-check.md)
- R3 [配和聲與和弦條件伴奏模型（2026-11-21）](../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)
- R4 [原型 02 的候選模型補查（2026-11-21）](../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
- R5 [伴奏挑選指標（2026-11-22）](../docs/research-accompaniment-metrics-r5/research-accompaniment-metrics-r5.md)
