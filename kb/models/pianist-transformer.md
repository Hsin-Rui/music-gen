---
id: pianist-transformer
type: model
task: '表情演奏：樂譜 MIDI → 演奏 MIDI'
status: '已用於 prototype-01'
updated: '2026-11-21'
---

# Pianist Transformer

| 項目 | 內容 |
|---|---|
| 做什麼 | 表情演奏：樂譜 MIDI → 演奏 MIDI |
| 連結 | [GitHub](https://github.com/yhj137/PianistTransformer)、[HF rendering](https://huggingface.co/yhj137/pianist-transformer-rendering)、[arXiv 2512.02652](https://arxiv.org/abs/2512.02652) |
| 程式碼授權 | Apache-2.0 |
| 權重授權 | Apache-2.0（HF 標籤） |
| 大小 | 1.35 億參數 |
| 輸入 | 樂譜 MIDI |
| 輸出 | 可編輯 MIDI（速度曲線＋踏板） |
| Mac（M3 Pro 18GB） | ✅ CPU、MPS（README 寫 CPU 即可） |
| 我們的使用狀態 | 已用於 prototype-01 |
| 實測效能 | 一段旋律數秒；記憶體約 0.6GB |

## 重點與坑

- ICML 2026。Python 3.11、PyTorch 2.7.1。
- 通常比原速快 10–30%。
- 音符全部保留（prototype-01 實測）。
- 使用者評：差強人意，可用。

## 文獻

—

## 出處

[R2 [6][7]](../../docs/research-prototype-model-check/research-prototype-model-check.md)、[prototype-01](../experiments/prototype-01-melody-to-performance.md)
