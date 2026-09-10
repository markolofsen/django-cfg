"""Response unpacking for OpenRouter image-edit transports.

The compatibility chat endpoint wraps bytes in a data URL under
``choices[0].message.images``. The dedicated Image API returns raw base64 under
``data[0].b64_json``. Keeping both parsers here makes endpoint selection in the
client explicit and prevents shape-probing fallback.
"""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Any

logger = logging.getLogger(__name__)


def extract_image_bytes(body: dict[str, Any]) -> tuple[bytes | None, str | None]:
    """Pull image bytes out of ``choices[0].message.images[*]``.

    Returns ``(None, None)`` when the model emitted no image — the
    caller should treat that as a soft refusal and raise
    :class:`NoImageReturnedError`.

    May be a single image (typical for Nano Banana edit) or several
    in theory; we take the first usable one. The MIME comes from the
    data URL header so a caller can store the right extension.
    """
    choices = body.get("choices") or []
    if not choices:
        return None, None
    msg = choices[0].get("message") or {}
    images = msg.get("images") or []
    for img in images:
        url = (img.get("image_url") or {}).get("url") or ""
        if not url.startswith("data:"):
            continue
        try:
            header, b64 = url.split(",", 1)
            mime = header.split(":", 1)[1].split(";")[0]
            return base64.b64decode(b64), mime
        except (ValueError, IndexError):
            continue
    return None, None


def extract_text(body: dict[str, Any]) -> str:
    """Pull the model's text answer out of the response.

    On a successful generation this is empty or a short caption. On
    a refusal it carries the model's own explanation (e.g. ``"I'm
    just a language model and can't help with that."``) and the
    caller persists it as the refusal reason.
    """
    choices = body.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            p.get("text", "") for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        ]
        return "\n".join(parts).strip()
    return ""


def extract_image_api_bytes(
    body: dict[str, Any],
) -> tuple[bytes | None, str | None]:
    """Pull the first dedicated Image API ``data[].b64_json`` result.

    OpenRouter omits ``media_type`` for normal raster PNG output. Invalid or
    absent base64 is treated as no image, allowing the client to raise its
    stable ``NoImageReturnedError`` contract rather than leaking decoder
    details.
    """
    data = body.get("data") or []
    if not isinstance(data, list) or not data:
        return None, None
    first = data[0]
    if not isinstance(first, dict):
        return None, None
    encoded = first.get("b64_json")
    if not isinstance(encoded, str) or not encoded:
        return None, None
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        return None, None
    media_type = first.get("media_type")
    if not isinstance(media_type, str) or not media_type:
        media_type = "image/png"
    return image_bytes, media_type
