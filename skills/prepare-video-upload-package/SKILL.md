---
name: prepare-video-upload-package
description: Use when the user wants a local code agent to prepare video artifacts before sending them to a cloud GPT Pro or Agent workflow, including downloading Bilibili or YouTube video files, subtitles, metadata, cover images, and transcribing audio to SRT when captions are missing, without doing the token-heavy summarization itself.
---

# Prepare Video Upload Package

Prepare a local upload package for the cloud `uploaded-video` Markdown or PDF skills. This skill handles the low-token, local execution phase: download source files, collect metadata, obtain or transcribe subtitles, normalize filenames, and package everything for upload.

Do not perform the deep summary, teaching-note writing, frame-by-frame explanation, or PDF/Markdown final synthesis here. Those belong to the cloud uploaded-video skills.

## Output Contract

Create one folder per video:

```text
<safe-video-title>-upload/
├── video.mp4
├── subtitles.srt
├── metadata.json
├── cover.jpg
├── README.md
└── source/
    ├── raw files from yt-dlp
    ├── optional audio.wav
    └── optional alternate subtitle tracks
```

Required when available:

- `video.mp4`: playable local video file
- `subtitles.srt`: timestamped subtitle or speech-to-text transcript
- `metadata.json`: `yt-dlp --dump-single-json` output
- `cover.jpg`: cover/thumbnail image
- `README.md`: original URL, platform, selected part/range, subtitle source, missing files, and intended downstream skill

If a required artifact cannot be obtained, keep the package and record the limitation in `README.md`.

## Environment Rules

- Use local execution for downloads and transcription.
- Use `yt-dlp` for metadata, subtitles, thumbnails, and video.
- Use Whisper or another available speech-to-text tool only when platform subtitles are missing or unusable.
- Prefer video up to 1080p unless the user requests higher resolution; higher resolutions can make upload packages unnecessarily large.
- For Bilibili HD content, use browser cookies only when the user permits it.
- Do not summarize the content beyond a short README description.

## Common Setup

Create a working directory:

```bash
mkdir -p video-upload-work/source
cd video-upload-work
```

Check `yt-dlp`:

```bash
yt-dlp --version
```

If `yt-dlp` is missing, install it using the environment's preferred package manager. If Python package installation is needed, use `uv tool install yt-dlp` or another `uv`-based command rather than system `pip`.

## Bilibili Workflow

### 1. Save metadata

```bash
yt-dlp --dump-single-json "<BILIBILI_URL_OR_BV>" > source/metadata.json
```

### 2. Inspect parts and formats

```bash
yt-dlp --list-formats "<BILIBILI_URL_OR_BV>"
```

For multi-part videos, inspect metadata and ask the user which part(s) to prepare if unclear. Name outputs with `part-01`, `part-02`, etc.

### 3. Download platform subtitles

```bash
yt-dlp \
  --write-subs \
  --sub-langs "zh-Hans,zh-CN,zh,ai-zh" \
  --convert-subs srt \
  --skip-download \
  -o "source/%(title).120B [%(id)s].%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

Prefer manual subtitles over auto-generated subtitles when both exist.

### 4. Download cover and video

Without cookies:

```bash
yt-dlp \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*[height<=1080]+ba/b[height<=1080]/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

With Chrome cookies when needed and permitted:

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

### 5. Transcribe if subtitles are missing

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<BILIBILI_URL_OR_BV>"
whisper source/audio.wav --model medium --language zh --output_format srt --output_dir source
```

Use a smaller Whisper model only when speed or hardware constraints matter more than transcript quality.

## YouTube Workflow

### 1. Save metadata

```bash
yt-dlp --dump-single-json "<YOUTUBE_URL>" > source/metadata.json
```

### 2. Download subtitles

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

Prefer manual captions. If the final note will be Chinese and only English captions exist, upload the English SRT and mention it in `README.md`; the cloud agent can translate while summarizing.

### 3. Download thumbnail and video

```bash
yt-dlp \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*[height<=1080]+ba/b[height<=1080]/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<YOUTUBE_URL>"
```

### 4. Transcribe if captions are missing

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<YOUTUBE_URL>"
whisper source/audio.wav --model medium --output_format srt --output_dir source
```

Set `--language zh` only when the speech language is known to be Chinese.

## Normalize Package Files

After downloads finish, normalize filenames:

```bash
cp source/metadata.json metadata.json
cp source/video.mp4 video.mp4
cp source/*.srt subtitles.srt
cp source/*.jpg cover.jpg
```

If globbing selects the wrong file, choose manually and record the selected subtitle/cover in `README.md`.

Create `README.md`:

```markdown
# Upload Package

- Original URL:
- Platform: Bilibili / YouTube
- Video file: video.mp4
- Subtitle file: subtitles.srt
- Subtitle source: platform CC / auto captions / Whisper
- Metadata file: metadata.json
- Cover file: cover.jpg
- Selected parts or ranges:
- Missing or low-quality artifacts:
- Intended downstream skill: bilibili-uploaded-video-markdown / youtube-uploaded-video-markdown / bilibili-uploaded-video-render-pdf / youtube-uploaded-video-render-pdf
```

## Verification Checklist

Before handing the package to the user:

- `video.mp4` exists and is playable
- `subtitles.srt` exists, is timestamped, and roughly matches the video
- `metadata.json` exists and is valid JSON
- `cover.jpg` exists, or `README.md` states why no cover was available
- `README.md` records URL, platform, subtitle source, and missing artifacts
- package does not contain unrelated large files
- multi-part videos have clear part names and ordering

## Handoff

Tell the user to upload the package folder or zip to the cloud agent together with the target uploaded-video skill link. The cloud agent should use the uploaded-video Markdown or PDF skill for the token-heavy reading, frame selection, writing, and final synthesis phase.
