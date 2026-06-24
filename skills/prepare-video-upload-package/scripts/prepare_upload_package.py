#!/usr/bin/env python3
"""Prepare a cloud-uploadable video package from a Bilibili or YouTube URL."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any


ROOT_FILES = ("video.mp4", "subtitles.srt", "metadata.json", "cover.jpg", "README.md")
MIB = 1024 * 1024


def run(args: list[str], *, stdout: Any = None, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(args), flush=True)
    subprocess.run(args, check=True, stdout=stdout, env=env)


def capture_json(args: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    print("+ " + " ".join(args), flush=True)
    result = subprocess.run(args, check=True, capture_output=True, text=True, env=env)
    return json.loads(result.stdout)


def port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def safe_name(text: str, max_len: int = 80) -> str:
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^\w.-]+", "-", text, flags=re.UNICODE)
    text = text.strip("-._")
    return (text or "video")[:max_len]


def platform_from(metadata: dict[str, Any], url: str) -> str:
    extractor = (metadata.get("extractor_key") or metadata.get("extractor") or "").lower()
    if "bilibili" in extractor or "bilibili.com" in url:
        return "bilibili"
    if "youtube" in extractor or "youtu" in url:
        return "youtube"
    return safe_name(extractor or "video", 24).lower()


def build_ytdlp_base(args: argparse.Namespace, proxy: str | None) -> list[str]:
    cmd = ["yt-dlp"]
    if proxy:
        cmd += ["--proxy", proxy]
    if args.allow_browser_cookies:
        cmd += ["--cookies-from-browser", args.browser]
    return cmd


def subtitle_langs(platform: str) -> str:
    if platform == "bilibili":
        return "zh-Hans,zh-CN,zh,ai-zh"
    if platform == "youtube":
        return "zh-Hans,zh-CN,zh,en.*"
    return "zh-Hans,zh-CN,zh,en.*"


def format_selector(platform: str, requested: str | None) -> str:
    if requested:
        return requested
    if platform == "bilibili":
        # Prefer browser-compatible H.264 when available, then fall back to best.
        return "bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/bv*+ba/best"
    return "bv*+ba/best"


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def choose_subtitle(source_dir: Path) -> tuple[Path | None, str]:
    subtitles = sorted(source_dir.glob("video*.srt"))
    if not subtitles:
        return None, "missing"
    priorities = ("zh-Hans", "zh-CN", ".zh.", "zh", "ai-zh", "en")
    for marker in priorities:
        for subtitle in subtitles:
            if marker in subtitle.name:
                return subtitle, f"platform subtitle: {subtitle.name}"
    return subtitles[0], f"platform subtitle: {subtitles[0].name}"


def ffprobe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name,r_frame_rate",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def quality_summary(path: Path) -> dict[str, str]:
    info = ffprobe(path)
    stream = (info.get("streams") or [{}])[0]
    fmt = info.get("format") or {}
    return {
        "codec": str(stream.get("codec_name") or "unknown"),
        "width": str(stream.get("width") or "unknown"),
        "height": str(stream.get("height") or "unknown"),
        "fps": str(stream.get("r_frame_rate") or "unknown"),
        "duration": str(fmt.get("duration") or "unknown"),
        "size": str(fmt.get("size") or path.stat().st_size),
    }


def numeric(value: str, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def scale_filter(width: int, video_kbps: int) -> str:
    if video_kbps < 420:
        max_width = min(width, 854)
    elif video_kbps < 850:
        max_width = min(width, 1280)
    else:
        max_width = min(width, 1920)
    return f"scale='min({max_width},iw)':-2"


def compress_for_upload(source: Path, dest: Path, max_upload_mib: int) -> tuple[dict[str, str], str]:
    source_quality = quality_summary(source)
    source_size = source.stat().st_size
    max_bytes = max_upload_mib * MIB
    if source_size <= max_bytes:
        shutil.copy2(source, dest)
        return source_quality, f"not compressed; source video is within {max_upload_mib} MiB"

    duration = max(numeric(source_quality.get("duration", "0")), 1.0)
    width = int(numeric(source_quality.get("width", "1280"), 1280))
    # Leave room for subtitles, cover, metadata, README, and MP4/container variance.
    target_bytes = max((max_upload_mib - 12) * MIB, int(max_bytes * 0.82))
    attempts = [1.0, 0.88, 0.76]
    last_note = ""

    for i, factor in enumerate(attempts, 1):
        adjusted_target = int(target_bytes * factor)
        total_kbps = max(int((adjusted_target * 8) / duration / 1000), 260)
        audio_kbps = 64 if total_kbps < 800 else 96
        video_kbps = max(total_kbps - audio_kbps, 180)
        vf = scale_filter(width, video_kbps)
        tmp = dest.with_suffix(f".compressed-{i}.mp4")
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(source),
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-b:v",
                f"{video_kbps}k",
                "-maxrate",
                f"{int(video_kbps * 1.25)}k",
                "-bufsize",
                f"{int(video_kbps * 2.5)}k",
                "-c:a",
                "aac",
                "-b:a",
                f"{audio_kbps}k",
                "-movflags",
                "+faststart",
                str(tmp),
            ]
        )
        final_size = tmp.stat().st_size
        last_note = (
            f"compressed from {source_size} bytes to {final_size} bytes "
            f"with target video bitrate {video_kbps}k and audio bitrate {audio_kbps}k"
        )
        if final_size <= max_bytes:
            tmp.replace(dest)
            return source_quality, last_note
        tmp.unlink()

    raise RuntimeError(f"Compressed video still exceeds {max_upload_mib} MiB; last attempt: {last_note}")


def normalize(
    package_dir: Path,
    source_dir: Path,
    subtitle_path: Path | None,
    max_upload_mib: int,
) -> dict[str, str]:
    video = source_dir / "video.mp4"
    if not video.exists():
        candidates = sorted(source_dir.glob("video.*"))
        video = first_existing([p for p in candidates if p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}]) or video
    if not video.exists():
        raise FileNotFoundError("No downloaded video file found under source/")

    source_quality, compression_note = compress_for_upload(video, package_dir / "video.mp4", max_upload_mib)
    if subtitle_path and subtitle_path.exists():
        shutil.copy2(subtitle_path, package_dir / "subtitles.srt")

    shutil.copy2(source_dir / "metadata.json", package_dir / "metadata.json")

    cover = first_existing(
        sorted(source_dir.glob("video.jpg"))
        + sorted(source_dir.glob("video.jpeg"))
        + sorted(source_dir.glob("video.png"))
        + sorted(source_dir.glob("video.webp"))
    )
    if cover:
        shutil.copy2(cover, package_dir / "cover.jpg")

    upload_quality = quality_summary(package_dir / "video.mp4")
    upload_quality["source_codec"] = source_quality.get("codec", "unknown")
    upload_quality["source_width"] = source_quality.get("width", "unknown")
    upload_quality["source_height"] = source_quality.get("height", "unknown")
    upload_quality["source_size"] = source_quality.get("size", "unknown")
    upload_quality["compression_note"] = compression_note
    return upload_quality


def transcribe_if_needed(args: argparse.Namespace, package_dir: Path, source_dir: Path, skill_dir: Path) -> tuple[Path | None, str]:
    subtitle_path, subtitle_source = choose_subtitle(source_dir)
    if subtitle_path:
        return subtitle_path, subtitle_source
    if args.skip_asr:
        return None, "missing; ASR skipped by --skip-asr"

    audio = source_dir / "audio.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source_dir / "video.mp4"),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio),
        ]
    )
    output = source_dir / "subtitles.srt"
    env = os.environ.copy()
    env.setdefault("MODELSCOPE_CACHE", str(package_dir / ".modelscope-cache"))
    run(
        [
            "uv",
            "run",
            "--with",
            "funasr",
            "--with",
            "modelscope",
            "--with",
            "torch",
            "--with",
            "torchaudio",
            "--with",
            "soundfile",
            "python",
            str(skill_dir / "sensevoice_to_srt.py"),
            str(audio),
            "--language",
            args.language,
            "--device",
            args.device,
            "-o",
            str(output),
        ],
        env=env,
    )
    return output, "SenseVoiceSmall local ASR"


def write_readme(
    package_dir: Path,
    metadata: dict[str, Any],
    platform: str,
    args: argparse.Namespace,
    quality: dict[str, str],
    subtitle_source: str,
    proxy: str | None,
) -> None:
    title = metadata.get("title") or metadata.get("fulltitle") or ""
    uploader = metadata.get("uploader") or metadata.get("channel") or metadata.get("owner") or ""
    duration = quality.get("duration", "unknown")
    size = quality.get("size", "unknown")
    cookie_line = (
        f"{args.browser} browser cookies, explicitly enabled with --allow-browser-cookies"
        if args.allow_browser_cookies
        else "anonymous/no browser cookies"
    )
    text = f"""# Video Cloud Summary Upload Package

