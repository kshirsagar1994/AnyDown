import asyncio
import html
import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Tuple, Callable, Any, Coroutine, List, Optional, Dict
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
                    if isinstance(img_exc, (ContentAccessError, ContentNotFoundError)):
                        raise img_exc
            raise

    @staticmethod
    async def _scrape_post_html(url: str) -> Dict[str, Any]:
        """
        Scrapes public Instagram post HTML using Mobile Safari User-Agent.
        Extracts original full-size image candidate(s), dimensions, creator, and title.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        result: Dict[str, Any] = {
            "best_image_url": None,
            "images": [],
            "width": None,
            "height": None,
            "title": "Instagram Photo",
            "creator": None,
            "thumbnail_preview": None
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return result

                html_text = resp.text

                # 1. Parse Polaris / Relay JSON scripts to locate full-resolution candidates
                scripts = re.findall(r'<script\s+type="application/json"[^>]*>(.*?)</script>', html_text, re.DOTALL)
                images: List[str] = []

                for s in scripts:
                    if "image_versions2" in s or "xig_polaris_media" in s or "display_resources" in s:
                        try:
                            data = json.loads(s)

                            def search_tree(d):
                                nonlocal result
                                if isinstance(d, dict):
                                    # Extract metadata from if_not_gated_logged_out if present
                                    if "if_not_gated_logged_out" in d and isinstance(d["if_not_gated_logged_out"], dict):
                                        media = d["if_not_gated_logged_out"]
                                        orig_w = media.get("original_width")
                                        orig_h = media.get("original_height")
                                        if orig_w and orig_h:
                                            result["width"] = orig_w
                                            result["height"] = orig_h
                                        caption = media.get("caption")
                                        if caption and isinstance(caption, dict) and caption.get("text"):
                                            result["title"] = caption.get("text")
                                        user = media.get("user")
                                        if user and isinstance(user, dict):
                                            result["creator"] = user.get("username") or user.get("full_name")
                                        if media.get("display_uri"):
                                            result["thumbnail_preview"] = media.get("display_uri")

                                    # Extract candidate images: candidates[0] is the original full size
                                    if "image_versions2" in d and isinstance(d["image_versions2"], dict):
                                        cands = d["image_versions2"].get("candidates", [])
                                        if cands and isinstance(cands, list) and len(cands) > 0:
                                            first_cand = cands[0].get("url")
                                            if first_cand and first_cand not in images:
                                                images.append(first_cand)

                                    # Extract from display_resources fallback
                                    if "display_resources" in d and isinstance(d["display_resources"], list):
                                        resources = d["display_resources"]
                                        if resources:
                                            sorted_res = sorted(
                                                resources,
                                                key=lambda x: (x.get("config_width", 0) * x.get("config_height", 0)),
                                                reverse=True
                                            )
                                            best_src = sorted_res[0].get("src")
                                            if best_src and best_src not in images:
                                                images.append(best_src)
                                                if not result["width"] and "config_width" in sorted_res[0]:
                                                    result["width"] = sorted_res[0]["config_width"]
                                                    result["height"] = sorted_res[0]["config_height"]

                                    for v in d.values():
                                        search_tree(v)
                                elif isinstance(d, list):
                                    for item in d:
                                        search_tree(item)

                            search_tree(data)
                        except Exception:
                            pass

                result["images"] = images
                if images:
                    result["best_image_url"] = images[0]

                # 2. Extract og:image fallback if JSON had no candidates
                if not result["best_image_url"]:
                    img_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']\s+content=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
                    if not img_match:
                        img_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']', html_text, re.IGNORECASE)
                    if img_match:
                        og_img = html.unescape(img_match.group(1))
                        result["best_image_url"] = og_img
                        result["images"].append(og_img)

                # 3. Extract title/creator fallback from meta tags
                if result["title"] == "Instagram Photo":
                    title_match = re.search(r'<meta\s+(?:property|name)=["\'](?:og:title|twitter:title)["\']\s+content=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
                    if not title_match:
                        title_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\'](?:og:title|twitter:title)["\']', html_text, re.IGNORECASE)
                    if title_match:
                        raw_title = html.unescape(title_match.group(1))
                        if " on Instagram: " in raw_title:
                            parts = raw_title.split(" on Instagram: ", 1)
                            result["creator"] = result["creator"] or parts[0].strip()
                            extracted = parts[1].strip().strip('"').strip("'")
                            result["title"] = extracted if extracted else raw_title
                        elif "• Instagram photo" in raw_title:
                            result["creator"] = result["creator"] or raw_title.split("•")[0].strip()
                            result["title"] = raw_title
                        else:
                            result["title"] = raw_title

                if not result["thumbnail_preview"]:
                    result["thumbnail_preview"] = result["best_image_url"]

                return result
        except Exception as exc:
            logger.warning(f"Failed to scrape Instagram post HTML: {exc}")
            return result

    async def _analyze_image_post(self, url: str) -> AnalyzeResponse:
        data = await self._scrape_post_html(url)
        title = data.get("title") or "Instagram Photo"
        creator = data.get("creator")
        best_image_url = data.get("best_image_url")
        images = data.get("images", [])
        width = data.get("width")
        height = data.get("height")
        thumbnail = data.get("thumbnail_preview") or best_image_url

        # Fallback to gallery-dl if no image candidates found
        if not best_image_url and not images:
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
                    parsed = json.loads(stdout.strip())
                    item = None
                    if isinstance(parsed, list) and len(parsed) > 0:
                        first = parsed[0]
                        if isinstance(first, list) and len(first) > 1 and isinstance(first[1], dict):
                            item = first[1]
                        elif isinstance(first, dict):
                            item = first
                    if item:
                        creator = creator or item.get("author") or item.get("username")
                        description = item.get("description") or item.get("caption") or ""
                        if description:
                            title = description[:100] + "..." if len(description) > 100 else description
                        best_image_url = item.get("url") or item.get("thumbnail")
                        thumbnail = best_image_url
            except Exception as exc:
                logger.debug(f"gallery-dl analysis fallback failed: {exc}")

        if not best_image_url and not images:
            raise ContentNotFoundError(
                "Could not retrieve media from this Instagram post. Ensure the post is public."
            )

        metadata = MediaMetadata(
            title=title,
            creator=creator,
            thumbnail_url=best_image_url or thumbnail,
            duration_seconds=None,
            source_url=url
        )

        quality_label = f"Full Resolution ({width}x{height} JPG)" if (width and height) else "Full Resolution (Original Upload)"
        formats: List[MediaFormat] = [
            MediaFormat(
                format_id="image-jpg",
                media_type="image",
                container="jpg",
                quality_label=f"Photo 1 - {quality_label}" if len(images) > 1 else quality_label,
                width=width,
                height=height,
                estimated_size_bytes=int(width * height * 0.25) if (width and height) else None,
                requires_conversion=False,
                note="Original Full-Size Upload"
            )
        ]

        # Additional photos for carousel posts
        for i in range(1, len(images)):
            formats.append(
                MediaFormat(
                    format_id=f"image-{i+1}",
                    media_type="image",
                    container="jpg",
                    quality_label=f"Photo {i+1} - Full Resolution (Original Upload)",
                    width=None,
                    height=None,
                    estimated_size_bytes=None,
                    requires_conversion=False,
                    note="Original Full-Size Upload"
                )
            )

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

        if content_type in ("image", "carousel") or format_id.startswith("image"):
            await progress_callback(20.0, "Preparing full-size image download...")
            out_filename = sanitize_filename(title or "Instagram Photo", "jpg")
            out_path = storage_dir / out_filename
            temp_file = storage_dir / f"temp_{uuid.uuid4().hex[:8]}.jpg"

            # 1. Determine target full-size image URL
            target_img_url = None

            # If user selected a specific carousel photo (e.g. image-2)
            if format_id.startswith("image-") and format_id[6:].isdigit():
                idx = int(format_id[6:]) - 1
                post_info = await self._scrape_post_html(url)
                cand_images = post_info.get("images", [])
                if 0 <= idx < len(cand_images):
                    target_img_url = cand_images[idx]

            # Otherwise, use full-size URL: check if thumbnail has full resolution, or scrape original
            if not target_img_url:
                if thumbnail and ("stp=dst-jpg" in thumbnail or "scontent" in thumbnail) and "s640x640" not in thumbnail:
                    target_img_url = thumbnail
                else:
                    post_info = await self._scrape_post_html(url)
                    cand_images = post_info.get("images", [])
                    target_img_url = cand_images[0] if cand_images else post_info.get("best_image_url")

            # Fallback if target_img_url is somehow still empty
            if not target_img_url:
                target_img_url = thumbnail

            if target_img_url:
                await progress_callback(40.0, "Downloading original full-resolution image...")
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
                            if resp.content.startswith(b"\xff\xd8\xff"):
                                # Original full-resolution JPEG: preserve exact lossless bytes
                                if out_path.exists():
                                    out_path.unlink()
                                temp_file.rename(out_path)
                            else:
                                convert_to_jpg(temp_file, out_path)
                                if temp_file.exists():
                                    temp_file.unlink()
                            validate_file_magic_number(out_path, "jpg")
                            await progress_callback(100.0, "Full-size photo ready for download")
                            return out_path, out_filename, MIME_TYPES["jpg"]
                except Exception as exc:
                    logger.warning(f"Direct full-resolution CDN download failed: {exc}")
                    if temp_file.exists():
                        temp_file.unlink()

            # 2. Secondary fallback via gallery-dl
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
