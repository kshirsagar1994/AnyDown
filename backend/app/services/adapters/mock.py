import asyncio
import uuid
import subprocess
from pathlib import Path
from typing import List, Tuple, Callable, Any, Coroutine
from app.services.adapters.base import BaseAdapter
from app.schemas.analysis import AnalyzeResponse, MediaFormat, MediaMetadata
from app.services.storage_service import sanitize_filename, MIME_TYPES
from app.services.conversion_service import convert_to_mp3, convert_or_merge_to_mp4, convert_to_jpg
from PIL import Image

class MockAdapter(BaseAdapter):
    id = "mock"
    name = "Mock Platform (Testing)"
    hostname_patterns = ["mock-media.anydown.local", "fixtures.anydown.local"]
    supported_content_types = ["video", "audio", "image"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Used exclusively for local automated testing and UI development."

    async def analyze(self, url: str) -> AnalyzeResponse:
        analysis_id = str(uuid.uuid4())
        
        formats: List[MediaFormat] = [
            MediaFormat(
                format_id="mock-1080p",
                media_type="video",
                container="mp4",
                quality_label="1080p Full HD",
                width=1920,
                height=1080,
                estimated_size_bytes=15_200_000,
                requires_conversion=False,
                note="H.264 / AAC 60fps"
            ),
            MediaFormat(
                format_id="mock-720p",
                media_type="video",
                container="mp4",
                quality_label="720p HD",
                width=1280,
                height=720,
                estimated_size_bytes=8_500_000,
                requires_conversion=False,
                note="H.264 / AAC 30fps"
            ),
            MediaFormat(
                format_id="mock-360p",
                media_type="video",
                container="mp4",
                quality_label="360p SD",
                width=640,
                height=360,
                estimated_size_bytes=3_100_000,
                requires_conversion=False,
                note="H.264 / AAC"
            ),
            MediaFormat(
                format_id="mock-mp3",
                media_type="audio",
                container="mp3",
                quality_label="Audio (MP3 192kbps)",
                width=None,
                height=None,
                estimated_size_bytes=2_800_000,
                requires_conversion=True,
                note="High Quality MP3 Audio"
            ),
            MediaFormat(
                format_id="mock-jpg",
                media_type="image",
                container="jpg",
                quality_label="High-Res Cover (JPG)",
                width=1920,
                height=1080,
                estimated_size_bytes=450_000,
                requires_conversion=False,
                note="Standard JPEG"
            )
        ]

        metadata = MediaMetadata(
            title="Sample Creative Commons Demonstration Video",
            creator="OpenSourceMedia",
            thumbnail_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=640",
            duration_seconds=124,
            source_url=url
        )

        return AnalyzeResponse(
            analysis_id=analysis_id,
            platform=self.id,
            content_type="video",
            metadata=metadata,
            formats=formats,
            warnings=[]
        )

    async def download(
        self,
        analysis_data: dict,
        format_id: str,
        storage_dir: Path,
        progress_callback: Callable[[float, str], Coroutine[Any, Any, None]]
    ) -> Tuple[Path, str, str]:
        title = analysis_data.get("metadata", {}).get("title", "sample_media")

        await progress_callback(15.0, "Preparing mock test stream...")
        await asyncio.sleep(0.3)
        await progress_callback(45.0, "Generating media payload...")
        await asyncio.sleep(0.3)

        if format_id == "mock-mp3":
            out_filename = sanitize_filename(title, "mp3")
            out_path = storage_dir / out_filename
            # Generate 2 seconds of pure tone audio with ffmpeg
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                "-acodec", "libmp3lame", "-ab", "192k",
                str(out_path)
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            await progress_callback(90.0, "Finalizing MP3 tags...")
            return out_path, out_filename, MIME_TYPES["mp3"]

        elif format_id == "mock-jpg":
            out_filename = sanitize_filename(title, "jpg")
            out_path = storage_dir / out_filename
            # Generate valid JPEG using Pillow
            img = Image.new("RGB", (640, 360), color=(30, 60, 90))
            img.save(out_path, "JPEG", quality=90)
            await progress_callback(90.0, "Finalizing image...")
            return out_path, out_filename, MIME_TYPES["jpg"]

        else:
            # Video: generate 2 seconds of test video with sound using ffmpeg
            out_filename = sanitize_filename(title, "mp4")
            out_path = storage_dir / out_filename
            h = 1080 if "1080" in format_id else (720 if "720" in format_id else 360)
            w = int(h * 16 / 9)
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"testsrc=duration=2:size={w}x{h}:rate=24",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                "-c:v", "libx264", "-preset", "ultrafast", "-threads", "1", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-movflags", "+faststart",
                str(out_path)
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            await progress_callback(90.0, "Finalizing MP4 container...")
            return out_path, out_filename, MIME_TYPES["mp4"]

