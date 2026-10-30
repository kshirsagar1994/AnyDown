import asyncio
import uuid
import os
from pathlib import Path
from typing import List, Tuple, Callable, Any, Coroutine, Optional, Dict
import yt_dlp

from app.core.exceptions import (
    ContentAccessError,
    ContentNotFoundError,
    AnalysisFailedError,
    FormatUnavailableError,
    ConversionError
)
from app.schemas.analysis import AnalyzeResponse, MediaFormat, MediaMetadata
from app.services.storage_service import sanitize_filename, MIME_TYPES, validate_file_magic_number
from app.services.conversion_service import convert_to_mp3, convert_to_jpg, convert_or_merge_to_mp4
import httpx

def map_ytdlp_error(error_msg: str) -> Exception:
    err = error_msg.lower()

    # YouTube bot verification or explicit request rejection.
    bot_indicators = (
        "sign in to confirm you're not a bot",
        "sign in to confirm you’re not a bot",
        "confirm you're not a bot",
        "confirm you’re not a bot",
        "bot verification",
    )

    if any(indicator in err for indicator in bot_indicators):
        return ContentAccessError(
            "YouTube requires additional verification for this request. "
            "The server could not retrieve the media. Please try again "
            "later or use another supported source."
        )

    # Authentication and access restrictions.
    restricted_indicators = (
        "private video",
        "login required",
        "members-only",
        "age-restricted",
        "age verification",
        "drm",
        "protected video",
        "not available in your country",
    )

    if any(indicator in err for indicator in restricted_indicators):
        return ContentAccessError(
            "This media is restricted or requires additional access "
            "permissions."
        )

    # Content that no longer exists.
    unavailable_indicators = (
        "video unavailable",
        "video is unavailable",
        "has been removed",
        "video has been removed",
        "content not available",
    )

    if any(indicator in err for indicator in unavailable_indicators):
        return ContentNotFoundError(
            "The requested content is unavailable or has been removed."
        )

    # Preserve the original exception text for server-side diagnostics.
    return AnalysisFailedError(
        f"Media extraction failed: {error_msg[:500]}"
    )

def get_base_ydl_opts() -> dict:
    """
    Return yt-dlp options shared by metadata extraction and downloads.

    Let yt-dlp select compatible YouTube clients by default rather than
    forcing a fixed list of clients that may become incompatible.
    """
    opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": False,
        "no_color": True,
        "socket_timeout": 30,
        "retries": 2,
        "extractor_retries": 2,
        "fragment_retries": 2,
        "noplaylist": True,
        "js_runtimes": {
            "node": {
                "path": "node"
            }
        },
    }

    # Optional cookies exported by the account owner.
    # Never commit cookies or expose them to frontend JavaScript.
    cookie_file = os.getenv("COOKIES_FILE_PATH")

    if not cookie_file:
        for candidate in (
            "/app/secrets/cookies.txt",
            "/app/cookies.txt",
            "cookies.txt",
            "backend/cookies.txt",
        ):
            if Path(candidate).is_file():
                cookie_file = candidate
                break

    cookies_content = os.getenv("YOUTUBE_COOKIES_CONTENT")

    if cookies_content and not cookie_file:
        temp_cookie_path = (
            Path("/tmp/yt_cookies.txt")
            if os.name != "nt"
            else Path(os.environ.get("TEMP", ".")) / "yt_cookies.txt"
        )

        try:
            temp_cookie_path.write_text(
                cookies_content.strip() + "\n",
                encoding="utf-8",
            )
            cookie_file = str(temp_cookie_path)
        except OSError:
            # Do not log cookie contents.
            raise RuntimeError(
                "Unable to prepare the configured YouTube cookies file."
            )

    if cookie_file:
        cookie_path = Path(cookie_file)

        if not cookie_path.is_file():
            raise RuntimeError(
                "COOKIES_FILE_PATH points to a file that does not exist."
            )

        try:
            temp_cookie = (
                Path("/tmp/active_cookies.txt")
                if os.name != "nt"
                else Path(os.environ.get("TEMP", ".")) / "active_cookies.txt"
            )
            temp_cookie.write_text(
                cookie_path.read_text(encoding="utf-8", errors="ignore"),
                encoding="utf-8",
            )
            opts["cookiefile"] = str(temp_cookie)
        except Exception:
            opts["cookiefile"] = str(cookie_path)

    # Configure a proxy only when explicitly supplied by the administrator.
    # A proxy does not guarantee that YouTube will accept the request.
    proxy = os.getenv("PROXY_URL")

    if proxy:
        opts["proxy"] = proxy

    return opts

