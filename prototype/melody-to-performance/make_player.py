"""Build a local listening page for the prototype's outputs.

    uv run make_player.py            # then open output/player.html in a browser

For each melody in output/<name>/ it renders the input melody to output/<name>/input.wav
(if missing) and writes output/player.html, which plays input + the 6 versions and shows
the numbers from run-notes.json. The page references the WAVs by relative path, so it
must stay in output/. A "blind" mode shuffles the three versions of each prompt variant.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pretty_midi

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(ROOT / "steps"))
from runner import DEFAULT_SOUNDFONT  # noqa: E402

TITLES = {"ode_to_joy": "快樂頌（貝多芬）", "greensleeves": "綠袖子 Greensleeves", "jasmine": "茉莉花"}
VARIANTS = {"noprompt": "不給開頭", "chords": "柱式和弦開頭"}
VERSIONS = {"plain": "① 直接播放（旋律＋伴奏）", "pianoflow": "② PianoFlow 演奏", "pianist": "③ Pianist Transformer 演奏"}


def ensure_input_wav(name, soundfont):
    src = EXAMPLES / f"{name}.mid"
    d = OUT / name
    wav = d / "input.wav"
    if src.exists() and not wav.exists():
        shutil.copy(src, d / "input.mid")
        subprocess.run([str(ROOT / "steps" / "to_wav.sh"), str(d / "input.mid"), str(wav), soundfont], check=True)
    return wav.exists()


def program_names(progs):
    return [pretty_midi.program_to_instrument_name(int(p)) for p in progs]


def collect(soundfont):
    melodies = []
    for d in sorted(p for p in OUT.iterdir() if (p / "run-notes.json").exists()):
        name = d.name
        notes = json.loads((d / "run-notes.json").read_text())
        has_input = ensure_input_wav(name, soundfont)
        mel = {"name": name, "title": TITLES.get(name, name),
               "input": f"{name}/input.wav" if has_input else None, "variants": []}
        for v, vlabel in VARIANTS.items():
            amt = notes.get("amt", {}).get(v, {})
            res = amt.get("result") or {}
            info = []
            if res:
                info.append(f"AMT 生成 {res.get('accompaniment_notes')} 個伴奏音，花 {amt.get('sec')} 秒")
                if res.get("instruments") is not None:
                    non_piano = any(int(p) > 7 for p in res["instruments"])
                    info.append("AMT 原本挑的樂器：" + "、".join(program_names(res["instruments"]))
                                + ("（已改成鋼琴）" if non_piano else ""))
                if res.get("chords"):
                    info.append(f"開頭：{res.get('key')}，{res.get('bars')} 小節 " + "–".join(res["chords"]))
            versions = []
            for k, klabel in VERSIONS.items():
                rec = notes.get("versions", {}).get(v, {}).get(k, {})
                wav = d / v / f"{k}.wav"
                meta = []
                w = rec.get("wav")
                if w:
                    meta.append(f"{w['duration_sec']} 秒")
                f = rec.get("fidelity")
                if f:
                    meta.append(f"保留 {f['multiset_kept']}/{f['score_notes']} 個音")
                versions.append({"key": k, "label": klabel,
                                 "src": f"{name}/{v}/{k}.wav" if wav.exists() else None,
                                 "meta": "・".join(meta),
                                 "error": None if rec.get("ok") else rec.get("reason", "沒有產生")})
            mel["variants"].append({"key": v, "label": vlabel, "info": info, "versions": versions})
        melodies.append(mel)
    return melodies


PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>原型試聽</title>
<style>
:root { --bg:#f7f6f3; --card:#fff; --text:#1d1d1f; --muted:#6b6b70; --line:#e3e1dc; --accent:#3b5bdb; --warn:#b54708; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#151517; --card:#1f1f23; --text:#ececee; --muted:#9a9aa2; --line:#33333a; --accent:#8da2fb; --warn:#f5a46b; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:15px/1.6 -apple-system, "PingFang TC", "Noto Sans TC", sans-serif; }
main { max-width:960px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:22px; margin:0 0 4px; }
.sub { color:var(--muted); margin:0 0 16px; }
.bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:24px; }
button { font:inherit; padding:6px 12px; border-radius:8px; border:1px solid var(--line);
  background:var(--card); color:var(--text); cursor:pointer; }
button.on { background:var(--accent); color:#fff; border-color:var(--accent); }
section.melody { background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:16px; margin-bottom:20px; }
h2 { font-size:18px; margin:0 0 12px; }
h3 { font-size:15px; margin:16px 0 4px; }
.info { color:var(--muted); font-size:13px; margin:0 0 8px; padding-left:18px; }
.row { display:grid; grid-template-columns: 220px 1fr; gap:4px 12px; align-items:center;
  padding:8px 0; border-top:1px solid var(--line); }
.row .label { font-weight:600; }
.row .meta { color:var(--muted); font-size:13px; grid-column:2; }
.row .err { color:var(--warn); font-size:13px; }
audio { width:100%; height:36px; }
details.explain { background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:12px 16px; margin-bottom:20px; }
details.explain summary { font-weight:600; cursor:pointer; }
details.explain ol { padding-left:20px; }
details.explain li { margin-bottom:10px; }
.why { color:var(--muted); font-size:13px; }
@media (max-width:600px) { .row { grid-template-columns:1fr; } .row .meta { grid-column:1; } }
</style>
</head>
<body>
<main>
<h1>原型試聽：旋律 → 伴奏 → 表情演奏</h1>
<p class="sub">每段旋律先聽輸入，再比較兩種伴奏開頭下的三個版本。一次只會播放一個音檔。</p>
<details class="explain" open>
<summary>這個原型在做什麼？</summary>
<p><b>要回答的問題：</b>把現成的開源模型串起來，在 Mac 上能不能把一段單旋律變成「願意拿給別人聽」的鋼琴演奏？</p>
<ol>
  <li><b>輸入旋律</b>：一段 20 到 30 秒、已經對齊拍子的單旋律 MIDI。<br>
    <span class="why">意圖：從你之前做過的單旋律 MIDI 接著往下走。</span></li>
  <li><b>生成伴奏：AMT</b>（Anticipatory Music Transformer，Stanford）。它讀過大量多樂器的 MIDI，能「看著」一條旋律，替它寫出其他聲部。<br>
    <span class="why">意圖：讓單旋律變成完整的音樂。每段試兩種開頭：「不給開頭」是 AMT 只看旋律、從零開始寫；「柱式和弦開頭」是先放 2 到 3 小節 I–IV–V–I 和弦，讓它照著接下去。因為查證發現，沒給開頭時伴奏品質可能會掉，兩種都試，才分得出是 AMT 本身不行，還是少了開頭才不行。生成時只允許 AMT 寫鋼琴（其他樂器的機率設成零），讓兩種開頭的比較只差在開頭本身。</span></li>
  <li><b>合併成一軌鋼琴</b>：把 AMT 的鋼琴伴奏對齊到十六分音符的格子，再和旋律合成一軌。<br>
    <span class="why">意圖：下一步的演奏模型只吃「一軌、對齊拍子的鋼琴譜」。這一版就是 ① 直接播放：每個音的力度一樣、時間完全照格子，是用來比較的基準。</span></li>
  <li><b>表情演奏：PianoFlow</b>（SyMuPe，ACM MM 2025）。它讀過大量「樂譜和真人演奏」的配對，學會人怎麼把譜彈出來：哪裡快一點、哪裡重一點、踏板怎麼踩。音符本身不改。<br>
    <span class="why">意圖：測試「看譜彈出表情」這一層能不能補上機器聲的缺點。注意：它會自己決定整體速度，不看譜上寫的速度，所以有些版本會比原曲慢很多。</span></li>
  <li><b>表情演奏：Pianist Transformer</b>（ICML 2026）。做的事和 PianoFlow 一樣，但是是另一套模型和訓練方式，會輸出踏板，速度通常比原曲稍快。<br>
    <span class="why">意圖：和 PianoFlow 對照，決定哪一個留下來。原本的候選 Aria 已經排除，因為它只會接著寫，不會照譜彈。</span></li>
  <li><b>轉成音檔</b>：用 FluidSynth 加上你的 GeneralUser GS 鋼琴音色，把每個版本的 MIDI 轉成 WAV。<br>
    <span class="why">意圖：三個版本用同一個音色，聽到的差別才是演奏造成的，而不是音色。想聽更好的音色，可以把 output 資料夾裡的 .mid 拖進 Logic 或 Vienna。</span></li>
</ol>
<p><b>旁邊的數字：</b>「保留 N/N 個音」是檢查演奏模型有沒有偷改音符，目前兩個模型都完全保留。<br>
<b>放棄條件：</b>如果沒有一段伴奏和旋律搭得起來，或者 ②③ 聽起來和 ① 沒有明顯差別，就不再走「拼現成模型」這條路。</p>
</details>
<div class="bar">
  <button id="blind">盲聽模式：關</button>
  <button id="reveal" hidden>揭曉答案</button>
  <span class="sub" id="hint" style="margin:0"></span>
</div>
<div id="app"></div>
</main>
<script>
const DATA = __DATA__;
let blind = false, revealed = false, order = {};

function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }

function el(tag, cls, text) { const e = document.createElement(tag);
  if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

function row(label, src, meta, error) {
  const r = el("div", "row");
  r.append(el("div", "label", label));
  if (src) { const a = document.createElement("audio"); a.controls = true; a.preload = "none"; a.src = src; r.append(a); }
  else r.append(el("div", "err", error || "沒有音檔"));
  if (meta) r.append(el("div", "meta", meta));
  return r;
}

function render() {
  const app = document.getElementById("app"); app.innerHTML = "";
  for (const m of DATA) {
    const s = el("section", "melody"); s.append(el("h2", null, m.title));
    s.append(row("輸入旋律", m.input, "", "沒有輸入音檔"));
    for (const v of m.variants) {
      s.append(el("h3", null, v.label));
      if (!blind || revealed) { const ul = el("ul", "info"); v.info.forEach(t => ul.append(el("li", null, t))); s.append(ul); }
      const id = m.name + "/" + v.key;
      const list = blind ? (order[id] ||= shuffle(v.versions)) : v.versions;
      list.forEach((x, i) => {
        const letter = "ABC"[i];
        const label = !blind ? x.label : revealed ? `${letter} = ${x.label}` : `版本 ${letter}`;
        s.append(row(label, x.src, (!blind || revealed) ? x.meta : "", x.error));
      });
    }
    app.append(s);
  }
}

document.getElementById("blind").onclick = e => {
  blind = !blind; revealed = false; order = {};
  e.target.textContent = "盲聽模式：" + (blind ? "開" : "關"); e.target.classList.toggle("on", blind);
  document.getElementById("reveal").hidden = !blind;
  document.getElementById("hint").textContent = blind ? "三個版本已打亂、隱藏名稱。先猜哪個是直接播放的，再按揭曉。" : "";
  render();
};
document.getElementById("reveal").onclick = () => { revealed = true; render(); };
document.addEventListener("play", e => {
  document.querySelectorAll("audio").forEach(a => { if (a !== e.target) a.pause(); });
}, true);
render();
</script>
</body>
</html>
"""


def main():
    soundfont = os.environ.get("SOUNDFONT", DEFAULT_SOUNDFONT)
    data = collect(soundfont)
    if not data:
        sys.exit("output/ has no run-notes.json yet — run run.py first")
    page = OUT / "player.html"
    page.write_text(PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print(f"wrote {page} ({len(data)} melodies)")


if __name__ == "__main__":
    main()
