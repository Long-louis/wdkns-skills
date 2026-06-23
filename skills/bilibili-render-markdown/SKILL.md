---
name: bilibili-render-markdown
description: Use when the user provides a Bilibili video URL or BV id and wants a lightweight Markdown learning note, buying guide, review digest, or screenshot-rich summary instead of a LaTeX/PDF note, especially for short knowledge videos, product comparisons, recommendations, tutorials, and videos where key frames plus concise explanations matter more than polished typesetting.
---

# Bilibili Render Markdown

Turn a Bilibili video into a Markdown note with local image assets. Prefer this skill for short or medium videos, review videos, shopping guides, product roundups, practical tutorials, and dense knowledge clips where the user wants to read the key information without watching the whole video.

Do not create LaTeX or render a PDF unless the user explicitly asks for it.

## Output Contract

Create a folder containing:

- `notes.md`: the final Markdown document
- `assets/`: cover image, selected key frames, crops, and any optional comparison charts
- optional `source/`: metadata JSON, subtitles, transcript, and frame contact sheets when useful for auditability

The Markdown must be self-contained enough to read offline, with relative image links such as `![caption](assets/frame-001-monitor-comparison.jpg)`.

## Source Acquisition

1. Inspect metadata first: title, uploader, duration, cover, chapters, pages, description, and subtitle availability.
2. Expand `b23.tv` short links before processing.
3. Detect multi-part videos. If multiple parts are present and the user did not specify a part, list the parts and ask which ones to process.
4. Prefer Bilibili CC subtitles when available:

```bash
yt-dlp --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt --skip-download "<URL>"
```

5. If subtitles are unavailable and the video has meaningful speech, extract audio and transcribe with Whisper or another available speech-to-text tool.
6. Download the best usable video or stream segment needed for frame extraction. For 1080P+ on Bilibili, try browser cookies when the user permits it.
7. Save the official cover image when available. Use it near the top of `notes.md`; do not replace it with a random frame.

## Frame Selection

Use frames as evidence, not decoration.

- For product reviews and buying guides, capture the frame where each recommended item, ranking table, parameter table, price card, measured result, visual comparison, or conclusion slide is most readable.
- For knowledge videos, capture diagrams, formulas, code, flowcharts, before/after states, whiteboard conclusions, and any screen state the narration depends on.
- Generate dense candidates around subtitle-aligned intervals, inspect contact sheets or individual images, then keep only high-information frames.
- Do not infer frame content from nearby subtitles alone. Visually inspect frames before naming, captioning, or citing them.
- Prefer the final fully revealed state of progressive slides, dashboards, animations, or whiteboards.
- Crop when the useful region is small, but keep the original frame if context is important.
- Record timestamp provenance in captions, for example: `图 3：27 英寸 4K 显示器推荐表（12:31-12:46）`.

## Markdown Structure

Choose the structure that matches the video type.

For product reviews, rankings, and buying guides:

```markdown
# 标题

![cover](assets/cover.jpg)

## 一句话结论
## 适合谁买 / 不适合谁买
## 推荐清单
| 档位/场景 | 型号 | 关键优点 | 主要短板 | 价格/条件 | 证据时间点 |
## 关键参数与实测表现
## 分产品笔记
### 产品 A
![frame](assets/...)
- 核心卖点：
- 主要问题：
- 适合人群：
- 原视频依据：
## 购买决策
## 时间线索引
```

For knowledge videos and tutorials:

```markdown
# 标题

![cover](assets/cover.jpg)

## 核心问题
## 结论速览
## 知识点拆解
### 知识点 1
![frame](assets/...)
## 操作步骤 / 机制解释
## 易错点
## 可复用清单
## 时间线索引
```

## Writing Rules

- Write in Chinese unless the user asks for another language.
- Optimize for information density, evidence, and retrieval. Avoid polished textbook expansion when a concise guide is more useful.
- Preserve concrete names, prices, parameters, rankings, caveats, timestamps, and scenario constraints.
- Separate the video's claims from your synthesis. Use labels such as `原视频观点` and `整理判断` when adding interpretation.
- Keep sponsored content, greetings, calls to like/subscribe, and routine channel logistics out of the main note unless they affect the recommendation.
- For formulas or code, use normal Markdown fences and math syntax; do not introduce LaTeX document structure.
- Add a final `时间线索引` table with important moments and local image references.

## Quality Checklist

Before delivery:

- every included screenshot is readable and directly supports nearby text
- every recommended product, tool, method, or conclusion has a timestamp or frame-backed source
- important negative caveats are preserved, not only the positive recommendations
- image links are relative and resolve from `notes.md`
- no `.tex`, LaTeX template, or PDF compilation step remains in the workflow
