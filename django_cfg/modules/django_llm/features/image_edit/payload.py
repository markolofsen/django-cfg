"""OpenRouter ``/chat/completions`` payload construction for image-edit.

Turns an :class:`ImageEditRequest` into the dict the OpenRouter API
expects. Auto-compresses the source bytes at the transport boundary —
so a caller can hand off a 4K JPEG and we don't quietly burn input
tokens shipping it to Nano Banana, which can't use detail above
~1536px anyway.
"""

from __future__ import annotations

from typing import Any

from ...core.image_io import EDIT_MAX_SIDE, EDIT_MAX_SIDE_BY_QUALITY
from ..image_input import normalize_image_input
from .models import ImageEditRequest

def build_payload(
    request: ImageEditRequest,
    model: str,
    *,
    auto_compress: bool = True,
    max_side: int | None = None,
    compress_quality: int = 85,
) -> dict[str, Any]:
    """Build the OpenRouter chat-completion payload for an edit call.

    ``auto_compress=True`` (the default) caps the source image and
    re-encodes as JPEG at ``compress_quality``. Already-small JPEGs
    pass through unchanged (see ``compress_image`` for the fast-path
    conditions). Disable when the caller has prepared bytes
    precisely — lossless masks, alpha channels.

    ``max_side=None`` (default) picks the cap from
    ``EDIT_MAX_SIDE_BY_QUALITY[request.model_quality]`` — Fast gets
    1024 (matches Banana 1 output), Balanced 1536, Premium 2048
    (matches Pro's 2K-4K ceiling). Pass an explicit integer to
    override per call. See `@docs/insights/image-edit/input-
    resolution.md` for the rationale.
    """
    effective_max_side = None
    if auto_compress:
        effective_max_side = (
            max_side
            if max_side is not None
            else EDIT_MAX_SIDE_BY_QUALITY.get(request.model_quality, EDIT_MAX_SIDE)
        )
    normalized = normalize_image_input(
        request.resolved_source(),
        declared_mime=request.source_image_mime,
        resize_max_side=effective_max_side,
        compress_quality=compress_quality,
    )

    prompt = request.prompt
    if request.output_quality == "hd":
        # Hint toward HD output. Nano Banana Pro respects this natively
        # (2K/4K). On Flash SKUs the prompt hint helps.
        prompt = (
            "Render the output at high definition (≥2048px on the "
            "longest side). "
        ) + prompt

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": normalized.value}},
                {"type": "text", "text": prompt},
            ],
        }],
        "modalities": ["image", "text"],
    }

    if request.aspect_ratio:
        # OpenRouter passes provider-specific knobs through. Nano Banana
        # respects aspect_ratio inside the request body.
        payload["aspect_ratio"] = request.aspect_ratio

    if request.extra:
        for k, v in request.extra.items():
            payload.setdefault(k, v)

    return payload
