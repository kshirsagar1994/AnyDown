import pytest
import ipaddress
from app.core.security import is_ip_disallowed, validate_url_syntax, verify_destination_ip
from app.core.exceptions import InvalidUrlError, SSRFSecurityError
from app.services.storage_service import sanitize_filename, get_job_storage_dir

def test_private_ip_detection():
    # Loopback
    assert is_ip_disallowed(ipaddress.ip_address("127.0.0.1"))
    assert is_ip_disallowed(ipaddress.ip_address("127.0.0.254"))
    assert is_ip_disallowed(ipaddress.ip_address("::1"))

    # RFC 1918 Private
    assert is_ip_disallowed(ipaddress.ip_address("10.0.0.1"))
    assert is_ip_disallowed(ipaddress.ip_address("172.16.0.5"))
    assert is_ip_disallowed(ipaddress.ip_address("192.168.1.100"))

    # Cloud metadata / Link local
    assert is_ip_disallowed(ipaddress.ip_address("169.254.169.254"))
    assert is_ip_disallowed(ipaddress.ip_address("fe80::1"))

    # Public IP should not be disallowed
    assert not is_ip_disallowed(ipaddress.ip_address("8.8.8.8"))
    assert not is_ip_disallowed(ipaddress.ip_address("1.1.1.1"))

def test_url_syntax_validation():
    # Valid HTTPS URL
    clean, host = validate_url_syntax("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert host == "www.youtube.com"

    # Reject non-https protocols
    with pytest.raises(InvalidUrlError):
        validate_url_syntax("file:///etc/passwd")

    with pytest.raises(InvalidUrlError):
        validate_url_syntax("ftp://example.com/file.mp4")

    with pytest.raises(InvalidUrlError):
        validate_url_syntax("javascript:alert(1)")

    # Reject URLs with embedded credentials
    with pytest.raises(InvalidUrlError):
        validate_url_syntax("https://admin:secret@youtube.com/video")

    # Reject empty URL
    with pytest.raises(InvalidUrlError):
        validate_url_syntax("")

def test_filename_sanitization():
    # Remove traversal and illegal chars
    res = sanitize_filename("../../../etc/passwd", "mp4")
    assert ".." not in res
    assert "/" not in res
    assert res.endswith(".mp4")

    # Clean special characters
    res = sanitize_filename('My Great Video: Episode 1? *Special* <4K> | "Fun"', "mp4")
    assert ":" not in res
    assert "?" not in res
    assert "*" not in res
    assert "<" not in res
    assert ">" not in res
    assert '"' not in res
    assert res.endswith(".mp4")

def test_path_traversal_job_id():
    # Prevent traversal in job storage
    with pytest.raises(Exception):
        get_job_storage_dir("../../../sensitive")

