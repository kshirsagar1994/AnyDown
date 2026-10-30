import asyncio
import html
import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Tuple, Callable, Any, Coroutine, List, Optional
import httpx

from app.services.adapters.base import BaseAdapter
from app.schemas.analysis import AnalyzeResponse, MediaFormat, MediaMetadata
from app.services.adapters.ytdlp_base import YtDlpAdapterHelper
from app.core.exceptions import ContentAccessError, ContentNotFoundError, AnalysisFailedError, FormatUnavailableError
from app.services.storage_service import sanitize_filename, MIME_TYPES, validate_file_magic_number
from app.services.conversion_service import convert_to_jpg

logger = logging.getLogger(__name__)

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
            if "no video in this post" in err_str or "no video formats found" in err_str or "/p/" in url:
                try:
                    return await self._analyze_image_post(url)
                except Exception as img_exc:
                    logger.debug(f"Image post analysis attempt failed: {img_exc}")
                    # If it was explicitly an image error, let it propagate, otherwise raise original
                    if isinstance(img_exc, (ContentAccessError, ContentNotFoundError)):
                        raise img_exc
            raise

    @staticmethod
    async def _scrape_post_html(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Scrapes public Instagram post HTML using Mobile Safari User-Agent.
        Returns: (title, creator, thumbnail_url)
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return None, None, None

                html_text = resp.text

                # Extract og:image or twitter:image
                img_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']\s+content=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
                if not img_match:
                    img_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']', html_text, re.IGNORECASE)

                thumbnail = html.unescape(img_match.group(1)) if img_match else None

                # Extract og:title or twitter:title
                title_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:title|twitter:title)["\']\s+content=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
                if not title_match:
                    title_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\'](?:og:title|twitter:title)["\']', html_text, re.IGNORECASE)

                raw_title = html.unescape(title_match.group(1)) if title_match else None

                creator = None
                title = "Instagram Photo"
                if raw_title:
                    if " on Instagram: " in raw_title:
                        parts = raw_title.split(" on Instagram: ", 1)
                        creator = parts[0].strip()
                        extracted_title = parts[1].strip().strip('"').strip("'")
                        title = extracted_title if extracted_title else raw_title
                    elif "• Instagram photo" in raw_title:
                        creator = raw_title.split("•")[0].strip()
                        title = raw_title
                    else:
                        title = raw_title

                return title, creator, thumbnail
        except Exception as exc:
            logger.warning(f"Failed to scrape Instagram post HTML: {exc}")
            return None, None, None

    async def _analyze_image_post(self, url: str) -> AnalyzeResponse:
        # Step 1: Scrape public post metadata using mobile Safari headers (bypasses GraphQL 429)
        title, creator, thumbnail = await self._scrape_post_html(url)

        # Step 2: If HTML scrape did not return a thumbnail, try gallery-dl fallback
        if not thumbnail:
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
                if code == 0 and stdout.strip():
                    data = json.loads(stdout.strip())
                    item = None
                    if isinstance(data, list) and len(data) > 0:
                        first = data[0]
                        if isinstance(first, list) and len(first) > 1 and isinstance(first[1], dict):
                            item = first[1]
                        elif isinstance(first, dict):
                            item = first
                    if item:
                        creator = creator or item.get("author") or item.get("username")
                        description = item.get("description") or item.get("caption") or ""
                        if description:
                            title = description[:100] + "..." if len(description) > 100 else description
                        thumbnail = item.get("thumbnail") or item.get("url")
            except Exception as exc:
                logger.debug(f"gallery-dl analysis fallback failed: {exc}")

        if not thumbnail:
            raise ContentNotFoundError(
                "Could not retrieve media from this Instagram post. Ensure the post is public."
            )

        metadata = MediaMetadata(
            title=title or "Instagram Photo",
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
            out_filename = sanitize_filename(title or "Instagram Photo", "jpg")
            out_path = storage_dir / out_filename
            temp_file = storage_dir / f"temp_{uuid.uuid4().hex[:8]}.jpg"

            # 1. First priority: Direct CDN download via thumbnail / og:image
            target_img_url = thumbnail
            if not target_img_url:
                _, _, target_img_url = await self._scrape_post_html(url)

            if target_img_url:
                await progress_callback(40.0, "Fetching image from CDN...")
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Referer": "https://www.instagram.com/",
                }
                try:
                    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                        resp = await client.get(target_img_url)
                        if resp.status_code == 200 and len(resp.content) > 0:
                            temp_file.write_bytes(resp.content)
                            convert_to_jpg(temp_file, out_path)
                            if temp_file.exists():
                                temp_file.unlink()
                            validate_file_magic_number(out_path, "jpg")
                            await progress_callback(100.0, "Image ready for download")
                            return out_path, out_filename, MIME_TYPES["jpg"]
                except Exception as exc:
                    logger.warning(f"Direct Instagram CDN download failed: {exc}")
                    if temp_file.exists():
                        temp_file.unlink()

            # 2. Second priority: If direct CDN fetch failed, try gallery-dl
            await progress_callback(60.0, "Attempting download via media extractor...")
            try:
                cookie_file = os.getenv("COOKIES_FILE_PATH", "/app/secrets/cookies.txt")
                cmd = ["gallery-dl", "--retries", "0", "--directory", str(storage_dir)]
                if Path(cookie_file).is_file():
                    cmd.extend(["--cookies", str(cookie_file)])
                cmd.append(url)

                def run_dl():
                    import subprocess
                    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

                await asyncio.to_thread(run_dl)
                found_images = list(storage_dir.glob("**/*.jpg")) + list(storage_dir.glob("**/*.jpeg")) + list(storage_dir.glob("**/*.webp")) + list(storage_dir.glob("**/*.png"))
                if found_images:
                    chosen = found_images[0]
                    if chosen != out_path:
                        convert_to_jpg(chosen, out_path)
                    validate_file_magic_number(out_path, "jpg")
                    await progress_callback(100.0, "Image ready for download")
                    return out_path, out_filename, MIME_TYPES["jpg"]
            except Exception as exc:
                logger.warning(f"gallery-dl fallback failed: {exc}")

            raise FormatUnavailableError("Could not retrieve the requested image from Instagram. Ensure the post is public.")

        # For videos / reels, use standard yt-dlp helper
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )
