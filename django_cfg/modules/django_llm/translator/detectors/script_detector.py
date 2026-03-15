"""
Script-based language detection.

Detects language based on character scripts (CJK, Cyrillic, etc.).
"""

import re


class ScriptDetector:
    """Detect language based on character scripts."""

    def __init__(self):
        # CJK character ranges for detection
        self.cjk_ranges = [
            (0x4E00, 0x9FFF),   # CJK Unified Ideographs
            (0x3400, 0x4DBF),   # CJK Extension A
            (0x20000, 0x2A6DF), # CJK Extension B
            (0x2A700, 0x2B73F), # CJK Extension C
            (0x2B740, 0x2B81F), # CJK Extension D
            (0x3040, 0x309F),   # Hiragana
            (0x30A0, 0x30FF),   # Katakana
            (0xAC00, 0xD7AF),   # Hangul Syllables
        ]

    def detect_language(self, text: str) -> str:
        """
        Detect language of text using character scripts.

        Args:
            text: Text to analyze

        Returns:
            Language code (ko, ja, zh, ru, or en)
        """
        if not text or not text.strip():
            return 'unknown'

        # Clean text for better detection
        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            return 'unknown'

        # Check for CJK characters
        if self.contains_cjk(text):
            # Simple CJK detection
            if self.contains_korean(text):
                return 'ko'
            elif self.contains_japanese(text):
                return 'ja'
            else:
                return 'zh'  # Default to Chinese for other CJK

        # Check for Cyrillic (Russian/Ukrainian/Belarusian)
        if self.contains_cyrillic(text):
            return 'ru'  # Default to Russian for Cyrillic

        # Default to English for Latin script
        return 'en'

    def contains_cjk(self, text: str) -> bool:
        """
        Check if text contains CJK characters.

        Args:
            text: Text to check

        Returns:
            True if text contains CJK characters
        """
        for char in text:
            char_code = ord(char)
            for start, end in self.cjk_ranges:
                if start <= char_code <= end:
                    return True
        return False

    def contains_korean(self, text: str) -> bool:
        """
        Check if text contains Korean characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Hangul syllables
        """
        for char in text:
            char_code = ord(char)
            if 0xAC00 <= char_code <= 0xD7AF:  # Hangul Syllables
                return True
        return False

    def contains_japanese(self, text: str) -> bool:
        """
        Check if text contains Japanese characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Hiragana or Katakana
        """
        for char in text:
            char_code = ord(char)
            if (0x3040 <= char_code <= 0x309F or  # Hiragana
                0x30A0 <= char_code <= 0x30FF):   # Katakana
                return True
        return False

    def contains_cyrillic(self, text: str) -> bool:
        """
        Check if text contains Cyrillic characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Cyrillic characters
        """
        for char in text:
            char_code = ord(char)
            if 0x0400 <= char_code <= 0x04FF:  # Cyrillic
                return True
        return False

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text for better language detection.

        Removes URLs, excessive whitespace, and numbers.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove URLs and technical terms
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        text = re.sub(r'\b\d+\b', '', text)  # Remove standalone numbers

        return text.strip()
