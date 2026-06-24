---
name: youtube-uploaded-video-render-pdf
description: Use when the user wants a cloud-friendly YouTube video-to-PDF workflow and has uploaded the video file, subtitles, transcript, metadata, thumbnail, or related artifacts to GPT Pro or another cloud agent, so the agent must create a detailed LaTeX note and rendered PDF from uploaded files without downloading from YouTube.
---

# YouTube Uploaded Video Render PDF

Create a professional Chinese LaTeX note and rendered PDF from already uploaded YouTube video artifacts. Use this skill when the cloud agent cannot call `yt-dlp`, fetch the full video, retrieve captions, or browse YouTube directly.

Do not rely on the YouTube URL as the content source. Use the URL only as metadata/provenance when the user provides it.

## What the User Should Prepare Locally

Ask the user to upload one package folder or zip with these files:

- `video.mp4` or another playable video file
- `subtitles.srt` or `subtitles.vtt` whenever speech matters
- `metadata.json` from `yt-dlp`
- `cover.jpg` or `thumbnail.jpg` when available
- optional `README.md` with the original URL, target language, and user preference

If the user has not prepared these files yet, tell them to run the `prepare-video-upload-package` skill locally first. That local skill handles the low-token download/transcription/package phase before this cloud PDF workflow.

### Local Preparation Commands

Run these commands on a local machine before uploading files to the cloud agent.

Create a work folder:

```bash
mkdir -p youtube-upload/source
cd youtube-upload
```

Save metadata:

```bash
yt-dlp --dump-single-json "<YOUTUBE_URL>" > source/metadata.json
```

Download manual and auto captions when available:

```bash
yt-dlp \
  --write-subs \
  --write-auto-subs \
  --sub-langs "zh-Hans,zh-CN,zh,en.*" \
  --convert-subs srt \
  --skip-download \
  -o "source/%(title).120B [%(id)s].%(ext)s" \
  "<YOUTUBE_URL>"
```

Download thumbnail and video:

```bash
yt-dlp \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*+ba/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<YOUTUBE_URL>"
```

If the highest quality requires age-gated, private, member-only, or otherwise authenticated access, ask for explicit authorization to use browser cookies/login state before adding `--cookies-from-browser chrome`.

If no captions are available, extract audio and create an SRT locally. Prefer SenseVoiceSmall through FunASR for Chinese, English, and mixed-language videos. Use Moonshine Voice only for English-only low-latency transcription when available. Keep Whisper only as a last-resort fallback.

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<YOUTUBE_URL>"
uv run --with funasr --with modelscope --with torch --with torchaudio --with soundfile \
  python <prepare-video-upload-package>/scripts/sensevoice_to_srt.py \
  source/audio.wav --language auto --device cpu -o source/subtitles.srt
```

Rename files before upload so the cloud agent can identify them easily:

```bash
mv source/video.mp4 video.mp4
cp source/*.srt subtitles.srt
cp source/metadata.json metadata.json
cp source/*.jpg cover.jpg
```

If multiple subtitle languages exist, upload the best one for the requested output language and keep the original filename in `README.md`.

## Expected Uploaded Inputs

Use whichever uploaded files are available:

- video file: `.mp4`, `.mkv`, `.mov`, or similar
- subtitle file: `.srt`, `.vtt`, `.json`, or transcript text
- metadata JSON or text with title, channel, duration, description, chapters, links, and thumbnail information
- cover image or thumbnail
- optional pre-extracted screenshots/contact sheets

If both video and subtitles are missing, ask the user to upload at least one primary content source before writing.

## Workflow

1. Inventory uploaded files first. State which files are being used as video, subtitles/transcript, thumbnail, metadata, and optional screenshots.
2. Use uploaded subtitles as the primary timeline for segmenting and locating figures.
3. Use the uploaded video only through tools available in the current environment. Extract frames from local uploaded files; never fetch missing video content from YouTube.
4. If subtitles are missing but video is available, transcribe locally only if the environment has a transcription tool. Otherwise write a visual-only or partial PDF and clearly state the limitation.
5. For long videos, split by uploaded chapters or coherent subtitle ranges before writing.
6. Start from `assets/notes-template.tex`, fill metadata and cover path, write a complete `.tex`, then compile it to PDF.

## Writing Standard

Follow the original `youtube-render-pdf` teaching-note standard, adapted to uploaded files:

- write in Chinese unless the user asks for another language
- reconstruct the teaching flow instead of dumping transcript order
- include all high-value frames needed for understanding
- preserve concrete timestamps for every inserted frame or crop
- use `importantbox`, `knowledgebox`, `warningbox`, and `dialoguebox` only when they carry real teaching value
- skip sponsorship, greetings, like/subscribe prompts, and routine channel logistics unless they affect the lesson
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
- `assets/` containing thumbnail/cover and all referenced figures
- any generated subtitles if speech-to-text was used
- a short note listing the uploaded files used and any missing evidence

## Asset

- `assets/notes-template.tex`: default LaTeX template to copy and fill
