# 原型 02：先定和聲，再生伴奏（配和聲 × 伴奏模型 全部交叉）

用完即丟的研究原型，只供研究、非商用。三個方法替旋律配和弦，每份和弦都交給三個伴奏模型，各生 8 份伴奏，用和聲指標挑最好的一份，再做成「直接播放／PianoFlow／Pianist Transformer」三個版本，最後放進盲聽頁面。

- 原型計畫：`docs/prototype-plan-harmony-first/prototype-plan-harmony-first.md`
- 建置計畫：`docs/plan-harmony-first-prototype.md`
- 沿用原型 01：`prototype/melody-to-performance/`（合併成一軌鋼琴、兩個演奏模型、轉 WAV、音符忠實度、子行程執行器、AMT 包裝程式、範例旋律）。這裡只 import 或呼叫，不複製。

## 安裝

需要：macOS（M3 Pro 18GB 測過）、uv、git、FluidSynth、**原型 01 已經裝好**（`../melody-to-performance/setup.sh`）。

```bash
cd prototype/harmony-first
./setup.sh
```

`setup.sh` 可以重複執行，遇到失敗不會中斷，最後列出缺了什麼：

| 模型 | 環境 | 來源 | 權重／資料 |
|---|---|---|---|
| MelodyT5（配和聲） | `envs/melodyt5`：Python 3.10、新版 torch（CPU）、`transformers==4.30.2`、music21 | `models/melodyt5`（git clone） | HF `sander-wood/melodyt5/weights.pth`（1.4GB，含 optimizer） |
| AccoMontage2（配和聲） | `envs/accomontage2`：Python 3.10、`numpy<2`、`pandas<2.2` | `models/AccoMontage2` | 只用和弦模組；需要的資料檔已經在 repo 裡 |
| AccoMontage（伴奏） | `envs/accomontage`：Python 3.10 | `models/AccoMontage` | Google Drive `checkpoints.zip`（317MB，用 gdown 下載） |
| Polyffusion（伴奏） | `envs/polyffusion`：Python 3.10、`torch==2.1.2` | `models/polyffusion` | **下載不到**（見〈限制〉） |
| AMT（伴奏，加和弦條件） | 沿用原型 01 的 `envs/amt` | 原型 01 的 `models/anticipation` | 原型 01 的 HF 快取 |

`models/`、`envs/`、`output/`、`*.wav`、`*.sf2` 都被 `.gitignore` 擋掉，不會進 git。音色庫沿用原型 01：用路徑指向你的 GeneralUser GS（`SOUNDFONT=` 或 `--soundfont` 可以換）。

## 使用

```bash
uv run smoke_test.py                       # 每個新模型跑前 8 小節 → output/smoke-test.md
uv run run.py ../melody-to-performance/examples/ode_to_joy.mid --amt-device mps
uv run run.py ../melody-to-performance/examples/greensleeves.mid --amt-device mps
uv run run.py ../melody-to-performance/examples/jasmine.mid --amt-device mps
uv run make_player.py && open output/player.html
```

選項：`--samples 8`（每格幾份）、`--seed 0`、`--device cpu|mps`（全部模型）、`--amt-device`（只給 AMT）、`--sources llm,melodyt5,accomontage2`、`--models amt,accomontage,polyffusion`、`--resume`（已有的和弦和完整的 8 份候選不重跑，只重做挑選、演奏、轉檔）。

AMT 在 CPU 上加了和弦條件之後很慢（控制音變多，同時跑三段時一份要 5–8 分鐘），所以完整執行時 AMT 用 MPS（一份約 1 分鐘），其他模型都用 CPU。

## 檔案結構

