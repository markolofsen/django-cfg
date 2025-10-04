"""
Django LLM Service for django_cfg.

Auto-configuring LLM and translation service that integrates with DjangoConfig.
"""

# from .service import DjangoLLM, LLMError, LLMConfigError  # Removed - using LLMClient directly
from .translator import DjangoTranslator, TranslationError
from .llm import LLMClient, LLMCache

# Convenience functions
def chat_completion(
    messages: list,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = None,
    fail_silently: bool = False
) -> dict:
    """Send chat completion using LLMClient."""
    llm = LLMClient()
    return llm.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
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
    'TranslationError',
    'chat_completion',
    'translate_text',
    'translate_json',
    'get_available_models'
]
