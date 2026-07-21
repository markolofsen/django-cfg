"""Image generation through OpenRouter with real usage/cost evidence."""
from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Literal, Optional

import httpx
from openai import OpenAI

from ..._integration import BaseCfgModule, get_api_keys
from ...providers import PROVIDER_BASE_URLS
from ..image_edit.response_parser import extract_text
from .errors import ImageGenerationError, NoImageGeneratedError
from .models import (
    DEFAULT_IMAGE_GEN_MODEL,
    IMAGE_GEN_PRESETS,
    GeneratedImage,
    ImageGenResponse,
    ImageQuality,
    ImageSize,
    ImageStyle,
    ModelQuality,
    get_image_gen_price,
)
from .response_parser import (
    decode_inline_image,
    image_references,
    validate_https_reference,
    validate_raster,
)


ResponseFormat = Literal["url", "b64_json"]
logger = logging.getLogger(__name__)


class ImageGenClient(BaseCfgModule):
    """Provider-neutral text-to-image client.

    Gemini/Nano Banana models use OpenRouter's multimodal chat contract because
    image output lives in ``message.images`` and the OpenAI SDK strips it.
    Non-Gemini legacy image models retain the OpenAI-compatible images endpoint.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        *,
        base_url: str = PROVIDER_BASE_URLS["openrouter"],
        timeout: float = 300.0,
        app_title: str = "modules.django_llm-image_gen",
        app_url: str = "https://cmdop.com/",
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        super().__init__()
        if api_key is None:
            api_key = get_api_keys().get("openrouter") or ""
        if not api_key:
            raise RuntimeError("OpenRouter key missing — set OPENROUTER_API_KEY or CMDOP_LLM_KEYS__OPENROUTER")
        self.api_key = api_key
        self._default_model = default_model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.app_title = app_title
        self.app_url = app_url
        self.transport = transport

    @property
    def default_model(self) -> str:
        return self._default_model or DEFAULT_IMAGE_GEN_MODEL

    def _select_model(
        self, model: Optional[str] = None, model_quality: Optional[ModelQuality] = None,
    ) -> str:
        if model:
            return model
        return IMAGE_GEN_PRESETS.get(model_quality) or self.default_model

    @staticmethod
    def _uses_chat_multimodal(model: str) -> bool:
        return model.startswith("google/gemini-") and "image" in model

    def _chat_once(
        self, prompt: str, *, model: str, size: ImageSize, quality: ImageQuality,
    ) -> tuple[GeneratedImage, dict, str]:
        started = time.time()
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
        }
        if size != "auto":
            body["image_config"] = {"size": size, "quality": quality}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_title,
        }
        with httpx.Client(
            timeout=self.timeout, transport=self.transport, follow_redirects=True,
        ) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=body)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ImageGenerationError(
                    f"OpenRouter {response.status_code}: {(response.text or '')[:500]}"
                ) from exc
            payload = response.json()
            references = image_references(payload)
            image_bytes: bytes | None = None
            mime: str | None = None
            for reference in references:
                if reference.startswith("data:"):
                    image_bytes, mime = decode_inline_image(reference)
                    break
                url = validate_https_reference(reference)
                fetched = client.get(url, headers={"Accept": "image/png,image/jpeg,image/webp"})
                fetched.raise_for_status()
                if len(fetched.content) > 32 * 1024 * 1024:
                    raise ImageGenerationError("provider image exceeds 32 MiB safety limit")
                validate_raster(fetched.content)
                header_mime = fetched.headers.get("content-type", "").split(";", 1)[0]
                if header_mime not in {"image/png", "image/jpeg", "image/webp"}:
                    raise ImageGenerationError(f"provider URL returned unsupported MIME {header_mime!r}")
                image_bytes, mime = fetched.content, header_mime
                break
        text = extract_text(payload)
        if image_bytes is None:
            raise NoImageGeneratedError("Model returned no image bytes", model_text=text)
        usage = payload.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        image = GeneratedImage(
            b64_json=base64.b64encode(image_bytes).decode("ascii"),
            revised_prompt=text or None,
            content_type=mime or "image/png",
        )
        evidence = {
            "cost": float(usage.get("cost") or 0.0),
            "prompt_tokens": int(usage.get("prompt_tokens") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or 0),
            "image_tokens": int(details.get("image_tokens") or 0),
            "elapsed_ms": (time.time() - started) * 1000.0,
        }
        return image, evidence, text

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        n: int = 1,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        style: ImageStyle = "vivid",
        response_format: ResponseFormat = "b64_json",
    ) -> ImageGenResponse:
        selected_model = self._select_model(model, model_quality)
        if n < 1 or n > 10:
            raise ValueError("n must be between 1 and 10")
        if self._uses_chat_multimodal(selected_model):
            images: list[GeneratedImage] = []
            total = {"cost": 0.0, "prompt_tokens": 0, "completion_tokens": 0, "image_tokens": 0}
            texts: list[str] = []
            for _ in range(n):
                image, evidence, text = self._chat_once(
                    prompt, model=selected_model, size=size, quality=quality,
                )
                images.append(image)
                texts.append(text)
                for key in total:
                    total[key] += evidence[key]
            provider_cost = float(total["cost"])
            return ImageGenResponse(
                images=images, model=selected_model, prompt=prompt,
                cost_usd=provider_cost or get_image_gen_price(selected_model, size) * n,
                cost_source="provider-usage" if provider_cost else "registry-estimate",
                prompt_tokens=int(total["prompt_tokens"]),
                completion_tokens=int(total["completion_tokens"]),
                image_tokens=int(total["image_tokens"]),
                model_text="\n".join(value for value in texts if value),
            )

        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        response = client.images.generate(
            model=selected_model, prompt=prompt, n=n, size=size,
            quality=quality, style=style, response_format=response_format,
        )
        images = [
            GeneratedImage(
                url=getattr(item, "url", None), b64_json=getattr(item, "b64_json", None),
                revised_prompt=getattr(item, "revised_prompt", None),
            )
            for item in response.data or []
        ]
        return ImageGenResponse(
            images=images, model=selected_model, prompt=prompt,
            cost_usd=get_image_gen_price(selected_model, size) * n,
            cost_source="registry-estimate",
        )

    async def agenerate(self, prompt: str, **kwargs) -> ImageGenResponse:
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def generate_quick(self, prompt: str, size: ImageSize = "1024x1024") -> Optional[str]:
        result = self.generate(prompt, model_quality="fast", size=size)
        return result.first_url or result.images[0].to_data_url(result.images[0].content_type)

    async def agenerate_quick(self, prompt: str, size: ImageSize = "1024x1024") -> Optional[str]:
        return await asyncio.to_thread(self.generate_quick, prompt, size)
