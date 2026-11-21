# 語言模型配的和弦

由 Claude（claude-opus-5-5）在 2026-11-21 的對話中，讀 `prototype/melody-to-performance/examples/make_examples.py` 裡的旋律音符後手動配和弦。不是自動程式，也沒有呼叫 API。

- 格式：`bars` 是每小節的 `[和弦, 拍數]` 清單，第 1 小節就是 MIDI 的第 1 小節（弱起小節也算一整小節）。
- `why` 是每段的配法理由，方便你聽的時候對照。
- 快樂頌 16 小節（4/4）、綠袖子 17 小節（3/4，含弱起）、茉莉花 14 小節（2/4）。
