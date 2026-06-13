"""django_llm — single LLM transport surface for any host Django app.

Every model call in the host project funnels through this package:
chat, structured extraction, vision, image generation, image edit,
embeddings, translation. Apps stay thin — they import an
``LLMClient`` / ``LLMRouter`` / ``ImageEditClient`` and let the
module own HTTP, auth, cost, retry, structured-output repair,
provider-policy adaptation, and registry math.

The host project re-exports everything below via a thin shim
(``modules/llm_router.py`` in the host's package). Apps then write::

    from modules.llm_router import LLMClient, sanitize_edit_prompt, ...

The shim only exists so a single env var (``DJANGO_LLM_SOURCE``)
switches between this sandbox copy and the published
``django_cfg.modules.django_llm`` copy. The public surface is
identical on both sides, so app code never knows which one is live.

# Adding a new public symbol

1. Implement it in the right submodule (``features/``, ``core/``, …).
2. Add it to the appropriate ``from .X import Y`` block below.
3. Add the name to ``__all__``.
4. Done — the host shim re-exports it automatically via ``__all__``.

See ``CLAUDE.md`` next to this file for the full contract.
"""

from typing import TYPE_CHECKING

# Host integration seam — provider keys, telegram alerter, the django
# config object. Exposed so callers that want to bypass the clients
# (rare) can still read API keys from the same place clients do.
from ._integration import BaseCfgModule, get_api_keys

# Core primitives — used directly by apps that prepare bytes / track
# lifecycles without going through a client.
from .core.errors import LLMTruncationError, LLMValidationError
from .core.image_io import (
    EDIT_MAX_SIDE,
    EDIT_MAX_SIDE_BY_QUALITY,
    VISION_MAX_SIDE,
    compress_image,
    load_image,
)
from .core.job_status import LLMJobStatus

# Catalog — model registry + role taxonomy.
from .catalog import ModelRole

# Storage — local L1 cache wrapper.
from .storage import LLMCache

# Provider abstraction.
from .providers import LLMProvider

# Routing — cascade engine + presets (sync + async twins + fan-out).
from .routing import (
    LLMRouter,
    LLMRouterError,
    aclassify,
    achat_with_tools,
    aescalate,
    aextract,
    aextract_chat,
    chat_with_tools,
    classify,
    classify_many,
    escalate,
    extract,
    extract_chat,
    extract_many,
)

# Client + features.
from .client import LLMClient
from .features.image_edit import (
    DEFAULT_EDIT_MODEL,
    DEFAULT_MODEL_QUALITY,
    IMAGE_EDIT_MODELS,
    AspectRatio,
    ImageEditClient,
    ImageEditError,
    ImageEditRequest,
    ImageEditResponse,
    ModelQuality,
    NoImageReturnedError,
    OutputQuality,
    build_payload,
    edit_many,
    extract_image_bytes,
    extract_text,
    resolve_model,
    sanitize_edit_prompt,
)
from .features.image_gen import ImageGenClient
from .features.translator import DjangoTranslator, TranslationError
from .features.vision import VisionClient

# Embeddings — the single embedding entry point for apps. Two ready
# methods (fast / quality), both 1536-dim, real OpenAI/OpenRouter path.
from .features.embeddings import (
    EMBEDDING_DIMENSIONS,
    FAST_MODEL as EMBEDDING_FAST_MODEL,
    QUALITY_MODEL as EMBEDDING_QUALITY_MODEL,
    embed_fast,
    embed_fast_many,
    embed_quality,
    embed_quality_many,
    embed_response,
    embed_text,
    embed_texts,
)
from .core.types import EmbeddingResponse
from .embeddings import OpenRouterEmbedder

# Structured-output repair — exposed for callers that drive their own
# ``chat_completion`` loop and want the same parse→repair→re-validate
# ladder ``LLMRouter.parse`` uses internally.
from .structured.repair import parse_into_schema

if TYPE_CHECKING:
    from .core.types import ChatCompletionResponse


# ── Convenience functions ────────────────────────────────────────────


def chat_completion(
    messages: list,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> "ChatCompletionResponse":
    """Send chat completion using LLMClient. Returns a
    ``ChatCompletionResponse`` (use ``.content`` / ``.tokens_used`` /
    ``.cost_usd``), not a dict."""
    return LLMClient().chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def translate_text(
    text: str,
    target_language: str = "en",
    source_language: str = "auto",
    fail_silently: bool = False,
) -> str:
    """Translate text using the auto-configured translator."""
    return DjangoTranslator().translate(
        text=text,
        target_language=target_language,
        source_language=source_language,
        fail_silently=fail_silently,
    )


def translate_json(
    data: dict,
    target_language: str = "en",
    source_language: str = "auto",
    fail_silently: bool = False,
) -> dict:
    """Translate JSON object using the auto-configured translator."""
    return DjangoTranslator().translate_json(
        data=data,
        target_language=target_language,
        source_language=source_language,
        fail_silently=fail_silently,
    )


def get_available_models() -> list:
    """Get available LLM models from the active provider."""
    return LLMClient().get_available_models()


# ── Public API ───────────────────────────────────────────────────────
# Host shim re-exports every name listed here. Add a new symbol → add
# a name here → it shows up at the host import boundary on next
# Python restart. Do not add private names.

__all__ = [
    # Host integration seam
    "BaseCfgModule",
    "get_api_keys",
    # Core
    "EDIT_MAX_SIDE",
    "EDIT_MAX_SIDE_BY_QUALITY",
    "LLMJobStatus",
    "LLMTruncationError",
    "LLMValidationError",
    "VISION_MAX_SIDE",
    "compress_image",
    "load_image",
    "parse_into_schema",
    # Catalog
    "ModelRole",
    # Storage
    "LLMCache",
    # Providers
    "LLMProvider",
    # Routing
    "LLMRouter",
    "LLMRouterError",
    "chat_with_tools",
    "classify",
    "classify_many",
    "escalate",
    "extract",
    "extract_chat",
    "extract_many",
    "aclassify",
    "achat_with_tools",
    "aescalate",
    "aextract",
    "aextract_chat",
    # Client
    "LLMClient",
    # Image-edit feature
    "AspectRatio",
    "DEFAULT_EDIT_MODEL",
    "DEFAULT_MODEL_QUALITY",
    "IMAGE_EDIT_MODELS",
    "ImageEditClient",
    "ImageEditError",
    "ImageEditRequest",
    "ImageEditResponse",
    "ModelQuality",
    "NoImageReturnedError",
    "OutputQuality",
    "build_payload",
    "edit_many",
    "extract_image_bytes",
    "extract_text",
    "resolve_model",
    "sanitize_edit_prompt",
    # Image-gen feature
    "ImageGenClient",
    # Vision feature
    "VisionClient",
    # Translator feature
    "DjangoTranslator",
    "TranslationError",
    # Embeddings — the single embedding entry point for apps
    "EMBEDDING_DIMENSIONS",
    "EMBEDDING_FAST_MODEL",
    "EMBEDDING_QUALITY_MODEL",
    "EmbeddingResponse",
    "OpenRouterEmbedder",
    "embed_fast",
    "embed_fast_many",
    "embed_quality",
    "embed_quality_many",
    "embed_response",
    "embed_text",
    "embed_texts",
    # Convenience functions
    "chat_completion",
    "translate_text",
    "translate_json",
    "get_available_models",
]
