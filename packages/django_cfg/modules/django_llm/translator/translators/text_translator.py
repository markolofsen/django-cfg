"""
Single text translation.

Handles translation of single text strings with caching.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Base exception for translation-related errors."""
    pass


class LanguageDetectionError(TranslationError):
    """Raised when language detection fails."""
    pass


class TextTranslator:
    """Translate single text strings."""

    def __init__(
        self,
        llm_client,
        translation_cache,
        stats_tracker,
        script_detector,
        text_utils,
        prompt_builder
    ):
        """
        Initialize text translator.

        Args:
            llm_client: LLM client for API calls
            translation_cache: Cache manager
            stats_tracker: Statistics tracker
            script_detector: Script detector for language detection
            text_utils: Text utilities
            prompt_builder: Prompt builder
        """
        self.client = llm_client
        self.cache = translation_cache
        self.stats = stats_tracker
        self.script_detector = script_detector
        self.text_utils = text_utils
        self.prompt_builder = prompt_builder

    def translate(
        self,
        text: str,
        target_language: str = "en",
        source_language: str = "auto",
        fail_silently: bool = False,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Translate single text.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code ('auto' for detection)
            fail_silently: Don't raise exceptions on failure
            model: Optional model override
            temperature: Optional temperature override

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails and fail_silently is False
        """
        try:
            # Auto-detect source language if needed
            if source_language == 'auto':
                source_language = self.script_detector.detect_language(text)
                if source_language == 'unknown':
                    logger.warning(f"Could not detect language for: {text[:50]}...")
                    if not fail_silently:
                        raise LanguageDetectionError("Could not detect source language")
                    return text

            # Check if translation is needed
            if not self.text_utils.needs_translation(
                text, source_language, target_language, self.script_detector
            ):
                return text

            # Check translation cache
            cached_translation = self.cache.get(text, source_language, target_language)
            if cached_translation:
                self.stats.record_cache_hit()
                return cached_translation

            self.stats.record_cache_miss()

            # Generate prompt
            prompt = self.prompt_builder.build_text_translation_prompt(
                text, source_language, target_language
            )

            # Use LLM client for translation
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature if temperature is not None else 0.1,
                max_tokens=1000
            )

            # Extract translation
            translated_text = response.get('content', '').strip()

            if not translated_text:
                if not fail_silently:
                    raise TranslationError("Empty translation response")
                return text

            # Cache the result
            self.cache.set(text, source_language, target_language, translated_text)

            # Update stats
            self.stats.record_translation(source_language, target_language, response)

            return translated_text

        except Exception as e:
            self.stats.record_failure()
            error_msg = f"Failed to translate text: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TranslationError(error_msg) from e
            return text
