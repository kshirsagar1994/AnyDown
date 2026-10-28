from fastapi import APIRouter
from app.api.v1.analyze import router as analyze_router
from app.api.v1.downloads import router as downloads_router
from app.api.v1.platforms import router as platforms_router
from app.api.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(analyze_router)
api_v1_router.include_router(downloads_router)
api_v1_router.include_router(platforms_router)

__all__ = ["api_v1_router"]

