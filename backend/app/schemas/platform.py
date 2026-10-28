from typing import List, Optional
from pydantic import BaseModel, Field

class PlatformCapability(BaseModel):
    id: str = Field(..., description="Unique platform identifier (e.g. youtube, instagram)")
    name: str = Field(..., description="Human readable name (e.g. YouTube)")
    hostname_patterns: List[str] = Field(..., description="Hostnames matched by this platform")
    supported_content_types: List[str] = Field(..., description="Supported content types: video, audio, image, post, etc.")
    supported_formats: List[str] = Field(..., description="Target output formats (mp4, mp3, jpg)")
    enabled: bool = Field(True, description="Whether this adapter is currently active")
    policy_notice: str = Field(..., description="Compliance and terms notice")

class PlatformListResponse(BaseModel):
    platforms: List[PlatformCapability]
    legal_disclaimer: str

