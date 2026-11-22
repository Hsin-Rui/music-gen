"""Write the round-3 report: reports/round3-report.html (self-contained, zh-TW, light/dark, no external requests).

    uv run make_report_r3.py

Reads reports/round3-scores.json (the committed copy of output/round3/summary.json written by round3.py).
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from make_player_r3 import AXIS_LABELS, GATE_LABELS, MODEL_LABELS, SOURCE_LABELS, TITLES  # noqa: E402

SRC = ROOT / "reports" / "round3-scores.json"
OUT = ROOT / "reports" / "round3-report.html"
E = html.escape


def k1(k):
    return "–" if k is None else f"第 {k + 1} 份"


def f(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def cell_name(c):
    return f"{TITLES.get(c['melody'], c['melody'])} × {SOURCE_LABELS.get(c['source'], c['source'])} × {MODEL_LABELS.get(c['model'], c['model'])}"


def build(d):
    cells = d["cells"]
    ok = [c for c in cells if not c["missing"]]
    sel = [c for c in ok if c["selectable"]]
    diff = [c for c in sel if not c["same_as_old"]]
    fb = [c for c in sel if c["fallback"]]
    models = list(d["models"])
    th = d["thresholds"]

    # ------------------------------------------------ picks table
    rows = []
    for c in cells:
        if c["missing"]:
            rows.append(f"<tr><td>{E(cell_name(c))}</td><td colspan=5 class=warn>缺：{E(c['reason'])}</td></tr>")
            continue
        if c["selectable"]:
            same = '<span class=ok>相同</span>' if c["same_as_old"] else '<span class=accent>不同</span>'
            note = '<span class=warn>退回</span>' if c["fallback"] else ""
            rows.append(f"<tr><td>{E(cell_name(c))}</td><td>{k1(c['chosen'])}</td><td>{k1(c['old_chosen'])}</td>"
                        f"<td>{same}</td><td>{c['passers']}/{c['n']}</td><td>{note}</td></tr>")
        else:
            x = c["candidates"][0]
            st = "過全部門檻" if not x["failed"] else "沒過：" + "、".join(GATE_LABELS[g] for g in x["failed"])
            rows.append(f"<tr><td>{E(cell_name(c))}</td><td colspan=3 class=muted>只有一份，不挑選</td>"
                        f"<td>{c['passers']}/{c['n']}</td><td>{E(st)}</td></tr>")
    picks = "\n".join(rows)

    # ------------------------------------------------ gate pass counts per gate x model
    def count(model, gate=None):
        cs = [x for c in ok if c["model"] == model for x in c["candidates"] if x.get("notes")]
        n = len(cs)
        p = sum(1 for x in cs if (not x["failed"] if gate is None else gate not in x["failed"]))
        return p, n
    head = "".join(f"<th>{E(MODEL_LABELS.get(m, m))}</th>" for m in models)
    grows = []
    for g in d["gates"] + [None]:
        tds = []
        for m in models:
            p, n = count(m, g)
            tds.append(f"<td>{p}/{n}</td>" if n else "<td>–</td>")
        label = "<b>全部通過</b>" if g is None else E(GATE_LABELS[g])
        grows.append(f"<tr><td>{label}</td>{''.join(tds)}</tr>")
    n_empty = {m: sum(1 for c in ok if c["model"] == m for x in c["candidates"] if not x.get("notes")) for m in models}
    grows.append("<tr><td class=muted>空白候選（0 個音，不計入上面各列）</td>"
                 + "".join(f"<td class=muted>{n_empty[m]}</td>" for m in models) + "</tr>")
    tot_rows = []
    for g in d["gates"]:
        cs = [x for c in ok for x in c["candidates"] if x.get("notes")]
        tot_rows.append(f"{E(GATE_LABELS[g])} {sum(1 for x in cs if g not in x['failed'])}/{len(cs)}")

    # main blocker per selectable model
    blockers = []
    for m in models:
        cs = [x for c in sel if c["model"] == m for x in c["candidates"] if x.get("notes")]
        if not cs:
            continue
        worst = min(d["gates"], key=lambda g: sum(1 for x in cs if g not in x["failed"]))
        fails = sum(1 for x in cs if worst in x["failed"])
        empty = sum(1 for c in sel if c["model"] == m for x in c["candidates"] if not x.get("notes"))
        blockers.append(f"<li><b>{E(MODEL_LABELS[m])}</b>：非空白的 {len(cs)} 份裡，最常擋下的是「{E(GATE_LABELS[worst])}」"
                        f"（{fails} 份）" + (f"；另有 {empty} 份是空白的（0 個音）" if empty else "") + "。</li>")

    # ------------------------------------------------ fallback cells
    if fb:
        fbt = "".join(
            f"<li>{E(cell_name(c))}：挑了{k1(c['chosen'])}，它沒過「"
            f"{'、'.join(GATE_LABELS[g] for g in next(x for x in c['candidates'] if x['k'] == c['chosen'])['failed'])}」。</li>"
            for c in fb)
        fb_html = f"<ul>{fbt}</ul>"
    else:
        fb_html = "<p>沒有。每一格都至少有一份過全部門檻。</p>"

    # ------------------------------------------------ rank tables per cell
    det = []
    for c in ok:
        trs = []
        for x in c["candidates"]:
            mark = ("★" if c["selected"] and x["k"] == c["chosen"] else "") + \
                   ("○" if c["selectable"] and x["k"] == c["old_chosen"] else "")
            gate = "讀不到檔案" if x.get("error") else ("✓" if not x["failed"] else "✗ " + "、".join(GATE_LABELS[g] for g in x["failed"]))
            r = x.get("ranks") or {}
            trs.append(
                f"<tr class='{'pick' if mark.startswith('★') else ''}'><td>{x['k'] + 1}</td><td>{x.get('notes', '–')}</td>"
                f"<td class='{'ok' if not x['failed'] else 'warn'} l'>{E(gate)}</td>"
                f"<td>{f(x.get('prompt_doc'))}</td><td>{f(x.get('chord_match'))}</td><td>{f(x.get('copy'))}</td>"
                f"<td>{r.get('prompt_sim', '–')}（{f(x.get('prompt_sim'))}）</td>"
                f"<td>{r.get('rules', '–')}（{f(x.get('rules'), 3)}）</td>"
                f"<td>{r.get('bass_ok', '–')}（{f(x.get('bass_ok'))}）</td>"
                f"<td>{'–' if x.get('borda') is None else x['borda']}</td><td>{mark}</td></tr>")
        tag = ("新舊相同" if c["same_as_old"] else "新舊不同") if c["selectable"] else "只有一份"
        if c["fallback"]:
            tag += "・退回"
        det.append(f"<details><summary>{E(cell_name(c))} <span class=muted>（{tag}）</span></summary><div class=tw><table>"
                   "<tr><th>份</th><th>音數</th><th class=l>門檻</th><th>抄提示</th><th>和弦吻合</th><th>抄旋律</th>"
                   f"<th>{AXIS_LABELS['prompt_sim']}</th><th>{AXIS_LABELS['rules']}</th><th>{AXIS_LABELS['bass_ok']}</th>"
                   f"<th>加總</th><th></th></tr>{''.join(trs)}</table></div></details>")
    details = "\n".join(det)

    return PAGE.format(
        n_ok=len(ok), n_cells=len(cells), n_sel=len(sel), n_diff=len(diff), n_same=len(sel) - len(diff), n_fb=len(fb),
        created=E(d.get("created", "")), picks=picks, ghead=head, grows="\n".join(grows),
        gtot="；".join(tot_rows), blockers="\n".join(blockers), fb=fb_html, details=details,
        eb=int(th["empty_beat_max"] * 100), cp=th["copy_max"], doc=th["doc_max"], cm=th["chord_match_min"],
        ook=int(th["ook_max"] * 100), hn=th["hand_notes"], hs=th["hand_span"], tol=int(th["onset_tol"] * 1000))


PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第三輪挑選報告</title>
<style>
:root {{ --bg:#f7f6f3; --card:#fff; --text:#1d1d1f; --muted:#6b6b70; --line:#e3e1dc; --accent:#3b5bdb;
  --warn:#b54708; --ok:#2b7a3d; --chip:#eef1fb; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#151517; --card:#1f1f23; --text:#ececee; --muted:#9a9aa2; --line:#33333a; --accent:#8da2fb;
    --warn:#f5a46b; --ok:#7fd18f; --chip:#272b3a; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.7 -apple-system, "PingFang TC", "Noto Sans TC", sans-serif; }}
main {{ max-width:980px; margin:0 auto; padding:28px 16px 64px; }}
h1 {{ font-size:24px; margin:0 0 4px; }} h2 {{ font-size:19px; margin:32px 0 8px; }}
.muted {{ color:var(--muted); }} .ok {{ color:var(--ok); }} .warn {{ color:var(--warn); }} .accent {{ color:var(--accent); }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px 18px; margin:12px 0; }}
.stats {{ display:flex; flex-wrap:wrap; gap:10px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:8px 14px; }}
.stat b {{ font-size:22px; display:block; }}
.tw {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:13.5px; margin:6px 0; }}
th, td {{ border-bottom:1px solid var(--line); padding:4px 8px; text-align:right; vertical-align:top; }}
th:first-child, td:first-child, .l {{ text-align:left; }}
tr.pick td {{ font-weight:600; color:var(--accent); }}
.def td, .def th {{ text-align:left; }}
details {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:8px 12px; margin:8px 0; }}
summary {{ cursor:pointer; font-weight:600; }}
code {{ background:var(--chip); border-radius:5px; padding:0 4px; font-size:13px; }}
.next {{ border-left:4px solid var(--accent); }}
</style>
</head>
<body>
<main>
<h1>原型 02 第三輪：先過門檻、再排名的挑選指標</h1>
<p class="muted">產生時間 {created}。資料：<code>reports/round3-scores.json</code>（由 <code>round3.py</code> 產生）。這一輪沒有重跑任何模型，也沒有呼叫 Gemini：AMT、AccoMontage 用第二輪存下的 8 份候選重新挑選，所以新舊挑選面對的是同一批候選，差別只來自指標。</p>

<div class="stats">
<div class="stat"><b>{n_ok}/{n_cells}</b>格有產出</div>
<div class="stat"><b>{n_diff}/{n_sel}</b>格新舊挑得不同</div>
<div class="stat"><b>{n_same}</b>格新舊相同</div>
<div class="stat"><b>{n_fb}</b>格退回（沒有一份過全部門檻）</div>
</div>

<h2>一、指標怎麼算</h2>
<div class="card">
<p><b>為什麼改：</b>第二輪的分數把「忠於和弦」和「不抄旋律」等項目加在一起比高低，結果常挑到幾乎照抄柱式和弦提示的那份。R5 研究發現「忠於和弦」和「不照抄提示」會互相拉扯，所以這一輪把「忠於和弦」改成門檻：先淘汰不合格的，剩下的再比「有沒有變化、守不守規則」。</p>
<p><b>門檻</b>（五道都過才算通過；起始值都可以調，這輪不調）：</p>
<div class="tw"><table class="def">
<tr><th>門檻</th><th>白話</th><th>條件</th></tr>
<tr><td>彈得夠多</td><td>不能幾乎什麼都沒彈</td><td>音數 ≥ 小節數，而且空拍比例 ≤ {eb}%。一拍裡只要有任何伴奏音<b>正在響</b>就不算空拍（延長的和弦也算）。</td></tr>
<tr><td>不抄旋律</td><td>不能只是把旋律重彈一次或平移</td><td>和旋律同時起音、距離固定（同音、八度、平行三度等）的伴奏音比例 &lt; {cp}（沿用第二輪的「抄旋律」）。</td></tr>
<tr><td>不照抄提示</td><td>不能只是把柱式和弦提示原樣彈出來</td><td>抄襲程度 = 2 × 配對數 ÷（伴奏音數＋提示音數）&lt; {doc}。配對：音名相同（不管八度）、起音差 ≤ {tol} 毫秒，一個音只能配一次。提示原樣彈出來 = 1.0。</td></tr>
<tr><td>守住和弦</td><td>要照和弦表走，不亂彈調外音</td><td>逐拍和弦吻合率 ≥ {cm}（一拍裡響著的伴奏，至少一半時間是當下和弦的音，這一拍才算吻合），而且調外音 ≤ {ook}%。</td></tr>
<tr><td>彈得到</td><td>一個人兩隻手彈得出來</td><td>同時起音的一組音，一隻手彈得下，或能切成左右兩手、每隻手 ≤ {hn} 個音且跨度 ≤ {hs} 個半音，就算彈得到。兩隻手怎麼切都不行的，就不合格。</td></tr>
</table></div>
<p><b>排名</b>（只在通過門檻的候選之間排，每項 1 = 最好，同分同名次；三項名次加總最小的勝出；再同分就選「不像提示」比較低的，再同分選編號小的）：</p>
<div class="tw"><table class="def">
<tr><th>項目</th><th>白話</th><th>怎麼算</th></tr>
<tr><td>不像提示</td><td>越不像柱式和弦提示越好</td><td>兩個數的平均：① 音符比對 F1（音高相同、起音差 ≤ 50 毫秒、結束時間也接近才算配對）；② 節奏格子相似度（十六分音符格子上「有沒有起音」的餘弦相似度）。越低越好。</td></tr>
<tr><td>不違規</td><td>少一點和聲規則上的毛病</td><td>低音和旋律之間的平行五度、平行八度（每個旋律音的比例），加上刺耳重疊（旋律與伴奏同時響小二度、三全音、大七度的時間比例）。越低越好。</td></tr>
<tr><td>低音正確</td><td>換和弦時，最低的音是不是和弦的低音</td><td>每次換和弦，看換和弦後半拍內起音的最低伴奏音，音名是不是和弦的低音（斜線和弦看斜線後面的音）。越高越好。這一項是自訂的，沒有文獻依據。</td></tr>
</table></div>
<p><b>退回：</b>如果一格裡沒有任何一份過全部門檻，就在「擋掉的門檻數最少」的那幾份裡用同樣方法排名，並標成「退回」。</p>
<p><b>Claude、Gemini 寫伴奏</b>每格只有一份，指標照樣計算、顯示，但不參與挑選。</p>
</div>

<h2>二、每格挑選結果：新 vs 舊</h2>
<div class="tw"><table>
<tr><th>格子</th><th>新指標挑的</th><th>舊指標挑的</th><th>新舊</th><th>過全部門檻</th><th>備註</th></tr>
{picks}
</table></div>

<h2>三、門檻通過數</h2>
<p class="muted">每格、每份候選分開算（AMT、AccoMontage 每格 8 份，Claude、Gemini 每格 1 份）。只算非空白的候選：空白（0 個音）的候選只算沒過「彈得夠多」，其他門檻不評估，數量另列在表的最後一列。</p>
<div class="tw"><table>
<tr><th>門檻</th>{ghead}</tr>
{grows}
</table></div>
<p class="muted">全部模型合計：{gtot}。</p>
<ul>
{blockers}
</ul>

<h2>四、退回的格子</h2>
<div class="card">{fb}</div>

<h2>五、每格的名次表</h2>
<p class="muted">名次欄的括號是原始數值。★ = 新指標挑的，○ = 第二輪舊指標挑的。「抄提示」「和弦吻合」「抄旋律」是門檻用的數值。</p>
{details}

<h2>六、和計畫字面不同的地方</h2>
<div class="card"><ul>
<li><b>空拍看「正在響」，不看「起音」：</b>MusPy 的空拍是數起音，但那樣會把「一個和弦延長一整小節」的織體判成空拍、擋掉。這裡改成「一拍裡有任何伴奏音在響就不算空」。</li>
<li><b>「彈得到」是兩隻手的檢查：</b>計畫的表寫「同時發聲 ≤ 5 個、跨度 ≤ 14 個半音」，照字面當成一隻手，會擋掉所有「低音＋和弦」的織體，連 Claude、Gemini 的規劃也過不了。計畫的本意是「彈得到」，所以改成兩隻手的檢查：試過所有左右手的切法，只要有一種切法兩手都彈得下就合格。</li>
<li><b>只看「起音」相同的一組音：</b>彈得到的檢查只看同時按下的音，不管前面還在延長的音（例如踏板留著的低音）。</li>
<li><b>平行五八度只看相鄰的兩個旋律音：</b>兩個旋律音中任何一個當下沒有伴奏音在響，這一對就跳過。比例的分母是全部旋律音數。</li>
<li><b>舊指標挑的那份</b>取自第二輪 <code>candidates/scores.json</code> 的 <code>best</code>（它是候選清單的索引，再對應到編號）。</li>
<li><b>AccoMontage 常被「彈得到」擋下：</b>它的伴奏來自 POP909 流行歌鋼琴譜，常有一次橫跨三個音域的大和弦（例如低音 37、中間 52–57、上面 67–69），左手撐不開；而且只要整首有一個這樣的和弦，整份就不合格。這是門檻的結果，不是程式錯誤，但門檻值（5 音、14 半音）沒有文獻依據，聽過之後可以再調。</li>
</ul></div>

<div class="card next">
<p><b>下一步：請你盲聽。</b>打開 <code>prototype/harmony-first/output/round3/player.html</code>：</p>
<ol>
<li>用「盲聽二：新 vs 舊」聽新舊挑得不同的 {n_diff} 格，每格記下 A 或 B 哪個比較好、為什麼，再按揭曉。</li>
<li>用「盲聽一：模型」聽每份和弦的四個模型，看新指標挑的 AMT、AccoMontage 和 Claude、Gemini 寫的比起來如何。</li>
</ol>
<p>如果新指標挑的多半比較好，下一步才開始調參數；如果沒有比較好，先回頭看是哪道門檻或哪一項名次判斷錯了。</p>
</div>
</main>
</body>
</html>
"""


def main():
    if not SRC.exists():
        sys.exit("reports/round3-scores.json not found — run round3.py first")
    d = json.loads(SRC.read_text())
    OUT.write_text(build(d), encoding="utf-8")
    print(f"wrote {OUT} ({len(d['cells'])} cells)")


if __name__ == "__main__":
    main()
