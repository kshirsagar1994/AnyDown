import os
import re
import time
import shutil
from pathlib import Path
from typing import Tuple, Optional
from app.core.config import settings
from app.core.exceptions import AnyDownException

MIME_TYPES = {
    "mp4": "video/mp4",
    "mp3": "audio/mpeg",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png"
}

def sanitize_filename(title: str, extension: str) -> str:
    """
    Sanitizes user or video title into a safe filesystem attachment filename.
    Removes path traversal components, control characters, and reserved characters.
    """
    ext = extension.lstrip(".").lower()
    if ext == "jpeg":
        ext = "jpg"

    # Remove non-alphanumeric/non-space/non-dash characters
    clean = re.sub(r'[\\/*?:"<>|]', '', title)
    clean = re.sub(r'[\x00-\x1f\x7f]', '', clean)
    clean = clean.strip().replace(" ", "_")
    clean = re.sub(r'_+', '_', clean)
    clean = clean.strip("._-")

    if not clean:
        clean = "anydown_media"

    # Limit length
    if len(clean) > 80:
        clean = clean[:80].rstrip("._-")

    return f"{clean}.{ext}"

def get_job_storage_dir(job_id: str) -> Path:
    """Returns the dedicated storage directory for a specific job, preventing path traversal."""
    if not job_id or "/" in job_id or "\\" in job_id or ".." in job_id:
        raise AnyDownException("Security violation: path traversal detected.", code="PATH_TRAVERSAL", status_code=403)

    safe_job_id = re.sub(r'[^a-zA-Z0-9_\-]', '', job_id)
    if not safe_job_id or safe_job_id != job_id:
        raise AnyDownException("Invalid job identifier format.", code="INVALID_JOB_ID", status_code=400)

    base = Path(settings.TEMP_DIR).resolve()
    target = (base / safe_job_id).resolve()

    # Ensure target is strictly within base directory
    if not str(target).startswith(str(base)):
        raise AnyDownException("Security violation: path traversal detected.", code="PATH_TRAVERSAL", status_code=403)

    target.mkdir(parents=True, exist_ok=True)
    return target

def validate_file_magic_number(file_path: Path, expected_container: str) -> bool:
    """
    Verifies that the file on disk genuinely matches the expected media container format
    by checking binary signatures / magic numbers.
    """
    if not file_path.exists() or file_path.stat().st_size == 0:
        return False

    with open(file_path, "rb") as f:
        header = f.read(32)

    expected = expected_container.lower()
    if expected == "mp4":
        # MP4 files typically have 'ftyp' at bytes 4..8
        return len(header) >= 8 and (b"ftyp" in header[:16] or b"moov" in header[:16])
    elif expected == "mp3":
        # MP3 files usually start with 'ID3' or 0xFF followed by MPEG sync bits
        if header.startswith(b"ID3"):
            return True
        if len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0:
            return True
        return False
    elif expected in ("jpg", "jpeg"):
        # JPEG starts with FF D8 FF
        return header.startswith(b"\xFF\xD8\xFF")
    elif expected == "png":
        # PNG starts with 89 50 4E 47 0D 0A 1A 0A
        return header.startswith(b"\x89PNG\r\n\x1a\n")

    return True

def cleanup_expired_storage():
    """Removes job temporary folders older than FILE_RETENTION_SECONDS."""
    base = Path(settings.TEMP_DIR)
    if not base.exists():
        return

    now = time.time()
    for item in base.iterdir():
        if item.is_dir():
            try:
                mtime = item.stat().st_mtime
                if now - mtime > settings.FILE_RETENTION_SECONDS:
                    shutil.rmtree(item, ignore_errors=True)
            except Exception:
                pass
