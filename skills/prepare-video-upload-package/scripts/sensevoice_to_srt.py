#!/usr/bin/env python3
"""Transcribe an audio/video file with SenseVoiceSmall and write SRT."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def fmt_ts(ms: int) -> str:
    ms = max(0, int(ms))
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def clean_text(text: str) -> str:
    from funasr.utils.postprocess_utils import rich_transcription_postprocess

    return html.unescape(rich_transcription_postprocess(text)).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Audio or video file to transcribe")
    parser.add_argument("-o", "--output", default="subtitles.srt")
    parser.add_argument("--language", default="auto", choices=["auto", "zh", "en", "yue", "ja", "ko", "nospeech"])
    parser.add_argument("--device", default="cpu", help="Use cpu on Mac unless a supported GPU device is explicitly available")
    parser.add_argument("--model", default="iic/SenseVoiceSmall")
    args = parser.parse_args()

    from funasr import AutoModel

    model = AutoModel(
        model=args.model,
        trust_remote_code=True,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30_000},
        device=args.device,
    )
    result = model.generate(
        input=args.input,
        cache={},
        language=args.language,
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )

    segments = result[0].get("sentence_info") or []
    output = Path(args.output)
    with output.open("w", encoding="utf-8") as f:
        if segments:
            for i, seg in enumerate(segments, 1):
                start = seg.get("start", 0)
                end = seg.get("end", max(start + 1000, start))
                text = clean_text(seg.get("text", ""))
                if not text:
                    continue
                f.write(f"{i}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}\n\n")
        else:
            text = clean_text(result[0].get("text", ""))
            if text:
                f.write(f"1\n00:00:00,000 --> 99:59:59,000\n{text}\n\n")


if __name__ == "__main__":
    main()
