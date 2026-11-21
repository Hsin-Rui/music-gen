---
title: "原型計畫：旋律→伴奏→表情演奏"
template: prototype-plan
version: 1.1.0
status: final
created: "2026-11-20"
updated: "2026-11-21"
inputs:
  - docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md（建議 1）
  - docs/brief-music-gen/brief-music-gen.md（暫停中）
  - docs/brainstorm-music-gen-motivations/research-proposal-draft.md
  - docs/research-prototype-model-check/research-prototype-model-check.md
---

# 原型計畫：旋律→伴奏→表情演奏

## Table of Contents

- [目的與目標](#目的與目標)：要做什麼、要回答的問題、放棄的條件
- [時間框](#時間框)：投入多久、時間用完怎麼辦
- [在哪裡做](#在哪裡做)：資料夾、git
- [平台與技術](#平台與技術)：M3 Pro、Python、uv 環境、AMT、PianoFlow、Pianist Transformer、音色庫
- [要比較的選項](#要比較的選項)：SyMuPe/PianoFlow 對 Pianist Transformer、MAJEPPA 備案
- [驗證](#驗證)：誰來聽、怎麼判斷
- [決定](#決定)：已定下的取捨
- [建置](#建置)：自動建置、可以假造或略過的部分、審查深度
- [結果](#結果)：原型跑完後再填

## 目的與目標

**要做的東西：** 一條在本機跑的流程。輸入一段單旋律 MIDI，用 AMT 生成鋼琴伴奏，再把「旋律＋伴奏」交給表情演奏模型，輸出有表情的鋼琴 MIDI 和音檔。這是研究報告建議 1 的研究版原型。

**為什麼現在做：** 先動手累積經驗，回答「單旋律 MIDI 之後的下一步」，再回頭決定 brief 的主角。重點是學會把現成開源模型串起來、摸清楚它們的能耐，不是做出產品。

**這個原型要回答的一個問題：** 把現成的開源模型串起來，在我的 M3 Pro 上，能不能把一段單旋律變成「我願意拿給同事或老師聽」的鋼琴演奏？

**放棄這個方向的條件（動手前先寫下）：** 拿 3 段不同風格的旋律跑完整條流程，如果我覺得沒有一段的伴奏是和旋律搭的，或者演奏聽起來和直接播放 MIDI 沒有明顯差別，就不再走「拼現成模型」這條路，改評估自己訓練或換模型。

## 時間框

依研究報告的估計，2 到 4 週，下班或研究空檔時做。時間到了還沒跑通整條流程，就停下來寫結果，記錄卡在哪一段。

## 在哪裡做

本專案底下新開 `prototype/melody-to-performance/` 資料夾。專案目前不是 git repo，開工前先 `git init` 並提交現有的 docs，讓自動建置有乾淨的工作區。

## 平台與技術

- **機器：** Mac M3 Pro，18GB 統一記憶體。先在本機做，跑不動的部分再考慮 Colab 或租機器。
- **語言與環境：** Python，用 uv 管理環境；PyTorch 用 MPS 加速，不行就退回 CPU。
- **伴奏：** AMT（Anticipatory Music Transformer），用 `controls=` 把旋律當條件生成伴奏。權重 Apache-2.0。中型模型約 3.6 億參數、fp32 約 1.4GB，18GB 記憶體裝得下。注意：
  - 舊版 `transformers==4.29.2` 在 Python 3.12 裝不起來，用獨立的 Python 3.10 環境。
  - 直接呼叫 `generate()`；官方的輔助腳本寫死 `.cuda()`，不要用。
  - 旋律要放在獨立的樂器（MIDI program）上，才能抽出來當條件。
  - 主分支沒有 KV 快取，生成會很慢。
- **表情演奏：** SyMuPe/PianoFlow 或 Pianist Transformer，兩個都能在 CPU 上跑、直接吃樂譜 MIDI。見〈要比較的選項〉。
- **MIDI 處理：** 用 pretty_midi 合併、切分旋律與伴奏軌。AMT 會自己挑樂器，生成後要把所有伴奏軌改成鋼琴、和旋律合併成一軌，再交給演奏模型。
- **轉成音檔：** FluidSynth 加一個免費鋼琴音色庫（SoundFont），輸出 WAV。
- **環境：** 三個模型的相依版本不同（AMT 要舊版 transformers；Pianist Transformer 要 Python 3.11、PyTorch 2.7.1），各用一個獨立的 uv 環境，主流程用子行程呼叫。先跑 CPU，再試 MPS。
- **授權：** 全部在研究或非商用授權下使用，產出不對外發布為商品。

## 要比較的選項

表情演奏有兩個候選，原型兩個都試，決定哪個留下來。依據是 [技術查證報告](../research-prototype-model-check/research-prototype-model-check.md)（2026-11-21）。Aria 已經排除，因為它只能續寫，不能照著給定的譜演奏。

| 選項 | 優點 | 風險 |
|---|---|---|
| **SyMuPe/PianoFlow** | 專為樂譜→表情演奏設計；約 2,400 萬參數，作者說 CPU 上接近即時；沒有只能用 CUDA 的套件 | 權重 CC BY-NC-SA；開源版**沒有**情緒文字引導；安裝要手動補 `numba`；專案新、維護者少 |
| **Pianist Transformer** | README 寫明 CPU 就夠、附 macOS 安裝；輸出踏板；有圖形介面；程式碼和權重都是 Apache-2.0 | 沒有明講會保留原本的音符；1.35 億參數，比 PianoFlow 大 |

**備案：** MAJEPPA（Aria 的照譜演奏微調版），只在兩個都不合用時到 Colab 試，因為它是為 CUDA 寫的。

**先檢查：** 建置的第一步，三個模型各在 CPU 上跑一小段，記下速度，再試 MPS；同時比對輸入和輸出的音高序列，確認演奏模型沒有改動音符。

**怎麼決定：** 能在 M3 Pro 上跑完、而且忠於原本的音符，再比聽起來誰比較像真人。如果兩個都跑不動，就把這一段搬到 Colab 試。

## 驗證

自己聽。每段旋律保留三個版本：①直接播放的 MIDI（旋律＋伴奏），②PianoFlow 版，③Pianist Transformer 版，對照聽。自己覺得好，再挑一兩段給同事、朋友或老師聽，問他們聽不聽得出哪個是機器直接播放的。

## 決定

- 不重用之前的單旋律 MIDI 生成器；輸入旋律直接用現成的 MIDI 檔或手寫幾段。原因：舊的生成器不成熟，這次要學的是串接現成模型。
- 只做鋼琴。原因：表情演奏模型幾乎都只支援鋼琴。
- AMT 伴奏每段旋律試兩種開頭：不給開頭，以及幾小節簡單的柱式和弦。原因：查證發現沒有伴奏開頭時品質可能會掉，這是最可能觸發放棄條件的一段。
- 這次不做採譜、不做樂譜（MusicXML）輸出、不微調任何模型。原因：先把最短的一條路跑通。微調留到下一個原型，等這次結果出來再決定微調哪一段；AMT 也沒有附微調說明。

## 建置

這是原型，你同意之後，用 `bmad-build-auto` 自動建置，盡量少停下來問。

**可以假造或略過：**
- 不需要介面，一個指令列腳本或 Jupyter notebook 就夠。
- 不需要測試覆蓋率，跑得出音檔就算數。
- 某個模型裝不起來時，記錄原因後略過，不硬修。
- 參數（取樣溫度、生成長度）用預設值，不調。

**第一步：** 煙霧測試（見〈要比較的選項〉的「先檢查」），結果寫進輸出資料夾的筆記。

**必須做到：** 一個指令吃一個單旋律 MIDI 檔，對兩種伴奏開頭各吐出〈驗證〉的三個版本，共六組 MIDI 和 WAV，放在同一個輸出資料夾，檔名看得出是哪種開頭、哪個版本。

**審查深度：** `quick`。

## 結果

（原型跑完後，透過更新填寫。）
