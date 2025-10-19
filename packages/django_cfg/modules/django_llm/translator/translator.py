"""
Django Translator Service orchestrator for django_llm.

Auto-configuring translation service with language detection and JSON support.
"""

import logging
from typing import Any, Dict, Optional

from django_cfg.modules import BaseCfgModule

from ..llm.client import LLMClient
from .cache import TranslationCacheManager

# Import specialized components
from .detectors import LanguageDetector, ScriptDetector
from .stats import StatsTracker
from .translators import JsonTranslator, TextTranslator, TranslationError
from .utils import PromptBuilder, TextUtils

logger = logging.getLogger(__name__)


class DjangoTranslator(BaseCfgModule):
    """
    Translation service orchestrator for django_cfg.

    Coordinates translation using specialized components:
    - ScriptDetector: Script-based language detection
    - LanguageDetector: Dictionary-based language detection
    - TextTranslator: Single text translation
    - JsonTranslator: JSON object translation
    - StatsTracker: Usage statistics
    """

    def __init__(self, client=None):
        self._client = client
        self._is_configured = None

        # Initialize translation cache manager
        self.translation_cache = TranslationCacheManager()

        # Initialize components
        self.script_detector = ScriptDetector()
        self.language_detector = LanguageDetector()
        self.text_utils = TextUtils()
        self.prompt_builder = PromptBuilder()
        self.stats_tracker = StatsTracker()

        # Initialize translators (will be created when client is available)
        self._text_translator = None
        self._json_translator = None

    @property
    def config(self):
        """Get the DjangoConfig instance."""
        return self.get_config()

    @property
    def is_configured(self) -> bool:
        """Check if translation service is properly configured."""
        if self._is_configured is None:
            try:
                # If client was passed directly, we're configured
                if self._client is not None:
                    self._is_configured = True
                # Otherwise check LLM config
                elif hasattr(self.config, 'llm') and self.config.llm:
                    llm_config = self.config.llm
                    self._is_configured = (
                        hasattr(llm_config, 'api_key') and
                        llm_config.api_key and
                        len(llm_config.api_key.strip()) > 0
                    )
                else:
                    self._is_configured = False
            except Exception:
                self._is_configured = False

        return self._is_configured

    @property
    def client(self) -> LLMClient:
        """Get LLM client instance."""
        if self._client is None:
            raise ValueError("LLM client not configured. Pass client to constructor.")
        return self._client

    @property
    def text_translator(self) -> TextTranslator:
        """Get or create text translator instance."""
        if self._text_translator is None:
            self._text_translator = TextTranslator(
                self.client,
                self.translation_cache,
                self.stats_tracker,
                self.script_detector,
                self.text_utils,
                self.prompt_builder
            )
        return self._text_translator

    @property
    def json_translator(self) -> JsonTranslator:
        """Get or create JSON translator instance."""
        if self._json_translator is None:
            self._json_translator = JsonTranslator(
                self.client,
                self.translation_cache,
                self.language_detector,
                self.text_utils,
                self.prompt_builder
            )
        return self._json_translator

    def detect_language(self, text: str) -> str:
        """
        Detect language of text.

        Delegates to ScriptDetector.

        Args:
            text: Text to analyze

        Returns:
            Language code
        """
        return self.script_detector.detect_language(text)

    def needs_translation(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> bool:
        """
        Determine if text needs translation.

        Delegates to TextUtils.

        Args:
            text: Text to check
            source_language: Source language code
            target_language: Target language code

        Returns:
            True if translation is needed
        """
        return self.text_utils.needs_translation(
            text, source_language, target_language, self.script_detector
        )

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

        Delegates to TextTranslator.

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
            if not self.is_configured:
                error_msg = "Translation service is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TranslationError(error_msg)
                return text

            return self.text_translator.translate(
                text=text,
                target_language=target_language,
                source_language=source_language,
                fail_silently=fail_silently,
                model=model,
                temperature=temperature
            )

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            if not fail_silently:
                raise
            return text

    def translate_json(
        self,
        data: Dict[str, Any],
        target_language: str = "en",
        source_language: str = "auto",
        fail_silently: bool = False,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Translate JSON object.

        Delegates to JsonTranslator.

        Args:
            data: JSON object to translate
            target_language: Target language for translation
            source_language: Source language ('auto' for detection)
            fail_silently: Don't raise exceptions on failure
            model: Optional model override
            temperature: Optional temperature override

        Returns:
            Translated JSON object

        Raises:
            TranslationError: If translation fails and fail_silently is False
        """
        try:
            if not self.is_configured:
                error_msg = "Translation service is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise TranslationError(error_msg)
                return data

            return self.json_translator.translate_json(
                data=data,
                target_language=target_language,
                source_language=source_language,
                fail_silently=fail_silently,
                model=model,
                temperature=temperature
            )

        except Exception as e:
            logger.error(f"JSON translation failed: {e}")
            if not fail_silently:
                raise
            return data

    def get_stats(self) -> Dict[str, Any]:
        """
        Get translation statistics.

        Delegates to StatsTracker.

        Returns:
            Dictionary with statistics
        """
        return self.stats_tracker.get_stats()

    def clear_cache(self) -> bool:
        """
        Clear translation cache.

        Returns:
            True if successful
        """
        try:
            self.translation_cache.clear()
            if self._client:
                self.client.clear_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to clear translation cache: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get translation service configuration information.

        Returns:
            Configuration info dictionary
        """
        try:
            client_info = self.client.get_client_info() if self._client else {}

            return {
                "configured": self.is_configured,
                "provider": client_info.get("provider", "unknown"),
                "cache_size": len(self.translation_cache._cache) if hasattr(self.translation_cache, '_cache') else 0,
                "client_info": client_info,
                "supported_languages": list(self.text_utils.language_names.keys()),
            }
        except Exception as e:
            logger.error(f"Failed to get config info: {e}")
            return {
                "configured": False,
                "error": str(e)
            }

    @classmethod
    def send_translation_alert(
        cls,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send translation alert via configured notification services.

        Args:
            message: Alert message
            context: Optional context data
        """
        try:
            # Try to send via Telegram if available
            from django_cfg.modules.django_telegram import DjangoTelegram
            telegram = DjangoTelegram()

            text = f"🌐 <b>Translation Alert</b>\n\n{message}"
            if context:
                text += "\n\n<b>Context:</b>\n"
                for key, value in context.items():
                    text += f"• {key}: {value}\n"

            telegram.send_message(text, parse_mode="HTML", fail_silently=True)

        except Exception as e:
            logger.error(f"Failed to send translation alert: {e}")
