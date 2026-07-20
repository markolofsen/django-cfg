"""Parse and validate OpenRouter multimodal image output references."""
from __future__ import annotations

import base64
import binascii
from typing import Any
from urllib.parse import urlparse

from ...core.image_io import validate_raster_image
from .errors import ImageGenerationError


def image_references(body: dict[str, Any]) -> list[str]:
    choices = body.get("choices") or []
    if not choices:
        return []
    message = choices[0].get("message") or {}
    result: list[str] = []
    for item in message.get("images") or []:
        value = (item.get("image_url") or {}).get("url")
        if isinstance(value, str):
            result.append(value)
    return result


def decode_inline_image(reference: str) -> tuple[bytes, str]:
    header, marker, encoded = reference.partition(",")
    if marker != "," or not header.startswith("data:image/") or not header.endswith(";base64"):
        raise ImageGenerationError("provider returned a malformed image data URL")
    mime = header[5:-7]
    if mime not in {"image/png", "image/jpeg", "image/webp"}:
        raise ImageGenerationError(f"provider returned unsupported image MIME {mime!r}")
    try:
        value = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageGenerationError("provider returned invalid base64 image bytes") from exc
    validate_raster(value)
    return value, mime


def validate_https_reference(reference: str) -> str:
    parsed = urlparse(reference)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ImageGenerationError("provider image reference must be inline data or HTTPS")
    return reference


def validate_raster(value: bytes) -> None:
    try:
        validate_raster_image(
            value,
            max_bytes=32 * 1024 * 1024,
            allowed_mimes={"image/png", "image/jpeg", "image/webp"},
        )
    except ValueError as exc:
        raise ImageGenerationError(f"invalid provider raster: {exc}") from exc
