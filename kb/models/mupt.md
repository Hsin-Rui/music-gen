---
id: mupt
type: model
task: 'ABC 記譜續寫（非配和聲）'
status: '不適用'
updated: '2026-11-21'
---

# MuPT

| 項目 | 內容 |
|---|---|
| 做什麼 | ABC 記譜續寫（非配和聲） |
| 連結 | [HF m-a-p/MuPT-v1-8192-190M](https://huggingface.co/m-a-p/MuPT-v1-8192-190M) |
| 程式碼授權 | — |
| 權重授權 | Apache-2.0（190M 版卡片） |
| 大小 | 1.1 億–13 億參數 |
| 輸入 | ABC 前綴 |
| 輸出 | ABC 續寫 |
| Mac（M3 Pro 18GB） | 小版本應可用 CPU（範例用 .cuda()） |
| 我們的使用狀態 | 不適用 |
| 實測效能 | — |

## 重點與坑

- ICLR 2025；700 萬首 ABC。
- 沒有替固定旋律配和聲的訓練或評估，只會續寫。

## 文獻

[arXiv 2404.06393](../literature/arxiv-2404.06393.md)

## 出處

[R4 [15]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
