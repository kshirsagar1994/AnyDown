import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Tuple, Callable, Any, Coroutine, List, Optional
from app.services.adapters.base import BaseAdapter
from app.schemas.analysis import AnalyzeResponse, MediaFormat, MediaMetadata
from app.services.adapters.ytdlp_base import YtDlpAdapterHelper, get_base_ydl_opts
from app.core.exceptions import ContentAccessError, ContentNotFoundError, AnalysisFailedError, FormatUnavailableError
from app.services.storage_service import sanitize_filename, MIME_TYPES, validate_file_magic_number
from app.services.conversion_service import convert_to_jpg
import httpx

class InstagramAdapter(BaseAdapter):
    id = "instagram"
    name = "Instagram"
    hostname_patterns = ["instagram.com", "www.instagram.com"]
    supported_content_types = ["reels", "posts", "stories", "video", "image"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports public posts and reels. Private profile content is strictly inaccessible."

    async def analyze(self, url: str) -> AnalyzeResponse:
        try:
            info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
            return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)
        except Exception as e:
            err_str = str(e).lower()
            if "no video in this post" in err_str or "no video formats found" in err_str:
                return await self._analyze_image_post(url)
            raise

    async def _analyze_image_post(self, url: str) -> AnalyzeResponse:
        # Fallback for photo / image posts using gallery-dl
        cookie_file = os.getenv("COOKIES_FILE_PATH", "/app/secrets/cookies.txt")
        cmd = ["gallery-dl", "-j", "--retries", "0"]
        if Path(cookie_file).is_file():
            cmd.extend(["--cookies", str(cookie_file)])
        cmd.append(url)

        def run_gallery_dl():
            import subprocess
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            return res.returncode, res.stdout, res.stderr

        try:
            code, stdout, stderr = await asyncio.to_thread(run_gallery_dl)
        except Exception as exc:
            raise AnalysisFailedError(f"Failed to analyze Instagram image post: {str(exc)}")

        if "429" in stderr or "too many requests" in stderr.lower():
            raise ContentAccessError(
                "Instagram requires an active session to view this image post. "
                "Ensure your cookies file includes an active Instagram login session."
            )

        if code != 0 or not stdout.strip():
            raise ContentNotFoundError(
                "Could not retrieve media from this Instagram post. Ensure the post is public."
            )

        # Parse gallery-dl JSON output
        try:
            data = json.loads(stdout.strip())
            # gallery-dl outputs [[code, metadata], ...] or [metadata]
            item = None
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, list) and len(first) > 1 and isinstance(first[1], dict):
                    item = first[1]
                elif isinstance(first, dict):
                    item = first
            
            title = "Instagram Photo"
            creator = None
            thumbnail = None
            if item:
                creator = item.get("author") or item.get("username")
                description = item.get("description") or item.get("caption") or ""
                if description:
                    title = description[:100] + "..." if len(description) > 100 else description
                thumbnail = item.get("thumbnail") or item.get("url")

            metadata = MediaMetadata(
                title=title,
                creator=creator,
                thumbnail_url=thumbnail,
                duration_seconds=None,
                source_url=url
            )

            formats = [
                MediaFormat(
                    format_id="image-jpg",
                    media_type="image",
                    container="jpg",
                    quality_label="High Quality Image (JPG)",
                    width=None,
                    height=None,
                    estimated_size_bytes=None,
                    requires_conversion=False,
                    note="Standard JPEG"
                )
            ]

            return AnalyzeResponse(
                analysis_id=str(uuid.uuid4()),
                platform=self.id,
                content_type="image",
                metadata=metadata,
                formats=formats,
                warnings=[]
            )
        except Exception as exc:
            raise AnalysisFailedError(f"Unable to parse Instagram post metadata: {str(exc)}")

    async def download(
        self,
        analysis_data: dict,
        format_id: str,
        storage_dir: Path,
        progress_callback: Callable[[float, str], Coroutine[Any, Any, None]]
    ) -> Tuple[Path, str, str]:
        url = analysis_data["metadata"]["source_url"]
        title = analysis_data["metadata"]["title"]
        thumbnail = analysis_data["metadata"].get("thumbnail_url")
        content_type = analysis_data.get("content_type", "video")

        if content_type == "image" or format_id == "image-jpg":
            await progress_callback(20.0, "Downloading Instagram image...")
            cookie_file = os.getenv("COOKIES_FILE_PATH", "/app/secrets/cookies.txt")
            cmd = ["gallery-dl", "--retries", "0", "--directory", str(storage_dir)]
            if Path(cookie_file).is_file():
                cmd.extend(["--cookies", str(cookie_file)])
            cmd.append(url)

            def run_dl():
                import subprocess
                return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

            res = await asyncio.to_thread(run_dl)
            if res.returncode != 0 and "429" in res.stderr:
                raise ContentAccessError("Instagram rate limited image download. Login session required in cookies.")

            # Look for any downloaded image in storage_dir recursively
            found_images = list(storage_dir.glob("**/*.jpg")) + list(storage_dir.glob("**/*.jpeg")) + list(storage_dir.glob("**/*.webp")) + list(storage_dir.glob("**/*.png"))
            if found_images:
                chosen = found_images[0]
                out_filename = sanitize_filename(title, "jpg")
                out_path = storage_dir / out_filename
                if chosen != out_path:
                    convert_to_jpg(chosen, out_path)
                validate_file_magic_number(out_path, "jpg")
                await progress_callback(100.0, "Image ready for download")
                return out_path, out_filename, MIME_TYPES["jpg"]

            # If gallery-dl couldn't save, try downloading thumbnail if available
            if thumbnail:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                }
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(thumbnail)
                    if resp.status_code == 200 and len(resp.content) > 0:
                        out_filename = sanitize_filename(title, "jpg")
                        out_path = storage_dir / out_filename
                        temp_file = storage_dir / f"temp_{uuid.uuid4().hex[:8]}"
                        temp_file.write_bytes(resp.content)
                        convert_to_jpg(temp_file, out_path)
                        if temp_file.exists():
                            temp_file.unlink()
                        validate_file_magic_number(out_path, "jpg")
                        await progress_callback(100.0, "Image ready for download")
                        return out_path, out_filename, MIME_TYPES["jpg"]

            raise FormatUnavailableError("Could not retrieve the requested image from Instagram.")

        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

