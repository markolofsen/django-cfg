"""
Language detection modules.

Script-based and dictionary-based language detection.
"""

from .language_detector import LanguageDetector
from .script_detector import ScriptDetector

__all__ = [
    'ScriptDetector',
    'LanguageDetector',
]
