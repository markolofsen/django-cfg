"""
Dictionary-based language detection.

Detects language using common word dictionaries.
"""

from typing import Optional


class LanguageDetector:
    """Detect language using common word dictionaries."""

    def __init__(self):
        # Common words for each language
        self.english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        }

        self.russian_words = {
            'и', 'в', 'не', 'на', 'я', 'быть', 'он', 'с', 'что', 'а', 'по',
            'это', 'она', 'этот', 'к', 'но', 'они', 'мы', 'как', 'из', 'у',
            'который', 'то', 'за', 'свой', 'от', 'со', 'для', 'о', 'же', 'ты',
            'все', 'если', 'люди', 'время', 'так', 'его', 'жизнь', 'может',
            'год', 'только', 'над', 'еще', 'дом', 'после', 'большой', 'должен',
            'хотеть', 'между'
        }

        self.spanish_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no',
            'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al',
            'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'ha', 'me', 'si',
            'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta',
            'ser', 'dos', 'también', 'fue', 'había', 'muy', 'hasta', 'desde',
            'está'
        }

        self.portuguese_words = {
            'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é',
            'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as',
            'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu',
            'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está',
            'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre',
            'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas',
            'numa', 'pelos', 'pelas'
        }

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text using common word dictionaries.

        Args:
            text: Text to analyze

        Returns:
            Language code or None if detection fails
        """
        if not text or len(text.strip()) < 3:
            return None

        text_lower = text.lower().strip()
        words = set(text_lower.split())

        # Count matches for each language
        en_matches = len(words & self.english_words)
        ru_matches = len(words & self.russian_words)
        es_matches = len(words & self.spanish_words)
        pt_matches = len(words & self.portuguese_words)

        # Find the language with most matches
        max_matches = max(en_matches, ru_matches, es_matches, pt_matches)

        if max_matches == 0:
            return 'en'  # Default to English if no matches

        if en_matches == max_matches:
            return 'en'
        elif ru_matches == max_matches:
            return 'ru'
        elif es_matches == max_matches:
            return 'es'
        elif pt_matches == max_matches:
            return 'pt'

        return 'en'  # Default fallback
