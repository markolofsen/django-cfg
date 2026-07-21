"""Bounded source loading and content identity for media routing."""

from __future__ import annotations

import base64
import binascii
import hashlib
import ipaddress
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, TypeAlias
from urllib.parse import unquote, urlsplit

from ...core.image_io import FieldFileLike
from .errors import MediaSourceError

MediaSource: TypeAlias = bytes | bytearray | memoryview | str | Path | FieldFileLike

_MIME_EXTENSIONS = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
    "image/gif": ".gif", "image/avif": ".avif", "video/mp4": ".mp4",
    "video/webm": ".webm",
}


@dataclass(frozen=True, slots=True)
class LocalMedia:
    data: bytes
    filename: str
    content_type: str
    sha256: str


def is_remote_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def validate_public_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise MediaSourceError("public media URL must be absolute HTTPS without credentials")
    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith(".local"):
        raise MediaSourceError("public media URL must not target a local host")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return value
    if not address.is_global:
        raise MediaSourceError("public media URL must not target a private address")
    return value


def filename_from_url(value: str) -> str:
    name = Path(unquote(urlsplit(value).path)).name
    return name or "remote-media"


def decode_data_url(value: str, *, max_bytes: int) -> LocalMedia:
    header, separator, encoded = value.partition(",")
    if separator != "," or not header.startswith("data:") or not header.endswith(";base64"):
        raise MediaSourceError("media data URL must use base64 encoding")
    content_type = header[5:-7].lower()
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise MediaSourceError("media data URL contains invalid base64") from exc
    _validate_size(data, max_bytes=max_bytes)
    detected = _detect_content_type(data)
    if detected is None or detected != content_type:
        raise MediaSourceError("media data URL MIME does not match structurally valid bytes")
    return LocalMedia(
        data=data,
        filename=f"inline{_MIME_EXTENSIONS.get(content_type, '.bin')}",
        content_type=content_type,
        sha256=hashlib.sha256(data).hexdigest(),
    )


def encode_data_url(media: LocalMedia) -> str:
    encoded = base64.b64encode(media.data).decode("ascii")
    return f"data:{media.content_type};base64,{encoded}"


def _read_bounded(stream: BinaryIO, *, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while chunk := stream.read(min(1024 * 1024, max_bytes + 1 - size)):
        size += len(chunk)
        if size > max_bytes:
            raise MediaSourceError(f"media source exceeds {max_bytes} bytes")
        chunks.append(chunk)
    return b"".join(chunks)


def _validate_size(data: bytes, *, max_bytes: int) -> None:
    if not data:
        raise MediaSourceError("media source is empty")
    if len(data) > max_bytes:
        raise MediaSourceError(f"media source exceeds {max_bytes} bytes")


def _detect_content_type(data: bytes) -> str | None:
    if (
        len(data) >= 24
        and data.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
        and int.from_bytes(data[16:20], "big") > 0
        and int.from_bytes(data[20:24], "big") > 0
    ):
        return "image/png"
    if len(data) >= 4 and data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9"):
        return "image/jpeg"
    if len(data) >= 14 and data.startswith((b"GIF87a", b"GIF89a")) and data.endswith(b";"):
        return "image/gif"
    if (
        len(data) >= 16
        and data[:4] == b"RIFF"
        and data[8:12] == b"WEBP"
        and int.from_bytes(data[4:8], "little") == len(data) - 8
    ):
        return "image/webp"
    if len(data) >= 16 and data[4:8] == b"ftyp":
        box_size = int.from_bytes(data[:4], "big")
        brand = data[8:12]
        if box_size < 16 or box_size > len(data):
            return None
        if brand in {b"avif", b"avis"}:
            return "image/avif"
        if brand in {b"isom", b"iso2", b"avc1", b"mp41", b"mp42", b"M4V ", b"qt  "}:
            return "video/mp4"
    if len(data) >= 8 and data.startswith(b"\x1aE\xdf\xa3"):
        return "video/webm"
    return None


def _content_type(data: bytes, name: str, declared: str | None) -> str:
    sniffed = _detect_content_type(data)
    normalized = declared.split(";", 1)[0].strip().lower() if declared else None
    if sniffed is None:
        raise MediaSourceError("media source is not a structurally recognized format")
    if normalized and normalized != sniffed:
        raise MediaSourceError(f"declared content type {normalized} does not match {sniffed}")
    if normalized:
        return normalized
    return sniffed


def load_local_media(
    source: MediaSource,
    *,
    max_bytes: int,
    filename: str | None,
    content_type: str | None,
) -> LocalMedia:
    source_name: str | None = None
    try:
        if isinstance(source, (bytes, bytearray, memoryview)):
            data = bytes(source)
        elif isinstance(source, Path):
            source_name = source.name
            with source.expanduser().open("rb") as stream:
                data = _read_bounded(stream, max_bytes=max_bytes)
        elif isinstance(source, str):
            if is_remote_url(source) or source.startswith("data:"):
                raise MediaSourceError("URL sources must be routed before local loading")
            path = Path(source).expanduser()
            source_name = path.name
            with path.open("rb") as stream:
                data = _read_bounded(stream, max_bytes=max_bytes)
        elif isinstance(source, FieldFileLike):
            if not source.name:
                raise MediaSourceError("FieldFile-like source has an empty name")
            source_name = Path(source.name).name
            with source.open("rb") as stream:
                data = _read_bounded(stream, max_bytes=max_bytes)
        else:
            raise MediaSourceError(f"unsupported media source type: {type(source).__name__}")
    except OSError as exc:
        raise MediaSourceError("cannot read media source") from exc
    _validate_size(data, max_bytes=max_bytes)
    resolved_name = filename or source_name
    resolved_type = _content_type(data, resolved_name or "", content_type)
    if resolved_name is None:
        resolved_name = f"upload{_MIME_EXTENSIONS.get(resolved_type, '.bin')}"
    resolved_name = Path(resolved_name).name
    if not resolved_name or resolved_name in {".", ".."}:
        raise MediaSourceError("media filename is invalid")
    return LocalMedia(
        data=data,
        filename=resolved_name,
        content_type=resolved_type,
        sha256=hashlib.sha256(data).hexdigest(),
    )
