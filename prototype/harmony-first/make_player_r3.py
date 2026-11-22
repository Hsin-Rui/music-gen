"""Build the round-3 listening page: new (gate-then-rank) pick vs old (z-sum) pick.

    uv run make_player_r3.py         # then open output/round3/player.html

Reads output/round3/summary.json (written by round3.py) and writes output/round3/player.html:
- per melody: the input melody and, per chart, the melody + block-chord prompt (../<m>/harmony/<s>.wav);
- per cell (chart x model): the new pick's plain audio; for AMT and AccoMontage also the round-2 pick
  (../<m>/<s>/<model>/plain.wav) with a "新舊相同" badge when they are the same candidate; a candidate
  table with gates, the three axis ranks, the Borda sum, ★ new pick and ○ old pick.
- 盲聽一: the four models of each chart shuffled, names and tables hidden.
- 盲聽二: A/B of new vs old pick in random order, only for cells where they differ.
- 揭曉 reveals names. One audio plays at a time. The page uses relative paths, so it stays in output/round3/.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
R3 = OUT / "round3"

TITLES = {"ode_to_joy": "快樂頌（貝多芬）", "greensleeves": "綠袖子 Greensleeves", "jasmine": "茉莉花"}
SOURCE_LABELS = {"llm": "Claude 的和弦", "gemini": "Gemini 的和弦"}
MODEL_LABELS = {"amt": "AMT + 和弦條件", "accomontage": "AccoMontage", "claude": "Claude 寫伴奏", "gemini": "Gemini 寫伴奏"}
GATE_LABELS = {"enough_notes": "彈得夠多", "melody_copy": "不抄旋律", "prompt_copy": "不照抄提示",
               "chord_fit": "守住和弦", "playable": "彈得到"}
AXIS_LABELS = {"prompt_sim": "不像提示", "rules": "不違規", "bass_ok": "低音正確"}


def collect(summary):
    melodies = {}
    for c in summary["cells"]:
        m, s, md = c["melody"], c["source"], c["model"]
        mel = melodies.setdefault(m, {"name": m, "title": TITLES.get(m, m),
                                      "input": f"../{m}/input.wav" if (OUT / m / "input.wav").exists() else None,
                                      "charts": {}})
        ch = mel["charts"].setdefault(s, {"key": s, "label": SOURCE_LABELS.get(s, s),
                                          "prompt": f"../{m}/harmony/{s}.wav" if (OUT / m / "harmony" / f"{s}.wav").exists() else None,
                                          "cells": []})
        cell = {"model": md, "label": MODEL_LABELS.get(md, md), "missing": c["missing"], "reason": c.get("reason"),
                "selectable": c["selectable"]}
        if not c["missing"]:
            new = R3 / m / s / md / "plain.wav"
            old = OUT / m / s / md / "plain.wav"
            cell.update(chosen=c["chosen"], old=c["old_chosen"], same=c["same_as_old"], fallback=c["fallback"],
                        passers=c["passers"], n=c["n"], selected=c["selected"],
                        new_src=f"{m}/{s}/{md}/plain.wav" if new.exists() else None,
                        old_src=f"../{m}/{s}/{md}/plain.wav" if c["selectable"] and old.exists() else None,
                        cands=[{"k": x["k"], "notes": x.get("notes"), "failed": x.get("failed", []), "error": x.get("error"),
                                "ranks": x.get("ranks"), "borda": x.get("borda"),
                                "vals": {a: x.get(a) for a in AXIS_LABELS},
                                "doc": x.get("prompt_doc"), "copy": x.get("copy"), "cm": x.get("chord_match")}
                               for x in c["candidates"]])
        ch["cells"].append(cell)
    order = [m for m in summary.get("melodies", []) if m in melodies] + [m for m in melodies if m not in summary.get("melodies", [])]
    return [{**melodies[m], "charts": list(melodies[m]["charts"].values())} for m in order]


PAGE = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第三輪挑選試聽</title>
<style>
:root { --bg:#f7f6f3; --card:#fff; --text:#1d1d1f; --muted:#6b6b70; --line:#e3e1dc; --accent:#3b5bdb;
  --warn:#b54708; --ok:#2b7a3d; --chip:#eef1fb; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#151517; --card:#1f1f23; --text:#ececee; --muted:#9a9aa2; --line:#33333a; --accent:#8da2fb;
    --warn:#f5a46b; --ok:#7fd18f; --chip:#272b3a; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:15px/1.6 -apple-system, "PingFang TC", "Noto Sans TC", sans-serif; }
main { max-width:1100px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:22px; margin:0 0 4px; }
h2 { font-size:19px; margin:0 0 8px; }
h3 { font-size:16px; margin:20px 0 6px; }
.sub { color:var(--muted); margin:0 0 16px; }
.bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:24px;
  position:sticky; top:0; background:var(--bg); padding:8px 0; z-index:2; }
button { font:inherit; padding:6px 12px; border-radius:8px; border:1px solid var(--line);
  background:var(--card); color:var(--text); cursor:pointer; }
button.on { background:var(--accent); color:#fff; border-color:var(--accent); }
section.melody { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:24px; }
.row { display:grid; grid-template-columns:200px 1fr; gap:4px 12px; align-items:center; padding:6px 0; border-top:1px solid var(--line); }
.row .label { font-weight:600; }
audio { width:100%; height:34px; }
.cells { display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:10px; }
.cell { border:1px solid var(--line); border-radius:10px; padding:10px; min-width:0; }
.cell .title { font-weight:600; margin-bottom:4px; }
.v { font-size:13px; margin-top:6px; color:var(--muted); }
.badge { display:inline-block; font-size:12px; border-radius:6px; padding:0 6px; margin-left:6px; background:var(--chip); }
.badge.same { color:var(--ok); } .badge.diff { color:var(--accent); } .badge.fb { color:var(--warn); }
.err { color:var(--warn); font-size:13px; }
.meta { color:var(--muted); font-size:13px; }
.tablewrap { overflow-x:auto; }
table { border-collapse:collapse; margin-top:6px; font-size:12.5px; width:100%; }
th, td { border-bottom:1px solid var(--line); padding:2px 5px; text-align:right; white-space:nowrap; }
th:nth-child(3), td:nth-child(3) { text-align:left; white-space:normal; }
tr.new td { font-weight:600; color:var(--accent); }
.fail { color:var(--warn); } .pass { color:var(--ok); }
details.explain { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 16px; margin-bottom:20px; }
details.explain summary { font-weight:600; cursor:pointer; }
details.explain li { margin-bottom:6px; }
@media (max-width:720px) { .row { grid-template-columns:1fr; } .cells { grid-template-columns:1fr; } }
</style>
</head>
<body>
<main>
<h1>原型 02 第三輪：新挑選指標試聽</h1>
<p class="sub">同一批第二輪候選，只換挑選方法。新指標：先過五道門檻，再比三項名次，名次加總最小的勝出。只有「直接播放」版本。一次只會播放一個音檔。</p>
<details class="explain">
<summary>怎麼看這一頁？</summary>
<ul>
<li><b>提示音檔</b>：旋律＋柱式和弦，就是 AMT 收到的和弦提示。新指標懲罰「照抄這個提示」。</li>
<li><b>門檻</b>：彈得夠多（音數 ≥ 小節數、空拍 ≤ 25%）、不抄旋律（&lt; 0.5）、不照抄提示（抄襲程度 &lt; 0.5）、守住和弦（逐拍吻合 ≥ 0.7、調外音 ≤ 5%）、彈得到（兩手各 ≤ 5 音、跨度 ≤ 14 半音）。</li>
<li><b>名次</b>（只在通過門檻的候選之間排，1 = 最好）：不像提示（越不像越好）、不違規（平行五八度＋刺耳重疊，越少越好）、低音正確（換和弦時最低音是和弦低音，越多越好）。</li>
<li>★ = 新指標挑的，○ = 第二輪舊指標挑的。「退回」= 沒有任何一份過全部門檻，只好在擋掉最少的幾份裡排。</li>
<li>AMT、AccoMontage 每格 8 份，新指標實際替它們挑選。Claude、Gemini 寫伴奏每格只有一份：只計算、顯示，不參與挑選。</li>
<li><b>盲聽一</b>：每份和弦的四個模型打亂、隱藏名稱。<b>盲聽二</b>：新舊挑得不同的格子，A／B 順序隨機，猜哪個是新指標挑的。</li>
</ul>
</details>
<div class="bar">
  <button id="m-normal" class="on">一般</button>
  <button id="m-blind1">盲聽一：模型</button>
  <button id="m-blind2">盲聽二：新 vs 舊</button>
  <button id="reveal" hidden>揭曉答案</button>
  <span class="meta" id="hint"></span>
</div>
<div id="app"></div>
</main>
<script>
const DATA = __DATA__;
const GATES = __GATES__, AXES = __AXES__;
let mode = "normal", revealed = false, order = {};

function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function el(tag, cls, text) { const e = document.createElement(tag);
  if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
function audio(src) { if (!src) return el("div", "err", "沒有音檔");
  const a = document.createElement("audio"); a.controls = true; a.preload = "none"; a.src = src; return a; }
function fmt(x, d) { return x == null ? "–" : Number(x).toFixed(d); }
function row(label, src) { const r = el("div", "row"); r.append(el("div", "label", label), audio(src)); return r; }

function table(c) {
  const wrap = el("div", "tablewrap"), tb = el("table"), hr = el("tr");
  ["份", "音數", "門檻", ...Object.values(AXES), "加總", ""].forEach(h => hr.append(el("th", null, h)));
  tb.append(hr);
  for (const x of c.cands) {
    const tr = el("tr", x.k === c.chosen && c.selected ? "new" : null);
    tr.append(el("td", null, String(x.k + 1)), el("td", null, x.notes == null ? "–" : String(x.notes)));
    const g = el("td", x.failed.length ? "fail" : "pass");
    g.textContent = x.error ? "✗ 讀不到檔案" : x.failed.length ? "✗ " + x.failed.map(k => GATES[k]).join("、") : "✓";
    tr.append(g);
    const digits = {prompt_sim: 2, rules: 3, bass_ok: 2};
    for (const a of Object.keys(AXES)) {
      const r = x.ranks ? x.ranks[a] : null;
      tr.append(el("td", null, (r == null ? "–" : r) + `（${fmt(x.vals[a], digits[a])}）`));
    }
    tr.append(el("td", null, x.borda == null ? "–" : String(x.borda)));
    const mark = (c.selected && x.k === c.chosen ? "★" : "") + (c.selectable && x.k === c.old ? "○" : "");
    tr.append(el("td", null, mark));
    tb.append(tr);
  }
  wrap.append(tb); return wrap;
}

function cellBox(c, title, showInfo) {
  const box = el("div", "cell"), t = el("div", "title", title);
  if (showInfo && !c.missing && c.selectable) {
    t.append(el("span", "badge " + (c.same ? "same" : "diff"), c.same ? "新舊相同" : "新舊不同"));
    if (c.fallback) t.append(el("span", "badge fb", "退回：沒有一份過全部門檻"));
  }
  if (showInfo && !c.missing && !c.selectable) t.append(el("span", "badge", "只有一份，不挑選"));
  box.append(t);
  if (c.missing) { box.append(el("div", "err", "缺：" + c.reason)); return box; }
  box.append(el("div", "v", showInfo && c.selectable ? `★ 新指標挑的：第 ${c.chosen + 1} 份` : "直接播放"));
  box.append(audio(c.new_src));
  if (showInfo && c.selectable) {
    box.append(el("div", "v", c.old == null ? "○ 舊指標沒有挑出" : `○ 舊指標挑的：第 ${c.old + 1} 份` + (c.same ? "（同一份）" : "")));
    box.append(audio(c.old_src));
  }
  if (showInfo) {
    box.append(el("div", "meta", c.selectable ? `過全部門檻：${c.passers}/${c.n} 份` :
      (c.passers ? "這一份過了全部門檻" : "這一份沒過：" + c.cands[0].failed.map(k => GATES[k]).join("、"))));
    box.append(table(c));
  }
  return box;
}

function render() {
  const app = document.getElementById("app"); app.innerHTML = "";
  const show = mode === "normal" || revealed;
  for (const m of DATA) {
    const s = el("section", "melody");
    s.append(el("h2", null, m.title));
    s.append(row("輸入旋律", m.input));
    for (const ch of m.charts) {
      s.append(el("h3", null, ch.label));
      s.append(row("提示：旋律＋柱式和弦", ch.prompt));
      const box = el("div", "cells");
      if (mode === "normal") {
        ch.cells.forEach(c => box.append(cellBox(c, c.label, true)));
      } else if (mode === "blind1") {
        const list = order[m.name + "/" + ch.key] ||= shuffle(ch.cells.filter(c => !c.missing));
        list.forEach((c, i) => box.append(cellBox(c, revealed ? `伴奏 ${i + 1} = ${c.label}` : `伴奏 ${i + 1}`, revealed)));
      } else {
        const diff = ch.cells.filter(c => !c.missing && c.selectable && !c.same && c.old_src);
        if (!diff.length) box.append(el("div", "meta", "這份和弦的格子，新舊挑的都一樣，沒有可比的。"));
        for (const c of diff) {
          const key = m.name + "/" + ch.key + "/" + c.model;
          const ab = order[key] ||= shuffle(["new", "old"]);
          const b = el("div", "cell");
          b.append(el("div", "title", revealed ? c.label : "一格伴奏（模型隱藏）"));
          ab.forEach((w, i) => {
            const letter = "AB"[i];
            b.append(el("div", "v", revealed ? `${letter} = ${w === "new" ? "★ 新指標" : "○ 舊指標"}（第 ${(w === "new" ? c.chosen : c.old) + 1} 份）` : letter));
            b.append(audio(w === "new" ? c.new_src : c.old_src));
          });
          box.append(b);
        }
      }
      s.append(box);
    }
    app.append(s);
  }
  document.getElementById("reveal").hidden = mode === "normal";
  document.getElementById("hint").textContent = mode === "blind1" ? "四個模型已打亂、隱藏名稱與分數。先記下你喜歡哪幾個，再按揭曉。"
    : mode === "blind2" ? "每格 A／B 一個是新指標挑的、一個是舊的，順序隨機。先記下你喜歡哪個，再按揭曉。" : "";
}

function setMode(m) {
  mode = m; revealed = false; order = {};
  for (const id of ["normal", "blind1", "blind2"]) document.getElementById("m-" + id).classList.toggle("on", id === m);
  render();
}
document.getElementById("m-normal").onclick = () => setMode("normal");
document.getElementById("m-blind1").onclick = () => setMode("blind1");
document.getElementById("m-blind2").onclick = () => setMode("blind2");
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
    p = R3 / "summary.json"
    if not p.exists():
        sys.exit("output/round3/summary.json not found — run round3.py first")
    data = collect(json.loads(p.read_text()))
    page = R3 / "player.html"
    page.write_text(PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
                    .replace("__GATES__", json.dumps(GATE_LABELS, ensure_ascii=False))
                    .replace("__AXES__", json.dumps(AXIS_LABELS, ensure_ascii=False)), encoding="utf-8")
    n = sum(1 for m in data for ch in m["charts"] for c in ch["cells"] if not c["missing"])
    missing_audio = [src for m in data for ch in m["charts"] for src in [ch["prompt"]] + [
        x for c in ch["cells"] if not c["missing"] for x in ([c["new_src"]] + ([c["old_src"]] if c["selectable"] else []))]
        if src is None]
    print(f"wrote {page} ({len(data)} melodies, {n} cells{', MISSING AUDIO: ' + str(len(missing_audio)) if missing_audio else ''})")


if __name__ == "__main__":
    main()
