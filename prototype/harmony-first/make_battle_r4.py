"""Round 4 A/B battle page: output/round4/battle.html (reads output/round4/manifest.json).

    uv run make_battle_r4.py

Single-elimination knockouts, blind: for each model, champion = knockout over its clips; 2nd =
knockout over the clips that lost directly to the champion; 3rd = knockout over the remaining
clips that lost directly to the champion or the 2nd. Then the three models' top 3 (9 clips) are
ranked the same way. Pairings and A/B order are random (seeded per browser, stored with the
answers). A pair that already met is not asked again. Answers live in localStorage; "下載結果"
saves a JSON file. Names, settings and metrics are shown only after the last answer.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "round4"
MODEL_LABELS = {"amt": "AMT + 和弦條件", "accomontage": "AccoMontage", "compose_embellish": "Compose & Embellish"}
STYLE = {"sustain": "長和弦", "short": "短和弦", "beat": "每拍重按"}


def label(c):
    p = c["params"]
    if c["model"] == "amt":
        return f"提示 {STYLE[p['prompt_style']]}、top_p {p['top_p']}"
    if c["model"] == "accomontage":
        return "不篩選" if p["density"] is None else f"密度 {p['density']}、發聲數 {p['voices']}"
    return f"溫度 {p['temp']}、top_p {p['top_p']}"


def main():
    man = json.loads((OUT / "manifest.json").read_text())
    order = [m for m in ["accomontage", "compose_embellish", "amt"] if any(c["model"] == m for c in man["clips"])]
    clips = [{"id": c["id"], "model": c["model"], "wav": c["wav"], "seed": c["seed"], "label": label(c),
              "also": [label(a) + f"（種子 {a['seed']}）" for a in c["also"]],
              "old_score": c.get("old_score"), "new_borda": c.get("new_borda"), "new_pool": c.get("new_pool"),
              "failed": c["new_metrics"]["failed"], "doc": c["new_metrics"].get("prompt_doc")}
             for c in man["clips"]]
    data = {"order": order, "models": MODEL_LABELS, "clips": clips, "clip_sec": man["clip_sec"],
            "blank": len(man["blank"]), "dups": sum(len(c["also"]) for c in man["clips"])}
    page = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    (OUT / "battle.html").write_text(page)
    print(f"wrote {OUT / 'battle.html'} ({len(clips)} clips, models {order})")


TEMPLATE = r"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>伴奏 A/B 對決</title>
<style>
:root{--bg:#fbfaf8;--fg:#1d1d1f;--muted:#5f6368;--card:#fff;--line:#e3e0da;--accent:#2f6f8f;--soft:#eef4f7;--gold:#b8860b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141517;--fg:#e8e6e3;--muted:#a3a6ab;--card:#1d1f22;--line:#33363b;--accent:#7cb8d6;--soft:#1f2a30;--gold:#e0b84a}}
:root[data-theme="dark"]{--bg:#141517;--fg:#e8e6e3;--muted:#a3a6ab;--card:#1d1f22;--line:#33363b;--accent:#7cb8d6;--soft:#1f2a30;--gold:#e0b84a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:1.45rem;margin:0 0 4px}
.muted{color:var(--muted);font-size:.9rem}
.bar{height:8px;background:var(--soft);border-radius:99px;overflow:hidden;margin:10px 0 18px}
.bar>div{height:100%;background:var(--accent);width:0}
.duel{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.side{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;text-align:center}
.side h2{margin:0 0 10px;font-size:2rem}
audio{width:100%}
button{font:inherit;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);padding:10px 14px;cursor:pointer}
button.pick{width:100%;margin-top:12px;background:var(--accent);color:#fff;border:0;font-weight:600}
.row{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.stage{display:inline-block;background:var(--soft);border-radius:99px;padding:2px 12px;font-size:.85rem;margin-bottom:6px}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin:10px 0}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.medal{color:var(--gold);font-weight:700}
.scroll{overflow-x:auto}
@media (max-width:560px){.duel{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<h1>伴奏 A/B 對決（快樂頌 × Gemini 和弦）</h1>
<div class="muted">每組兩段，各約 16 秒（前 8 小節）。只要選「哪一段比較好聽」。名稱和設定都隱藏，全部比完才揭曉。進度會自動存在這個瀏覽器裡，可以隨時關掉、下次繼續。</div>
<div id="app"></div>
</div>
<script>
const D = __DATA__;
const KEY = "battle-r4-v1";
const byId = Object.fromEntries(D.clips.map(c => [c.id, c]));
function load(){ try { const s = JSON.parse(localStorage.getItem(KEY)); if (s && s.results) return s; } catch(e){} return null; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e){} }
let S = load() || {seed: Math.floor(Math.random() * 2**31), results: {}, history: []};
save();
function hash(str){ let h = 2166136261; for (const ch of str){ h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
function rng(tag){ let a = (S.seed ^ hash(tag)) >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function shuffle(arr, tag){ const r = rng(tag), a = arr.slice(); for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const pk = (a, b) => a < b ? a + "|" + b : b + "|" + a;
class Need { constructor(a, b, stage){ this.a = a; this.b = b; this.stage = stage; } }
function ask(a, b, stage){ const w = S.results[pk(a, b)]; if (w === undefined) throw new Need(a, b, stage); return w; }
function knockout(items, tag, beats, stage){
  let cur = shuffle(items, tag);
  while (cur.length > 1){
    const next = [];
    for (let i = 0; i + 1 < cur.length; i += 2){
      const a = cur[i], b = cur[i + 1], w = ask(a, b, stage), l = w === a ? b : a;
      (beats[w] ||= []).push(l); next.push(w);
    }
    if (cur.length % 2) next.push(cur[cur.length - 1]);
    cur = next;
  }
  return cur[0];
}
function top3(items, tag, stage){
  const beats = {};
  if (!items.length) return [];
  const c1 = knockout(items, tag + ":1", beats, stage);
  const l1 = [...new Set(beats[c1] || [])];
  if (!l1.length) return [c1];
  const c2 = knockout(l1, tag + ":2", beats, stage);
  const cand = [...new Set([...l1, ...(beats[c2] || [])])].filter(x => x !== c1 && x !== c2);
  if (!cand.length) return [c1, c2];
  const c3 = knockout(cand, tag + ":3", beats, stage);
  return [c1, c2, c3];
}
function estimate(n){ return n <= 1 ? 0 : (n - 1) + 2 * Math.ceil(Math.log2(n)); }
function solve(){
  const tops = {};
  const stages = D.order.length + 1;
  try {
    D.order.forEach((m, i) => { tops[m] = top3(D.clips.filter(c => c.model === m).map(c => c.id), m, `第 ${i + 1} 階段／共 ${stages} 階段`); });
    const fin = top3(D.order.flatMap(m => tops[m]), "final", `決賽（第 ${stages} 階段）`);
    return {done: true, tops, fin};
  } catch(e){ if (e instanceof Need) return {done: false, need: e}; throw e; }
}
const total = D.order.reduce((s, m) => s + estimate(D.clips.filter(c => c.model === m).length), 0) + estimate(3 * D.order.length);
function render(){
  const r = solve(), app = document.getElementById("app");
  const done = S.history.length;
  const pct = r.done ? 100 : Math.min(98, Math.round(100 * done / total));
  let h = `<div class="bar"><div style="width:${pct}%"></div></div>`;
  if (!r.done){
    const {a, b, stage} = r.need, flip = hash(pk(a, b) + S.seed) % 2 === 1;
    const [A, B] = flip ? [b, a] : [a, b];
    h += `<div class="stage">${stage}</div> <span class="muted">已比 ${done} 組，全部約 ${total} 組</span>
      <div class="duel">
        <div class="side"><h2>A</h2><audio id="aA" controls preload="auto" src="${byId[A].wav}"></audio><button class="pick" data-w="${A}">A 比較好聽</button></div>
        <div class="side"><h2>B</h2><audio id="aB" controls preload="auto" src="${byId[B].wav}"></audio><button class="pick" data-w="${B}">B 比較好聽</button></div>
      </div>
      <div class="row"><button id="seq">依序播放 A → B</button><button id="undo" ${done ? "" : "disabled"}>上一組（改答案）</button><button id="dl">下載目前結果</button></div>`;
    app.innerHTML = h;
    app.querySelectorAll(".pick").forEach(btn => btn.onclick = () => { S.results[pk(a, b)] = btn.dataset.w; S.history.push({pair: pk(a, b), winner: btn.dataset.w, a_shown: A, b_shown: B, stage, t: new Date().toISOString()}); save(); render(); window.scrollTo(0, 0); });
    const aA = document.getElementById("aA"), aB = document.getElementById("aB");
    aA.onplay = () => aB.pause(); aB.onplay = () => aA.pause();
    document.getElementById("seq").onclick = () => { aB.pause(); aB.currentTime = 0; aA.currentTime = 0; aA.play(); aA.onended = () => { aB.currentTime = 0; aB.play(); aA.onended = null; }; };
  } else {
    const row = (id, i) => { const c = byId[id]; return `<tr><td class="medal">${["🥇","🥈","🥉"][i] || ""}</td><td>${D.models[c.model]}</td><td>${c.label}（種子 ${c.seed}）${c.also.length ? "<br><span class=muted>同一份也來自：" + c.also.join("、") + "</span>" : ""}</td><td><audio controls preload="none" src="${c.wav}"></audio></td></tr>`; };
    h += `<h2>結果揭曉</h2><p class="muted">共比了 ${done} 組。自動淘汰的完全空白版本 ${D.blank} 份；重複的版本 ${D.dups} 份已合併。</p>
      <h3>總排名</h3><div class="scroll"><table><tr><th></th><th>模型</th><th>設定</th><th>試聽</th></tr>${r.fin.map(row).join("")}</table></div>`;
    for (const m of D.order){
      const cs = D.clips.filter(c => c.model === m);
      const oldBest = cs.filter(c => c.old_score != null).sort((x, y) => y.old_score - x.old_score)[0];
      const newBest = cs.filter(c => c.new_borda != null).sort((x, y) => x.new_borda - y.new_borda)[0];
      h += `<h3>${D.models[m]}（${cs.length} 段）</h3><div class="scroll"><table><tr><th></th><th>模型</th><th>設定</th><th>試聽</th></tr>${r.tops[m].map(row).join("")}</table></div>
        <p class="muted">指標會挑哪一段：舊指標 → ${oldBest ? oldBest.label + "（種子 " + oldBest.seed + "）" : "–"}；新指標 → ${newBest ? newBest.label + "（種子 " + newBest.seed + "）" : "–"}。</p>`;
    }
    h += `<div class="row"><button id="dl">下載結果</button><button id="undo">上一組（改答案）</button><button id="reset">全部重來</button></div>`;
    app.innerHTML = h;
    document.getElementById("reset").onclick = () => { if (confirm("確定要清掉所有答案、重新開始？")){ S = {seed: Math.floor(Math.random() * 2**31), results: {}, history: []}; save(); render(); } };
  }
  const u = document.getElementById("undo");
  if (u) u.onclick = () => { const last = S.history.pop(); if (last) delete S.results[last.pair]; save(); render(); };
  document.getElementById("dl").onclick = () => {
    const out = {...S, finished: r.done, result: r.done ? {final: r.fin, per_model: r.tops} : null, clips: D.clips, saved: new Date().toISOString()};
    const url = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], {type: "application/json"}));
    const a = document.createElement("a"); a.href = url; a.download = "round4-battle-results.json"; a.click(); URL.revokeObjectURL(url);
  };
}
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
