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
from .presets import OCR_FALLBACKS, get_ocr_prompt, select_ocr_model


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
    # An explicit model is the caller's choice and fails loudly; the default one has fallbacks, because a catalogue changes under a library.
    ladder = (chosen,) if model else (chosen, *(m for m in OCR_FALLBACKS if m != chosen))
    failure: Exception | None = None
    for slug in ladder:
        try:
            response = await vision.aanalyze(image_source=source, query=query or get_ocr_prompt(mode), model=slug, max_tokens=max_tokens)
            return (response.content or "").strip()
        except Exception as exc:  # noqa: BLE001 - any failure of one model moves to the next vendor
            failure = exc
    assert failure is not None
    raise failure


__all__ = ["aread_image_text"]
