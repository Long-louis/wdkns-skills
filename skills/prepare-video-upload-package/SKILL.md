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

Also create a minimal upload ZIP next to the folder:

```text
<safe-video-title>-upload-minimal.zip
```

The minimal ZIP must contain only the root upload files, not `source/`, caches, audio intermediates, or low-quality comparison downloads.

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
- Ask for explicit user authorization before reading browser cookies or login state. Once authorized, use the login state to fetch the highest available quality, not merely the highest anonymous quality.
- Prefer the user's actual logged-in browser when known. On this Mac, Brave is the usual browser, so use `--cookies-from-browser brave` after explicit authorization.
- Avoid reusing an existing `source/video.mp4` blindly. `yt-dlp` may skip a better download when a lower-quality file already exists. Archive or overwrite old files deliberately, then verify the final video with `ffprobe`.
- Prefer the highest available video quality that is practically uploadable. If the file is too large, keep the high-quality source in `source/` and create a smaller upload copy only after recording the tradeoff in `README.md`.
- Use SenseVoiceSmall as the default local ASR model when platform subtitles are missing or unusable. It is preferred over Whisper for Chinese and Chinese-English mixed videos, and also supports English.
- For English-only live/low-latency transcription, Moonshine Voice is an optional alternative. Use it only when its file-transcription tooling is available locally.
- Keep Whisper only as a last-resort fallback when SenseVoice/Moonshine cannot run.
- Do not summarize the content beyond a short README description.

## ASR Model Policy

As of 2026-06, prefer these local Mac-friendly transcription choices:

1. **Default for Chinese, Cantonese, English, and mixed Chinese-English:** SenseVoiceSmall through FunASR.
   It supports Mandarin, Cantonese, English, Japanese, and Korean; is designed for low-latency inference; and is better suited to Chinese than Whisper in this workflow.
2. **Optional for English-only, live, or very low-latency use:** Moonshine Voice.
   It runs on device and supports macOS, but use it only if its local CLI/API can transcribe files into a usable transcript for the current environment.
3. **Fallback only:** Whisper.
   Use it only if the preferred models cannot be installed or executed.

Model download priority in China-region environments:

1. Try ModelScope model names first, such as `iic/SenseVoiceSmall`.
2. If HuggingFace is required, try `HF_ENDPOINT=https://aifasthub.com`, then `HF_ENDPOINT=https://hf-mirror.com`.
3. Use the local proxy only after mirrors fail.

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

## Preferred One-Command Workflow

Use `scripts/prepare_upload_package.py` for normal Bilibili and YouTube preparation. Manual commands below are for debugging or unusual cases.

After the user explicitly authorizes browser login state, run:

```bash
uv run python <path-to-this-skill>/scripts/prepare_upload_package.py \
  --allow-browser-cookies \
  --browser brave \
  "<VIDEO_URL>"
```

Without browser cookies:

```bash
uv run python <path-to-this-skill>/scripts/prepare_upload_package.py "<VIDEO_URL>"
```

Useful options:

- `--output-root outputs`: place packages under an output directory.
- `--format "<yt-dlp-format-selector>"`: override the default quality selector.
- `--skip-asr`: skip SenseVoiceSmall when platform subtitles are missing.
- `--no-proxy`: do not auto-use `http://127.0.0.1:7890`.

The script:

1. auto-detects local proxy port `7890`;
2. saves `yt-dlp --dump-single-json` metadata;
3. downloads video, subtitles, and cover into `source/`;
4. archives any pre-existing `source/video.mp4` before downloading a new one;
5. uses platform subtitles first, then SenseVoiceSmall only if subtitles are missing and ASR is not skipped;
6. normalizes `video.mp4`, `subtitles.srt`, `metadata.json`, `cover.jpg`, and `README.md` at the package root;
7. creates `<package>-minimal.zip` containing only the upload files.

For Bilibili, the default selector prefers browser-compatible H.264 video when available, then falls back to the best stream. If Bilibili reports premium-only formats such as `1080P 高码率` as unavailable, record that limitation in `README.md` and use the highest stream available to the authorized login state.

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

