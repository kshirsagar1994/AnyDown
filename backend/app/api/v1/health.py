import shutil
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check():
    ffmpeg_available = shutil.which("ffmpeg") is not None
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "ffmpeg": "available" if ffmpeg_available else "missing",
        "temp_storage": "ready"
    }

