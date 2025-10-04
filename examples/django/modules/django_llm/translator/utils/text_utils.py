"""
Text utility functions.

Utilities for text processing and validation.
"""

import re


class TextUtils:
    """Utilities for text processing."""

    def __init__(self):
        self.language_names = {
            "en": "English",
            "ru": "Russian",
            "ko": "Korean",
            "zh": "Chinese",
            "ja": "Japanese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ar": "Arabic",
            "hi": "Hindi",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "be": "Belarusian",
            "kk": "Kazakh"
        }

    def needs_translation(
        self,
        text: str,
        source_language: str,
        target_language: str,
        script_detector=None
    ) -> bool:
        """
        Determine if text needs translation.

        Args:
            text: Text to check
            source_language: Source language code
            target_language: Target language code
            script_detector: Optional ScriptDetector for CJK check

        Returns:
            True if translation is needed
        """
        if not text or not text.strip():
            return False

        # Skip URLs and technical content
        if self.is_technical_content(text):
            return False

        # If source and target are the same, no translation needed
        if source_language == target_language:
            return False

        # Force translation for CJK content
        if script_detector and script_detector.contains_cjk(text):
            return True

        # Auto-detect if source is 'auto'
        if source_language == 'auto':
            if script_detector:
                detected_lang = script_detector.detect_language(text)
                return detected_lang != target_language

        return True

    def is_technical_content(self, text: str) -> bool:
        """
        Check if text is technical content that shouldn't be translated.

        Args:
            text: Text to check

        Returns:
            True if text is technical content
        """
        # URLs
        if text.startswith(('http://', 'https://', '//', 'www.')):
            return True

        # File paths
        if '/' in text and ('.' in text or text.startswith('/')):
            return True

        # Numbers only
        if re.match(r'^\d+(\.\d+)?$', text.strip()):
            return True

        # Technical identifiers
        if re.match(r'^[A-Z_][A-Z0-9_]*$', text):
            return True

        return False

    def get_language_name(self, code: str) -> str:
        """
        Get full language name from code.

        Args:
            code: Language code

        Returns:
            Language name or code if not found
        """
        return self.language_names.get(code, code)
