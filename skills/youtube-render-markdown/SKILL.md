---
name: youtube-render-markdown
description: Use when the user provides a YouTube URL and wants a lightweight Markdown learning note, buying guide, review digest, recommendation summary, or screenshot-rich tutorial note instead of a LaTeX/PDF document, especially for short knowledge videos, product comparisons, rankings, practical demos, and videos where key frames plus concise explanations matter more than polished typesetting.
---

# YouTube Render Markdown

Turn a YouTube video into a Markdown note with local image assets. Prefer this skill for short or medium videos, product reviews, buying guides, recommendation roundups, tutorials, and dense knowledge clips.

Do not create LaTeX or render a PDF unless the user explicitly asks for it.

## Output Contract

Create a folder containing:

- `notes.md`: the final Markdown document
- `assets/`: cover image, selected key frames, crops, and optional charts
- optional `source/`: metadata JSON, subtitles, transcript, and contact sheets when useful for auditability

Use relative Markdown image links so the folder remains portable.

## Source Acquisition

1. Inspect metadata first: title, channel, duration, chapters, description, thumbnail, and subtitle tracks.
2. Prefer manual subtitles over auto-generated subtitles. Prefer the language requested by the user; otherwise use the video's primary language or the closest available track.
3. Preserve subtitle timestamps until frame selection is complete.
4. Download the official thumbnail when available and place it near the top of `notes.md`.
5. Download the best usable video source needed for frame extraction. If the video is long, download only the needed ranges when practical.
6. If subtitles are unavailable and speech matters, extract audio and transcribe with an available speech-to-text tool.

Example subtitle command:

```bash
yt-dlp --write-subs --write-auto-subs --convert-subs srt --skip-download "<URL>"
```

## Frame Selection

Use frames as evidence, not decoration.

- For reviews and buying guides, capture product lineups, ranking tables, spec tables, measured results, price cards, comparison shots, and final recommendation slides.
- For tutorials and knowledge videos, capture diagrams, formulas, code, workflows, terminal/browser states, UI settings, and visual examples that the explanation depends on.
- Start from subtitle or chapter intervals, generate dense nearby candidates, inspect them visually, and keep the most readable final state.
- Do not infer image content only from subtitles, filenames, or timestamps.
- Crop when it improves readability, but preserve enough context for trust.
- Put timestamp provenance in captions, for example: `图 2：推荐档位对比（08:12-08:44）`.

## Markdown Structure

For product reviews, rankings, and buying guides:

```markdown
# 标题

![cover](assets/cover.jpg)

## 一句话结论
## 适合谁买 / 不适合谁买
## 推荐清单
| 场景 | 产品 | 推荐理由 | 短板 | 条件/价格 | 证据时间点 |
## 关键参数与实测表现
## 分产品笔记
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
## 操作步骤 / 机制解释
## 易错点
## 可复用清单
## 时间线索引
```

## Writing Rules

- Write in Chinese unless the user asks for another language.
- Optimize for fast reading, source-backed claims, and practical reuse.
- Preserve concrete names, prices, parameters, rankings, settings, caveats, and scenario constraints.
- Separate the video's claims from your own synthesis when adding interpretation.
- Skip greetings, sponsor reads, like/subscribe prompts, and routine channel logistics unless they materially affect the recommendation.
- For code, commands, formulas, and tables, use standard Markdown. Do not introduce LaTeX document scaffolding.
- Add a final `时间线索引` with important timestamps, brief descriptions, and related local image files.

## Quality Checklist

Before delivery:

- every screenshot is visually inspected and supports nearby text
- each recommendation or key conclusion has timestamped evidence
- negative caveats and conditional advice are preserved
- image paths are relative and resolve from `notes.md`
- no `.tex`, LaTeX template, or PDF compilation step remains in the workflow
