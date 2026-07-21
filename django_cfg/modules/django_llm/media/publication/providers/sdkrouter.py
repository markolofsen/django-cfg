"""No-key client for the CMDOP-owned cdn.sdkrouter.com gateway."""
from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import math
import re
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import BinaryIO, Iterator
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..errors import (
    TemporaryPublicationError,
    TemporaryPublicationInvalidResponseError,
    TemporaryPublicationRateLimitError,
    TemporaryPublicationTooLargeError,
    TemporaryPublicationTransportError,
)
from ..models import PublishedMedia

DEFAULT_BASE_URL = "https://cdn.sdkrouter.com"
SDKROUTER_MAX_BYTES = 8 * 1024 * 1024
ALLOWED_CONTENT_TYPES = frozenset(
    {"image/png", "image/jpeg", "image/webp", "image/gif", "image/avif", "video/mp4", "video/webm"}
)


class _UploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    publication_id: str = Field(alias="publicationId", min_length=1)
    url: str = Field(min_length=1)
    delete_token: str = Field(alias="deleteToken", min_length=32)
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime = Field(alias="expiresAt")
    bytes: int = Field(gt=0)
    content_type: str = Field(alias="contentType", min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _validate_public_https(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise TemporaryPublicationInvalidResponseError("publisher returned an invalid HTTPS URL")
    if parsed.hostname.lower() == "localhost" or parsed.hostname.lower().endswith(".local"):
        raise TemporaryPublicationInvalidResponseError("publisher returned a non-public URL")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return
    if not address.is_global:
        raise TemporaryPublicationInvalidResponseError("publisher returned a non-public URL")


def _validate_gateway_url(url: str, base_url: str) -> None:
    _validate_public_https(url)
    parsed = urlsplit(url)
    base = urlsplit(base_url)
    try:
        origin = (parsed.scheme, parsed.hostname, parsed.port)
        base_origin = (base.scheme, base.hostname, base.port)
    except ValueError as exc:
        raise TemporaryPublicationInvalidResponseError("publisher returned an invalid gateway port") from exc
    if origin != base_origin:
        raise TemporaryPublicationInvalidResponseError("publisher returned a URL outside its gateway origin")
    if not parsed.path.startswith("/v1/media/") or parsed.query or parsed.fragment:
        raise TemporaryPublicationInvalidResponseError("publisher returned an invalid media URL")


def _header_filename(filename: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", filename).strip("-")[:120]
    if not normalized:
        raise TemporaryPublicationError("publication filename must contain a safe filename character")
    return normalized


@contextmanager
def _source(source: bytes | Path) -> Iterator[tuple[bytes | BinaryIO, int, str]]:
    if isinstance(source, bytes):
        yield source, len(source), hashlib.sha256(source).hexdigest()
        return
    path = source.expanduser().resolve()
    try:
        with path.open("rb") as original, tempfile.TemporaryFile() as snapshot:
            digest = hashlib.sha256()
            size = 0
            while chunk := original.read(1024 * 1024):
                size += len(chunk)
                if size > SDKROUTER_MAX_BYTES:
                    raise TemporaryPublicationTooLargeError(
                        f"publication source exceeds {SDKROUTER_MAX_BYTES} bytes"
                    )
                digest.update(chunk)
                snapshot.write(chunk)
            snapshot.seek(0)
            yield snapshot, size, digest.hexdigest()
    except OSError as exc:
        raise TemporaryPublicationError(f"cannot read publication source: {path}") from exc


def _raise_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    if response.status_code == 413:
        raise TemporaryPublicationTooLargeError("temporary-media gateway rejected the input size")
    if response.status_code == 429:
        raise TemporaryPublicationRateLimitError("temporary-media gateway rate limit exceeded")
    if response.status_code >= 500:
        raise TemporaryPublicationTransportError(
            f"temporary-media gateway failed with HTTP {response.status_code}"
        )
    raise TemporaryPublicationError(f"temporary-media gateway rejected the request with HTTP {response.status_code}")


class SdkRouterPublisher:
    """Publish exact bytes to the shared temporary gateway without an API key."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
        client_id: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        _validate_public_https(base_url)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = client_id or f"cmdop-llm-{uuid.uuid4()}"
        self.transport = transport

    def publish(
        self,
        source: bytes | Path,
        *,
        filename: str,
        content_type: str,
        expires_in: timedelta,
        expected_sha256: str | None = None,
    ) -> PublishedMedia:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise TemporaryPublicationError(f"unsupported publication content type: {content_type}")
        seconds = math.ceil(expires_in.total_seconds())
        if seconds < 300 or seconds > 86_400:
            raise TemporaryPublicationError("publication TTL must be between 5 minutes and 24 hours")
        with _source(source) as (body, size, actual_sha256):
            if size <= 0:
                raise TemporaryPublicationError("publication source is empty")
            if size > SDKROUTER_MAX_BYTES:
                raise TemporaryPublicationTooLargeError(
                    f"publication source exceeds {SDKROUTER_MAX_BYTES} bytes"
                )
            if expected_sha256 is not None and expected_sha256 != actual_sha256:
                raise TemporaryPublicationError("publication source SHA-256 does not match expected_sha256")
            headers = {
                "Content-Type": content_type,
                "Content-Length": str(size),
                "X-Cmdop-Client": self.client_id,
                "X-Cmdop-Filename": _header_filename(filename),
                "X-Cmdop-TTL-Seconds": str(seconds),
            }
            try:
                with httpx.Client(timeout=self.timeout, transport=self.transport, follow_redirects=False) as client:
                    response = client.post(f"{self.base_url}/v1/media", headers=headers, content=body)
            except httpx.HTTPError as exc:
                raise TemporaryPublicationTransportError("temporary-media gateway request failed") from exc
        _raise_status(response)
        try:
            payload = _UploadResponse.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise TemporaryPublicationInvalidResponseError("temporary-media gateway returned invalid JSON") from exc
        _validate_gateway_url(payload.url, self.base_url)
        if payload.bytes != size or payload.content_type != content_type or payload.sha256 != actual_sha256:
            raise TemporaryPublicationInvalidResponseError("temporary-media gateway receipt does not match source")
        now = datetime.now(timezone.utc)
        if payload.created_at.tzinfo is None or payload.expires_at.tzinfo is None:
            raise TemporaryPublicationInvalidResponseError("temporary-media gateway returned naive timestamps")
        if payload.expires_at < now + timedelta(seconds=seconds - 10):
            raise TemporaryPublicationInvalidResponseError("temporary-media gateway returned an insufficient TTL")
        return PublishedMedia(
            provider="sdkrouter-cdn",
            publication_id=payload.publication_id,
            url=payload.url,
            revoke_token=payload.delete_token,
            created_at=payload.created_at,
            expires_at=payload.expires_at,
            content_type=payload.content_type,
            bytes=payload.bytes,
            sha256=payload.sha256,
            filename=filename,
        )

    async def apublish(
        self,
        source: bytes | Path,
        *,
        filename: str,
        content_type: str,
        expires_in: timedelta,
        expected_sha256: str | None = None,
    ) -> PublishedMedia:
        return await asyncio.to_thread(
            self.publish,
            source,
            filename=filename,
            content_type=content_type,
            expires_in=expires_in,
            expected_sha256=expected_sha256,
        )

    def revoke(self, publication: PublishedMedia) -> None:
        if publication.provider != "sdkrouter-cdn":
            raise TemporaryPublicationError("publication belongs to a different provider")
        url = publication.url.get_secret_value()
        _validate_gateway_url(url, self.base_url)
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport, follow_redirects=False) as client:
                response = client.delete(
                    url,
                    headers={"Authorization": f"Bearer {publication.revoke_token.get_secret_value()}"},
                )
        except httpx.HTTPError as exc:
            raise TemporaryPublicationTransportError("temporary-media revoke request failed") from exc
        if response.status_code in {404, 410}:
            return
        _raise_status(response)

    async def arevoke(self, publication: PublishedMedia) -> None:
        await asyncio.to_thread(self.revoke, publication)
