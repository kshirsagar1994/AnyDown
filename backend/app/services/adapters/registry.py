from typing import List, Optional
from app.services.adapters.base import BaseAdapter
from app.services.adapters.mock import MockAdapter
from app.services.adapters.youtube import YouTubeAdapter
from app.services.adapters.instagram import InstagramAdapter
from app.services.adapters.social_adapters import (
    TikTokAdapter,
    TwitterAdapter,
    RedditAdapter,
    PinterestAdapter,
    FacebookAdapter,
    SnapchatAdapter,
    GenericSocialAdapter
)
from app.core.exceptions import UnsupportedPlatformError
from app.schemas.platform import PlatformCapability

class AdapterRegistry:
    def __init__(self):
        self.adapters: List[BaseAdapter] = [
            MockAdapter(),
            YouTubeAdapter(),
            InstagramAdapter(),
            TikTokAdapter(),
            TwitterAdapter(),
            RedditAdapter(),
            PinterestAdapter(),
            FacebookAdapter(),
            SnapchatAdapter(),
            GenericSocialAdapter(),
        ]

    def find_adapter(self, hostname: str, url: str) -> BaseAdapter:
        hostname_lower = hostname.lower()
        for adapter in self.adapters:
            if adapter.enabled and adapter.can_handle(hostname_lower, url):
                return adapter
        raise UnsupportedPlatformError(f"No adapter available for platform host '{hostname}'.")

    def get_all_capabilities(self) -> List[PlatformCapability]:
        return [adapter.capabilities() for adapter in self.adapters if adapter.enabled and adapter.id != "mock"]

adapter_registry = AdapterRegistry()

