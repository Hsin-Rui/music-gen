---
id: harmonyrl
type: model
task: '配和聲（旋律 → 和弦）'
status: 'R4 建議加入原型 02'
updated: '2026-11-21'
---

# HarmonyRL

| 項目 | 內容 |
|---|---|
| 做什麼 | 配和聲（旋律 → 和弦） |
| 連結 | [GitHub](https://github.com/HarmonyRL/HarmonyRL)、[HF](https://huggingface.co/CloudHolic/harmonyrl-chromatic)、`pip install harmonyrl` |
| 程式碼授權 | MIT |
| 權重授權 | CC BY-NC-SA 3.0（HF 要登入同意條款） |
| 大小 | 1,840 萬參數 |
| 輸入 | MusicXML／MIDI 旋律（MusicXML 可帶既有和弦） |
| 輸出 | 和弦記號（MusicXML）或旋律＋和弦音符（MIDI） |
| Mac（M3 Pro 18GB） | README 說可用 CPU；Python ≥ 3.12 |
| 我們的使用狀態 | R4 建議加入原型 02 |
| 實測效能 | — |

## 重點與坑

- 2026-11-16 發布，沒有論文；HookTheory（Sheet Sage 版）訓練，transformer 先預訓練再用強化學習微調；三個版本 base／smooth／chromatic。
- 支援 2/4、3/4、6/8 等拍子（拍號分母 4 或 8；見程式碼 meter.py，README 沒寫）；拍號改變時分段；一次最多 32 小節，更長用重疊視窗；整首只有一個調。
- 可以只重配指定小節，其他保留；有 temperature、seed 參數，適合系統性調參。
- 自報評估：調外和弦時間 base 6.9%、smooth 5.5%、chromatic 12.9%（人類 9.6%）；聽覺測試只有 1 位聽者。

## 文獻

—

## 出處

[R4 [16][17]](../../docs/research-accompaniment-candidates-r4/research-accompaniment-candidates-r4.md)