## Source

- Platform: {platform}
- URL: {args.url}
- ID: {metadata.get("id") or metadata.get("display_id") or ""}
- Title: {title}
- Uploader: {uploader}
- Duration seconds: {duration}

## Files

- `video.mp4`: final upload video.
- `subtitles.srt`: timestamped subtitle or transcript, when available.
- `metadata.json`: `yt-dlp --dump-single-json` metadata.
- `cover.jpg`: cover or thumbnail image, when available.
- `source/`: raw and intermediate local files; do not upload unless debugging is needed.

## Preparation Details

- Video format selector: `{format_selector(platform, args.format)}`
- Final video: {quality.get("codec")} {quality.get("width")}x{quality.get("height")} at {quality.get("fps")}
- Final size bytes: {size}
- Source video: {quality.get("source_codec")} {quality.get("source_width")}x{quality.get("source_height")}, {quality.get("source_size")} bytes
- Upload compression: {quality.get("compression_note")}
- Max upload ZIP target: {args.max_upload_mib} MiB
- Subtitle source: {subtitle_source}
- Login state: {cookie_line}
- Proxy: {proxy or "not used"}

## Upload Guidance

Upload the minimal ZIP next to this folder, or upload only the five root files:

- `video.mp4`
- `subtitles.srt`
- `metadata.json`
- `cover.jpg`
- `README.md`

