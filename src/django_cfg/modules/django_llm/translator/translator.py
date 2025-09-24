"""
Django Translator Service for django_llm.

Auto-configuring translation service with language detection and JSON support.
"""

import json
import logging
import hashlib
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path

from django_cfg.modules import BaseCfgModule
from ..llm.client import LLMClient
from ..llm.cache import LLMCache
from .cache import TranslationCacheManager

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Base exception for translation-related errors."""
    pass


class LanguageDetectionError(TranslationError):
    """Raised when language detection fails."""
    pass


class DjangoTranslator(BaseCfgModule):
    """
    Translation Service for django_cfg, configured via DjangoConfig.

    Provides translation functionality with automatic configuration
    from the main DjangoConfig instance.
    """

    def __init__(self, client=None):
        self._client = client
        self._is_configured = None
        self._translation_cache = {}
        
        # Language mappings
        self.language_names = {
            "en": "English", "ru": "Russian", "ko": "Korean", "zh": "Chinese",
            "ja": "Japanese", "es": "Spanish", "fr": "French", "de": "German",
            "it": "Italian", "pt": "Portuguese", "ar": "Arabic", "hi": "Hindi",
            "tr": "Turkish", "pl": "Polish", "uk": "Ukrainian", "be": "Belarusian",
            "kk": "Kazakh"
        }
        
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
        
        # Initialize translation cache manager (like in unreal_llm)
        self.translation_cache = TranslationCacheManager()
        
        # Statistics
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'language_pairs': {},
            'successful_translations': 0,
            'failed_translations': 0
        }

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

    def detect_language(self, text: str) -> str:
        """
        Detect language of text using simple heuristics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code
        """
        if not text or not text.strip():
            return 'unknown'
        
        # Clean text for better detection
        cleaned_text = self._clean_text(text)
        
        if not cleaned_text:
            return 'unknown'
        
        # Check for CJK characters
        if self._contains_cjk(text):
            # Simple CJK detection
            if self._contains_korean(text):
                return 'ko'
            elif self._contains_japanese(text):
                return 'ja'
            else:
                return 'zh'  # Default to Chinese for other CJK
        
        # Check for Cyrillic (Russian/Ukrainian/Belarusian)
        if self._contains_cyrillic(text):
            return 'ru'  # Default to Russian for Cyrillic
        
        # Default to English for Latin script
        return 'en'

    def _contains_cjk(self, text: str) -> bool:
        """Check if text contains CJK characters."""
        for char in text:
            char_code = ord(char)
            for start, end in self.cjk_ranges:
                if start <= char_code <= end:
                    return True
        return False

    def _contains_korean(self, text: str) -> bool:
        """Check if text contains Korean characters."""
        for char in text:
            char_code = ord(char)
            if 0xAC00 <= char_code <= 0xD7AF:  # Hangul Syllables
                return True
        return False

    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters."""
        for char in text:
            char_code = ord(char)
            if (0x3040 <= char_code <= 0x309F or  # Hiragana
                0x30A0 <= char_code <= 0x30FF):   # Katakana
                return True
        return False

    def _contains_cyrillic(self, text: str) -> bool:
        """Check if text contains Cyrillic characters."""
        for char in text:
            char_code = ord(char)
            if 0x0400 <= char_code <= 0x04FF:  # Cyrillic
                return True
        return False

    def _clean_text(self, text: str) -> str:
        """Clean text for better language detection."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove URLs and technical terms
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        text = re.sub(r'\b\d+\b', '', text)  # Remove standalone numbers
        
        return text.strip()

    def needs_translation(self, text: str, source_language: str, target_language: str) -> bool:
        """
        Determine if text needs translation.
        
        Args:
            text: Text to check
            source_language: Source language code
            target_language: Target language code
            
        Returns:
            True if translation is needed
        """
        if not text or not text.strip():
            return False
        
        # Skip URLs and technical content
        if self._is_technical_content(text):
            return False
        
        # If source and target are the same, no translation needed
        if source_language == target_language:
            return False
        
        # Force translation for CJK content
        if self._contains_cjk(text):
            return True
        
        # Auto-detect if source is 'auto'
        if source_language == 'auto':
            detected_lang = self.detect_language(text)
            return detected_lang != target_language
        
        return True

    def _is_technical_content(self, text: str) -> bool:
        """Check if text is technical content that shouldn't be translated."""
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

    def _get_translation_prompt(self, text: str, source_language: str, target_language: str) -> str:
        """Generate translation prompt."""
        source_name = self.language_names.get(source_language, source_language)
        target_name = self.language_names.get(target_language, target_language)
        
        prompt = f"""You are a professional translator. Translate the following text from {source_name} to {target_name}.

IMPORTANT INSTRUCTIONS:
1. Translate ONLY the text provided
2. Preserve original formatting, numbers, URLs, and technical values
3. Keep the translation accurate and natural
4. Return ONLY the translation, no explanations or comments
5. If the text contains mixed languages, translate only the parts in {source_name}

Text to translate:
{text}

Translation:"""
        
        return prompt

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

            # Auto-detect source language if needed
            if source_language == 'auto':
                source_language = self.detect_language(text)
                if source_language == 'unknown':
                    logger.warning(f"Could not detect language for: {text[:50]}...")
                    if not fail_silently:
                        raise LanguageDetectionError("Could not detect source language")
                    return text

            # Check if translation is needed
            if not self.needs_translation(text, source_language, target_language):
                return text

            # Check translation cache (by language pair like in unreal_llm)
            cached_translation = self.translation_cache.get(text, source_language, target_language)
            if cached_translation:
                self.stats['cache_hits'] += 1
                return cached_translation

            self.stats['cache_misses'] += 1

            # Generate prompt
            prompt = self._get_translation_prompt(text, source_language, target_language)

            # Use LLM client for translation
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature if temperature is not None else 0.1,  # Low temperature for consistent translations
                max_tokens=1000
            )

            # Extract translation
            translated_text = response.get('content', '').strip()
            
            if not translated_text:
                if not fail_silently:
                    raise TranslationError("Empty translation response")
                return text

            # Cache the result (by language pair like in unreal_llm)
            self.translation_cache.set(text, source_language, target_language, translated_text)

            # Update stats
            self.stats['total_translations'] += 1
            self.stats['successful_translations'] += 1
            if response.get('tokens_used'):
                self.stats['total_tokens_used'] += response['tokens_used']
            if response.get('cost_usd'):
                self.stats['total_cost_usd'] += response['cost_usd']
            
            lang_pair = f"{source_language}-{target_language}"
            self.stats['language_pairs'][lang_pair] = self.stats['language_pairs'].get(lang_pair, 0) + 1

            return translated_text

        except Exception as e:
            self.stats['failed_translations'] += 1
            error_msg = f"Failed to translate text: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TranslationError(error_msg) from e
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
        Translate JSON object with automatic language detection.

        Args:
            data: JSON object to translate
            target_language: Target language for translation
            source_language: Source language ('auto' for detection)
            fail_silently: Don't raise exceptions on failure

        Returns:
            Translated JSON object
        """
        try:
            # Extract translatable texts
            translatable_texts = self._extract_translatable_texts(data, source_language, target_language)
            
            if not translatable_texts:
                logger.info("No texts need translation in JSON object")
                return data

            logger.info(f"Found {len(translatable_texts)} texts to translate")

            # Translate entire JSON in one request
            return self._translate_json_batch(
                data=data,
                target_language=target_language,
                source_language=source_language,
                model=model,
                temperature=temperature,
                fail_silently=fail_silently
            )

        except Exception as e:
            error_msg = f"Failed to translate JSON: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise TranslationError(error_msg) from e
            return data

    def _translate_json_batch(self, data: Any, target_language: str, source_language: str = 'auto', 
                             model: Optional[str] = None, temperature: Optional[float] = None,
                             fail_silently: bool = False) -> Any:
        """Translate JSON object with smart text-level caching."""
        try:
            # Extract all translatable texts from JSON
            translatable_texts = self._extract_translatable_texts(data, source_language, target_language)
            
            if not translatable_texts:
                logger.info("No texts need translation in JSON object")
                return data
            
            # Detect actual source language from first text if auto
            actual_source_lang = source_language
            if source_language == 'auto' and translatable_texts:
                first_text = list(translatable_texts)[0]
                detected_lang = self._detect_language(first_text)
                if detected_lang and detected_lang != 'unknown':
                    actual_source_lang = detected_lang
                    logger.info(f"Detected source language: {actual_source_lang}")
                else:
                    actual_source_lang = 'en'  # fallback to English
                    logger.info(f"Language detection failed, using fallback: {actual_source_lang}")
            
            # Check cache for each text and separate cached vs uncached
            cached_translations = {}
            uncached_texts = []
            
            for text in translatable_texts:
                cached_translation = self.translation_cache.get(text, actual_source_lang, target_language)
                if cached_translation:
                    cached_translations[text] = cached_translation
                    logger.debug(f"Cache hit for text: '{text[:50]}...'")
                else:
                    uncached_texts.append(text)
            
            logger.info(f"Found {len(cached_translations)} cached translations, {len(uncached_texts)} need translation")
            
            # If everything is cached, just reconstruct
            if not uncached_texts:
                logger.info("All translations found in cache, reconstructing JSON")
                return self._apply_translations(data, cached_translations)
            
            # Create JSON with only uncached texts for LLM
            uncached_json = self._create_partial_json(data, uncached_texts)
            json_str = json.dumps(uncached_json, ensure_ascii=False, indent=2)
            
            # Create translation prompt
            prompt = f"""You are a professional translator. Your task is to translate ONLY the VALUES in this JSON, NEVER the keys.

