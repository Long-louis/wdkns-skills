---
name: bilibili-render-markdown
description: Use when the user provides a Bilibili video URL or BV id and wants a full-depth, figure-rich Markdown learning note, product review digest, buying guide, tutorial note, or screenshot-backed study artifact instead of a LaTeX/PDF document. Use for short or long Bilibili videos when Markdown is only the delivery format; content depth, teaching detail, evidence coverage, and figure rigor should match the PDF skill.
---

# Bilibili Render Markdown

Turn a Bilibili video into a full-depth Markdown note with local image assets. Markdown is only the carrier: do not simplify the knowledge, reasoning, evidence, figure coverage, or explanation depth compared with `bilibili-render-pdf`.

Use this skill for:

- short knowledge videos where the user wants dense study notes
- long lectures or tutorials where Markdown is preferred over PDF
- review, ranking, recommendation, and shopping-guide videos where screenshots and concrete claims must be preserved
- technical talks, code demos, formulas, diagrams, architecture explanations, and visual tutorials

Do not create LaTeX or render a PDF unless the user explicitly asks for it.

## Bilibili-Specific Handling

| Aspect | Handling |
|--------|----------|
| Subtitle scarcity | Try CC subtitles first, then Whisper/speech-to-text, then visual-only mode with explicit limitations |
| Login-gated HD | 1080P+ often requires cookies; use `yt-dlp --cookies-from-browser chrome` when allowed |
| Multi-part videos | Detect 分P videos and ask which parts to process before downloading |
| URL formats | Support `bilibili.com/video/BV...` and `b23.tv` short links |
| Danmaku | Do not use danmaku as a teaching source unless the user explicitly requests it |

## Output Contract

Create a portable folder containing:

- `notes.md`: the final full-depth Markdown document
- `assets/`: cover image, selected key frames, crops, generated charts, and diagrams
- optional `source/`: metadata JSON, subtitles, transcript, candidate frames, and contact sheets when useful for auditability

Use relative image links such as:

```markdown
![图 3：推荐表的完整展开状态（12:31-12:46）](assets/frame-003-monitor-table.jpg)
```

The Markdown must be readable offline and should not depend on the original video being available.

## Source Acquisition

### Metadata Inspection

1. Inspect metadata before writing: title, uploader, BV id, duration, cover, chapters, 分P list, description, subtitle availability, and thumbnail availability.
2. Expand `b23.tv` short links before processing.
3. Detect multi-part videos. List all parts and ask which parts to process when the user did not specify them.

### Subtitle Acquisition

Priority 1: CC subtitles.

Prefer manual subtitles over auto-generated subtitles. Prefer `zh-Hans`, `zh-CN`, `zh`, or `ai-zh`. Preserve timestamps until figure selection is complete.

```bash
yt-dlp --write-subs --sub-langs "zh-Hans,zh-CN,zh,ai-zh" --convert-subs srt \
  --skip-download -o "%(title)s.%(ext)s" "<URL>"
```

Priority 2: speech-to-text.

If no usable subtitles exist and speech matters, extract audio and transcribe to a timestamped SRT.

```bash
yt-dlp -x --audio-format wav -o "audio.%(ext)s" "<URL>"
whisper audio.wav --model medium --language zh --output_format srt --output_dir .
```

Priority 3: visual-only mode.

Use this only when subtitles/transcription are unavailable or unusable. State the limitation in `notes.md`.

### Video and Cover Download

1. Save the official cover image whenever available and place it near the top of `notes.md`.
2. Download the best usable video source for frame extraction. Use cookies when needed and allowed.
3. Keep source artifacts local when practical: metadata, cover, subtitles, transcript, video, extracted frames, and contact sheets.

## Pedagogical Standard

The Markdown notes must read like a strong human teacher is guiding the reader through the material.

- Keep the same knowledge density and teaching depth expected from the PDF version.
- Organize each major section so the reader understands motivation, main idea, mechanism, example/evidence, and takeaway.
- Explain why each concept appears, what problem it solves, and how the next idea follows.
- Preserve technical depth while introducing formalism only after plain-language intuition.
- Break dense sections into progressive subsections instead of compressing them into a shallow summary.
- Do not dump subtitles chronologically. Reconstruct the teaching flow when that improves understanding.
- Avoid vague abstractions. Ground claims in mechanisms, examples, variables, steps, observed phenomena, timestamps, figures, or speaker evidence.

## Long Video Strategy

For longer videos, do not rely on one monolithic pass.

- If the video is longer than 20 minutes, or the subtitle file contains more than 300 subtitle entries, split the work into smaller segments.
- Prefer chapter boundaries or 分P boundaries. If unavailable, split by coherent time windows or subtitle ranges.
- When subagents are available, process segments in parallel. Require each segment result to include: teaching goal, core claims, formulas/code, required figures with time provenance, and ambiguities.
- Keep small overlaps between neighboring segments when explanations cross boundaries.
- Integrate segment outputs into one coherent `notes.md`. The final Markdown must read like a unified note, not pasted chunks.

## Teaching Content Rules

Build the note from all available high-signal sources:

- title, description, chapters, 分P structure, and metadata
- official cover image
- on-screen diagrams, formulas, tables, plots, slides, architecture views, dashboards, UI states, and visual comparisons
- subtitle explanations, examples, jokes or metaphors that clarify a concept, and verbal emphasis
- short high-information dialogue segments when exact wording adds insight or presence
- code snippets shown or described in the video
- product names, model numbers, prices, rankings, measured values, test conditions, caveats, and scenario constraints for review videos

Skip low-value content:

- greetings and routine small talk
- repeated channel logistics, 一键三连, 关注投币, and routine sign-offs
- sponsorship unless it affects a recommendation or claim
- repetitive dialogue that adds no information

