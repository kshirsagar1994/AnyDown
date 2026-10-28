import asyncio
import time
import uuid
from typing import Dict, Optional, Any, AsyncGenerator
from pathlib import Path
from app.core.exceptions import (
    JobNotFoundError,
    FormatUnavailableError,
    StorageLimitError,
    AnyDownException
)
from app.services.analysis_service import analysis_service
from app.services.adapters.registry import adapter_registry
from app.services.storage_service import (
    get_job_storage_dir,
    cleanup_expired_storage,
    validate_file_magic_number
)
from app.schemas.downloads import DownloadJobResponse, SSEEventPayload
from app.core.config import settings

class DownloadJob:
    def __init__(self, job_id: str, analysis_id: str, format_id: str):
        self.job_id = job_id
        self.analysis_id = analysis_id
        self.format_id = format_id
        self.status = "queued"  # queued, downloading, converting, completed, failed, cancelled
        self.percent: Optional[float] = 0.0
        self.message = "Queued download job..."
        self.file_path: Optional[Path] = None
        self.filename: Optional[str] = None
        self.file_size: Optional[int] = None
        self.mime_type: Optional[str] = None
        self.created_at = time.time()
        self.updated_at = time.time()
        self.events_queue: asyncio.Queue = asyncio.Queue()
        self.task: Optional[asyncio.Task] = None
        self.cancelled = False

    def update(self, status: str, percent: Optional[float], message: str):
        if self.cancelled:
            return
        self.status = status
        if percent is not None:
            # Monotonic progress rule: do not decrease progress
            if self.percent is not None:
                self.percent = max(self.percent, percent)
            else:
                self.percent = percent
        self.message = message
        self.updated_at = time.time()

        payload = SSEEventPayload(
            status=self.status,
            percent=self.percent,
            message=self.message,
            download_url=f"/api/v1/downloads/{self.job_id}/file" if self.status == "completed" else None,
            filename=self.filename,
            file_size=self.file_size
        )
        self.events_queue.put_nowait(payload)

    def to_response(self) -> DownloadJobResponse:
        return DownloadJobResponse(
            job_id=self.job_id,
            status=self.status,
            events_url=f"/api/v1/downloads/{self.job_id}/events",
            download_url=f"/api/v1/downloads/{self.job_id}/file" if self.status == "completed" else None,
            percent=self.percent,
            message=self.message,
            filename=self.filename,
            file_size=self.file_size
        )

# Global Job Registry
JOBS: Dict[str, DownloadJob] = {}

class DownloadService:
    @staticmethod
    def create_job(analysis_id: str, format_id: str) -> DownloadJob:
        cleanup_expired_storage()

        # Validate analysis session exists
        analysis_item = analysis_service.get_analysis(analysis_id)
        formats = analysis_item["data"].get("formats", [])
        
        # FR-04: Truthful format selection (cannot choose a format not in analysis response)
        matched_format = next((f for f in formats if f["format_id"] == format_id), None)
        if not matched_format:
            raise FormatUnavailableError(f"Format ID '{format_id}' is not available for this media.")

        job_id = str(uuid.uuid4())
        job = DownloadJob(job_id, analysis_id, format_id)
        JOBS[job_id] = job

        # Launch background async worker task
        job.task = asyncio.create_task(DownloadService._run_worker(job, analysis_item, matched_format))
        return job

    @staticmethod
    async def _run_worker(job: DownloadJob, analysis_item: dict, matched_format: dict):
        try:
            job.update("downloading", 5.0, "Contacting media server...")
            storage_dir = get_job_storage_dir(job.job_id)

            platform_id = analysis_item["platform_id"]
            url = analysis_item["url"]

            hostname = analysis_item["data"]["metadata"]["source_url"]
            from urllib.parse import urlparse
            parsed_host = urlparse(hostname).hostname or ""
            adapter = adapter_registry.find_adapter(parsed_host, url)

            async def progress_hook(pct: float, msg: str):
                if job.cancelled:
                    raise asyncio.CancelledError()
                # If preparing/converting, adjust stage status
                new_status = "converting" if pct > 80.0 else "downloading"
                job.update(new_status, pct, msg)

            file_path, filename, mime_type = await adapter.download(
                analysis_item["data"],
                job.format_id,
                storage_dir,
                progress_hook
            )

            if job.cancelled:
                return

            if not file_path.exists():
                raise AnyDownException("Output file was not generated.", code="FILE_NOT_FOUND", status_code=500)

            file_size = file_path.stat().st_size
            if file_size > settings.MAX_DOWNLOAD_BYTES:
                file_path.unlink(missing_ok=True)
                raise StorageLimitError(f"File size ({file_size} bytes) exceeds maximum limit of {settings.MAX_DOWNLOAD_BYTES} bytes.")

            job.file_path = file_path
            job.filename = filename
            job.file_size = file_size
            job.mime_type = mime_type

            # Finalize only after validation
            job.update("completed", 100.0, "Media processing complete! File ready for download.")

        except asyncio.CancelledError:
            job.status = "cancelled"
            job.update("cancelled", None, "Download cancelled by user.")
        except Exception as e:
            job.status = "failed"
            err_msg = str(e)
            job.update("failed", None, f"Download failed: {err_msg}")

    @staticmethod
    def get_job(job_id: str) -> DownloadJob:
        job = JOBS.get(job_id)
        if not job:
            raise JobNotFoundError("The requested download job was not found or has expired.")
        return job

    @staticmethod
    def cancel_job(job_id: str) -> DownloadJob:
        job = DownloadService.get_job(job_id)
        if job.status not in ("completed", "failed", "cancelled"):
            job.cancelled = True
            if job.task and not job.task.done():
                job.task.cancel()
            job.update("cancelled", None, "Download was cancelled.")
        return job

    @staticmethod
    async def stream_job_events(job_id: str) -> AsyncGenerator[dict, None]:
        job = DownloadService.get_job(job_id)

        # Send initial immediate snapshot state
        initial_payload = SSEEventPayload(
            status=job.status,
            percent=job.percent,
            message=job.message,
            download_url=f"/api/v1/downloads/{job.job_id}/file" if job.status == "completed" else None,
            filename=job.filename,
            file_size=job.file_size
        )
        yield {"event": "progress" if job.status != "completed" else "completed", "data": initial_payload.model_dump_json()}

        if job.status in ("completed", "failed", "cancelled"):
            return

        # Stream upcoming queue events
        while True:
            try:
                payload: SSEEventPayload = await asyncio.wait_for(job.events_queue.get(), timeout=15.0)
                event_name = "completed" if payload.status == "completed" else ("error" if payload.status == "failed" else "progress")
                yield {"event": event_name, "data": payload.model_dump_json()}

                if payload.status in ("completed", "failed", "cancelled"):
                    break
            except asyncio.TimeoutError:
                # Heartbeat keep-alive
                yield {"event": "ping", "data": '{"ping": true}'}

download_service = DownloadService()

