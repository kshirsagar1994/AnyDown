from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.schemas.downloads import DownloadRequest, DownloadJobResponse
from app.services.download_service import download_service
from app.core.exceptions import JobNotFoundError, AnyDownException

router = APIRouter(prefix="/downloads", tags=["Downloads"])

@router.post("", response_model=DownloadJobResponse)
async def create_download_job(req: DownloadRequest):
    job = download_service.create_job(req.analysis_id, req.format_id)
    return job.to_response()

@router.get("/{job_id}", response_model=DownloadJobResponse)
async def get_download_job(job_id: str):
    job = download_service.get_job(job_id)
    return job.to_response()

@router.get("/{job_id}/events")
async def stream_download_events(job_id: str):
    # Verify job exists first
    download_service.get_job(job_id)
    return EventSourceResponse(download_service.stream_job_events(job_id))

@router.get("/{job_id}/file")
async def download_final_file(job_id: str):
    job = download_service.get_job(job_id)
    if job.status != "completed" or not job.file_path or not job.file_path.exists():
        raise HTTPException(
            status_code=400,
            detail="File is not yet ready or job has not completed."
        )

    import urllib.parse
    import re

    # Remove any non-ASCII characters for RFC fallback header
    raw_name = job.filename or "media_download"
    safe_ascii_filename = re.sub(r'[^\x20-\x7e]', '_', raw_name)
    safe_ascii_filename = re.sub(r'[\"\'\\/]', '', safe_ascii_filename).strip()
    if not safe_ascii_filename:
        safe_ascii_filename = "media_download"

    encoded_filename = urllib.parse.quote(raw_name)

    return FileResponse(
        path=str(job.file_path),
        filename=safe_ascii_filename,
        media_type=job.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )

@router.delete("/{job_id}", response_model=DownloadJobResponse)
async def cancel_download_job(job_id: str):
    job = download_service.cancel_job(job_id)
    return job.to_response()

