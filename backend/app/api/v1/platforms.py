from fastapi import APIRouter
from app.schemas.platform import PlatformListResponse
from app.services.adapters.registry import adapter_registry

router = APIRouter(prefix="/platforms", tags=["Platforms"])

@router.get("", response_model=PlatformListResponse)
async def list_platforms():
    capabilities = adapter_registry.get_all_capabilities()
    disclaimer = (
        "AnyDown only permits downloading content users own or are authorized to download. "
        "Support depends on each platform's lawful terms and official availability. "
        "We do not bypass DRM, authentication, paywalls, private-account controls, or anti-bot protections."
    )
    return PlatformListResponse(
        platforms=capabilities,
        legal_disclaimer=disclaimer
    )

