---
id: claude-accompaniment
type: model
task: '伴奏（Claude 逐小節規劃織體 → 規則展開）'
status: '原型 02 使用中'
updated: '2026-11-21'
---

# Claude 寫伴奏（本專案）

| 項目 | 內容 |
|---|---|
| 做什麼 | 伴奏（Claude 逐小節規劃織體 → 規則展開） |
| 連結 | `prototype/harmony-first/steps/accomp_claude.py`、`accompaniments/claude/` |
| 程式碼授權 | 本專案 |
| 權重授權 | 不需要 |
| 大小 | — |
| 輸入 | 旋律＋和弦表＋Claude 寫的逐小節織體計畫 |
| 輸出 | 鋼琴伴奏 MIDI（每格一份，沒有隨機性） |
| Mac（M3 Pro 18GB） | 純 Python |
| 我們的使用狀態 | 原型 02 使用中 |
| 實測效能 | — |

## 重點與坑

- 2026-11-21 依使用者要求加入。織體：柱式、分解和弦、Alberti、圓舞曲、空心五度、長音、終止琶音。
- 和弦一律放在旋律最低音下方至少小三度、不高過 G4。
- 指標分數照設計一定好看（全是和弦音），要用耳朵和模型比。

## 文獻

—

## 出處

原型 02（本專案實作）
