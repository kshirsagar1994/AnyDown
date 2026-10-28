import ipaddress
import socket
import re
import time
from urllib.parse import urlparse
from typing import Set, Tuple, Optional, Dict
from app.core.exceptions import InvalidUrlError, SSRFSecurityError, RateLimitError
from app.core.config import settings

# Disallowed private and special network blocks
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::ffff:0:0/96"),
    ipaddress.ip_network("100::/64"),
    ipaddress.ip_network("64:ff9b::/96"),
    ipaddress.ip_network("2001::/32"),
    ipaddress.ip_network("2001:db8::/32"),
    ipaddress.ip_network("2002::/16"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]

# Supported Platform Base Domains
ALLOWED_DOMAINS: Set[str] = {
    # YouTube
    "youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be",
    # Instagram
    "instagram.com", "www.instagram.com",
    # TikTok
    "tiktok.com", "www.tiktok.com", "vt.tiktok.com", "vm.tiktok.com",
    # Twitter / X
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    # Facebook
    "facebook.com", "www.facebook.com", "fb.watch", "m.facebook.com", "web.facebook.com",
    # Snapchat
    "snapchat.com", "www.snapchat.com", "story.snapchat.com",
    # Reddit
    "reddit.com", "www.reddit.com", "v.redd.it", "redd.it", "old.reddit.com",
    # Pinterest
    "pinterest.com", "www.pinterest.com", "pin.it",
    # LinkedIn
    "linkedin.com", "www.linkedin.com",
    # Threads
    "threads.net", "www.threads.net",
    # Discord
    "cdn.discordapp.com", "media.discordapp.net",
    # Quora
    "quora.com", "www.quora.com",
    # Mock / Test fixtures
    "mock-media.anydown.local", "fixtures.anydown.local"
}

def is_ip_disallowed(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks if an IP address falls inside any private, loopback, or reserved range."""
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    for net in BLOCKED_IP_NETWORKS:
        if ip in net:
            return True
    return False

def validate_url_syntax(url_str: str, allow_http: bool = False) -> Tuple[str, str]:
    """
    Validates URL format, ensures scheme is https (or http if permitted in tests),
    checks for control characters, user-info, IP literals, and returns (clean_url, hostname).
    """
    if not url_str or not isinstance(url_str, str):
        raise InvalidUrlError("URL is empty or missing.")

    clean_url = url_str.strip()
    if len(clean_url) > 2048:
        raise InvalidUrlError("URL exceeds maximum length of 2048 characters.")

    # Check for forbidden control characters or null bytes
    if any(ord(c) < 32 or ord(c) == 127 for c in clean_url):
        raise InvalidUrlError("URL contains invalid control characters.")

    try:
        parsed = urlparse(clean_url)
    except Exception as e:
        raise InvalidUrlError(f"Malformed URL: {str(e)}")

    scheme = parsed.scheme.lower()
    allowed_schemes = ["https", "http"] if allow_http else ["https"]
    if scheme not in allowed_schemes:
        raise InvalidUrlError(f"Protocol '{scheme}' is not supported. Only secure HTTPS URLs are permitted.")

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        raise InvalidUrlError("URL does not contain a valid hostname.")

    # Reject usernames/passwords in URLs (e.g. https://user:pass@domain.com)
    if parsed.username or parsed.password:
        raise InvalidUrlError("User credentials in URLs are strictly disallowed.")

    # Reject direct IP literal hosts to avoid internal scanning
    try:
        ip = ipaddress.ip_address(hostname)
        if is_ip_disallowed(ip):
            raise SSRFSecurityError(f"Access to private/internal IP address '{hostname}' is blocked.")
    except ValueError:
        pass  # Not an IP literal, which is preferred

    return clean_url, hostname

def is_hostname_allowed(hostname: str) -> bool:
    """Checks if hostname matches our platform allowlist or is an approved subdomain."""
    hostname = hostname.lower()
    if hostname in ALLOWED_DOMAINS:
        return True
    
    # Check if it's a subdomain of any allowed base domain
    for domain in ALLOWED_DOMAINS:
        if hostname.endswith("." + domain):
            return True
    return False

def verify_destination_ip(hostname: str, port: int = 443) -> None:
    """
    Performs DNS resolution on the hostname and validates every resolved IP address
    to ensure it does not resolve to an internal, loopback, or private network (SSRF defense).
    """
    # Special bypass for local mock fixtures in dev/test mode
    if hostname.endswith(".anydown.local"):
        return

    try:
        addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise InvalidUrlError(f"Failed to resolve domain name '{hostname}': {e.strerror}")

    resolved_ips = set()
    for item in addr_info:
        sockaddr = item[4]
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            resolved_ips.add(ip_obj)
            if is_ip_disallowed(ip_obj):
                raise SSRFSecurityError(
                    f"Domain '{hostname}' resolves to restricted IP '{ip_str}'."
                )
        except ValueError:
            raise SSRFSecurityError(f"Invalid resolved IP format '{ip_str}'.")

    if not resolved_ips:
        raise InvalidUrlError(f"No IP addresses found for domain '{hostname}'.")

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, limit_per_minute: int = 30):
        self.limit = limit_per_minute
        self.requests: Dict[str, list[float]] = {}

    def check(self, client_ip: str) -> None:
        now = time.time()
        window = 60.0
        timestamps = self.requests.get(client_ip, [])
        # Prune old timestamps
        timestamps = [ts for ts in timestamps if now - ts < window]
        if len(timestamps) >= self.limit:
            self.requests[client_ip] = timestamps
            raise RateLimitError(f"Rate limit of {self.limit} requests per minute exceeded.")
        timestamps.append(now)
        self.requests[client_ip] = timestamps

rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)