First try without cookies to see what public quality is available:

```bash
yt-dlp \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*+ba/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

If anonymous access is lower quality, ask the user for explicit approval to use browser login state. After approval, use the user's browser cookies and request the highest available quality. Prefer Brave on this Mac:

```bash
yt-dlp \
  --cookies-from-browser brave \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/bv*+ba/best" \
  --merge-output-format mp4 \
  --force-overwrites \
  -o "source/video.%(ext)s" \
  "<BILIBILI_URL_OR_BV>"
```

### 5. Transcribe if subtitles are missing or unusable

Extract audio:

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<BILIBILI_URL_OR_BV>"
```

Default Chinese/mixed-language transcription with SenseVoiceSmall:

```bash
uv run \
  --with funasr \
  --with modelscope \
  --with torch \
  --with torchaudio \
  --with soundfile \
  python <path-to-this-skill>/scripts/sensevoice_to_srt.py \
  source/audio.wav \
  --language auto \
  --device cpu \
  -o source/subtitles.srt
```

Use `--language zh` for clearly Mandarin videos and `--language en` for clearly English videos. Use `--language auto` for Chinese-English mixed videos.

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

Try to fetch the highest available quality. If YouTube login is needed for age-gated/private/member-only content, ask for explicit user authorization before using cookies:

```bash
yt-dlp \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*+ba/best" \
  --merge-output-format mp4 \
  -o "source/video.%(ext)s" \
  "<YOUTUBE_URL>"
```

With explicit authorization for browser login state, choose the browser that actually contains the login state:

```bash
yt-dlp \
  --cookies-from-browser brave \
  --write-thumbnail \
  --convert-thumbnails jpg \
  -f "bv*+ba/best" \
  --merge-output-format mp4 \
  --force-overwrites \
  -o "source/video.%(ext)s" \
  "<YOUTUBE_URL>"
```

### 4. Transcribe if captions are missing or unusable

```bash
yt-dlp -x --audio-format wav -o "source/audio.%(ext)s" "<YOUTUBE_URL>"
```

Default file transcription with SenseVoiceSmall:

```bash
uv run \
  --with funasr \
  --with modelscope \
  --with torch \
  --with torchaudio \
  --with soundfile \
  python <path-to-this-skill>/scripts/sensevoice_to_srt.py \
  source/audio.wav \
  --language auto \
  --device cpu \
  -o source/subtitles.srt
```

For English-only videos where Moonshine Voice is already available and file transcription works in the environment, it may be used instead. Keep SenseVoiceSmall as the default cross-language path.

## Normalize Package Files

After downloads finish, normalize filenames:

```bash
cp source/metadata.json metadata.json
cp source/video.mp4 video.mp4
cp <selected-platform-or-asr-subtitle>.srt subtitles.srt
cp <selected-cover>.jpg cover.jpg
```

Do not use broad globs such as `cp source/*.srt subtitles.srt`; they can select the wrong language or an old subtitle. Choose the final subtitle explicitly and record it in `README.md`.

Create `README.md`:

```markdown
# Upload Package

- Original URL:
- Platform: Bilibili / YouTube
- Video file: video.mp4
- Subtitle file: subtitles.srt
- Subtitle source: platform CC / auto captions / SenseVoiceSmall / Moonshine / Whisper fallback
- Metadata file: metadata.json
- Cover file: cover.jpg
- Video quality source: anonymous / browser cookies with user authorization
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
- `README.md` records whether browser cookies/login state were used with explicit user authorization
- minimal ZIP contains only root upload files and does not include `source/`, `.uv-cache`, model caches, extracted audio, or low-quality comparison downloads
- final video resolution/codec has been verified with `ffprobe`, especially after using browser cookies
- multi-part videos have clear part names and ordering

## Handoff

Tell the user to upload the package folder or zip to the cloud agent together with the target uploaded-video skill link. The cloud agent should use the uploaded-video Markdown or PDF skill for the token-heavy reading, frame selection, writing, and final synthesis phase.
