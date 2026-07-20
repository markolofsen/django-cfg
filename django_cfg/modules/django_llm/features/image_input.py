"""Provider-neutral normalization of image inputs for multimodal requests."""

from __future__ import annotations

import base64
import binascii
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from ..core.image_io import (
    SUPPORTED_RASTER_MIMES,
    compress_image,
    load_image,
    validate_raster_image,
)
from ..media.transport import MediaTarget, MediaTransportRouter
from .vision.image_encoder import ImageEncoder


ImageInputSource: TypeAlias = bytes | bytearray | memoryview | str | Path
ALLOWED_IMAGE_MIMES = SUPPORTED_RASTER_MIMES


class ImageInputError(ValueError):
    """An image cannot be represented safely for a provider request."""


class NormalizedImageInput(BaseModel):
    """Validated provider input plus evidence useful to payload builders."""

    model_config = ConfigDict(frozen=True)

    value: str = Field(repr=False, exclude=True)
    kind: Literal["data-url", "remote-url"]
    mime_type: str | None = None
    byte_size: int | None = None


def _validate_raster(data: bytes, *, max_bytes: int) -> str:
    try:
        return validate_raster_image(
            data, max_bytes=max_bytes, allowed_mimes=ALLOWED_IMAGE_MIMES,
        )
    except ValueError as exc:
        raise ImageInputError(str(exc)) from exc


def _decode_data_url(value: str) -> bytes:
    header, separator, encoded = value.partition(",")
    if separator != "," or not header.endswith(";base64"):
        raise ImageInputError("image data URL must use base64 encoding")
    declared_mime = header[5:-7] if header.startswith("data:") else ""
    if declared_mime not in ALLOWED_IMAGE_MIMES:
        raise ImageInputError(f"unsupported image MIME {declared_mime!r}")
    try:
        return base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageInputError("image data URL contains invalid base64") from exc


def _remote_url(value: str, *, declared_mime: str | None) -> NormalizedImageInput:
    try:
        prepared = MediaTransportRouter().prepare_for(
            MediaTarget.OPENROUTER_IMAGE,
            value,
            content_type=declared_mime,
        ).prepared
    except ValueError as exc:
        raise ImageInputError(str(exc)) from exc
    return NormalizedImageInput(
        value=prepared.as_reference(),
        kind="remote-url",
        mime_type=prepared.content_type,
        byte_size=None,
    )


def normalize_image_input(
    source: ImageInputSource,
    *,
    declared_mime: str | None = None,
    max_bytes: int = ImageEncoder.MAX_IMAGE_SIZE,
    resize_max_side: int | None = None,
    compress_quality: int = 85,
) -> NormalizedImageInput:
    """Normalize a path, bytes, data URL, or HTTP(S) URL.

    Local inputs become validated data URLs. Remote URLs are validated and
    preserved; normalization deliberately performs no surprising network I/O.
    """
    if isinstance(source, str) and ImageEncoder.is_http_url(source):
        return _remote_url(source, declared_mime=declared_mime)

    if isinstance(source, str) and ImageEncoder.is_data_url(source):
        data = _decode_data_url(source)
        source_mime = _validate_raster(data, max_bytes=max_bytes)
    else:
        try:
            data, _detected_mime = load_image(source)
        except (OSError, ValueError) as exc:
            raise ImageInputError(f"cannot load image input: {exc}") from exc
        source_mime = _validate_raster(data, max_bytes=max_bytes)
        if declared_mime is not None and declared_mime not in ALLOWED_IMAGE_MIMES:
            raise ImageInputError(f"unsupported declared image MIME {declared_mime!r}")

    if resize_max_side is not None:
        if resize_max_side <= 0:
            raise ImageInputError("resize_max_side must be positive")
        data, _compressed_mime = compress_image(
            data, source_mime, max_side=resize_max_side, quality=compress_quality,
        )
        source_mime = _validate_raster(data, max_bytes=max_bytes)

    prepared = MediaTransportRouter().prepare_for(
        MediaTarget.OPENROUTER_IMAGE,
        data,
        content_type=source_mime,
    ).prepared
    return NormalizedImageInput(
        value=prepared.as_reference(),
        kind="data-url",
        mime_type=prepared.content_type,
        byte_size=prepared.byte_size,
    )


__all__ = [
    "ALLOWED_IMAGE_MIMES", "ImageInputError", "ImageInputSource",
    "NormalizedImageInput", "normalize_image_input",
]
