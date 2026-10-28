from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class MediaFormat(BaseModel):
    format_id: str = Field(..., description="Opaque unique format identifier")
    media_type: str = Field(..., description="'video', 'audio', or 'image'")
    container: str = Field(..., description="Target extension/container: 'mp4', 'mp3', 'jpg', or 'png'")
    quality_label: str = Field(..., description="Human readable quality label, e.g. 1080p, 720p, 320 kbps")
    width: Optional[int] = Field(None, description="Width in pixels for video/image")
    height: Optional[int] = Field(None, description="Height in pixels for video/image")
    estimated_size_bytes: Optional[int] = Field(None, description="Estimated file size in bytes if known")
    requires_conversion: bool = Field(False, description="Whether server-side FFmpeg conversion/merging is needed")
    note: Optional[str] = Field(None, description="Additional format info or audio codec")

class MediaMetadata(BaseModel):
    title: str = Field(..., description="Media or post title")
    creator: Optional[str] = Field(None, description="Creator, channel, or author username")
    thumbnail_url: Optional[str] = Field(None, description="URL to safe media preview thumbnail")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds for video/audio")
    source_url: str = Field(..., description="Cleaned original URL")

class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="Public content URL to analyze")

class AnalyzeResponse(BaseModel):
    analysis_id: str = Field(..., description="Opaque analysis identifier")
    platform: str = Field(..., description="Detected platform ID")
    content_type: str = Field(..., description="Media type: video, audio, image, carousel")
    metadata: MediaMetadata
    formats: List[MediaFormat] = Field(default_factory=list, description="List of genuinely available formats")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings or limitations")

