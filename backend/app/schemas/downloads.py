from typing import Optional
from pydantic import BaseModel, Field

class DownloadRequest(BaseModel):
    analysis_id: str = Field(..., description="The ID received from a successful /analyze call")
    format_id: str = Field(..., description="The selected format_id from the available formats")

class DownloadJobResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current status: queued, downloading, converting, completed, failed, cancelled")
    events_url: str = Field(..., description="SSE endpoint to stream real-time progress events")
    download_url: Optional[str] = Field(None, description="Direct URL to download the finalized file once completed")
    percent: Optional[float] = Field(None, description="Current progress percentage (0-100) or null if indeterminate")
    message: Optional[str] = Field(None, description="Human readable progress status message")
    filename: Optional[str] = Field(None, description="Sanitized attachment filename")
    file_size: Optional[int] = Field(None, description="Actual finalized file size in bytes")

class SSEEventPayload(BaseModel):
    status: str
    percent: Optional[float] = None
    message: str
    download_url: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None

