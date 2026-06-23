---
name: bilibili-uploaded-video-markdown
description: Use when the user wants a cloud-friendly, full-depth Bilibili Markdown note and has already uploaded the video file, subtitles, transcript, screenshots, metadata, or related artifacts to GPT Pro or another cloud agent. Use when the agent must create a detailed learning note, review digest, buying guide, or tutorial note from uploaded files only, without downloading from Bilibili; Markdown is only the delivery format, not a reduction in content depth.
---

# Bilibili Uploaded Video Markdown

Create a full-depth Markdown note from already uploaded Bilibili video artifacts. Use this version for cloud agents that cannot fetch the whole video, call `yt-dlp`, access browser cookies, or download subtitles from Bilibili.

Markdown is only the carrier: do not simplify the knowledge, reasoning, evidence, figure coverage, or explanation depth compared with the PDF skills. Do not rely on the Bilibili URL as the content source. Use the URL or BV id only as metadata/provenance when the user provides it.

## Expected Inputs

Use whichever uploaded files are available:

- video file: `.mp4`, `.mkv`, `.mov`, or similar
- subtitle file: `.srt`, `.vtt`, `.ass`, `.json`, or plain transcript
- screenshots, extracted frames, cover image, thumbnail, or contact sheets
- metadata text or JSON: title, uploader, BV id, duration, description, chapter list, part list
- user preference: learning note, buying guide, product comparison, tutorial digest, or Q&A-oriented summary

If both video and subtitles are missing, ask the user to upload at least one primary content source before summarizing.

If the user has not prepared the upload package yet, tell them to run the `prepare-video-upload-package` skill locally first. That local skill should produce `video.mp4`, `subtitles.srt`, `metadata.json`, `cover.jpg`, and `README.md` for upload.

## Workflow

1. Inventory uploaded files first. State which files will be used as video, subtitles/transcript, frames, cover, metadata, and optional screenshots.
2. Prefer timestamped subtitles or transcripts as the narrative spine.
3. Use the uploaded video only through tools available in the current environment. If frame extraction is available, sample around important subtitle intervals.
4. Never ask the cloud agent to download the Bilibili URL, fetch the full video, retrieve missing CC subtitles, or use browser cookies.
5. For multi-part Bilibili uploads, process only the uploaded parts. If the part mapping is unclear, ask the user to identify file order.
6. If frame extraction is unavailable, use uploaded screenshots/contact sheets and clearly state visual limitations.
7. Save or reference extracted images in `assets/` when the environment supports file output. If only inline output is possible, still write Markdown with clear image labels and timestamps.

## Output Contract

Create:

- `notes.md`: full-depth Markdown note, guide, or review digest
- `assets/`: extracted frames, crops, uploaded screenshots, cover, generated charts, and diagrams used by the note
- optional `source-map.md`: mapping of uploaded files to sections when many files were provided

Use relative links for local assets:

```markdown
![图 8：27 英寸 4K 推荐表的完整状态（part-01.srt 12:31-12:46）](assets/frame-008-4k-monitor-table.jpg)
```

## Pedagogical Standard

The Markdown notes must read like a strong human teacher is guiding the reader through the material.

- Keep the same knowledge density and teaching depth expected from PDF versions.
- Organize each major section so the reader understands motivation, main idea, mechanism, example/evidence, and takeaway.
- Explain why each concept appears, what problem it solves, and how the next idea follows.
- Preserve technical depth while introducing formalism only after plain-language intuition.
- Break dense sections into progressive subsections instead of compressing them into a shallow summary.
- Do not dump subtitles chronologically. Reconstruct the teaching flow when that improves understanding.
- Ground claims in uploaded subtitles, transcript text, frames, screenshots, metadata, or source filenames.

## Long Video Strategy

For long uploaded videos, do not rely on one monolithic pass.

- If the video is longer than 20 minutes, or subtitles contain more than 300 entries, split by uploaded chapters, part boundaries, coherent time windows, or subtitle ranges.
- When subagents are available, process segments in parallel. Require each segment result to include: teaching goal, core claims, formulas/code, required figures with provenance, and ambiguities.
- Keep overlaps when explanations cross segment boundaries.
- Integrate segment outputs into one coherent `notes.md`.

## Teaching Content Rules

Build the note from all available uploaded evidence:

- uploaded metadata, title, description, cover, part list, and chapters
- uploaded subtitles, transcript, and timestamped speech
- uploaded video frames, screenshots, contact sheets, tables, slides, diagrams, UI states, formulas, code, and charts
- short high-information dialogue segments when exact wording adds insight
- product names, model numbers, prices, rankings, measured values, test conditions, caveats, and scenario constraints for review videos