```
harmonizations/llm/*.json      語言模型配的和弦（原封不動使用）
steps/chart.py                 和弦格式：解析和弦記號、檢查每小節拍數、做柱式和弦、逐拍和弦
steps/harmonize_melodyt5.py    旋律 → MelodyT5 → 和弦 JSON
steps/harmonize_accomontage2.py 旋律 → AccoMontage2 和弦模組 → 和弦 JSON
steps/accomp_amt.py            旋律＋和弦 → AMT（和弦當條件）× N 份
steps/accomp_accomontage.py    旋律＋和弦 → AccoMontage × N 份
steps/accomp_polyffusion.py    旋律＋和弦 → Polyffusion × N 份（沒有權重，沒實際跑過）
steps/metrics.py               CTnCTR、PCS、調外音比例、刺耳重疊比例、總分
steps/paths.py                 路徑、環境、沿用原型 01 的 runner
output/<旋律>/harmony/<來源>.{json,mid,wav}            和弦＋「旋律＋柱式和弦」
output/<旋律>/<來源>/<模型>/candidates/                 8 份候選＋scores.json
output/<旋律>/<來源>/<模型>/{plain,pianoflow,pianist}.{mid,wav}
output/<旋律>/run-notes.md（.json）                     每一格的狀態、分數、缺漏原因
output/player.html                                     試聽頁
```

## 和弦格式

所有來源都轉成語言模型那份的格式：`bars` 是每小節一個 `[和弦, 拍數]` 清單，第 1 小節就是 MIDI 第 1 小節（弱起小節算整小節）。每小節拍數必須等於拍號，小節數必須等於旋律小節數，不合格的來源整份標成失敗。柱式和弦是原位三和弦／七和弦，根音放在 C3–B3；斜線和弦另加低八度的低音。

## 挑選指標（`steps/metrics.py`）

- **CTnCTR**：伴奏的音是不是當下和弦的音（「經過音」接到相鄰的和弦音也算對），越高越好。
- **PCS**：每個十六分音符，旋律和伴奏同時響的每一對音：三度、五度、六度、同音／八度 +1，四度 0，其他 −1，取平均。
- **OOK**：伴奏裡調外音的比例（小調把升高的六、七級也算調內）。
- **刺耳重疊**：旋律和伴奏重疊的時間裡，小二度（小九度）、三全音、大七度所佔的比例。
- **總分** = z(CTnCTR) + z(PCS) − z(OOK) − z(刺耳重疊)，z 分數只在同一格 8 份之內算。音數少於小節數的候選不參與排名；如果 8 份都達不到，才改成所有非空白的候選一起排。

## 和計畫不同、或需要知道的地方

- **AccoMontage2 的和弦模組直接呼叫會當掉**（上游 bug：`Pipeline.__add_textures()` 少一個參數），加了一行本地修補。分句用「每 4 小節一句，A、B、C…」，沒有做樂句分析；不足 4 小節的尾巴補長最後一個音。
- **AccoMontage 和 Polyffusion 也只會 4/4。** 計畫只提到 AccoMontage2，但 AccoMontage 的樂句庫同樣是 4/4。茉莉花（2/4）和綠袖子（3/4）都被重新分成 4 拍一小節：和弦仍然逐拍對齊，但伴奏的強弱拍是 4/4，綠袖子尤其會「拍子不對」。頁面和 run-notes 都有標註。
- **AccoMontage 要有隨機性才會生出 8 份不同的伴奏**：預設 `RANDOMENESS=0` 每次都一樣，所以用它示範筆記本的 0.1。這是唯一動到的參數。
- **AccoMontage 的和弦直接從我們的和弦表給**，不經過它自己的和弦辨識（避免辨識錯誤）。
- **AMT 的和弦條件**：柱式和弦放在 program 48（弦樂合奏）當額外的 `controls`，旋律在 program 1；生成時只允許鋼琴（program 0），輸出只有 AMT 自己寫的音。上游會丟掉前 50 毫秒的控制音，所以第一個和弦和旋律第一個音 AMT 看不到（原型 01 就有的限制）。AMT 偶爾整份不寫任何音，這種候選記為 0 音、不參與排名。
- **MelodyT5** 用上游的預設取樣參數（top_p 0.8、top_k 8、temperature 2.6）。在配和聲模式下它逐小節照抄旋律，只取樣引號裡的和弦。和弦記號對齊到最近的一拍；沒有和弦記號的小節沿用前一個和弦。輸出小節數不對就換下一個種子（最多 3 次）。
- **Polyffusion**：計畫寫 `--inpaint_type=above`，但上游程式和 README 把「替旋律補伴奏」定義為 `below`，包裝程式用 `below`。

## 授權

