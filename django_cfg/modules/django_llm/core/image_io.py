"""Universal image loader — bytes-out from concrete source types.

Source taxonomy
---------------
``load_image`` accepts ONE OF (no model duck-typing, no
``getattr`` scans):

  * ``bytes`` / ``bytearray`` / ``memoryview`` — raw image bytes
  * ``str`` — URL (``http://`` / ``https://``) or filesystem path
  * ``Path`` — filesystem path
  * Django ``FieldFile`` — anything with ``.name`` AND ``.open()``;
    duck-typed only on those two attrs so we don't have to import
    Django at module load time

If a caller has a domain model (``catalog.Media``, etc.) with its
own conventions for "where the image lives", the caller pulls out
the right field and passes one of the four types above. The model
shape stays in the app where it's typed; this module stays
provider-agnostic.

MIME resolution
---------------
For every source we normalise to a recognised ``image/*`` MIME:
header (when fetching) → magic-byte sniff → extension lookup →
``image/jpeg`` fallback. The sniff layer matters because CDNs often
serve images as ``application/octet-stream``, which Gemini's
image-edit endpoint rejects even when the bytes ARE valid pixels.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol, Tuple, Union, runtime_checkable

import httpx

logger = logging.getLogger(__name__)


@runtime_checkable
class FieldFileLike(Protocol):
    """Minimal contract for Django's ``FieldFile`` / ``ImageFieldFile``.

    ``.name`` is the storage path; ``.open("rb")`` yields a file
    object readable into ``bytes``. We type against this Protocol so
    the helper works for *any* Django storage backend (local,
    S3-backed, etc.) without importing Django.
    """

    name: str

    def open(self, mode: str = "rb"): ...


ImageSource = Union[bytes, bytearray, memoryview, str, Path, FieldFileLike]


_MIME_BY_SUFFIX = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
}


# Magic-byte signatures — used when the Content-Type header is
# missing or generic.
_MAGIC_PREFIXES = [
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"BM", "image/bmp"),
]


def _is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def _guess_mime_from_suffix(name: str) -> str:
    return _MIME_BY_SUFFIX.get(Path(name).suffix.lower(), "image/jpeg")


def _sniff_mime_from_bytes(data: bytes) -> str | None:
    if not data:
        return None
    head = data[:16]
    for prefix, mime in _MAGIC_PREFIXES:
        if head.startswith(prefix):
            return mime
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    return None


def _normalize_mime(header_mime: str, data: bytes, hint_path: str) -> str:
    """Best MIME we can defend.

    Priority: header (if ``image/*``) → magic-byte sniff → extension
    lookup → ``image/jpeg``. We reject non-image header values
    explicitly because Gemini's image-edit endpoint refuses requests
    with ``application/octet-stream`` and similar even when the bytes
    are a valid JPEG.
    """
    if header_mime and header_mime.startswith("image/") and header_mime != "image/x-icon":
        return header_mime
    sniffed = _sniff_mime_from_bytes(data)
    if sniffed:
        return sniffed
    return _guess_mime_from_suffix(hint_path)


def _fetch_url(url: str, *, timeout: float) -> Tuple[bytes, str]:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        header_mime = r.headers.get("content-type", "").split(";")[0].strip()
        return r.content, _normalize_mime(header_mime, r.content, url)


def load_image(
    source: ImageSource,
    *,
    timeout: float = 30.0,
) -> Tuple[bytes, str]:
    """Return ``(image_bytes, mime_type)`` for a concrete source.

    Domain models (e.g. a ``Media`` row with ``.file`` and
    ``.original_url``) belong in the caller — pull out the field you
    want and pass it here. That keeps the model contract typed in
    the app while this module stays provider-agnostic.

    Raises ``ValueError`` on unrecognised source types and the usual
    httpx / OSError exceptions on transport failures.
    """
    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
        return data, _normalize_mime("", data, "")

    if isinstance(source, Path):
        data = source.read_bytes()
        return data, _normalize_mime("", data, str(source))

    if isinstance(source, str):
        if _is_url(source):
            return _fetch_url(source, timeout=timeout)
        data = Path(source).read_bytes()
        return data, _normalize_mime("", data, source)

    if isinstance(source, FieldFileLike):
        if not source.name:
            raise ValueError("FieldFile-like source has empty .name (not saved?)")
        with source.open("rb") as fh:
            data = fh.read()
        return data, _normalize_mime("", data, source.name)

    raise ValueError(
        f"load_image: unsupported source type {type(source).__name__}; "
        "expected bytes / str / Path / FieldFile-like"
    )


# Recommended caps per use case. Pinned to the provider's actual
# tokenisation math — not eyeballed.
#
# ── VISION_MAX_SIDE = 768 ─────────────────────────────────────────────
# Multimodal extraction / analyzer / OCR paths (anything where the
# model reads the photo and emits text or JSON).
#
# Gemini's image tokeniser tiles inputs into 768×768 chunks, each
# costing 258 tokens. An image ≤384px in both dimensions is a flat
# 258 tokens; above that it cuts into 768-tiles. So 768 on the long
# side is the provably optimal value — exactly one tile, 258 tokens
# — and going smaller does NOT save more. A 4K input cuts into ~25
# tiles ≈ 6450 tokens; downscaling to 768 buys a ~25× input-token cut
# with zero loss of subject-ID accuracy. Source:
# https://ai.google.dev/gemini-api/docs/tokens
#
# ── EDIT_MAX_SIDE_BY_QUALITY ──────────────────────────────────────────
# Image-edit (image-in, image-out) paths — Nano Banana family.
#
# Each Banana model has a different output ceiling. Sending input
# above that ceiling wastes tokens; sending input below it starves
# the model of detail for the edit decision. Match input to output:
#
#   * ``fast`` (Nano Banana 1, output 1024×1024)        → input 1024
#   * ``balanced`` (Nano Banana 2, output up to ~1792)  → input 1536
#   * ``premium`` (Nano Banana Pro, output 2K-4K)       → input 2048
#
# Premium intentionally sits below 4K — 2048 gives Pro 1:1 detail
# at its 2K mode and 2× headroom for 4K decisions, while still
# saving ~4× input tokens vs a raw 4K source. Going to 4K input
# adds cost without measurable edit-quality gain because Pro's
# preprocessing internally rescales anyway.
#
# ``EDIT_MAX_SIDE`` is the conservative default for callers that
# don't know the model quality yet (matches balanced).
#
# Sources:
#   https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-image
#   https://developers.googleblog.com/en/introducing-gemini-2-5-flash-image/
#
# Per-call override: ``compress_image(..., max_side=...)`` — every
# caller can deviate when a specific feature has a different sweet
# spot (a thumbnail sanity check at 256, an uncompressed diagnostic).
VISION_MAX_SIDE = 768
EDIT_MAX_SIDE_BY_QUALITY: dict[str, int] = {
    "fast": 1024,
    "balanced": 1536,
    "premium": 2048,
}
EDIT_MAX_SIDE = EDIT_MAX_SIDE_BY_QUALITY["balanced"]


def compress_image(
    data: bytes,
    mime: str = "image/jpeg",
    *,
    max_side: int = VISION_MAX_SIDE,
    quality: int = 80,
) -> Tuple[bytes, str]:
    """Re-encode bytes for transport — bounded long-side + JPEG quality.

    Idempotent on already-small images: if the source is already within
    ``max_side`` on its longest dimension AND under a sane byte budget,
    the original bytes are returned unchanged. Otherwise the image is
    downscaled (preserving aspect ratio) and re-encoded as JPEG.

    Use this AT THE TRANSPORT BOUNDARY — right before encoding to
    base64 / shipping to the provider — never on intermediate copies
    in the pipeline. The whole point is a single source-of-truth size
    cut so a caller can't accidentally ship a 4K JPEG to a vision model
    that only needs 768.

    Args:
        data: Raw image bytes (any format Pillow can decode — JPEG,
            PNG, WebP, AVIF, …).
        mime: Source MIME (informational; output is always JPEG).
        max_side: Cap on the longest side, in pixels. Aspect ratio
            preserved. See ``VISION_MAX_SIDE`` / ``EDIT_MAX_SIDE``.
        quality: JPEG quality (1-95). 70-85 is the perceptual sweet
            spot; below 60 introduces visible artifacts that confuse
            vision models.

    Returns:
        ``(compressed_bytes, "image/jpeg")``. MIME is always JPEG
        on the output because every provider accepts JPEG and the
        format choice is what gives us the predictable token cost.
    """
    # Lazy import — Pillow is a heavy dep; only pull it on the first
    # compress_image call so callers that never compress avoid the
    # cold-start cost.
    from io import BytesIO
    from PIL import Image, ImageOps

    if not data:
        return data, mime

    try:
        with Image.open(BytesIO(data)) as img:
            # Strip EXIF orientation BEFORE measuring — a 4000x3000
            # camera JPEG rotated by EXIF can mis-trigger the size
            # gate. ImageOps.exif_transpose bakes orientation into
            # pixel data so width/height read as the visible shape.
            img = ImageOps.exif_transpose(img)
            w, h = img.size
            longest = max(w, h)

            # Fast path: already small enough, and the source is a
            # JPEG-shaped MIME, and bytes are under 200 KB. No re-
            # encode — return as-is to avoid lossy re-compress on
            # already-lean input.
            if (
                longest <= max_side
                and mime.startswith("image/jpeg")
                and len(data) < 200_000
            ):
                return data, "image/jpeg"

            if longest > max_side:
                scale = max_side / longest
                new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
                img = img.resize(new_size, Image.LANCZOS)

            # JPEG can't carry alpha — flatten to white if needed.
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            out = BytesIO()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            return out.getvalue(), "image/jpeg"
    except Exception as exc:  # noqa: BLE001 — never throw at transport
        # Pillow can't decode (corrupt header, unsupported format) →
        # return the original. The provider's own validator decides
        # whether to accept; we shouldn't fail the whole call just
        # because we couldn't shrink it.
        logger.warning(
            "compress_image: cannot decode/resize input (mime=%s len=%d) — "
            "passing through original bytes: %s",
            mime, len(data), exc,
        )
        return data, mime
