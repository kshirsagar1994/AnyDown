from typing import Optional, Dict, Any

class AnyDownException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class InvalidUrlError(AnyDownException):
    def __init__(self, message: str = "Invalid URL syntax or unsupported protocol. Must be a valid web URL.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="INVALID_URL", status_code=400, details=details)

class UnsupportedPlatformError(AnyDownException):
    def __init__(self, message: str = "The provided platform or hostname is not supported.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="UNSUPPORTED_PLATFORM", status_code=400, details=details)

class SSRFSecurityError(AnyDownException):
    def __init__(self, message: str = "Destination IP address or hostname resolved to an unauthorized or private network address.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="SECURITY_VIOLATION_SSRF", status_code=403, details=details)

class ContentAccessError(AnyDownException):
    def __init__(self, message: str = "Cannot access the requested content. It may be private, removed, age-restricted, or protected by access controls.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONTENT_ACCESS_DENIED", status_code=403, details=details)

class ContentNotFoundError(AnyDownException):
    def __init__(self, message: str = "The requested media could not be found at this link.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONTENT_NOT_FOUND", status_code=404, details=details)

class AnalysisFailedError(AnyDownException):
    def __init__(self, message: str = "Failed to analyze media from the provided URL.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ANALYSIS_FAILED", status_code=422, details=details)

class FormatUnavailableError(AnyDownException):
    def __init__(self, message: str = "The requested format is not available for this media.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORMAT_UNAVAILABLE", status_code=400, details=details)

class JobNotFoundError(AnyDownException):
    def __init__(self, message: str = "Download job not found or has expired.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="JOB_NOT_FOUND", status_code=404, details=details)

class RateLimitError(AnyDownException):
    def __init__(self, message: str = "Too many requests. Please wait a moment before trying again.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", status_code=429, details=details)

class StorageLimitError(AnyDownException):
    def __init__(self, message: str = "Media exceeds maximum permissible download size or duration limits.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="MEDIA_LIMIT_EXCEEDED", status_code=413, details=details)

class ConversionError(AnyDownException):
    def __init__(self, message: str = "Failed to process or convert the media file into the requested container format.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONVERSION_FAILED", status_code=500, details=details)