class YtDlpAdapterHelper:
    @staticmethod
    def extract_info(url: str) -> dict:
        ydl_opts = get_base_ydl_opts()
        ydl_opts.update({
            'skip_download': True,
            'ignoreerrors': False,
        })
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise ContentNotFoundError("No media stream found at the given link.")
                return info
        except yt_dlp.utils.DownloadError as e:
            raise map_ytdlp_error(str(e))
        except Exception as e:
            raise AnalysisFailedError(f"Analysis failed: {str(e)}")

    @staticmethod
    def build_formats_and_metadata(info: dict, platform_id: str, url: str) -> AnalyzeResponse:
        title = info.get("title") or info.get("description") or "Untitled Media"
        if len(title) > 100:
            title = title[:100] + "..."
        creator = info.get("uploader") or info.get("channel") or info.get("creator")
        thumbnail = info.get("thumbnail")
        duration = info.get("duration")

        metadata = MediaMetadata(
            title=title,
            creator=creator,
            thumbnail_url=thumbnail,
            duration_seconds=int(duration) if duration else None,
            source_url=url
        )

        raw_formats = info.get("formats", [])
        available_formats: List[MediaFormat] = []
        resolution_seen = set()

        # Target standard resolutions or any video streams available
        video_streams = [
            f for f in raw_formats
            if f.get("vcodec") != "none"
        ]
        video_streams.sort(key=lambda x: (x.get("height") or 0, x.get("tbr") or 0), reverse=True)

        for f in video_streams:
            h = f.get("height")
            if h and h > 0:
                if h >= 2160:
                    label = "2160p (4K)"
                    key = 2160
                elif h >= 1440:
                    label = "1440p (2K)"
                    key = 1440
                elif h >= 1080:
                    label = "1080p Full HD"
                    key = 1080
                elif h >= 720:
                    label = "720p HD"
                    key = 720
                elif h >= 480:
                    label = "480p SD"
                    key = 480
                elif h >= 360:
                    label = "360p"
                    key = 360
                else:
                    label = f"{h}p"
                    key = h
            else:
                format_id_raw = str(f.get("format_id") or "video")
                format_note = f.get("format_note") or f.get("quality") or "HD"
                label = f"Video - {format_note} (MP4)"
                key = format_id_raw

            if key not in resolution_seen:
                resolution_seen.add(key)
                size_est = f.get("filesize") or f.get("filesize_approx")
                available_formats.append(
                    MediaFormat(
                        format_id=f"video-{key}",
                        media_type="video",
                        container="mp4",
                        quality_label=label,
                        width=f.get("width"),
                        height=h,
                        estimated_size_bytes=size_est,
                        requires_conversion=True,
                        note="MP4 Container (H.264 / AAC)"
                    )
                )

        # Fallback if raw_formats did not populate video but media contains video
        if not any(f.media_type == "video" for f in available_formats) and (
            info.get("url") or raw_formats or info.get("duration")
        ):
            available_formats.insert(
                0,
                MediaFormat(
                    format_id="video-best",
                    media_type="video",
                    container="mp4",
                    quality_label="Best Quality Video (MP4)",
                    width=info.get("width"),
                    height=info.get("height"),
                    estimated_size_bytes=info.get("filesize") or info.get("filesize_approx"),
                    requires_conversion=True,
                    note="Standard MP4 Video"
                )
            )

        # Audio export format if any audio exists
        has_audio = any(f.get("acodec") != "none" for f in raw_formats) or len(raw_formats) > 0
        if has_audio:
            available_formats.append(
                MediaFormat(
                    format_id="audio-mp3",
                    media_type="audio",
                    container="mp3",
                    quality_label="Audio (MP3 192kbps)",
                    width=None,
                    height=None,
                    estimated_size_bytes=None,
                    requires_conversion=True,
                    note="High Quality Audio Export"
                )
            )

        # Thumbnail / Image export if available
        if thumbnail:
            available_formats.append(
                MediaFormat(
                    format_id="image-jpg",
                    media_type="image",
                    container="jpg",
                    quality_label="Cover Image (JPG)",
                    width=None,
                    height=None,
                    estimated_size_bytes=None,
                    requires_conversion=False,
                    note="Standard JPEG"
                )
            )

        return AnalyzeResponse(
            analysis_id=str(uuid.uuid4()),
            platform=platform_id,
            content_type="video" if video_streams else "image",
            metadata=metadata,
            formats=available_formats,
            warnings=[]
        )

    @staticmethod
    async def execute_download(
        url: str,
        title: str,
        thumbnail_url: Optional[str],
        format_id: str,
        storage_dir: Path,
        progress_callback: Callable[[float, str], Coroutine[Any, Any, None]]
    ) -> Tuple[Path, str, str]:
        loop = asyncio.get_running_loop()

        if format_id == "image-jpg" and thumbnail_url:
            await progress_callback(20.0, "Downloading image...")
            out_filename = sanitize_filename(title, "jpg")
            out_path = storage_dir / out_filename
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(thumbnail_url)
                if res.status_code == 200:
                    temp_img = storage_dir / "temp_thumb"
                    temp_img.write_bytes(res.content)
                    convert_to_jpg(temp_img, out_path)
                    if temp_img.exists():
                        temp_img.unlink()
                    await progress_callback(100.0, "Image ready")
                    return out_path, out_filename, MIME_TYPES["jpg"]

        if format_id == "audio-mp3":
            await progress_callback(10.0, "Extracting audio stream...")
            out_filename = sanitize_filename(title, "mp3")
            out_template = str(storage_dir / "download_audio.%(ext)s")

            def progress_hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    if total and total > 0:
                        pct = min(80.0, (downloaded / total) * 80.0)
                        asyncio.run_coroutine_threadsafe(
                            progress_callback(pct, f"Downloading audio: {int(pct)}%"), loop
                        )
                elif d['status'] == 'finished':
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(85.0, "Converting to MP3 with FFmpeg..."), loop
                    )

            ydl_opts = get_base_ydl_opts()
            ydl_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': out_template,
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

            def run_ydl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

            try:
                await asyncio.to_thread(run_ydl)
            except yt_dlp.utils.DownloadError as exc:
                raise map_ytdlp_error(str(exc)) from exc

            # Locate the generated mp3
            final_path = storage_dir / "download_audio.mp3"
            target_path = storage_dir / out_filename
            if final_path.exists():
                if target_path.exists():
                    target_path.unlink()
                final_path.rename(target_path)
            elif not target_path.exists():
                # Check for any mp3 in the folder
                mp3s = list(storage_dir.glob("*.mp3"))
                if mp3s:
                    mp3s[0].rename(target_path)
                else:
                    raise ConversionError("MP3 output was not generated successfully.")

            validate_file_magic_number(target_path, "mp3")
            await progress_callback(100.0, "Audio ready for download")
            return target_path, out_filename, MIME_TYPES["mp3"]

        # Otherwise Video Download
        res_match = format_id.replace("video-", "")
        if res_match.isdigit():
            target_h = int(res_match)
            format_spec = f"bestvideo[height<={target_h}]+bestaudio/best[height<={target_h}]/best"
        elif res_match in ("best", "default"):
            format_spec = "bestvideo+bestaudio/best"
        else:
            format_spec = f"{res_match}/bestvideo+bestaudio/best"

        out_filename = sanitize_filename(title, "mp4")
        out_template = str(storage_dir / "download_video.%(ext)s")

        def video_progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total and total > 0:
                    pct = min(85.0, (downloaded / total) * 85.0)
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(pct, f"Downloading stream: {int(pct)}%"), loop
                    )
            elif d['status'] == 'finished':
                asyncio.run_coroutine_threadsafe(
                    progress_callback(90.0, "Finalizing MP4 container with FFmpeg..."), loop
                )

        ydl_opts = get_base_ydl_opts()
        ydl_opts.update({
            'format': format_spec,
            'outtmpl': out_template,
            'merge_output_format': 'mp4',
            'progress_hooks': [video_progress_hook],
        })

        def run_video_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await progress_callback(10.0, "Initializing video download...")
        try:
            await asyncio.to_thread(run_video_ydl)
        except yt_dlp.utils.DownloadError as exc:
            raise map_ytdlp_error(str(exc)) from exc

        final_path = storage_dir / "download_video.mp4"
        target_path = storage_dir / out_filename
        if final_path.exists():
            if target_path.exists():
                target_path.unlink()
            final_path.rename(target_path)
        else:
            downloaded_videos = [
                p for p in storage_dir.glob("download_video.*")
                if p.is_file() and not p.name.endswith(".part")
            ]
            if not downloaded_videos:
                downloaded_videos = [
                    p for p in storage_dir.glob("*")
                    if p.is_file() and p.suffix.lower() in (".mp4", ".webm", ".mkv", ".mov") and p != target_path
                ]

            if downloaded_videos:
                src_video = downloaded_videos[0]
                if src_video.suffix.lower() == ".mp4":
                    if target_path.exists():
                        target_path.unlink()
                    src_video.rename(target_path)
                else:
                    await convert_or_merge_to_mp4(src_video, target_path)
                    if src_video.exists():
                        src_video.unlink()
            else:
                raise ConversionError("MP4 video was not generated successfully.")

        validate_file_magic_number(target_path, "mp4")
        await progress_callback(100.0, "Video finalized and ready")
        return target_path, out_filename, MIME_TYPES["mp4"]

