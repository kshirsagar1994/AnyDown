import asyncio
from pathlib import Path
from typing import Tuple, Callable, Any, Coroutine
from app.services.adapters.base import BaseAdapter
from app.schemas.analysis import AnalyzeResponse
from app.services.adapters.ytdlp_base import YtDlpAdapterHelper

class InstagramAdapter(BaseAdapter):
    id = "instagram"
    name = "Instagram"
    hostname_patterns = ["instagram.com", "www.instagram.com"]
    supported_content_types = ["reels", "posts", "stories", "video", "image"]
    supported_formats = ["mp4", "mp3", "jpg"]
    enabled = True
    policy_notice = "Supports public posts and reels. Private profile content is strictly inaccessible."

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

