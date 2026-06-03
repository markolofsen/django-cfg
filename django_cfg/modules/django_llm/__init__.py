"""
Django LLM Service for django_cfg.

Auto-configuring LLM and translation service that integrates with DjangoConfig.
"""

# from .service import DjangoLLM, LLMError, LLMConfigError  # Removed - using LLMClient directly
from typing import TYPE_CHECKING

from .client import LLMClient
from .storage import LLMCache
from .providers import LLMProvider

if TYPE_CHECKING:
    from .core.types import ChatCompletionResponse
from .features.translator import DjangoTranslator, TranslationError
from .catalog import ModelRole
from .routing import (
    LLMRouter,
    LLMRouterError,
    extract,
    extract_chat,
    classify,
    chat_with_tools,
    escalate,
    aextract,
    aextract_chat,
    aclassify,
    achat_with_tools,
    aescalate,
    extract_many,
    classify_many,
)


# Convenience functions
def chat_completion(
    messages: list,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> "ChatCompletionResponse":
    """Send chat completion using LLMClient.

    Returns a ``ChatCompletionResponse`` (use ``.content`` / ``.tokens_used`` /
    ``.cost_usd``), not a dict.
    """
    llm = LLMClient()
    return llm.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def translate_text(
    text: str,
    target_language: str = "en",
    source_language: str = "auto",
    fail_silently: bool = False
) -> str:
    """Translate text using auto-configured service."""
    translator = DjangoTranslator()
    return translator.translate(
        text=text,
        target_language=target_language,
        source_language=source_language,
        fail_silently=fail_silently
    )

def translate_json(
    data: dict,
    target_language: str = "en",
    source_language: str = "auto",
    fail_silently: bool = False
) -> dict:
    """Translate JSON object using auto-configured service."""
    translator = DjangoTranslator()
    return translator.translate_json(
        data=data,
        target_language=target_language,
        source_language=source_language,
        fail_silently=fail_silently
    )

def get_available_models() -> list:
    """Get available LLM models."""
    llm = LLMClient()
    return llm.get_available_models()

# Export public API
__all__ = [
    'DjangoTranslator',
    'LLMClient',
    'LLMCache',
    'LLMProvider',
    'LLMRouter',
    'LLMRouterError',
    'ModelRole',
    'TranslationError',
    'chat_completion',
    'translate_text',
    'translate_json',
    'get_available_models',
    # Task presets — call an LLM by job, not by model (see presets.py).
    'extract',
    'extract_chat',
    'classify',
    'chat_with_tools',
    'escalate',
    # Async twins + fan-out (asyncio.to_thread over the same sync logic).
    'aextract',
    'aextract_chat',
    'aclassify',
    'achat_with_tools',
    'aescalate',
    'extract_many',
    'classify_many',
]
