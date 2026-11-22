"""Assemble the knowledge-base website source: kb/ + docs/ -> site/_src, then `mkdocs build`.

    uv run --with mkdocs-material python site/build.py [--serve]

kb/ and docs/ keep their relative layout, so links like ../../docs/... keep working.
Left out: dotfiles (.memlog.md, .template.md), imports/ (raw third-party material).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "_src"
SKIP = shutil.ignore_patterns(".*", "imports", "__pycache__", "*.py")


def title(md):
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md.stem


def main():
    if SRC.exists():
        shutil.rmtree(SRC)
    SRC.mkdir(parents=True)
    shutil.copytree(ROOT / "kb", SRC / "kb", ignore=SKIP)
    shutil.copytree(ROOT / "docs", SRC / "docs", ignore=SKIP)
    shutil.copy(ROOT / "site" / "extra.css", SRC / "extra.css")
    # BMad front matter uses `template:`, which MkDocs reads as a page template: rename it
    for md in SRC.rglob("*.md"):
        t = md.read_text(encoding="utf-8")
        if t.startswith("---") and re.search(r"(?m)^template:", t.split("---", 2)[1]):
            head, body = t.split("---", 2)[1:]
            md.write_text("---" + re.sub(r"(?m)^template:", "bmad_template:", head) + "---" + body, encoding="utf-8")
    # home page: knowledge base first, then every report folder's main document(s)
    rows = []
    for d in sorted(p for p in (SRC / "docs").iterdir() if p.is_dir()):
        mains = [f for f in sorted(d.iterdir()) if f.suffix in (".md", ".html") and f.is_file()]
        for f in mains:
            label = title(f) if f.suffix == ".md" else f.stem
            rows.append(f"| `{d.name}` | [{label}]({f.relative_to(SRC).as_posix()}) |")
    for f in sorted((SRC / "docs").glob("*.md")):
        rows.append(f"| — | [{title(f)}]({f.relative_to(SRC).as_posix()}) |")
    (SRC / "index.md").write_text(
        "# 音樂生成專案：知識庫與研究報告\n\n"
        "- **[知識庫目錄](kb/README.md)**：文獻、模型、資料集、實驗，每筆一頁。\n"
        "- 右上角可以搜尋（中文請用兩個字以上的詞）。\n\n"
        "## 研究報告與計畫\n\n| 資料夾 | 文件 |\n|---|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8")
    cmd = ["mkdocs", "serve" if "--serve" in sys.argv else "build", "-f", str(ROOT / "site" / "mkdocs.yml")]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