Cloud agent instruction: use the uploaded files as the source of truth. Do not download the video again from the original platform.
"""
    (package_dir / "README.md").write_text(text, encoding="utf-8")


def create_minimal_zip(package_dir: Path) -> Path:
    zip_path = package_dir.with_name(package_dir.name + "-minimal.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for name in ROOT_FILES:
            path = package_dir / name
            if path.exists():
                zf.write(path, arcname=name)
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--package-dir")
    parser.add_argument("--browser", default="brave", help="Browser name for yt-dlp --cookies-from-browser")
    parser.add_argument("--allow-browser-cookies", action="store_true", help="Explicitly allow reading browser login cookies")
    parser.add_argument("--format", help="Override yt-dlp format selector")
    parser.add_argument("--language", default="auto", choices=["auto", "zh", "en", "yue", "ja", "ko", "nospeech"])
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--skip-asr", action="store_true")
    parser.add_argument("--max-upload-mib", type=int, default=300, help="Compress root video when the upload package would exceed this size")
    parser.add_argument("--no-proxy", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent
    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    proxy = None if args.no_proxy else ("http://127.0.0.1:7890" if port_open("127.0.0.1", 7890) else None)
    base = build_ytdlp_base(args, proxy)

    metadata = capture_json(base + ["--dump-single-json", args.url])
    platform = platform_from(metadata, args.url)
    video_id = metadata.get("id") or metadata.get("display_id") or safe_name(args.url, 40)
    package_dir = Path(args.package_dir).expanduser().resolve() if args.package_dir else output_root / f"{platform}-{safe_name(str(video_id), 80)}-upload"
    source_dir = package_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = source_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    existing_video = source_dir / "video.mp4"
    if existing_video.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        archived = source_dir / f"video-existing-{stamp}.mp4"
        print(f"Archiving existing source/video.mp4 to {archived.name}", flush=True)
        existing_video.rename(archived)

    download_cmd = (
        base
        + [
            "--write-thumbnail",
            "--convert-thumbnails",
            "jpg",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            subtitle_langs(platform),
            "--convert-subs",
            "srt",
            "-f",
            format_selector(platform, args.format),
            "--merge-output-format",
            "mp4",
            "--force-overwrites",
            "-o",
            str(source_dir / "video.%(ext)s"),
            args.url,
        ]
    )
    run(download_cmd)

    subtitle_path, subtitle_source = transcribe_if_needed(args, package_dir, source_dir, skill_dir)
    quality = normalize(package_dir, source_dir, subtitle_path, args.max_upload_mib)
    write_readme(package_dir, metadata, platform, args, quality, subtitle_source, proxy)
    zip_path = create_minimal_zip(package_dir)

    print("\nPrepared upload package:", package_dir)
    print("Minimal upload ZIP:", zip_path)
    print("Root files:")
    for name in ROOT_FILES:
        path = package_dir / name
        if path.exists():
            print(f"- {name}: {path.stat().st_size} bytes")
        else:
            print(f"- {name}: missing")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        raise
