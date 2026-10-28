from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Callable, Any, Coroutine, Optional
from app.schemas.platform import PlatformCapability
from app.schemas.analysis import AnalyzeResponse, MediaFormat, MediaMetadata

class BaseAdapter(ABC):
    id: str
    name: str
    hostname_patterns: List[str]
    supported_content_types: List[str]
    supported_formats: List[str]
    enabled: bool = True
    policy_notice: str

    def can_handle(self, hostname: str, url: str) -> bool:
        hostname_lower = hostname.lower()
        for pattern in self.hostname_patterns:
            if pattern == hostname_lower or hostname_lower.endswith("." + pattern):
                return True
        return False

    def capabilities(self) -> PlatformCapability:
        return PlatformCapability(
            id=self.id,
            name=self.name,
            hostname_patterns=self.hostname_patterns,
            supported_content_types=self.supported_content_types,
            supported_formats=self.supported_formats,
            enabled=self.enabled,
            policy_notice=self.policy_notice
        )

    @abstractmethod
    async def analyze(self, url: str) -> AnalyzeResponse:
        """Extracts truthful available media formats and metadata without bypassing auth/DRM."""
        pass

    @abstractmethod
    async def download(
        self,
        analysis_data: dict,
        format_id: str,
        storage_dir: Path,
        progress_callback: Callable[[float, str], Coroutine[Any, Any, None]]
    ) -> Tuple[Path, str, str]:
        """
        Executes download for chosen format_id.
        Returns: (final_file_path, attachment_filename, mime_type)
        """
        pass

