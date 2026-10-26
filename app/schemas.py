<<<<<<< HEAD
import ipaddress
=======
>>>>>>> origin/main
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

<<<<<<< HEAD
# Paths served by the application itself. A short code with one of these names would be
# accepted but could never be resolved, because the framework route wins.
RESERVED_CODES = frozenset(
    {"api", "docs", "redoc", "openapi.json", "health", "static", "favicon.ico"}
)

BLOCKED_HOSTNAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})
BLOCKED_SUFFIXES = (".local", ".localhost", ".internal")


def is_disallowed_host(raw_host: str) -> bool:
    """Return True for hosts that point at loopback, private, link-local or reserved space.

    The service never fetches destinations, so this is not SSRF protection for the service
    itself. It prevents the shortener from being used to disguise links to internal
    infrastructure (e.g. cloud metadata at 169.254.169.254) behind a public short URL.
    """
    host = raw_host.strip().lower().rstrip(".").strip("[]")
    if not host:
        return True
    if host in BLOCKED_HOSTNAMES or host.endswith(BLOCKED_SUFFIXES):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False  # A DNS name; reputation/resolution checks are a documented limitation.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return not ip.is_global or ip.is_multicast

=======
>>>>>>> origin/main

class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_code: str | None = Field(
        default=None, min_length=4, max_length=32, pattern=r"^[A-Za-z0-9_-]+$"
    )

    @field_validator("url")
    @classmethod
<<<<<<< HEAD
    def reject_non_public_destinations(cls, value):
        # AnyHttpUrl already restricts the scheme to http/https.
        if is_disallowed_host(value.host or ""):
            raise ValueError("Destination must be a public host")
        return value

    @field_validator("custom_code")
    @classmethod
    def reject_reserved_codes(cls, value):
        if value is not None and value.lower() in RESERVED_CODES:
            raise ValueError("custom_code is reserved")
=======
    def reject_local_or_non_http_urls(cls, value):
        # AnyHttpUrl restricts scheme to http/https. Production deployments should additionally
        # apply an outbound/domain policy if the service ever fetches destination URLs.
        host = (value.host or "").lower()
        if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local"):
            raise ValueError("Local destination hosts are not allowed")
>>>>>>> origin/main
        return value


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str
    created_at: datetime


class AnalyticsResponse(BaseModel):
    code: str
    original_url: str
    clicks: int
    created_at: datetime
    last_clicked_at: datetime | None


class HealthResponse(BaseModel):
    status: str
