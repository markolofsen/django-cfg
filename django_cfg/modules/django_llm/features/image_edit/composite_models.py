"""Typed contracts for multi-reference image composition."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .models import (
    AspectRatio,
    ImageEditResponse,
    ImageEditTransportMode,
    ImageResolution,
    OutputQuality,
)
from .presets import ModelQuality, resolve_model


ImageEditReferenceRole = Literal[
    "character",
    "background",
    "object",
    "style",
    "composition",
    "mask",
    "other",
]


class ImageEditReference(BaseModel):
    """One ordered visual reference and its semantic purpose.

    The list position is the provider-visible identity (``Image 1``,
    ``Image 2``, ...). ``role`` and ``label`` make that position meaningful
    to prompt builders and downstream receipts without mutating the image.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    source_image: bytes | bytearray | memoryview | str | Path = Field(repr=False)
    role: ImageEditReferenceRole
    label: str | None = Field(default=None, min_length=1, max_length=120)
    source_image_mime: str | None = None


class CompositeImageEditRequest(BaseModel):
    """One image-edit call with 1..14 ordered visual references.

    No retry or fallback policy belongs to this value object. One request maps
    to one provider call so callers can account for every paid attempt.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    references: list[ImageEditReference] = Field(min_length=1, max_length=14)
    prompt: str = Field(min_length=1)
    model_quality: ModelQuality | None = None
    model: str | None = None
    output_quality: OutputQuality = "hd"
    aspect_ratio: AspectRatio = "auto"
    resolution: ImageResolution = "2K"
    transport_mode: ImageEditTransportMode | None = None
    extra: dict[str, Any] | None = None

    def resolved_model(self) -> str:
        """The OpenRouter id the client will actually call."""
        return resolve_model(model=self.model, quality=self.model_quality)


__all__ = [
    "CompositeImageEditRequest",
    "ImageEditReference",
    "ImageEditReferenceRole",
    "ImageEditResponse",
]
