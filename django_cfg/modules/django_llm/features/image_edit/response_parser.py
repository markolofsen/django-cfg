"""Response unpacking for OpenRouter image-edit calls.

OpenRouter wraps the model's image bytes inside the standard chat
completion ``choices[0].message.images[*].image_url.url`` slot as a
``data:image/...;base64,...`` URL. Tear that apart cleanly so the
client class stays free of plumbing.
"""

from __future__ import annotations

import base64
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
