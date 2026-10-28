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

    return FileResponse(
        path=str(job.file_path),
        filename=job.filename or "media_download",
        media_type=job.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{job.filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )

@router.delete("/{job_id}", response_model=DownloadJobResponse)
async def cancel_download_job(job_id: str):
    job = download_service.cancel_job(job_id)
    return job.to_response()

