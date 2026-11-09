"""Read the text of an image you already hold in memory: no URL, no file, no temporary upload.

    text = await aread_image_text(png_bytes, "image/png")                 # django_llm's own OCR model
    text = await aread_image_text(jpeg, "image/jpeg", mode="gundam")      # a more thorough prompt
    text = await aread_image_text(jpeg, "image/jpeg", query="Describe it.")  # your own question about the picture

The bytes travel inside the request as a base64 data URL, so a private picture never needs a public address. The model is the one
`select_ocr_model` picks (this package's `DEFAULT_OCR_MODEL`, or `model` / `model_quality` when given); cost and tokens go through
`VisionClient` like every other vision call.
"""

from __future__ import annotations

import base64
from typing import Optional

from .client import VisionClient
from .models import ModelQuality, OCRMode
from .presets import get_ocr_prompt, select_ocr_model


async def aread_image_text(
    data: bytes,
    mime: str,
    *,
    query: Optional[str] = None,
    mode: OCRMode = "base",
    model: Optional[str] = None,
    model_quality: Optional[ModelQuality] = None,
    max_tokens: Optional[int] = 1500,
    client: Optional[VisionClient] = None,
) -> str:
    """The text of the image (`mode` prompt), or the answer to `query`. Raises what `VisionClient` raises; the caller decides what a failure means."""
    if not data:
        raise ValueError("no image bytes")
    vision = client or VisionClient()
    chosen = select_ocr_model(model=model, model_quality=model_quality, models_registry=vision.models_registry)
    source = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
    response = await vision.aanalyze(image_source=source, query=query or get_ocr_prompt(mode), model=chosen, max_tokens=max_tokens)
    return (response.content or "").strip()


__all__ = ["aread_image_text"]
