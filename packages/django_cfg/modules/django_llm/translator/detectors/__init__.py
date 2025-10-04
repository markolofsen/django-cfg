"""
Language detection modules.

Script-based and dictionary-based language detection.
"""

from .script_detector import ScriptDetector
from .language_detector import LanguageDetector

__all__ = [
    'ScriptDetector',
    'LanguageDetector',
]
