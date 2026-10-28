import time
from typing import Dict
from app.core.security import validate_url_syntax, verify_destination_ip, rate_limiter
from app.services.adapters.registry import adapter_registry
from app.schemas.analysis import AnalyzeResponse
from app.core.exceptions import ContentNotFoundError, AnyDownException

# In-memory analysis cache (analysis_id -> dict with timestamp, response)
ANALYSIS_CACHE: Dict[str, dict] = {}
CACHE_TTL_SECONDS = 3600

def cleanup_analysis_cache():
    now = time.time()
    expired = [k for k, v in ANALYSIS_CACHE.items() if now - v["timestamp"] > CACHE_TTL_SECONDS]
    for k in expired:
        ANALYSIS_CACHE.pop(k, None)

class AnalysisService:
    @staticmethod
    async def analyze_url(raw_url: str, client_ip: str) -> AnalyzeResponse:
        cleanup_analysis_cache()
        rate_limiter.check(client_ip)

        # 1. URL syntax validation
        clean_url, hostname = validate_url_syntax(raw_url)

        # 2. SSRF check
        verify_destination_ip(hostname)

        # 3. Platform adapter lookup
        adapter = adapter_registry.find_adapter(hostname, clean_url)

        # 4. Extract metadata and available formats
        res = await adapter.analyze(clean_url)

        # 5. Store in analysis cache
        ANALYSIS_CACHE[res.analysis_id] = {
            "timestamp": time.time(),
            "data": res.model_dump(),
            "platform_id": adapter.id,
            "url": clean_url
        }

        return res

    @staticmethod
    def get_analysis(analysis_id: str) -> dict:
        cleanup_analysis_cache()
        item = ANALYSIS_CACHE.get(analysis_id)
        if not item:
            raise ContentNotFoundError("Analysis session expired or not found. Please analyze the link again.")
        return item

analysis_service = AnalysisService()

