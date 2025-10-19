"""
JSON object translation.

Handles translation of JSON objects with smart caching and batch processing.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class JsonTranslator:
    """Translate JSON objects with caching."""

    def __init__(
        self,
        llm_client,
        translation_cache,
        language_detector,
        text_utils,
        prompt_builder
    ):
        """
        Initialize JSON translator.

        Args:
            llm_client: LLM client for API calls
            translation_cache: Cache manager
            language_detector: Language detector
            text_utils: Text utilities
            prompt_builder: Prompt builder
        """
        self.client = llm_client
        self.cache = translation_cache
        self.language_detector = language_detector
        self.text_utils = text_utils
        self.prompt_builder = prompt_builder

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
            model: Optional model override
            temperature: Optional temperature override

        Returns:
            Translated JSON object
        """
        try:
            # Extract translatable texts
            translatable_texts = self._extract_translatable_texts(
                data, source_language, target_language
            )

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
                from .text_translator import TranslationError
                raise TranslationError(error_msg) from e
            return data

    def _translate_json_batch(
        self,
        data: Any,
        target_language: str,
        source_language: str = 'auto',
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        fail_silently: bool = False
    ) -> Any:
        """Translate JSON object with smart text-level caching."""
        try:
            # Extract all translatable texts
            translatable_texts = self._extract_translatable_texts(
                data, source_language, target_language
            )

            if not translatable_texts:
                return data

            # Detect actual source language from first text if auto
            actual_source_lang = source_language
            if source_language == 'auto' and translatable_texts:
                first_text = list(translatable_texts)[0]
                detected_lang = self.language_detector.detect_language(first_text)
                if detected_lang and detected_lang != 'unknown':
                    actual_source_lang = detected_lang
                else:
                    actual_source_lang = 'en'

            # Check cache for each text
            cached_translations = {}
            uncached_texts = []

            for text in translatable_texts:
                cached_translation = self.cache.get(text, actual_source_lang, target_language)
                if cached_translation:
                    cached_translations[text] = cached_translation
                else:
                    uncached_texts.append(text)

            logger.info(f"Cache: {len(cached_translations)} hits, {len(uncached_texts)} misses")

            # If everything is cached, just reconstruct
            if not uncached_texts:
                return self._apply_translations(data, cached_translations)

            # Create JSON with only uncached texts
            uncached_json = self._create_partial_json(data, uncached_texts)
            json_str = json.dumps(uncached_json, ensure_ascii=False, indent=2)

            # Create translation prompt
            prompt = self.prompt_builder.build_json_translation_prompt(
                json_str, actual_source_lang, target_language
            )

            # Make LLM request
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=temperature if temperature is not None else 0.1,
                max_tokens=4000
            )

            translated_json_str = response.get("content", "").strip()

            # Parse LLM response
            try:
                # Remove markdown formatting
                if translated_json_str.startswith("```json"):
                    translated_json_str = translated_json_str.replace("```json", "").replace("```", "").strip()
                elif translated_json_str.startswith("```"):
                    translated_json_str = translated_json_str.replace("```", "").strip()

                translated_partial_data = json.loads(translated_json_str)

                # Extract new translations
                new_translations = self._extract_translations_by_comparison(
                    uncached_json, translated_partial_data, uncached_texts
                )

                # Cache new translations
                for original_text, translated_text in new_translations.items():
                    self.cache.set(original_text, actual_source_lang, target_language, translated_text)

                # Combine cached + new translations
                all_translations = {**cached_translations, **new_translations}

                # Reconstruct full JSON
                result = self._apply_translations(data, all_translations)

                logger.info(f"Translation complete: {len(cached_translations)} cached, {len(new_translations)} new")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"LLM returned invalid JSON: {e}")
                if fail_silently:
                    return self._apply_translations(data, cached_translations)
                else:
                    from .text_translator import TranslationError
                    raise TranslationError(f"LLM returned invalid JSON: {e}")

        except Exception as e:
            logger.error(f"Batch JSON translation failed: {e}")
            if fail_silently:
                return data
            else:
                from .text_translator import TranslationError
                raise TranslationError(f"Batch JSON translation failed: {e}")

    def _extract_translatable_texts(
        self,
        obj: Any,
        source_language: str,
        target_language: str
    ) -> Set[str]:
        """Extract texts that need translation from JSON object."""
        translatable_texts = set()

        def _extract_recursive(item):
            if isinstance(item, str):
                if self.text_utils.needs_translation(item, source_language, target_language):
                    translatable_texts.add(item)
            elif isinstance(item, list):
                for sub_item in item:
                    _extract_recursive(sub_item)
            elif isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(key, str) and self.text_utils.needs_translation(key, source_language, target_language):
                        translatable_texts.add(key)
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
                translated_key = translations.get(key, key)
                translated_value = self._apply_translations(value, translations)
                translated_dict[translated_key] = translated_value
            return translated_dict
        else:
            return obj

    def _create_partial_json(self, data: Any, texts_to_include: List[str]) -> Any:
        """Create JSON containing only specified texts for translation."""
        texts_set = set(texts_to_include)

        def filter_recursive(obj):
            if isinstance(obj, str):
                return obj if obj in texts_set else "SKIP_TRANSLATION"
            elif isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    filtered_value = filter_recursive(value)
                    if self._contains_translatable_content(filtered_value, texts_set):
                        result[key] = filtered_value
                return result
            elif isinstance(obj, list):
                result = []
                for item in obj:
                    filtered_item = filter_recursive(item)
                    if self._contains_translatable_content(filtered_item, texts_set):
                        result.append(filtered_item)
                return result
            else:
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

    def _extract_translations_by_comparison(
        self,
        original_data: Any,
        translated_data: Any,
        uncached_texts: List[str]
    ) -> Dict[str, str]:
        """Extract translations by comparing original and translated data."""
        translations = {}
        uncached_set = set(uncached_texts)

        def _compare_recursive(original_item, translated_item):
            if isinstance(original_item, str) and isinstance(translated_item, str):
                if original_item in uncached_set and original_item != translated_item:
                    translations[original_item] = translated_item
            elif isinstance(original_item, list) and isinstance(translated_item, list):
                for orig, trans in zip(original_item, translated_item):
                    _compare_recursive(orig, trans)
            elif isinstance(original_item, dict) and isinstance(translated_item, dict):
                # Compare keys
                orig_keys = list(original_item.keys())
                trans_keys = list(translated_item.keys())

                for orig_key, trans_key in zip(orig_keys, trans_keys):
                    if orig_key in uncached_set and orig_key != trans_key:
                        translations[orig_key] = trans_key

                # Compare values
                for orig_key, orig_value in original_item.items():
                    trans_key = translations.get(orig_key, orig_key)
                    if trans_key in translated_item:
                        _compare_recursive(orig_value, translated_item[trans_key])

        _compare_recursive(original_data, translated_data)

        logger.info(f"Extracted {len(translations)} translations from LLM response")
        return translations
