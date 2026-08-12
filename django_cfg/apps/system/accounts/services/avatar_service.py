"""
Avatar image processing service.

Resizes uploaded avatars on the fly to a small square and re-encodes them to
WebP, so the original (potentially multi-megabyte) upload is **never** stored —
only the processed thumbnail lands in storage.

Business logic lives here (per the accounts services/ convention), not in the
view or serializer. The serializer calls :func:`process_avatar` from its
``validate_avatar`` hook so every path that saves an avatar (the upload
endpoint, admin, future callers) gets the same normalization for free.
"""

from __future__ import annotations

import io
import logging
from typing import Final

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

# Square target — avatars render as small round/rounded thumbnails everywhere,
# so anything larger than this is wasted bytes. Cropped to fill (center crop),
# not letterboxed, so the whole square is image.
AVATAR_SIZE: Final[int] = 400

# WebP quality: 82 is visually lossless for photographic avatars at this size
# while cutting file size ~3-5x vs JPEG/PNG. Method 6 = slowest/smallest encode
# (fine — we encode once per upload, not per request).
WEBP_QUALITY: Final[int] = 82
WEBP_METHOD: Final[int] = 6

# Content type / extension of the processed output.
OUTPUT_CONTENT_TYPE: Final[str] = "image/webp"
OUTPUT_EXT: Final[str] = ".webp"


def process_avatar(uploaded: UploadedFile) -> ContentFile:
    """
    Take a raw uploaded image and return a processed, square WebP file ready to
    assign to an ``ImageField``.

    - Corrects EXIF orientation (phone photos are often rotated in metadata).
    - Flattens transparency onto white (WebP keeps alpha, but a transparent
      avatar over a themed background looks broken — a solid matte is safer).
    - Center-crops to a square, then downscales to ``AVATAR_SIZE`` px.
    - Re-encodes to WebP. The original bytes are discarded.

    The returned :class:`~django.core.files.base.ContentFile` carries a
    ``.webp`` name derived from the upload, so ``upload_to`` produces a clean
    path regardless of the source format.

    Raises ``ValueError`` if the payload is not a decodable image (callers
    should surface this as a validation error).
    """
    # Pillow is a core dependency (django_ogimage), so import at module-call
    # time is fine; keep it local to avoid importing PIL on app load.
    from PIL import Image, ImageOps, UnidentifiedImageError

    # Read the whole upload into memory. Avatars are capped at a few MB upstream
    # (serializer size check), so this is bounded and cheap.
    raw = uploaded.read()
    try:
        uploaded.seek(0)
    except (AttributeError, ValueError):
        # Some file-likes are not seekable after read; not fatal — we already
        # have the bytes.
        pass

    try:
        with Image.open(io.BytesIO(raw)) as img:
            # Respect EXIF orientation before any geometry work.
            img = ImageOps.exif_transpose(img)

            # Normalize mode: flatten alpha/palette onto a white background so
            # the result is a clean RGB square.
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
                background = Image.new("RGBA", img.size, (255, 255, 255, 255))
                img = Image.alpha_composite(background, img).convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Center-crop to a square, then resize down to the target. ImageOps.fit
            # does both in one high-quality LANCZOS pass and never upscales past
            # the requested box (a tiny source just gets padded-to-fit dimensions,
            # which is acceptable for an avatar).
            img = ImageOps.fit(
                img,
                (AVATAR_SIZE, AVATAR_SIZE),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )

            buffer = io.BytesIO()
            img.save(
                buffer,
                format="WEBP",
                quality=WEBP_QUALITY,
                method=WEBP_METHOD,
            )
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        # OSError covers Pillow's "cannot identify"/truncated-image failures.
        logger.warning("Avatar processing failed: %s", exc)
        raise ValueError("Uploaded file is not a valid image.") from exc

    processed = ContentFile(buffer.getvalue(), name=_output_name(uploaded))
    logger.debug(
        "Avatar processed: %s bytes in -> %s bytes out (%dx%d webp)",
        len(raw),
        processed.size,
        AVATAR_SIZE,
        AVATAR_SIZE,
    )
    return processed


def _output_name(uploaded: UploadedFile) -> str:
    """Derive a ``.webp`` filename from the original upload name."""
    original = getattr(uploaded, "name", None) or "avatar"
    stem = original.rsplit("/", 1)[-1].rsplit(".", 1)[0].strip() or "avatar"
    return f"{stem}{OUTPUT_EXT}"
