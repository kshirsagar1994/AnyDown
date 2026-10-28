import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AnyDownException
from app.api.v1 import api_v1_router
from app.services.storage_service import cleanup_expired_storage

# Configure structured logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("anydown")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AnyDown API server...")
    cleanup_expired_storage()
    yield
    logger.info("Shutting down AnyDown API server...")
    cleanup_expired_storage()

app = FastAPI(
    title="AnyDown API",
    version="1.0.0",
    description="High-performance media-link analysis and lawful download engine.",
    lifespan=lifespan
)

# CORS configuration
allow_all = settings.FRONTEND_ORIGIN == "*"
origins = ["*"] if allow_all else [
    settings.FRONTEND_ORIGIN,
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(AnyDownException)
async def handle_anydown_exception(request: Request, exc: AnyDownException):
    logger.warning(f"Handled error [{exc.code}] on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {}
            }
        }
    )

@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request. Please try again later.",
                "details": {}
            }
        }
    )

# Include API v1 router
app.include_router(api_v1_router)

@app.get("/")
async def root():
    return {
        "app": "AnyDown",
        "status": "online",
        "docs": "/docs",
        "api_v1": "/api/v1"
    }