🚨 CRITICAL RULES - VIOLATION WILL RESULT IN FAILURE:
1. ❌ NEVER TRANSLATE JSON KEYS: "title" stays "title", NOT "título" or "заголовок"
2. ❌ NEVER TRANSLATE JSON KEYS: "description" stays "description", NOT "descripción" or "описание"  
3. ❌ NEVER TRANSLATE JSON KEYS: "navigation" stays "navigation", NOT "navegación" or "навигация"
4. ✅ ONLY translate the VALUES: "Hello" → "Hola", "World" → "Mundo"
5. ❌ DO NOT translate: URLs, emails, numbers, booleans, null, empty strings, "SKIP_TRANSLATION"
6. ✅ Keep exact JSON structure and key names in English

WRONG EXAMPLE (DO NOT DO THIS):
{{"título": "Hola", "descripción": "Mundo"}}

CORRECT EXAMPLE (DO THIS):
{{"title": "Hola", "description": "Mundo"}}

If you translate ANY JSON key, you have FAILED the task completely.

JSON to translate from {actual_source_lang} to {target_language}:
{json_str}

Return ONLY the JSON with translated VALUES and original English keys:"""

            # Make LLM request for uncached texts only
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=temperature if temperature is not None else 0.1,
                max_tokens=4000
            )
            
            translated_json_str = response.get("content", "").strip()
            
            # Parse LLM response
            try:
                # Remove any markdown formatting if present
                if translated_json_str.startswith("```json"):
                    translated_json_str = translated_json_str.replace("```json", "").replace("```", "").strip()
                elif translated_json_str.startswith("```"):
                    translated_json_str = translated_json_str.replace("```", "").strip()
                
                translated_partial_data = json.loads(translated_json_str)
                
                # Extract new translations by comparing original with translated
                new_translations = self._extract_translations_by_comparison(
                    uncached_json, translated_partial_data, uncached_texts
                )
                
                # Cache new translations
                for original_text, translated_text in new_translations.items():
                    self.translation_cache.set(original_text, actual_source_lang, target_language, translated_text)
                    logger.debug(f"Cached new translation: '{original_text[:30]}...' -> '{translated_text[:30]}...'")
                
                # Combine cached + new translations
                all_translations = {**cached_translations, **new_translations}
                
                # Reconstruct full JSON with all translations
                result = self._apply_translations(data, all_translations)
                
                logger.info(f"Successfully translated JSON: {len(cached_translations)} from cache, {len(new_translations)} new")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"LLM returned invalid JSON: {e}")
                logger.error(f"Response: {translated_json_str[:500]}...")
                
                if fail_silently:
                    # Fallback: use only cached translations
                    return self._apply_translations(data, cached_translations)
                else:
                    raise TranslationError(f"LLM returned invalid JSON: {e}")
                    
        except Exception as e:
            logger.error(f"Batch JSON translation failed: {e}")
            if fail_silently:
                return data
            else:
                raise TranslationError(f"Batch JSON translation failed: {e}")

    def _extract_translatable_texts(self, obj: Any, source_language: str, target_language: str) -> Set[str]:
        """Extract texts that need translation from JSON object."""
        translatable_texts = set()
        
        def _extract_recursive(item):
            if isinstance(item, str):
                if self.needs_translation(item, source_language, target_language):
                    translatable_texts.add(item)
            elif isinstance(item, list):
                for sub_item in item:
                    _extract_recursive(sub_item)
            elif isinstance(item, dict):
                for key, value in item.items():
                    # Check if key needs translation
                    if isinstance(key, str) and self.needs_translation(key, source_language, target_language):
                        translatable_texts.add(key)
                    # Check if value needs translation
                    _extract_recursive(value)
        
        _extract_recursive(obj)
        return translatable_texts

    def _apply_translations(self, obj: Any, translations: Dict[str, str]) -> Any:
        """Apply translations to JSON object."""
        if isinstance(obj, str):
            return translations.get(obj, obj)
        elif isinstance(obj, list):
            return [self._apply_translations(item, translations) for item in obj]
        elif isinstance(obj, dict):
            translated_dict = {}
            for key, value in obj.items():
                # Translate key if it's in translations
                translated_key = translations.get(key, key)
                # Translate value
                translated_value = self._apply_translations(value, translations)
                translated_dict[translated_key] = translated_value
            return translated_dict
        else:
            return obj

    def _create_minimal_json(self, data: Any, uncached_texts: List[str]) -> Any:
        """Create a minimal JSON containing only uncached texts for LLM translation."""
        uncached_set = set(uncached_texts)
        
        def _filter_recursive(item):
            if isinstance(item, str):
                return item if item in uncached_set else None
            elif isinstance(item, list):
                filtered_list = []
                for sub_item in item:
                    filtered = _filter_recursive(sub_item)
                    if filtered is not None:
                        filtered_list.append(filtered)
                return filtered_list if filtered_list else None
            elif isinstance(item, dict):
                filtered_dict = {}
                for key, value in item.items():
                    # Check if key needs translation
                    filtered_key = key if key in uncached_set else key
                    filtered_value = _filter_recursive(value)
                    
                    # Include if key needs translation or value contains translatable content
                    if key in uncached_set or filtered_value is not None:
                        filtered_dict[filtered_key] = filtered_value if filtered_value is not None else value
                
                return filtered_dict if filtered_dict else None
            else:
                return item
        
        result = _filter_recursive(data)
        return result if result is not None else {}

    def _extract_translations_by_comparison(self, original_data: Any, translated_data: Any, uncached_texts: List[str]) -> Dict[str, str]:
        """Extract translations by comparing original and translated data."""
        translations = {}
        uncached_set = set(uncached_texts)
        
        def _compare_recursive(original_item, translated_item):
            if isinstance(original_item, str) and isinstance(translated_item, str):
                if original_item in uncached_set and original_item != translated_item:
                    translations[original_item] = translated_item
                    logger.debug(f"Extracted translation: '{original_item}' -> '{translated_item}'")
            elif isinstance(original_item, list) and isinstance(translated_item, list):
                for orig, trans in zip(original_item, translated_item):
                    _compare_recursive(orig, trans)
            elif isinstance(original_item, dict) and isinstance(translated_item, dict):
                # Compare keys first
                orig_keys = list(original_item.keys())
                trans_keys = list(translated_item.keys())
                
                for orig_key, trans_key in zip(orig_keys, trans_keys):
                    if orig_key in uncached_set and orig_key != trans_key:
                        translations[orig_key] = trans_key
                        logger.debug(f"Extracted key translation: '{orig_key}' -> '{trans_key}'")
                
                # Compare values
                for orig_key, orig_value in original_item.items():
                    # Find corresponding translated key
                    trans_key = translations.get(orig_key, orig_key)
                    if trans_key in translated_item:
                        _compare_recursive(orig_value, translated_item[trans_key])
        
        _compare_recursive(original_data, translated_data)
        
        logger.info(f"Extracted {len(translations)} translations from LLM response")
        return translations

    def _create_partial_json(self, data: Any, texts_to_include: List[str]) -> Any:
        """Create JSON containing only specified texts for translation."""
        texts_set = set(texts_to_include)
        
        def filter_recursive(obj):
            if isinstance(obj, str):
                # Include only texts that need translation
                return obj if obj in texts_set else "SKIP_TRANSLATION"
            elif isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    filtered_value = filter_recursive(value)
                    # Only include if it contains translatable content
                    if self._contains_translatable_content(filtered_value, texts_set):
                        result[key] = filtered_value
                return result
            elif isinstance(obj, list):
                result = []
                for item in obj:
                    filtered_item = filter_recursive(item)
                    # Only include if it contains translatable content
                    if self._contains_translatable_content(filtered_item, texts_set):
                        result.append(filtered_item)
                return result
            else:
                # Keep non-string values as is (numbers, booleans, null)
                return obj
        
        return filter_recursive(data)
    
    def _contains_translatable_content(self, obj: Any, texts_set: set) -> bool:
        """Check if object contains any translatable text."""
        if isinstance(obj, str):
            return obj in texts_set
        elif isinstance(obj, dict):
            return any(self._contains_translatable_content(value, texts_set) for value in obj.values())
        elif isinstance(obj, list):
            return any(self._contains_translatable_content(item, texts_set) for item in obj)
        else:
            return False

    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of text using simple heuristics."""
        if not text or len(text.strip()) < 3:
            return None
        
        text_lower = text.lower().strip()
        
        # Simple language detection based on common words
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'}
        russian_words = {'и', 'в', 'не', 'на', 'я', 'быть', 'он', 'с', 'что', 'а', 'по', 'это', 'она', 'этот', 'к', 'но', 'они', 'мы', 'как', 'из', 'у', 'который', 'то', 'за', 'свой', 'что', 'от', 'со', 'для', 'о', 'же', 'ты', 'все', 'если', 'люди', 'время', 'так', 'его', 'жизнь', 'может', 'год', 'только', 'над', 'еще', 'дом', 'после', 'большой', 'должен', 'хотеть', 'между'}
        spanish_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'muy', 'hasta', 'desde', 'está'}
        portuguese_words = {'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas'}
        
        words = set(text_lower.split())
        
        # Count matches for each language
        en_matches = len(words & english_words)
        ru_matches = len(words & russian_words)
        es_matches = len(words & spanish_words)
        pt_matches = len(words & portuguese_words)
        
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

    def get_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        return self.stats.copy()

    def clear_cache(self) -> bool:
        """Clear translation cache."""
        try:
            self._translation_cache.clear()
            self.client.clear_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to clear translation cache: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """Get translation service configuration information."""
        try:
            client_info = self.client.get_client_info()
            
            return {
                "configured": self.is_configured,
                "provider": client_info.get("provider", "unknown"),
                "cache_size": len(self._translation_cache),
                "client_info": client_info,
                "supported_languages": list(self.language_names.keys()),
            }
        except Exception as e:
            logger.error(f"Failed to get config info: {e}")
            return {
                "configured": False,
                "error": str(e)
            }

    @classmethod
    def send_translation_alert(cls, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send translation alert via configured notification services."""
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