| 項目 | 程式碼 | 權重／資料 |
|---|---|---|
| MelodyT5 | MIT | MIT（HF 標籤） |
| AccoMontage2 | MIT（`chorderator/__init__.py` 另寫 GPL v3，兩者不一致） | 資料檔隨 repo |
| AccoMontage | MIT | checkpoints（含 POP909 樂句，POP909 為 MIT 標籤） |
| Polyffusion | MIT | 未取得 |
| AMT | Apache-2.0 | Apache-2.0 |
| PianoFlow | Apache-2.0 | CC BY-NC-SA（非商用） |
| Pianist Transformer | Apache-2.0 | Apache-2.0 |

## 限制

- **Polyffusion 沒有跑。** 作者把訓練好的權重和預訓練的和弦編碼器只放在 SharePoint，2026-11-21 所有連結都回「Sorry, you cannot access this document」，GitHub、Hugging Face 都找不到鏡像。環境裝得起來，包裝程式寫好了但沒有實際跑過；取得權重後放到 `models/polyffusion/result/<run>/chkpts/weights.pt`（旁邊要有 `params.yaml`）和 `models/polyffusion/polyffusion/pretrained/chd8bar/weights.pt` 就能重跑。
- 指標只負責初選，和聽感的關係沒有驗證過（R3：和弦正確率最高的模型，聽起來反而比較不和諧）。
- 每格只有 8 份，z 分數不穩定；分數不能跨格比較。
- 三段旋律同時跑，記錄的時間會比單獨跑長。
- 只測過三段範例旋律（都是 2/4、3/4、4/4、量化好、單軌）。
- AccoMontage 上游的 `dp_search` 在只有一個樂句時會當掉（`topk` 未定義），所以至少要 5 小節（4/4）；煙霧測試因此用前 8 小節。
- `--resume` 重用候選時，生成時間和記憶體沿用上一次的紀錄；和聲重用時時間記為 0（MelodyT5、AccoMontage2 各約 5–10 秒，見煙霧測試）。

## 初步觀察（2026-11-21，還沒有人聽過，只看數字）

- **產出：** 16 格伴奏（快樂頌 6、茉莉花 6、綠袖子 4），每格 3 個版本，共 48 個伴奏 WAV，加上 8 個「旋律＋柱式和弦」和 3 個輸入旋律，59 個 WAV 都不是靜音。缺的格子：Polyffusion 全部（沒有權重）、綠袖子的 AccoMontage2（3/4）。
- **MelodyT5 配得很稀疏：** 用上游預設參數時，很多小節沒有和弦記號，只能沿用前一個。快樂頌前 7 小節全是 D；綠袖子第 4–13 小節全是 G；茉莉花後 8 小節全是 F。聽和聲區時應該很容易分辨。
- **AccoMontage2 的和弦偏流行風：** 快樂頌從 Bm 開始（Bm–D–Bm–A…），茉莉花每兩小節（2/4）換一個和弦，用到 Dm、Am。
- **AccoMontage 照和弦走得最緊：** 被選中的伴奏 CTnCTR 0.91–0.99，伴奏密（每段 100–350 個音），但 PCS 比較低（0.43–0.66），刺耳重疊 0.5–5.8%。綠袖子和茉莉花是被重新分成 4/4 的，要特別聽拍子對不對。
- **AMT 加和弦條件之後，常常「不彈」：** 64 份裡有 12 份一個音都沒有，另有 4 份少於小節數（3–9 個音），綠袖子最嚴重（8 份裡有 5–6 份接近空白）。有寫的時候大多跟著和弦（CTnCTR 多在 0.7–0.98），也很少和旋律相撞，但很稀疏（每段約 40–130 個音）。
- **指標的偏誤：** 音越少，PCS 越容易高、刺耳重疊越容易是 0，所以第一版排名會挑到幾乎空白的伴奏（綠袖子 MelodyT5 × AMT 挑到一份只有 4 個音的）。已改成「音數少於小節數的候選不排名」，這是唯一的保護。分數仍然偏好「少而安全」的伴奏，請以耳朵為準。
- **演奏層和原型 01 一樣：** Pianist Transformer 沒有改任何音；PianoFlow 偶爾把幾個音的先後順序調換（音高計數不變），而且常把速度拉慢到 1.5–3 倍。
