---
id: melodyt5
type: model
task: '配和聲（ABC 旋律 → 帶和弦的 ABC），也做其他旋律任務'
status: '原型 02 候選'
updated: '2026-11-21'
---

# MelodyT5

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲（ABC 旋律 → 帶和弦的 ABC），也做其他旋律任務 |
| 連結 | [GitHub](https://github.com/sanderwood/melodyt5)、[HF](https://huggingface.co/sander-wood/melodyt5) |
| 程式碼授權 | MIT |
| 權重授權 | MIT（HF 標籤） |
| 大小 | 1.13 億參數 |
| 輸入 | ABC 旋律 |
| 輸出 | ABC＋和弦記號（含七和弦、轉位） |
| Mac（M3 Pro 18GB） | 應可 CPU；環境寫死 Python 3.7、CUDA 11.6（未驗證） |
| 我們的使用狀態 | 原型 02 候選 |
| 實測效能 | — |

## 重點與坑

- ISMIR 2024。訓練資料：民謠、巴哈聖詠、Nottingham（西方，無中國）。
- 指標：CTnCTR 0.844／PCS 0.508／MCTD 1.032；聽覺測試比 STHarm 受偏好。

## 文獻

[arxiv-2407.02277](../literature/arxiv-2407.02277.md)

## 出處

[R3 [1][2]](../../docs/research-harmonization-accompaniment/research-harmonization-accompaniment.md)

## 更新紀錄

- **原型 02（2026-11-21）：** 新版 PyTorch＋transformers 4.30.2 可在 CPU 跑（要濾掉 causal-mask buffer）。呼叫方式已逐行對照上游確認沒有錯。上游預設 temperature 2.6 下，和弦很少換（快樂頌前 7 小節都是 D）。使用者盲聽後認為 Claude 的和弦比它好。
