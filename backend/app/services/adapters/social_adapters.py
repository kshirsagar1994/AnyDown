import asyncio
from pathlib import Path
from typing import Tuple, Callable, Any, Coroutine
from app.services.adapters.base import BaseAdapter
from app.schemas.analysis import AnalyzeResponse
from app.services.adapters.ytdlp_base import YtDlpAdapterHelper

class TikTokAdapter(BaseAdapter):
    id = "tiktok"
    name = "TikTok"
    hostname_patterns = ["tiktok.com", "www.tiktok.com", "vt.tiktok.com", "vm.tiktok.com"]
    supported_content_types = ["video", "sound", "image"]
    supported_formats = ["mp4", "mp3"]
    enabled = True
    policy_notice = "Supports public TikTok videos and audio tracks."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class TwitterAdapter(BaseAdapter):
    id = "twitter"
    name = "X (Twitter)"
    hostname_patterns = ["twitter.com", "www.twitter.com", "x.com", "www.x.com"]
    supported_content_types = ["video", "image", "post"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports publicly available media in tweets/posts."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class RedditAdapter(BaseAdapter):
    id = "reddit"
    name = "Reddit"
    hostname_patterns = ["reddit.com", "www.reddit.com", "v.redd.it", "redd.it", "old.reddit.com"]
    supported_content_types = ["video", "image", "post"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports public posts and Reddit video streams with synchronized audio."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class PinterestAdapter(BaseAdapter):
    id = "pinterest"
    name = "Pinterest"
    hostname_patterns = ["pinterest.com", "www.pinterest.com", "pin.it"]
    supported_content_types = ["pin", "image", "video"]
    supported_formats = ["mp4", "jpg"]
    enabled = True
    policy_notice = "Supports public pins and media."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class FacebookAdapter(BaseAdapter):
    id = "facebook"
    name = "Facebook"
    hostname_patterns = ["facebook.com", "www.facebook.com", "fb.watch", "m.facebook.com", "web.facebook.com"]
    supported_content_types = ["video", "post", "image"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports public watch videos and posts. Private group/profile media is not accessible."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class SnapchatAdapter(BaseAdapter):
    id = "snapchat"
    name = "Snapchat"
    hostname_patterns = [
        "snapchat.com", "www.snapchat.com", "story.snapchat.com",
        "t.snapchat.com", "spotlight.snapchat.com"
    ]
    supported_content_types = ["spotlight", "public_stories", "video", "image"]
    supported_formats = ["mp4", "jpg"]
    enabled = True
    policy_notice = "Supports public Spotlight and public Stories only."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

class GenericSocialAdapter(BaseAdapter):
    id = "generic"
    name = "Other Platforms (Threads, LinkedIn, Discord, Quora)"
    hostname_patterns = [
        "threads.net", "www.threads.net",
        "linkedin.com", "www.linkedin.com",
        "cdn.discordapp.com", "media.discordapp.net",
        "quora.com", "www.quora.com"
    ]
    supported_content_types = ["video", "image", "post", "attachment"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports public posts and direct CDN attachments where permitted."

    async def analyze(self, url: str) -> AnalyzeResponse:
        info = await asyncio.to_thread(YtDlpAdapterHelper.extract_info, url)
        return YtDlpAdapterHelper.build_formats_and_metadata(info, self.id, url)

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
        return await YtDlpAdapterHelper.execute_download(
            url, title, thumbnail, format_id, storage_dir, progress_callback
        )