Keep the speaker's substantive closing discussion when it includes synthesis, limitations, future work, tradeoffs, advice, or open questions.

## Markdown Structure

Choose the structure that fits the video, but keep full detail.

For product reviews, rankings, and buying guides:

```markdown
# 标题

![封面](assets/cover.jpg)

## 视频信息与处理范围
## 一句话结论
## 适合谁 / 不适合谁
## 推荐清单
| 档位/场景 | 型号/方案 | 推荐理由 | 主要短板 | 价格/条件 | 证据时间点 |
## 评测标准与判断框架
## 关键参数与实测表现
## 分产品/分方案详解
### 产品 A
![图：完整可读的产品对比帧](assets/...)
- 原视频观点：
- 证据：
- 机制/原因：
- 风险和限制：
- 适合人群：
- 整理判断：
## 购买决策树
## 争议点与不确定性
## 总结与延伸
## 时间线索引
```

For knowledge videos and tutorials:

```markdown
# 标题

![封面](assets/cover.jpg)

## 视频信息与处理范围
## 核心问题
## 结论速览
## 知识点拆解
### 知识点 1
![图：支撑该知识点的关键帧](assets/...)
## 机制解释 / 推导 / 操作步骤
## 公式、代码与示例
## 易错点与误解
## 本章小结
## 总结与延伸
## 时间线索引
```

Use `## 本章小结` at the end of major sections when the content is substantial. Add `## 拓展阅读` when there are one or two worthwhile external links or concepts to follow.

## Writing Rules

1. Write in Chinese unless the user explicitly requests another language.
2. Preserve full content depth. A Markdown output may be visually simpler, but it must not be a thinner summary.
3. Separate the video's claims from your synthesis. Use labels such as `原视频观点`, `证据`, `机制解释`, `整理判断`, and `限制`.
4. Use Markdown callouts or bold labels instead of LaTeX boxes:
   - `> [!IMPORTANT]` for core concepts, definitions, central claims, algorithm steps, and compact restatements after dense explanations
   - `> [!NOTE]` for background, side knowledge, terminology comparisons, engineering context, and intuition-building analogies
   - `> [!WARNING]` for common misunderstandings, hidden assumptions, failure points, misleading heuristics, and implementation mistakes
   - `> [!QUOTE]` for short high-signal dialogue, with speaker labels and timestamp
5. Figures must stay outside callouts so image rendering remains reliable.
6. For formulas, explain the intuition first, then show math in Markdown display math, then list every symbol.
7. For code, explain its role before the fenced block and summarize expected behavior afterward.
8. Do not emit `[cite]` placeholders.

## Figure Handling

Select figures by necessity and teaching value, not by a quota or a bias toward visual sparsity.

- Bias toward recall before precision. Inspect more nearby candidates first rather than missing the complete frame.
- Frame understanding must come from direct visual inspection.
- Do not use OCR as a substitute for visual understanding.
- Do not infer semantic content only from subtitles, filenames, or guessed timestamps.
- Contact sheets and tiled strips are good for recall; final keep/reject decisions require inspecting actual images.
- For progressive slides, whiteboards, dashboards, or animations, find the final fully populated readable state.
- Include several figures in one section when the idea builds in stages.
- Omit repetitive or low-information frames.
- Crop, enlarge, or isolate the useful region when the full frame is too loose.
- Preserve readability of labels, formulas, parameters, and product names.

### Frame Selection Checklist

Before inserting any frame, verify:

- Relevance: it directly supports the surrounding paragraph.
- Required content visible: every referenced visual element is present.
- Fully revealed state: progressive content is complete.
- Best nearby candidate: compare multiple nearby frames.
- Readability: text, formulas, diagrams, or product details are legible.

### Frame Naming

- Use neutral timestamp-based names for raw candidates.
- Assign semantic names only after visual inspection.
- Name the actual visible content, not the intended paragraph topic.
- Reject partial, transitional, or ambiguous frames and keep searching.

## Figure Time Provenance

Every image derived from the video must include concrete provenance in the caption or nearby text:

```markdown
![图 4：完整的参数对比表（00:12:31-00:12:46）](assets/frame-004-parameter-table.jpg)
```

- Use subtitle-aligned intervals rather than vague chapter estimates.
- Crops inherit the original video interval.
- If several images share one interval, state it clearly once.
- If exact timestamps are unavailable, cite the source file and explain the limitation.

## Visualization

When screenshots and prose are insufficient, add accurate generated visualizations as image assets.

Use visualizations for:

- process flows, pipelines, and architecture overviews
- curves, benchmark charts, ablation comparisons, rankings, and recommendation matrices
- distributions, correlations, heatmaps, and other data relationships
- complex functions, surfaces, contour plots, and geometric intuition
- redrawn tables or comparisons that are clearer than screenshots
- summary diagrams that compress a section's core mechanism

Do not add decorative graphics.

## Final Checklist

Before delivery, verify:

- the Markdown has PDF-level knowledge depth, not a lightweight abstract
- no important teaching content, caveat, parameter, example, formula, or recommendation was dropped
- text and figures align; every figure supports nearby explanation
- chosen frames are complete and readable, not transitional
- every major recommendation or claim has timestamped evidence
- negative caveats and conditional advice are preserved
- generated diagrams or charts are accurate and useful
- image paths are relative and resolve from `notes.md`
- no `.tex`, LaTeX template, or PDF compilation step remains in the workflow

## Delivery

Deliver:

- `notes.md`
- `assets/` containing cover, selected frames, crops, and generated figures
- subtitles or transcript if created
- optional `source/` artifacts needed for auditability
