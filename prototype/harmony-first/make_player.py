"""Build the local listening page for prototype 02.

    uv run make_player.py            # then open output/player.html in a browser

Reads output/<melody>/run-notes.json (written by run.py) and writes output/player.html with
1. a harmony section: melody + block chords for every harmony source, and
2. a cross grid: harmony source x accompaniment model, each cell with plain / PianoFlow / Pianist
   and the chosen sample's metric scores.
Blind mode (prototype 01's pattern) shuffles and hides the harmony sources, and turns the grid into
a shuffled list of anonymous accompaniments; "reveal" shows names and scores. One audio plays at a time.
The page references WAVs by relative path, so it must stay in output/.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
sys.path.insert(0, str(ROOT / "steps"))
from paths import MODELS, SOURCES, VERSIONS  # noqa: E402
import chart as C  # noqa: E402

TITLES = {"ode_to_joy": "快樂頌（貝多芬）", "greensleeves": "綠袖子 Greensleeves", "jasmine": "茉莉花"}
VERSION_LABELS = {"plain": "① 直接播放", "pianoflow": "② PianoFlow", "pianist": "③ Pianist"}
ORDER = ["ode_to_joy", "greensleeves", "jasmine"]


def doubling(melody_notes, cand_path):
    """Share of accompaniment notes that start while a melody note of the same pitch class sounds
    (unison or octave doubling of the melody). Reported only; not part of the ranking score."""
    import pretty_midi
    acc = [n for i in pretty_midi.PrettyMIDI(str(cand_path)).instruments if not i.is_drum for n in i.notes]
    if not acc:
        return None
    hit = sum(1 for a in acc if any(m.start - 0.02 <= a.start < m.end and (a.pitch - m.pitch) % 12 == 0
                                    for m in melody_notes))
    return round(hit / len(acc), 3)


def zh_reason(reason, error=None):
    if not reason:
        return "沒有產生"
    r = reason
    if "supports 4/4 only" in r:
        return "AccoMontage2 只支援 4/4，這段是 3/4，所以沒有配"
    if "weights not available" in (error or ""):
        return "Polyffusion 的權重下載不到（作者的 SharePoint 連結拒絕存取），這格沒有產生"
    if "Polyffusion" in r:
        return "Polyffusion 執行失敗，詳見 run-notes"
    if r.startswith("no chart from"):
        return "這份和聲沒有產生，所以這格也沒有"
    return r


def collect():
    melodies = []
    dirs = [OUT / n for n in ORDER if (OUT / n / "run-notes.json").exists()]
    dirs += sorted(d for d in OUT.iterdir() if d.is_dir() and d not in dirs and (d / "run-notes.json").exists())
    for d in dirs:
        notes = json.loads((d / "run-notes.json").read_text())
        name = d.name
        mel_notes = C.melody_meta(d / "input.mid")["notes"]
        mel = {"name": name, "title": TITLES.get(name, name),
               "input": f"{name}/input.wav" if (d / "input.wav").exists() else None,
               "meter": f"{notes['meta']['numerator']}/{notes['meta']['denominator']}",
               "harmony": [], "cells": []}
        for s, h in notes["harmony"].items():
            wav = d / "harmony" / f"{s}.wav"
            mel["harmony"].append({"key": s, "label": SOURCES[s], "ok": h["ok"],
                                   "src": f"{name}/harmony/{s}.wav" if h["ok"] and wav.exists() else None,
                                   "chart": h.get("chart"), "reason": None if h["ok"] else zh_reason(h.get("reason"))})
        for s, row in notes["cells"].items():
            for m, c in row.items():
                cell = {"source": s, "model": m, "source_label": SOURCES[s], "model_label": MODELS[m][2],
                        "ok": bool(c.get("ok")), "reason": None if c.get("ok") else zh_reason(c.get("reason"), c.get("error")),
                        "versions": [], "scores": None, "warn": []}
                if c.get("ok"):
                    best = next(x for x in c["candidates"] if x["k"] == c["chosen"])
                    scores = [x["score"] for x in c["candidates"] if x.get("score") is not None]
                    cell["scores"] = {"chosen": c["chosen"], "n": len(c["candidates"]), "notes": best.get("notes"),
                                      "score": best.get("score"), "ctnctr": best.get("ctnctr"), "pcs": best.get("pcs"),
                                      "ook": best.get("ook"), "dis": best.get("dissonant_overlap"),
                                      "range": [min(scores), max(scores)] if scores else None}
                    cdir = d / s / m / "candidates"
                    cell["cands"] = [{"k": x["k"], "notes": x.get("notes"), "ctnctr": x.get("ctnctr"),
                                      "pcs": x.get("pcs"), "ook": x.get("ook"), "dis": x.get("dissonant_overlap"),
                                      "score": x.get("score"), "ranked": x.get("ranked"),
                                      "dbl": doubling(mel_notes, cdir / x["file"]) if (cdir / x["file"]).exists() else None}
                                     for x in c["candidates"]]
                    cell["scores"]["dbl"] = next(x["dbl"] for x in cell["cands"] if x["k"] == c["chosen"])
                    for v in VERSIONS:
                        vv = c["versions"].get(v, {})
                        wav = d / s / m / f"{v}.wav"
                        w = vv.get("wav")
                        cell["versions"].append({"key": v, "label": VERSION_LABELS[v],
                                                 "src": f"{name}/{s}/{m}/{v}.wav" if wav.exists() else None,
                                                 "meta": f"{w['duration_sec']} 秒" if w else "",
                                                 "error": None if vv.get("ok") else (vv.get("reason") or "沒有產生")})
                    if m in ("accomontage", "polyffusion") and mel["meter"] != "4/4":
                        cell["warn"].append(f"這段是 {mel['meter']}，{MODELS[m][2]} 只會 4/4，所以把拍子重新分成 4 拍一小節；"
                                            "和弦仍然對齊每一拍，但伴奏的強弱拍是 4/4 的。")
                mel["cells"].append(cell)
        melodies.append(mel)
    return melodies


PAGE = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>和聲優先試聽</title>
<style>
:root { --bg:#f7f6f3; --card:#fff; --text:#1d1d1f; --muted:#6b6b70; --line:#e3e1dc; --accent:#3b5bdb;
  --warn:#b54708; --chip:#eef1fb; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#151517; --card:#1f1f23; --text:#ececee; --muted:#9a9aa2; --line:#33333a; --accent:#8da2fb;
    --warn:#f5a46b; --chip:#272b3a; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:15px/1.6 -apple-system, "PingFang TC", "Noto Sans TC", sans-serif; }
main { max-width:1100px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:22px; margin:0 0 4px; }
.sub { color:var(--muted); margin:0 0 16px; }
.bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:24px;
  position:sticky; top:0; background:var(--bg); padding:8px 0; z-index:2; }
button { font:inherit; padding:6px 12px; border-radius:8px; border:1px solid var(--line);
  background:var(--card); color:var(--text); cursor:pointer; }
button.on { background:var(--accent); color:#fff; border-color:var(--accent); }
section.melody { background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:16px; margin-bottom:24px; }
h2 { font-size:19px; margin:0 0 8px; }
h3 { font-size:16px; margin:20px 0 6px; }
.row { display:grid; grid-template-columns: 200px 1fr; gap:4px 12px; align-items:center;
  padding:8px 0; border-top:1px solid var(--line); }
.row .label { font-weight:600; }
.row .meta, .cell .meta { color:var(--muted); font-size:13px; }
.row .meta { grid-column:2; }
.err { color:var(--warn); font-size:13px; }
.chart { font-family: ui-monospace, Menlo, monospace; font-size:12.5px; color:var(--muted);
  grid-column:2; overflow-wrap:anywhere; }
audio { width:100%; height:34px; }
.grid { display:grid; grid-template-columns: 130px repeat(var(--cols), minmax(0,1fr)); gap:8px; }
.grid .head { font-weight:600; font-size:14px; padding:4px; }
.cell { border:1px solid var(--line); border-radius:10px; padding:8px; min-width:0; }
.cell .v { font-size:13px; margin-top:4px; }
.cell .title { font-weight:600; margin-bottom:4px; }
.scores { display:flex; flex-wrap:wrap; gap:4px; margin-top:6px; }
.chip { background:var(--chip); border-radius:6px; padding:1px 6px; font-size:12px; white-space:nowrap; }
.list { display:grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap:8px; }
details.cands { margin-top:6px; font-size:13px; }
details.cands summary { cursor:pointer; color:var(--muted); }
details.cands table, details.explain table { border-collapse:collapse; margin-top:4px; font-size:13px; }
details.cands th, details.cands td, details.explain th, details.explain td { border-bottom:1px solid var(--line); padding:2px 6px; text-align:right; }
details.explain th, details.explain td { text-align:left; vertical-align:top; }
details.cands tr.chosen td { font-weight:600; color:var(--accent); }
.meta.warn { color:var(--warn); }
.formula { font-family:ui-monospace,Menlo,monospace; background:var(--chip); padding:2px 6px; border-radius:6px; }
details.explain { background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:12px 16px; margin-bottom:20px; }
details.explain summary { font-weight:600; cursor:pointer; }
details.explain ol, details.explain ul { padding-left:20px; }
details.explain li { margin-bottom:8px; }
.why { color:var(--muted); font-size:13px; }
@media (max-width:720px) {
  .row { grid-template-columns:1fr; } .row .meta, .chart { grid-column:1; }
  .grid { grid-template-columns:1fr; } .grid .head.col { display:none; }
  .grid .head.rowhead { margin-top:8px; }
}
</style>
</head>
<body>
<main>
<h1>原型 02 試聽：先定和聲，再生伴奏</h1>
<p class="sub">每段旋律分兩區：先聽「旋律＋柱式和弦」比較和聲，再聽「和聲來源 × 伴奏模型」的交叉比較。一次只會播放一個音檔。</p>
<details class="explain" open>
<summary>這個原型在做什麼？</summary>
<p><b>要回答的問題：</b>先把和聲定好，現成的伴奏模型能不能生出「和旋律搭得起來」的鋼琴伴奏？順便看：哪個方法配的和弦最順耳？語言模型配和聲行不行？和聲好壞會不會影響伴奏好壞？</p>
<ol>
  <li><b>配和聲（三個方法）</b>：
    <b>語言模型</b>（Claude 在對話裡讀音符後手配，原封不動使用）、
    <b>MelodyT5</b>（ISMIR 2024，吃 ABC 譜、輸出帶和弦記號的譜）、
    <b>AccoMontage2</b>（ISMIR 2022，從和弦進行庫裡挑，只支援 4/4）。
    三份和弦都轉成同一種格式，再做成「旋律＋柱式和弦」的音檔。<br>
    <span class="why">意圖：單獨聽和聲，不被伴奏的織體干擾。柱式和弦是原位三和弦或七和弦，放在 C3 到 C4 之間。綠袖子是 3/4，AccoMontage2 不支援，所以只有兩份；茉莉花是 2/4，兩小節併成一小節交給它，配完再拆回來。</span></li>
  <li><b>生伴奏（三個模型）</b>：每一份和弦都交給
    <b>AMT 加和弦條件</b>（原型 01 的 AMT，這次把柱式和弦當成額外的「條件」一起給它看，輸出時只留它寫的鋼琴）、
    <b>AccoMontage</b>（ISMIR 2021，從 POP909 流行歌的鋼琴伴奏裡挑樂句，再照我們的和弦改編）、
    <b>Polyffusion</b>（ISMIR 2023，擴散模型）。<br>
    <span class="why">意圖：和弦都用同一份，比較的就只是「誰把和聲彈成伴奏比較好」。Polyffusion 的權重下載不到，所以那一欄是空的。AccoMontage 只會 4/4，綠袖子（3/4）和茉莉花（2/4）的拍子被重新分成 4 拍一小節：和弦仍然對齊每一拍，但伴奏的強弱拍是 4/4 的，綠袖子聽起來可能會「拍子不對」。</span></li>
  <li><b>多生幾份挑最好的</b>：每格生 8 份，用四項和聲指標合成一個分數，挑最高分的一份。<br>
    <span class="why">意圖：模型每次生成都不一樣，挑掉明顯不好的。分數只負責初選，最後由你的耳朵決定。</span></li>
  <li><b>三個版本</b>：① 直接播放（對齊十六分音符、力度一樣）、② PianoFlow 表情演奏、③ Pianist Transformer 表情演奏，沿用原型 01 的設定。<br>
    <span class="why">意圖：比較伴奏時以 ① 為主，因為 PianoFlow 會自己改變速度。</span></li>
</ol>
<p><b>放棄條件：</b>在所有組合裡，如果 3 段旋律沒有任何一段有一份伴奏讓你覺得「和旋律搭得起來」，就不再走「拼現成伴奏模型」這條路。</p>
</details>
<details class="explain">
<summary>指標怎麼算？怎麼挑出「最佳」的那一份？</summary>
<p><b>為什麼要用指標：</b>每一格生 8 份伴奏，你不可能 24 格 × 8 份 = 192 份都聽。指標只負責「初選」：挑掉明顯和旋律打架、亂彈調外音的。最後好不好，由你的耳朵決定。</p>
<p><b>依據：</b>前兩項來自配和聲研究的常用指標（Yeh 等人 2021，JNMR，<a href="https://arxiv.org/abs/2001.02360">arXiv 2001.02360</a>），後兩項是 R3 研究整理的和聲一致性指標（見 <code>docs/research-harmonization-accompaniment/</code> 來源 [12][13]）。原本的論文是拿來評「旋律 vs 和弦」，這裡改成評「伴奏 vs 和弦」和「伴奏 vs 旋律」，所以是<b>借用、改編</b>，不是原封不動。數字都是程式算的（<code>steps/metrics.py</code>），只看伴奏的音，不含旋律本身。</p>
<table>
<tr><th>指標</th><th>要量什麼</th><th>怎麼算</th><th>方向</th></tr>
<tr><td><b>和弦音</b><br>CTnCTR</td><td>伴奏有沒有照著和弦走</td><td>對每個伴奏音，看它響起時和弦表上是什麼和弦。是和弦音就算「和弦音」；不是的話，如果下一個音往上或往下走 1–2 個半音、落到和弦音上（經過音、倚音），算「合理的非和弦音」。<br><span class="formula">(和弦音 + 合理的非和弦音) ÷ (和弦音 + 非和弦音)</span></td><td>0–1，越高越好</td></tr>
<tr><td><b>協和</b><br>PCS</td><td>旋律和伴奏同時響時，聽起來協不協和</td><td>每隔一個十六分音符取樣一次，把當下響著的每個「旋律音 × 伴奏音」配對算音程：同音、三度、五度、六度、八度 = +1；四度 = 0；其他（二度、三全音、七度）= −1。全部平均。</td><td>−1 到 1，越高越好</td></tr>
<tr><td><b>調外音</b><br>OOK</td><td>伴奏有沒有亂彈不在調上的音</td><td>伴奏音裡，音名不在這首的音階上的比例（大調用大音階；小調用自然小音階，再加上升高的第 6、7 音）。</td><td>0–1，越低越好</td></tr>
<tr><td><b>刺耳重疊</b></td><td>旋律和伴奏有沒有同時發出很衝的音程</td><td>旋律音和伴奏音重疊的時間裡，兩音是小二度（或小九度）、三全音、大七度的時間比例。</td><td>0–1，越低越好</td></tr>
</table>
<p><b>怎麼挑最佳：</b></p>
<ol>
<li>同一格的 8 份裡，音符數比小節數還少的（例如 AMT 幾乎什麼都沒寫的），先不參加排名；如果 8 份都這樣，才全部一起排。</li>
<li>每項指標在這一格參加排名的候選裡換成標準分數（z 分數：比平均高幾個標準差）。</li>
<li><span class="formula">總分 = z(和弦音) + z(協和) − z(調外音) − z(刺耳重疊)</span>，四項權重一樣。</li>
<li>總分最高的那份就是「選中」，拿去做 ① ② ③ 三個版本。</li>
</ol>
<p>所以總分<b>只能在同一格裡比較</b>：它的意思是「在這 8 份裡相對比較好」，不能拿快樂頌的 3.2 和茉莉花的 2.0 比。每格下面可以展開看 8 份各自的分數。</p>
<p><b>⚠ 這套指標的已知缺陷（看完結果才發現）：</b>它會獎勵「重複旋律」。AMT 常常把旋律原樣抄一遍，或高八度再彈一次。抄出來的音和旋律是同音或八度，協和一定滿分、刺耳重疊是 0；旋律本身大多是和弦音，和弦音分數也高。所以抄旋律的那份反而拿高分被選中。表上的<b>「旋律重複」</b>是後來加的檢查：伴奏音裡，有多少比例是在旋律正在響的時候彈同一個音名（同音或差八度）。它目前<b>只顯示、沒有算進總分</b>。超過 50% 的格子會標出來。</p>
<p><b>指標量不到的東西：</b>節奏好不好聽、織體是不是像鋼琴伴奏、聲部進行順不順、整體風格對不對。這些只能靠耳朵。文獻也發現，客觀指標和聽者的評分相關很弱。</p>
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
const show = () => !blind || revealed;

function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function el(tag, cls, text) { const e = document.createElement(tag);
  if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
function audio(src) { const a = document.createElement("audio"); a.controls = true; a.preload = "none"; a.src = src; return a; }
function fmt(x, d) { return x == null ? "–" : Number(x).toFixed(d); }

function row(label, src, meta, error) {
  const r = el("div", "row"); r.append(el("div", "label", label));
  if (src) r.append(audio(src)); else r.append(el("div", "err", error || "沒有音檔"));
  if (meta) r.append(el("div", "meta", meta));
  return r;
}

function cellBox(c, title) {
  const box = el("div", "cell");
  if (title) box.append(el("div", "title", title));
  if (!c.ok) { box.append(el("div", "err", c.reason)); return box; }
  for (const v of c.versions) {
    box.append(el("div", "v", v.label + (v.meta ? "（" + v.meta + "）" : "")));
    if (v.src) box.append(audio(v.src)); else box.append(el("div", "err", v.error || "沒有音檔"));
  }
  if (show() && c.scores) {
    const s = c.scores, sc = el("div", "scores");
    [["總分", fmt(s.score, 2)], ["和弦音", fmt(s.ctnctr, 2)], ["協和", fmt(s.pcs, 2)],
     ["調外音", fmt(s.ook, 2)], ["刺耳重疊", fmt(s.dis, 3)], ["音數", s.notes],
     ["旋律重複", s.dbl == null ? "–" : Math.round(s.dbl * 100) + "%"],
     ["選中", `第 ${s.chosen + 1}/${s.n} 份`]].forEach(([k, v]) => sc.append(el("span", "chip", `${k} ${v}`)));
    box.append(sc);
    if (s.dbl != null && s.dbl >= 0.5) box.append(el("div", "meta warn",
      "注意：選中的這份有一半以上的音，是在重複旋律（同音或差八度）。分數高是因為重複旋律一定「協和」，不代表它是好伴奏。"));
    const det = el("details", "cands"); det.append(el("summary", null, "8 份候選的分數（★ = 選中）"));
    const tb = el("table"); const hr = el("tr");
    ["份", "音數", "和弦音", "協和", "調外音", "刺耳重疊", "旋律重複", "總分"].forEach(h => hr.append(el("th", null, h)));
    tb.append(hr);
    for (const x of c.cands) {
      const tr = el("tr", x.k === s.chosen ? "chosen" : null);
      [(x.k === s.chosen ? "★ " : "") + (x.k + 1), x.notes, fmt(x.ctnctr, 2), fmt(x.pcs, 2), fmt(x.ook, 2),
       fmt(x.dis, 3), x.dbl == null ? "–" : Math.round(x.dbl * 100) + "%",
       x.score == null ? (x.notes ? "不排名" : "空的") : fmt(x.score, 2)].forEach(v => tr.append(el("td", null, v)));
      tb.append(tr);
    }
    det.append(tb); box.append(det);
  }
  if (show()) c.warn.forEach(w => box.append(el("div", "meta", "注意：" + w)));
  return box;
}

function render() {
  const app = document.getElementById("app"); app.innerHTML = "";
  for (const m of DATA) {
    const s = el("section", "melody");
    s.append(el("h2", null, `${m.title}（${m.meter}）`));
    s.append(row("輸入旋律", m.input, "", "沒有輸入音檔"));

    s.append(el("h3", null, "一、和聲：旋律＋柱式和弦"));
    const hs = blind ? (order[m.name + "/h"] ||= shuffle(m.harmony.filter(h => h.ok))) : m.harmony;
    hs.forEach((h, i) => {
      const letter = "ABC"[i];
      const label = !blind ? h.label : revealed ? `和聲 ${letter} = ${h.label}` : `和聲 ${letter}`;
      const r = row(label, h.src, "", h.reason);
      if (show() && h.chart) r.append(el("div", "chart", h.chart));
      s.append(r);
    });

    s.append(el("h3", null, "二、交叉比較：和聲來源 × 伴奏模型"));
    if (!blind) {
      const sources = [...new Set(m.cells.map(c => c.source))];
      const models = [...new Set(m.cells.map(c => c.model))];
      const g = el("div", "grid"); g.style.setProperty("--cols", models.length);
      g.append(el("div", "head col", ""));
      models.forEach(md => g.append(el("div", "head col", m.cells.find(c => c.model === md).model_label)));
      for (const src of sources) {
        const first = m.cells.find(c => c.source === src);
        g.append(el("div", "head rowhead", "和聲：" + first.source_label));
        for (const md of models) {
          const c = m.cells.find(x => x.source === src && x.model === md);
          g.append(cellBox(c, window.innerWidth <= 720 ? c.model_label : null));
        }
      }
      s.append(g);
    } else {
      const okCells = m.cells.filter(c => c.ok);
      const list = order[m.name + "/c"] ||= shuffle(okCells);
      const wrap = el("div", "list");
      list.forEach((c, i) => {
        const t = revealed ? `伴奏 ${i + 1} = ${c.source_label} × ${c.model_label}` : `伴奏 ${i + 1}`;
        wrap.append(cellBox(c, t));
      });
      s.append(wrap);
    }
    app.append(s);
  }
}

document.getElementById("blind").onclick = e => {
  blind = !blind; revealed = false; order = {};
  e.target.textContent = "盲聽模式：" + (blind ? "開" : "關"); e.target.classList.toggle("on", blind);
  document.getElementById("reveal").hidden = !blind;
  document.getElementById("hint").textContent = blind
    ? "和聲來源和伴奏組合都已打亂、隱藏名稱與分數。先記下你喜歡哪幾個，再按揭曉。" : "";
  render();
};
document.getElementById("reveal").onclick = () => { revealed = true; render(); };
document.addEventListener("play", e => {
  document.querySelectorAll("audio").forEach(a => { if (a !== e.target) a.pause(); });
}, true);
let lastNarrow = window.innerWidth <= 720;
window.addEventListener("resize", () => { const n = window.innerWidth <= 720; if (n !== lastNarrow) { lastNarrow = n; render(); } });
render();
</script>
</body>
</html>
"""


def main():
    data = collect()
    if not data:
        sys.exit("output/ has no run-notes.json yet — run run.py first")
    page = OUT / "player.html"
    page.write_text(PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    n_cells = sum(c["ok"] for m in data for c in m["cells"])
    print(f"wrote {page} ({len(data)} melodies, {n_cells} accompaniment cells)")


if __name__ == "__main__":
    main()