Skip low-value content:

- greetings, routine small talk, and sign-offs
- danmaku unless the user explicitly uploaded and requested it
- repeated channel logistics such as 一键三连, 关注投币
- sponsorship unless it affects a recommendation or claim

Keep substantive closing discussion when it includes synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Markdown Structure

For review, ranking, or purchase-guide videos:

```markdown
# 标题

## 输入文件与覆盖范围
## 一句话结论
## 适合谁 / 不适合谁
## 推荐清单
| 场景 | 型号/方案 | 推荐理由 | 风险/短板 | 证据 |
## 评测标准与判断框架
## 关键参数与实测表现
## 分产品/分方案详解
## 购买决策树
## 争议点与不确定性
## 总结与延伸
## 时间线索引
```

For knowledge videos and tutorials:

```markdown
# 标题

## 输入文件与覆盖范围
## 核心问题
## 结论速览
## 知识点拆解
## 机制解释 / 推导 / 操作步骤
## 公式、代码与示例
## 易错点与误解
## 本章小结
## 总结与延伸
## 时间线索引
```

Use `## 本章小结` at the end of major sections when the content is substantial.

## Writing Rules

- Write in Chinese unless the user asks for another language.
- Preserve full content depth. A Markdown output may be visually simpler, but it must not be a thinner summary.
- Separate `原视频观点`, `证据`, `机制解释`, `整理判断`, and `限制` when adding synthesis beyond uploaded source material.
- Use Markdown callouts or bold labels instead of LaTeX boxes:
  - `> [!IMPORTANT]` for core concepts, definitions, central claims, algorithm steps, and compact restatements after dense explanations
  - `> [!NOTE]` for background, side knowledge, terminology comparisons, engineering context, and intuition-building analogies
  - `> [!WARNING]` for common misunderstandings, hidden assumptions, failure points, misleading heuristics, and implementation mistakes
  - `> [!QUOTE]` for short high-signal dialogue, with speaker labels and timestamp/source file
- Keep figures outside callouts.
- For formulas, explain intuition first, show math in Markdown display math, then list every symbol.
- For code, explain the role before the fenced block and summarize expected behavior afterward.
- Do not fabricate missing screenshots, subtitles, prices, product names, measurements, timestamps, or benchmark values.
- Do not use LaTeX document structure or PDF compilation.

## Figure Handling

- Select frames from uploaded video, screenshots, or contact sheets only.
- Inspect candidate frames visually before naming, captioning, or inserting them.
- Do not infer frame meaning only from transcript text or filename.
- Prefer fully revealed slides, formulas, tables, whiteboards, dashboards, diagrams, and product comparison states.
- Compare nearby candidates when possible and keep the clearest complete frame.
- Crop or enlarge when necessary for readability.
- Include several figures when the video builds an idea in stages.
- Omit repetitive or low-information frames.

## Figure Time Provenance

Every image must include provenance in the caption or nearby text:

- If timestamps exist, include exact intervals from subtitles or transcript.
- If timestamps are missing, cite source filename and visible/contextual marker.
- Crops inherit the original frame or screenshot source.
- Do not invent timecodes.

## Visualization

When uploaded screenshots and prose are insufficient, add accurate generated visualizations as assets when the environment supports file output.

Use visualizations for process flows, architecture summaries, benchmark charts, ranking matrices, comparison tables, heatmaps, and summary diagrams. Do not add decorative graphics.

## Missing Data Policy

- Missing subtitles but video available: transcribe only if the environment has an audio/video transcription tool; otherwise summarize from visible frames and ask for subtitles for speech-level detail.
- Missing video but subtitles available: produce a transcript-grounded full-depth note and mark visual evidence as unavailable.
- Missing timestamps: preserve section order and cite source filenames, but do not invent timecodes.
- Low-quality frames: include only if they still support the claim; otherwise describe the limitation.

## Quality Checklist

Before delivery:

- the note explicitly lists which uploaded files were used
- the Markdown has PDF-level knowledge depth, not a lightweight abstract
- no instruction asks the agent to fetch Bilibili content remotely
- no important teaching content, caveat, parameter, example, formula, or recommendation was dropped
- recommendations and conclusions are backed by uploaded artifacts
- visual limitations are stated when uploaded files are incomplete
- chosen frames are complete and readable
- image links are relative where files are produced
