# 原型：旋律 → AMT 伴奏 → 表情鋼琴演奏

用完即丟的研究原型。輸入一段單旋律 MIDI，用 AMT（Anticipatory Music Transformer）生成伴奏，合併成一軌鋼琴，再交給兩個表情演奏模型（SyMuPe/PianoFlow、Pianist Transformer），每個版本都輸出 MIDI 和 WAV。計畫見 `docs/plan-melody-to-performance-prototype.md` 與 `docs/prototype-plan-melody-to-performance/`。

只供研究、非商用。

## 安裝

需要：macOS（在 M3 Pro 18GB 測過）、[uv](https://docs.astral.sh/uv/)、git、FluidSynth（`brew install fluid-synth`）。

```bash
cd prototype/melody-to-performance
./setup.sh
```

`setup.sh` 可以重複執行，會做這些事：

- `uv sync`：主流程用的環境（pretty_midi、psutil）。
- 三個互相獨立的 uv 環境（相依版本互相衝突，所以分開）：
  - `envs/amt`：Python 3.10，`transformers==4.29.2`，`models/anticipation`（git clone）。
  - `envs/pianoflow`：Python 3.11，`symupe` 加上手動補的 `numba`、`scipy`（SyMuPe issue #9）。
  - `envs/pianist`：Python 3.11，`torch==2.7.1`，`models/PianistTransformer`（git clone，權重下載到 `models/PianistTransformer/models/sft/`）。
- Hugging Face 權重快取在 `models/hf-cache/`。
- 產生三段範例旋律（`examples/make_examples.py`）。

`models/`、`envs/`、`output/`、`*.wav`、`*.sf2` 都在 `.gitignore` 裡，不會進 git。

### 音色庫（SoundFont）

不另外下載，直接用你電腦上已有的檔案，只用路徑指過去、不複製進 repo：

- 預設：`/Users/hsin-ruilin/dev/music_gen/magenta/sound_library/GeneralUser-GS.sf2`（32MB 的 GM 音色庫，鋼琴是 program 0）。
- 備選：`"/Applications/MuseScore 4.app/Contents/Resources/sound/MS Basic.sf3"`。
- 換音色庫：`uv run run.py ... --soundfont /路徑/檔案.sf2`，或設環境變數 `SOUNDFONT=/路徑/檔案.sf2`。

FluidSynth 只讀 SF2／SF3。想用自己的取樣音源聽，把輸出的 `.mid` 拖進 Logic、GarageBand 或 Vienna Synchron Player，指定鋼琴音色即可。

## 使用

```bash
# 1. 煙霧測試：三個模型各跑一小段（CPU，再 MPS），結果寫到 output/smoke-test.md
uv run smoke_test.py

# 2. 跑一段旋律
uv run run.py examples/ode_to_joy.mid
uv run run.py examples/greensleeves.mid
uv run run.py examples/jasmine.mid

# 選項
uv run run.py 你的旋律.mid --device mps          # 三個模型都用 MPS（預設 cpu）
uv run run.py 你的旋律.mid --soundfont 某.sf3     # 換音色庫
uv run run.py 你的旋律.mid --seed 1              # 換一個隨機種子，聽另一個版本
```

輸入：單旋律 MIDI，最好已經量化、20–30 秒左右（AMT 沒有 KV 快取，越長越慢；AMT 最多處理約 100 秒）。如果檔案裡有好幾軌，會拿第一個非鼓的軌當旋律，並在 run-notes 裡寫警告。

### 試聽頁面

```bash
uv run make_player.py      # 產生 output/player.html，並把輸入旋律轉成 input.wav
open output/player.html
```

每段旋律可以聽輸入和 6 個版本，旁邊列出長度、AMT 用了哪些樂器、音符保留數。按「盲聽模式」會打亂三個版本、藏起名稱，適合拿給同事或老師猜哪個是直接播放的。頁面用相對路徑讀音檔，要留在 `output/` 裡才放得出聲音。

各步驟也能單獨跑：

| 步驟 | 指令 |
|---|---|
| 伴奏 | `envs/amt/bin/python steps/amt_accompany.py 旋律.mid 伴奏.mid --prompt none\|chords` |
| 合併成一軌鋼琴 | `uv run steps/merge_piano.py 旋律.mid 伴奏.mid plain.mid` |
| PianoFlow | `envs/pianoflow/bin/python steps/render_pianoflow.py plain.mid out.mid` |
| Pianist Transformer | `envs/pianist/bin/python steps/render_pianist.py plain.mid out.mid` |
| 轉 WAV | `steps/to_wav.sh in.mid out.wav [soundfont]` |
| 音符忠實度 | `uv run steps/fidelity.py plain.mid out.mid` |

## 輸出

```
output/
  smoke-test.md            煙霧測試：每個模型 × CPU/MPS 能不能跑、時間、記憶體、錯誤摘要
  smoke/                   煙霧測試的中間檔和 log
  <旋律名>/
    noprompt/              AMT 不給開頭
      accompaniment.mid    AMT 生成的伴奏（原始，可能有多種樂器）
      plain.mid / .wav     ① 旋律＋伴奏，直接播放（量化好的一軌鋼琴，也是演奏模型的輸入）
      pianoflow.mid / .wav ② PianoFlow 演奏版
      pianist.mid / .wav   ③ Pianist Transformer 演奏版
    chords/                AMT 先給幾小節柱式和弦當開頭，其餘同上
    run-notes.md           時間、記憶體、失敗原因、音符忠實度、AMT 用了哪些樂器
    run-notes.json         同上，機器可讀
    logs/                  每個步驟的完整輸出
```

### 兩種伴奏開頭

- `noprompt`：不給開頭，AMT 從第 0 秒開始，只看旋律生成伴奏。
- `chords`：先放約 2 小節的柱式和弦（I–IV–V–I，依旋律的調；短於 4 秒時延長到 3 小節），AMT 從和弦結束的地方接著生成到旋律結尾。調性優先讀 MIDI 的調號，沒有就用 Krumhansl–Kessler 估計。旋律放在 program 1（明亮鋼琴），和弦放在 program 0（平台鋼琴），讓 AMT 分得出哪個是條件旋律。

### 只用鋼琴

`steps/amt_accompany.py` 在生成時把鋼琴（program 0）以外所有樂器的機率設成零：包住上游 `anticipation.sample.instr_logits`，它在取樣每個音符 token 時會被呼叫。這樣兩種開頭的伴奏都是 AMT 用「寫鋼琴」的思路寫的，比較時只差在開頭。想讓 AMT 自由挑樂器，加 `--all-instruments`。上游作者提醒過「強制單一樂器」可能出現重複音或零長度音符，聽的時候留意。

### 合併（`plain.mid`）

AMT 生成時已限定只寫鋼琴（見下方「只用鋼琴」）；合併時仍保險地把伴奏改成鋼琴（program 0）、丟掉鼓的音；AMT 以 10 毫秒為單位的時間對齊到旋律的十六分音符格子（演奏模型要吃量化的譜）；和旋律同時同音的重複音丟掉。

### 音符忠實度

`steps/fidelity.py` 把 `plain.mid` 和演奏版各自依起音時間排成音高序列（50 毫秒內的音視為同一個和弦、依音高排序），再對齊，算出保留／改變／漏掉／多出的音數。另外附一個不看順序的計數：如果音高的集合完全相同，序列上的差異只是表情時間造成的順序變動，不是改了音。

## 授權

| 東西 | 授權 |
|---|---|
| AMT 程式碼與權重 `stanford-crfm/music-medium-800k` | Apache-2.0 |
| SyMuPe 程式碼（`symupe`） | Apache-2.0 |
| PianoFlow-base 權重 | CC BY-NC-SA 4.0（非商用、相同方式分享） |
| Pianist Transformer 程式碼與權重 | Apache-2.0 |
| GeneralUser GS（S. Christian Collins） | GeneralUser GS License：免費使用，可用於音樂製作 |
| MS Basic.sf3（MuseScore） | MIT |
| 範例旋律 | 公有領域：《快樂頌》（貝多芬，1824）、Greensleeves（16 世紀英格蘭民謠）、〈茉莉花〉（18 世紀中國民歌），本專案自行打譜 |

PianoFlow 權重是非商用授權，所以 PianoFlow 版的輸出也只能非商用。

## 已知限制

- 參數全用預設值，沒有調。每次結果都是隨機取樣，`--seed` 可以換。
- AMT 很慢（沒有 KV 快取），伴奏可能有多種樂器（已一律改成鋼琴），沒給開頭時品質可能比較差。
- 合併時把伴奏量化到十六分音符，AMT 原本的細微時間會消失；三連音之類的節奏會被拉到格子上。
- `chords` 的和弦進行固定是 I–IV–V–I，不看旋律實際的和聲，開頭可能和旋律打架。
- PianoFlow 在 MPS 上要一個小修補（`steps/render_pianoflow.py` 的 `mps_float64_shim`，MPS 不支援 float64），其他都沒改上游程式碼。
- Pianist Transformer 輸出的是上游 `inference.sh` 的「可編輯」版（用速度曲線表現時間變化）；若上游的 `map_midi` 失敗，改寫原始的絕對時間演奏版，並在 log 裡警告。
- PianoFlow 輸出的是套用延音踏板後的版本（`perf_midi_sus`），MIDI 裡沒有踏板控制訊息；Pianist Transformer 的 MIDI 有踏板訊息。
- 上游 `generate()` 會丟掉 50 毫秒（`DELTA` 個時間單位）之前的條件音（`ops.clip(controls, DELTA, ...)`），所以旋律在第 0 秒的音不會傳給 AMT 當條件；`noprompt` 版受影響最明顯，因為那一刻沒有任何開頭可依靠（兩個版本最後的 `plain.mid` 仍保留這個音）。
- 沒有採譜、沒有 MusicXML、沒有介面、沒有微調、沒有測試（只有煙霧測試）。

## 第一次跑的觀察（2026-11-21，CPU）

詳細數字見 `output/smoke-test.md` 和各段的 `output/<旋律名>/run-notes.md`。

- 三個模型在 CPU 和 MPS 上都跑得動（PianoFlow 的 MPS 要上面提到的小修補）。兩個演奏模型很小，MPS 沒有比較快；AMT 在 MPS 上每個音比較快，但每次取樣的音數不同，不好直接比。預設用 CPU。
- AMT 最慢：一段 23–29 秒的旋律，每種開頭要 1–4 分鐘，記憶體約 3.4GB。
- 兩個演奏模型都沒有改音：六個版本的音高計數和輸入完全一樣。PianoFlow 的序列差異只是和弦內順序變了。
- PianoFlow 會自己決定速度，完全不看譜上的速度（同一份譜設 60 或 240 bpm，輸出一樣長）。《快樂頌》被它彈得比原速慢 1.6–3.6 倍；〈茉莉花〉反而稍快。Pianist Transformer 通常比原速快 10–30%。
- AMT 不給開頭時常挑非鋼琴樂器（大鍵琴、吉他、直笛、小提琴、電貝斯），《快樂頌》的伴奏很稀（29 秒只有 35 個音）；給柱式和弦開頭時都留在鋼琴上，伴奏也比較密。
- **改成只用鋼琴後重跑（2026-11-21）**：六份伴奏全是鋼琴，沒有零長度音符。柱式和弦開頭版和之前完全一樣（本來就只用鋼琴，同一個隨機種子）。不給開頭版變了：《快樂頌》更稀（32 秒 28 個音，其中 46% 是同一個音高），綠袖子 57 個音、茉莉花 128 個音，最常出現的音高各占約三成，有重複單一音的傾向。
