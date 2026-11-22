"""Rebuild kb/README.md from the entries in kb/. Run: python3 kb/build_index.py"""
import glob, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def title(f):
    m = re.search(r"^# (.+)$", open(f).read(), re.M); return m.group(1) if m else f
def fm(f, k):
    m = re.search(rf"^{k}: '?(.*?)'?$", open(f).read(), re.M); return m.group(1) if m else ""
def cell(f, k):
    m = re.search(rf"\| {k} \| (.*?) \|", open(f).read()); return m.group(1) if m else ""

L = ["# 知識庫", "",
     "音樂生成專案一路累積的文獻、模型、資料集和實驗。每一筆一個 Markdown 檔，放在 git 裡。", "",
     "## 怎麼用", "",
     "- **找東西：** 看下面的目錄，或在 `kb/` 裡搜尋關鍵字（`grep -ri 伴奏 kb/`）。",
     "- **新增：** 每次研究或做原型後，把新的文獻、模型、資料集各加一個檔（格式照同資料夾現有的檔），再執行 `python3 kb/build_index.py` 重建本頁。",
     "- **出處：** 每筆都連回它來自哪份研究報告或實驗。研究報告（`docs/research-*`）是原始證據，這裡是整理後的索引。R1＝技術路線圖、R2＝原型模型查證、R3＝配和聲與伴奏模型、R4＝原型 02 候選模型補查、R5＝伴奏挑選指標。",
     "- **信心：** 文獻的信心欄位沿用研究報告的判定；「尚未精讀」表示只用了報告查證過的那句話。", "",
     "## 實驗", ""]
for f in sorted(glob.glob("experiments/*.md")):
    L.append(f"- [{title(f)}]({f})：結論 `{fm(f,'verdict')}`，{fm(f,'date')}")
L += ["", "## 模型", "", "| 模型 | 做什麼 | 我們的使用狀態 |", "|---|---|---|"]
for f in sorted(glob.glob("models/*.md")):
    L.append(f"| [{title(f)}]({f}) | {fm(f,'task')} | {fm(f,'status')} |")
L += ["", "## 資料集", "", "| 資料集 | 類型 | 授權 | 文化／風格 |", "|---|---|---|---|"]
for f in sorted(glob.glob("datasets/*.md")):
    L.append(f"| [{title(f)}]({f}) | {cell(f,'類型')} | {cell(f,'授權')} | {cell(f,'文化／風格')} |")
L += ["", "## 文獻", "", "| 文獻（本專案取用的說法） | 發表 | 信心 |", "|---|---|---|"]
for f in sorted(glob.glob("literature/*.md")):
    L.append(f"| [{title(f)}]({f}) | {fm(f,'published')} | {fm(f,'confidence')} |")
L += ["", "## 來源研究", "",
      "- R1 [技術路線圖研究（2026-11-19）](../docs/research-music-generation-tech-roadmap/research-music-generation-tech-roadmap.md)",
      "- R2 [原型模型查證（2026-11-21）](../docs/research-prototype-model-check/research-prototype-model-check.md)",
      "- R3 [配和聲與和弦條件伴奏模型（2026-11-21）](../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)",
      "- R4 [原型 02 的候選模型補查（2026-11-21）](../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)",
      "- R5 [伴奏挑選指標（2026-11-22）](../docs/research-accompaniment-metrics-r5/research-accompaniment-metrics-r5.md)", ""]
open("README.md", "w").write("\n".join(L))
print("models", len(glob.glob("models/*.md")), "datasets", len(glob.glob("datasets/*.md")), "literature", len(glob.glob("literature/*.md")))
