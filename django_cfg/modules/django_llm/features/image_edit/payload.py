"""OpenRouter image-edit payload construction.

Builds both the dedicated ``/images`` and compatibility
``/chat/completions`` wire contracts. Both normalize source media at the same
transport boundary and preserve composite reference order exactly.
"""

from __future__ import annotations

from typing import Any

from ...core.image_io import EDIT_MAX_SIDE, EDIT_MAX_SIDE_BY_QUALITY
from ..image_input import ImageInputSource, normalize_image_input
from .composite_models import CompositeImageEditRequest, ImageEditReference
from .models import ImageEditRequest, OutputQuality


def _effective_max_side(
    *,
    auto_compress: bool,
    max_side: int | None,
    model_quality: str | None,
) -> int | None:
    if not auto_compress:
        return None
    if max_side is not None:
        return max_side
    return EDIT_MAX_SIDE_BY_QUALITY.get(model_quality, EDIT_MAX_SIDE)


def _normalized_url(
    source: ImageInputSource,
    *,
    declared_mime: str | None,
    effective_max_side: int | None,
    compress_quality: int,
) -> str:
    return normalize_image_input(
        source,
        declared_mime=declared_mime,
        resize_max_side=effective_max_side,
        compress_quality=compress_quality,
    ).value


def _quality_prompt(prompt: str, output_quality: OutputQuality) -> str:
    if output_quality != "hd":
        return prompt
    return (
        "Render the output at high definition (≥2048px on the "
        "longest side). "
    ) + prompt


def _payload(
    *,
    model: str,
    image_urls: list[str],
    prompt: str,
    aspect_ratio: str,
    extra: dict[str, Any] | None,
) -> dict[str, Any]:
    content = [
        {"type": "image_url", "image_url": {"url": image_url}}
        for image_url in image_urls
    ]
    content.append({"type": "text", "text": prompt})
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if extra:
        for key, value in extra.items():
            payload.setdefault(key, value)
    return payload


def _image_api_payload(
    *,
    model: str,
    image_urls: list[str],
    prompt: str,
    aspect_ratio: str,
    resolution: str,
    extra: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build the dedicated OpenRouter Image API wire shape.

    ``input_references`` is assembled directly from ``image_urls`` so Python's
    list order is the caller's declared reference order. Core fields cannot be
    replaced through ``extra``.
    """
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "input_references": [
            {"type": "image_url", "image_url": {"url": image_url}}
            for image_url in image_urls
        ],
    }
    # "auto" is a cmdop convenience value, not an Image API enum. Omitting it
    # asks the selected endpoint to infer/default the output ratio.
    if aspect_ratio != "auto":
        payload["aspect_ratio"] = aspect_ratio
    payload["resolution"] = resolution
    if extra:
        for key, value in extra.items():
            payload.setdefault(key, value)
    return payload


def _reference_map(references: list[ImageEditReference]) -> str:
    lines = ["Reference image map (use the declared roles exactly):"]
    for index, reference in enumerate(references, start=1):
        label = f" — {reference.label}" if reference.label else ""
        lines.append(f"- Image {index}: {reference.role}{label}")
    return "\n".join(lines)


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
    effective_max_side = _effective_max_side(
        auto_compress=auto_compress,
        max_side=max_side,
        model_quality=request.model_quality,
    )
    image_url = _normalized_url(
        request.resolved_source(),
        declared_mime=request.source_image_mime,
        effective_max_side=effective_max_side,
        compress_quality=compress_quality,
    )
    return _payload(
        model=model,
        image_urls=[image_url],
        prompt=_quality_prompt(request.prompt, request.output_quality),
        aspect_ratio=request.aspect_ratio,
        extra=request.extra,
    )


def build_image_api_payload(
    request: ImageEditRequest,
    model: str,
    *,
    auto_compress: bool = True,
    max_side: int | None = None,
    compress_quality: int = 85,
) -> dict[str, Any]:
    """Build a single-reference ``POST /api/v1/images`` payload."""
    effective_max_side = _effective_max_side(
        auto_compress=auto_compress,
        max_side=max_side,
        model_quality=request.model_quality,
    )
    image_url = _normalized_url(
        request.resolved_source(),
        declared_mime=request.source_image_mime,
        effective_max_side=effective_max_side,
        compress_quality=compress_quality,
    )
    return _image_api_payload(
        model=model,
        image_urls=[image_url],
        prompt=request.prompt,
        aspect_ratio=request.aspect_ratio,
        resolution=request.resolution,
        extra=request.extra,
    )


def build_composite_payload(
    request: CompositeImageEditRequest,
    model: str,
    *,
    auto_compress: bool = True,
    max_side: int | None = None,
    compress_quality: int = 85,
) -> dict[str, Any]:
    """Build one OpenRouter payload from ordered typed references.

    All image blocks are emitted in declared order and the sole text block is
    emitted last. The text begins with a stable position-to-role map so the
    provider can distinguish character, background and style references.
    """
    effective_max_side = _effective_max_side(
        auto_compress=auto_compress,
        max_side=max_side,
        model_quality=request.model_quality,
    )
    image_urls = [
        _normalized_url(
            reference.source_image,
            declared_mime=reference.source_image_mime,
            effective_max_side=effective_max_side,
            compress_quality=compress_quality,
        )
        for reference in request.references
    ]
    prompt = f"{_reference_map(request.references)}\n\n{request.prompt}"
    return _payload(
        model=model,
        image_urls=image_urls,
        prompt=_quality_prompt(prompt, request.output_quality),
        aspect_ratio=request.aspect_ratio,
        extra=request.extra,
    )


def build_composite_image_api_payload(
    request: CompositeImageEditRequest,
    model: str,
    *,
    auto_compress: bool = True,
    max_side: int | None = None,
    compress_quality: int = 85,
) -> dict[str, Any]:
    """Build an ordered multi-reference ``POST /api/v1/images`` payload."""
    effective_max_side = _effective_max_side(
        auto_compress=auto_compress,
        max_side=max_side,
        model_quality=request.model_quality,
    )
    image_urls = [
        _normalized_url(
            reference.source_image,
            declared_mime=reference.source_image_mime,
            effective_max_side=effective_max_side,
            compress_quality=compress_quality,
        )
        for reference in request.references
    ]
    prompt = f"{_reference_map(request.references)}\n\n{request.prompt}"
    return _image_api_payload(
        model=model,
        image_urls=image_urls,
        prompt=prompt,
        aspect_ratio=request.aspect_ratio,
        resolution=request.resolution,
        extra=request.extra,
    )


__all__ = [
    "build_composite_image_api_payload",
    "build_composite_payload",
    "build_image_api_payload",
    "build_payload",
]
