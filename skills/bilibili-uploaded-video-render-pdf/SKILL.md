---
name: bilibili-uploaded-video-render-pdf
description: Use when the user wants a cloud-friendly Bilibili video-to-PDF workflow and has uploaded the video file, subtitles, metadata, cover image, or related artifacts to GPT Pro or another cloud agent, so the agent must create a detailed LaTeX note and rendered PDF from uploaded files without downloading from Bilibili.
---

# Bilibili Uploaded Video Render PDF

Create a professional Chinese LaTeX note and rendered PDF from already uploaded Bilibili video artifacts. Use this skill when the cloud agent cannot fetch the full video, use browser cookies, call `yt-dlp`, or retrieve Bilibili subtitles directly.

Do not rely on the Bilibili URL as the content source. Use the URL or BV id only as metadata/provenance when the user provides it.

## What the User Should Prepare Locally

Ask the user to upload one package folder or zip with these files:

- `video.mp4` or another playable video file
- `subtitles.srt` or `subtitles.vtt` whenever speech matters
- `metadata.json` from `yt-dlp`
- `cover.jpg` or `cover.png` when available
- optional `README.md` with the original URL, selected part number, target language, and any user preference

For Bilibili multi-part videos, upload only the selected parts or name files clearly as `part-01.mp4`, `part-01.srt`, etc.

### Local Preparation Commands

Run these commands on a local machine before uploading files to the cloud agent.

Create a work folder:

```bash
mkdir -p bilibili-upload/source
cd bilibili-upload
```

Save metadata:

```bash
yt-dlp --dump-single-json "<BILIBILI_URL_OR_BV>" > source/metadata.json
```

Download subtitles if Bilibili exposes them:

```bash
yt-dlp \
  --write-subs \
  --sub-langs "zh-Hans,zh-CN,zh,ai-zh" \
  --convert-subs srt \
  --skip-download \
  -o "source/%(title).120B [%(id)s].%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

Download the cover and video. Add `--cookies-from-browser chrome` when the desired resolution requires login:

```bash
yt-dlp \
  --cookies-from-browser chrome \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*[height<=1080]+ba/b[height<=1080]/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

If no platform subtitles are available, extract audio and create an SRT locally:

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<BILIBILI_URL_OR_BV>"
whisper source/audio.wav --model medium --language zh --output_format srt --output_dir source
```

Rename files before upload so the cloud agent can identify them easily:

```bash
mv source/video.mp4 video.mp4
cp source/*.srt subtitles.srt
cp source/metadata.json metadata.json
cp source/*.jpg cover.jpg
```

If a file is missing, do not fabricate it. Upload the best available set and state what is missing.

## Expected Uploaded Inputs

Use whichever uploaded files are available:

- video file: `.mp4`, `.mkv`, `.mov`, or similar
- subtitle file: `.srt`, `.vtt`, `.ass`, `.json`, or transcript text
- metadata JSON or text with title, uploader, BV id, duration, description, chapters, and part list
- cover image or thumbnail
- optional pre-extracted screenshots/contact sheets

If both video and subtitles are missing, ask the user to upload at least one primary content source before writing.

## Workflow

1. Inventory uploaded files first. State which files are being used as video, subtitles/transcript, cover, metadata, and optional screenshots.
2. Use uploaded subtitles as the primary timeline for segmenting and locating figures.
3. Use the uploaded video only through tools available in the current environment. Extract frames from local uploaded files; never fetch missing video content from Bilibili.
4. If subtitles are missing but video is available, transcribe locally only if the environment has a transcription tool. Otherwise write a visual-only or partial PDF and clearly state the limitation.
5. For long videos, split by uploaded chapters, part boundaries, or coherent subtitle ranges before writing.
6. Start from `assets/notes-template.tex`, fill metadata and cover path, write a complete `.tex`, then compile it to PDF.

## Writing Standard

Follow the original `bilibili-render-pdf` teaching-note standard, adapted to uploaded files:

- write in Chinese unless the user asks for another language
- reconstruct the teaching flow instead of dumping transcript order
- include all high-value frames needed for understanding
- preserve concrete timestamps for every inserted frame or crop
- use `importantbox`, `knowledgebox`, `warningbox`, and `dialoguebox` only when they carry real teaching value
- keep Bilibili danmaku out of the teaching source unless the user explicitly uploaded and requested it
- include the speaker's substantive closing discussion when present
- end with a synthesis section such as `\section{总结与延伸}`

## Figure Rules

- Select frames from uploaded video or uploaded screenshots only.
- Inspect candidate frames visually before naming, captioning, or inserting them.
- Prefer fully revealed slides, formulas, tables, whiteboards, dashboards, and diagrams.
- Crop or enlarge when necessary for readability.
- Add a concrete time interval footnote for every video-derived figure when timestamps exist.
- If timestamps are missing, cite the source filename and explain that exact time provenance is unavailable.

## Delivery

Deliver:

- the final `.tex` file
- the compiled `.pdf` file
- `assets/` containing cover and all referenced figures
- any generated subtitles if speech-to-text was used
- a short note listing the uploaded files used and any missing evidence

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
