"""Image-edit client — multimodal in/out via OpenRouter.

Why this can't reuse the OpenAI SDK
-----------------------------------
The OpenAI SDK strips ``message.images`` — it's not in the OpenAI
``ChatCompletion`` schema. OpenRouter, for Gemini-family Nano Banana
models, puts the OUTPUT image bytes (as ``data:image/...;base64,``
strings) inside ``choices[0].message.images[*].image_url.url`` after
the request opts in via ``modalities=["image", "text"]``. So this
client talks to the REST endpoint with ``httpx`` directly.

Why this lives here (not in the host app)
-----------------------------------------
Every caller of an LLM in the project funnels through django_llm.
Putting the multimodal-edit transport inside django_llm means apps
(real-estate AIPhoto today, vehicle ai_photo, others later) don't
reimplement HTTP, auth, cost, or pricing — they pass an
``ImageEditRequest`` and get an ``ImageEditResponse`` back.

Decomposition
-------------
This file holds the public class + the HTTP transport. Single-purpose
neighbours:

* :mod:`.errors` — ``ImageEditError`` / ``NoImageReturnedError``.
* :mod:`.payload` — request → OpenRouter payload (with auto-compress).
* :mod:`.response_parser` — body → ``(image_bytes, mime, text)``.
* :mod:`.prompt_safety` — provider-policy phrase rewrites.
* :mod:`.models` / :mod:`.presets` — typed request/response shapes.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from ..._integration import BaseCfgModule, get_api_keys
from .errors import ImageEditError, NoImageReturnedError
from .models import (
    DEFAULT_EDIT_MODEL,
    ImageEditRequest,
    ImageEditResponse,
)
from .payload import build_payload
from .response_parser import extract_image_bytes, extract_text

logger = logging.getLogger(__name__)


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class ImageEditClient(BaseCfgModule):
    """Sync image-edit client over OpenRouter.

    Auto-detects the OpenRouter key from the django_llm integration
    seam (``get_api_keys()["openrouter"]``); the host doesn't pass
    keys around.
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str | None = None,
        base_url: str = OPENROUTER_BASE_URL,
        timeout: float = 120.0,
        app_title: str = "django_llm-image_edit",
        app_url: str = "https://djangocfg.com/",
        transport: httpx.BaseTransport | None = None,
    ):
        super().__init__()
        if api_key is None:
            api_key = get_api_keys().get("openrouter") or ""
        if not api_key:
            raise RuntimeError(
                "OpenRouter key missing — set API_KEYS__OPENROUTER in env."
            )
        self.api_key = api_key
        self.default_model = default_model or DEFAULT_EDIT_MODEL
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.app_title = app_title
        self.app_url = app_url
        # Test seam: pass an httpx.MockTransport from a test to intercept
        # the OpenRouter call without hitting the network. Production
        # callers leave this None and httpx uses its default transport.
        self.transport = transport

    # ── public ─────────────────────────────────────────────────────

    def edit(
        self,
        request: ImageEditRequest,
        *,
        auto_compress: bool = True,
    ) -> ImageEditResponse:
        """Issue one edit call. Sync.

        Model selection: ``request.model_quality`` preset (fast /
        balanced / premium) resolved via ``presets.IMAGE_EDIT_MODELS``
        unless ``request.model`` is set explicitly.

        ``auto_compress=True`` (default) caps the input image at
        ~1536px on the longest side and re-encodes as JPEG. Disable
        when the caller has prepared bytes precisely (lossless masks,
        alpha channel) and doesn't want them touched.

        Raises :class:`NoImageReturnedError` when the model answered
        but emitted no image — caller persists ``model_text`` as
        the refusal reason without retrying.
        """
        started = time.time()
        resolved_model = request.resolved_model()
        payload = build_payload(
            request, resolved_model, auto_compress=auto_compress,
        )
        body = self._post(payload)

        image_bytes, image_mime = extract_image_bytes(body)
        text = extract_text(body)

        if image_bytes is None:
            raise NoImageReturnedError(
                "Model returned no image bytes",
                model_text=text,
            )

        usage = body.get("usage") or {}
        cost = float(usage.get("cost") or 0.0)

        return ImageEditResponse(
            image_bytes=image_bytes,
            image_mime=image_mime or "image/png",
            text=text,
            model=resolved_model,
            cost_usd=cost,
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            image_tokens=int(
                (usage.get("completion_tokens_details") or {}).get(
                    "image_tokens", 0,
                ) or 0,
            ),
            elapsed_ms=(time.time() - started) * 1000.0,
            raw_response=body,
        )

    # ── async twin ────────────────────────────────────────────────
    #
    # Mirrors the chat-side `aextract` / `aparse` pattern: await the
    # sync `edit` on a worker thread. The HTTP call releases the GIL
    # during network wait, so this is real concurrency with ZERO
    # duplicated transport logic — `edit` stays the single source of
    # truth for payload building, response parsing, cost extraction
    # and error classification.
    #
    # The unit of work for the `edit_many` fan-out helper.

    async def aedit(
        self,
        request: ImageEditRequest,
        *,
        auto_compress: bool = True,
    ) -> ImageEditResponse:
        """Async ``edit`` — awaits the sync call on a worker thread."""
        return await asyncio.to_thread(
            self.edit, request, auto_compress=auto_compress,
        )

    # ── convenience shortcuts (parity with image_gen) ──────────────

    def edit_fast(
        self,
        source_image_bytes: bytes,
        prompt: str,
        *,
        source_image_mime: str = "image/jpeg",
        **kwargs: Any,
    ) -> ImageEditResponse:
        """Shortcut for Nano Banana GA (cheapest, stable). ~$0.07/edit."""
        return self.edit(ImageEditRequest(
            source_image_bytes=source_image_bytes,
            source_image_mime=source_image_mime,
            prompt=prompt,
            model_quality="fast",
            **kwargs,
        ))

    def edit_premium(
        self,
        source_image_bytes: bytes,
        prompt: str,
        *,
        source_image_mime: str = "image/jpeg",
        **kwargs: Any,
    ) -> ImageEditResponse:
        """Shortcut for Nano Banana Pro (highest quality)."""
        return self.edit(ImageEditRequest(
            source_image_bytes=source_image_bytes,
            source_image_mime=source_image_mime,
            prompt=prompt,
            model_quality="premium",
            **kwargs,
        ))

    # ── internals ──────────────────────────────────────────────────

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_title,
        }
        with httpx.Client(
            timeout=self.timeout, transport=self.transport,
        ) as client:
            r = client.post(url, headers=headers, json=payload)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = (r.text or "")[:500]
                raise ImageEditError(
                    f"OpenRouter {r.status_code}: {detail}"
                ) from exc
            return r.json()
