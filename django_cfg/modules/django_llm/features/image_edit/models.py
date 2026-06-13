"""Data models for image-edit requests + responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from .presets import DEFAULT_MODEL_QUALITY, ModelQuality, resolve_model


# Default OpenRouter model — derived from the quality preset so when
# Google ships a new SKU, only ``presets.IMAGE_EDIT_MODELS`` changes.
DEFAULT_EDIT_MODEL = resolve_model(quality=DEFAULT_MODEL_QUALITY)


# OUTPUT resolution preset (≠ model quality):
#   "auto" → no override; provider default (≈1024px on Flash)
#   "hd"   → request HD output (~2048px on Nano Banana Pro; on the
#            Flash SKUs the model is hinted via the prompt header)
OutputQuality = Literal["auto", "hd"]


# Output aspect-ratio hint. ``auto`` preserves the source image's
# aspect ratio (Nano Banana family respects this when ``image_config``
# is omitted). Explicit values are honoured by Nano Banana Pro.
AspectRatio = Literal["auto", "1:1", "16:9", "9:16", "4:3", "3:4"]


class ImageEditRequest(BaseModel):
    """One image-edit call.

    Pick the model EITHER by ``model_quality`` preset (``fast`` /
    ``balanced`` / ``premium``) OR by explicit ``model`` id. Explicit
    id wins when both are set. Default = the preset's PREMIUM
    (Nano Banana Pro).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_image_bytes: bytes
    source_image_mime: str = "image/jpeg"
    prompt: str

    # Preset-based selection (recommended).
    model_quality: Optional[ModelQuality] = None

    # Explicit OpenRouter id override — set this when you need a
    # specific SKU. Wins over ``model_quality``.
    model: Optional[str] = None

    # OUTPUT resolution preset, not the model selector (see
    # OutputQuality alias).
    output_quality: OutputQuality = "hd"
    aspect_ratio: AspectRatio = "auto"

    # Pass-through knobs (e.g. ``seed`` for repro) merged into payload root.
    extra: Optional[Dict[str, Any]] = None

    def resolved_model(self) -> str:
        """The OpenRouter id the client will actually call."""
        return resolve_model(model=self.model, quality=self.model_quality)


class ImageEditResponse(BaseModel):
    """Result of one edit call."""

    image_bytes: Optional[bytes] = None
    image_mime: str = "image/png"

    text: str = ""
    model: str = ""
    cost_usd: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    image_tokens: int = 0
    elapsed_ms: float = 0.0

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    raw_response: Optional[Dict[str, Any]] = None

    @property
    def has_image(self) -> bool:
        return bool(self.image_bytes)
