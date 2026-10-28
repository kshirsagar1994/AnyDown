import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from PIL import Image
from app.core.exceptions import ConversionError
from app.services.storage_service import validate_file_magic_number

async def convert_to_mp3(input_path: Path, output_path: Path) -> Path:
    """
    Converts any valid audio/video input file into a standardized MP3 file using FFmpeg.
    Uses argument list execution without shell interpretation.
    """
    cmd = [
        "ffmpeg",
        "-y",               # Overwrite output
        "-i", str(input_path),
        "-vn",              # Disable video
        "-acodec", "libmp3lame",
        "-ab", "192k",      # High quality 192kbps
        "-ar", "44100",     # 44.1kHz sampling rate
        str(output_path)
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace")[-500:] if stderr else "Unknown ffmpeg error"
            raise ConversionError(f"Audio conversion failed: {err_msg}")

        if not validate_file_magic_number(output_path, "mp3"):
            raise ConversionError("Converted file failed MP3 container validation.")

        return output_path
    except Exception as e:
        if isinstance(e, ConversionError):
            raise
        raise ConversionError(f"Failed to execute audio conversion: {str(e)}")

async def convert_or_merge_to_mp4(
    video_path: Path,
    output_path: Path,
    audio_path: Optional[Path] = None
) -> Path:
    """
    Converts or merges video/audio streams into a standard, browser-playable MP4 container
    with H.264 video and AAC audio with +faststart for immediate web streaming.
    """
    if audio_path and audio_path.exists():
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            "-movflags", "+faststart",
            str(output_path)
        ]
    else:
        # Check if already mp4 container, or convert
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(output_path)
        ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace")[-500:] if stderr else "Unknown ffmpeg error"
            raise ConversionError(f"Video container conversion failed: {err_msg}")

        if not validate_file_magic_number(output_path, "mp4"):
            raise ConversionError("Converted file failed MP4 container validation.")

        return output_path
    except Exception as e:
        if isinstance(e, ConversionError):
            raise
        raise ConversionError(f"Failed to execute video conversion: {str(e)}")

def convert_to_jpg(input_path: Path, output_path: Path) -> Path:
    """
    Converts any image (PNG, WebP, AVIF, etc.) to a standardized JPEG file.
    Uses PIL with RGB conversion to discard transparency safely.
    """
    try:
        with Image.open(input_path) as img:
            rgb_im = img.convert("RGB")
            rgb_im.save(output_path, "JPEG", quality=92, optimize=True)

        if not validate_file_magic_number(output_path, "jpg"):
            raise ConversionError("Converted image failed JPEG container validation.")

        return output_path
    except Exception as e:
        raise ConversionError(f"Image conversion to JPG failed: {str(e)}")

