---
name: youtube-uploaded-video-markdown
description: Use when the user wants a cloud-friendly YouTube video summary skill and has already uploaded the video file, subtitles, transcript, screenshots, metadata, or related files to GPT Pro or another cloud agent, so the agent must create a Markdown learning note, review digest, or buying guide from uploaded artifacts without downloading from the YouTube URL.
---

# YouTube Uploaded Video Markdown

Create a Markdown note from already uploaded YouTube video artifacts. Use this version for cloud agents that cannot call `yt-dlp`, fetch the full video, retrieve captions, or browse YouTube directly.

Do not rely on the YouTube URL as the content source. The URL may be used only as metadata or provenance if the user provided it.

## Expected Inputs

Use whichever uploaded files are available:

- video file: `.mp4`, `.mkv`, `.mov`, or similar
- subtitle file: `.srt`, `.vtt`, `.json`, or plain transcript
- screenshots, extracted frames, cover image, thumbnail, or contact sheets
- metadata text: title, channel, duration, description, chapter list, product list, links
- user preference: learning note, buying guide, product comparison, tutorial digest, or Q&A-oriented summary

If both video and subtitles are missing, ask the user to upload at least one primary content source before summarizing.

## Workflow

1. Inventory uploaded files first. State which files will be used as video, subtitles/transcript, frames, thumbnail, and metadata.
2. Prefer timestamped subtitles or transcripts as the narrative spine.
3. Use the uploaded video only through tools available in the current environment. If frame extraction is available, sample around important subtitle intervals. If not, use uploaded screenshots/contact sheets and clearly note any visual limitation.
4. Never ask the cloud agent to download the YouTube URL, fetch captions, or retrieve the full video remotely.
5. Use uploaded chapters or description metadata when present, but verify important claims against subtitles, transcript, or frames.
6. Save or reference extracted images in `assets/` when the environment supports file output. If the environment only supports an inline answer, still write Markdown with clear image labels and timestamps.

## Output Contract

Create:

- `notes.md`: Markdown note, guide, or review digest
- `assets/`: extracted frames or uploaded screenshots used by the note when file output is supported
- optional `source-map.md`: a brief mapping of uploaded files to sections when many files were provided

Use relative links for local assets:

```markdown
![实测结果表](assets/frame-018-benchmark-table.jpg)
```

## Markdown Structure

For review, ranking, or purchase-guide videos:

```markdown
# 标题

## 输入文件与覆盖范围
## 一句话结论
## 适合谁买 / 不适合谁买
## 推荐清单
| 场景 | 产品/方案 | 推荐理由 | 风险/短板 | 证据 |
## 分产品笔记
## 关键截图
## 购买决策
## 时间线索引
```

For knowledge videos and tutorials:

```markdown
# 标题

## 输入文件与覆盖范围
## 核心问题
## 结论速览
## 知识点拆解
## 操作步骤 / 机制解释
## 易错点
## 时间线索引
```

## Writing Rules

- Write in Chinese unless the user asks for another language.
- Ground every important claim in uploaded subtitles, transcript text, frames, screenshots, chapters, or metadata.
- Preserve timestamps when available. If timestamps are unavailable, cite the source file and nearby visible/contextual marker.
- Separate `原视频观点` from `整理判断` when adding interpretation beyond the uploaded transcript.
- Skip greetings, sponsor reads, like/subscribe prompts, and routine channel logistics unless they materially affect the recommendation.
- Do not fabricate missing screenshots, subtitles, prices, product names, measurements, or benchmark results.
- Do not use LaTeX document structure or PDF compilation.

## Missing Data Policy

- Missing subtitles but video available: transcribe only if the environment has an audio/video transcription tool; otherwise summarize from visible frames and ask for subtitles for speech-level detail.
- Missing video but subtitles available: produce a transcript-grounded Markdown note and mark visual evidence as unavailable.
- Missing timestamps: preserve section order and cite source filenames, but do not invent timecodes.
- Low-quality frames: include only if they still support the claim; otherwise describe the limitation.

## Quality Checklist

Before delivery:

- the note explicitly lists which uploaded files were used
- no instruction asks the agent to fetch YouTube content remotely
- recommendations and conclusions are backed by uploaded artifacts
- visual limitations are stated when uploaded files are incomplete
- image links are relative where files are produced
