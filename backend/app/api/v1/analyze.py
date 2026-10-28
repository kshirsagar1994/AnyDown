from fastapi import APIRouter, Request, HTTPException
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("", response_model=AnalyzeResponse)
async def analyze_url(req: AnalyzeRequest, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    # Check X-Forwarded-For if behind reverse proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    return await analysis_service.analyze_url(req.url, client_ip)

