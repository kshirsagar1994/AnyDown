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
from app.services.conversion_service import convert_to_mp3, convert_to_jpg
import httpx

def map_ytdlp_error(error_msg: str) -> Exception:
    err = error_msg.lower()
    if "sign in to confirm you’re not a bot" in err or "sign in to confirm you're not a bot" in err:
        return ContentAccessError(
            "YouTube bot verification triggered. This server's IP address has been temporarily restricted by YouTube. "
            "Please try again in a few moments or try another video link."
        )
    if any(k in err for k in ["private", "sign in", "login", "members-only", "drm", "copyright", "protected"]):
        return ContentAccessError(f"Access restricted: {error_msg.split(';')[-1].strip()}")
    if any(k in err for k in ["not found", "404", "unavailable", "removed", "deleted"]):
        return ContentNotFoundError("The requested content could not be found or was removed.")
    return AnalysisFailedError(f"Platform extraction error: {error_msg}")

def get_base_ydl_opts() -> dict:
    opts: Dict[str, Any] = {
        'quiet': True,
        'no_warnings': True,
        'no_color': True,
        'socket_timeout': 30,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web_embedded', 'mweb', 'ios'],
                'player_skip': ['webpage', 'configs'],
            }
        }
    }

    # Optional server-side cookie configuration for YouTube if provided by host/admin
    cookie_file = os.getenv("COOKIES_FILE_PATH")
    if not cookie_file:
        for p in ["/app/cookies.txt", "cookies.txt", "backend/cookies.txt"]:
            if Path(p).exists():
                cookie_file = p
                break

    # If YOUTUBE_COOKIES_CONTENT is provided in environment variables, write to a temp file
    cookies_content = os.getenv("YOUTUBE_COOKIES_CONTENT")
    if cookies_content and not cookie_file:
        temp_cookie_path = Path("/tmp/yt_cookies.txt") if os.name != "nt" else Path("./temp_yt_cookies.txt")
        try:
            temp_cookie_path.write_text(cookies_content.strip(), encoding="utf-8")
            cookie_file = str(temp_cookie_path)
        except Exception:
            pass

    # Optional proxy support if configured in environment
    proxy = os.getenv("PROXY_URL") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if proxy:
        opts['proxy'] = proxy

    if cookie_file and Path(cookie_file).exists():
        opts['cookiefile'] = cookie_file

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

        # Target standard resolutions: 2160p (4K), 1440p (2K), 1080p, 720p, 480p, 360p
        # We sort by resolution descending
        video_streams = [
            f for f in raw_formats
            if f.get("vcodec") != "none" and (f.get("height") or 0) > 0
        ]
        video_streams.sort(key=lambda x: (x.get("height") or 0, x.get("tbr") or 0), reverse=True)

        for f in video_streams:
            h = f.get("height")
            if not h:
                continue

            # Standardize quality label
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

            await asyncio.to_thread(run_ydl)

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
        try:
            target_h = int(res_match)
            format_spec = f"bestvideo[height<={target_h}]+bestaudio/best[height<={target_h}]/best"
        except ValueError:
            format_spec = "bestvideo+bestaudio/best"

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
        await asyncio.to_thread(run_video_ydl)

        final_path = storage_dir / "download_video.mp4"
        target_path = storage_dir / out_filename
        if final_path.exists():
            if target_path.exists():
                target_path.unlink()
            final_path.rename(target_path)
        else:
            mp4s = list(storage_dir.glob("*.mp4"))
            if mp4s:
                mp4s[0].rename(target_path)
            else:
                raise ConversionError("MP4 video container was not generated.")

        validate_file_magic_number(target_path, "mp4")
        await progress_callback(100.0, "Video finalized and ready")
        return target_path, out_filename, MIME_TYPES["mp4"]

