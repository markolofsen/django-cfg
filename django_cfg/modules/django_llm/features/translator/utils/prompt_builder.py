"""
Prompt generation for translation.

Builds prompts for text and JSON translation.
"""



class PromptBuilder:
    """Build prompts for translation."""

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

    def build_text_translation_prompt(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        """
        Build prompt for text translation.

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code

        Returns:
            Translation prompt
        """
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

    def build_json_translation_prompt(
        self,
        json_str: str,
        source_language: str,
        target_language: str,
        domain: str | None = None,
    ) -> str:
        """
        Build prompt for JSON translation.

        Args:
            json_str: JSON string to translate
            source_language: Source language code
            target_language: Target language code
            domain: Optional subject matter, e.g. "used car listings". Short
                values carry no context of their own, and a weak model guesses
                from the word alone — measured 2026-09-21 against `@cf-json`:
                "Sunroof" came back as "Крыша-складка" (a folding roof) rather
                than "Люк", "Alloy wheels" as "Окрашенные диски" (painted),
                "Leather seats" as "Лаковые сиденья" (lacquered). Prose in the
                same payload translated correctly. Naming the domain is the
                cheapest fix that does not require a glossary per language.

        Returns:
            JSON translation prompt
        """
        source_name = self.language_names.get(source_language, source_language)
        target_name = self.language_names.get(target_language, target_language)
        domain_line = (
            f"\nThese values come from {domain}. Use the vocabulary a native "
            f"{target_name} speaker in that field would use, not a literal "
            f"word-by-word rendering.\n"
            if domain else ""
        )

        prompt = f"""You are a professional translator. Your task is to translate ONLY the VALUES in this JSON, NEVER the keys.

TRANSLATE EVERY VALUE. A value returned unchanged in {source_name} is a
failure unless rule 5 below explicitly exempts it. Short values — one or two
words — are still values and must be translated.
{domain_line}

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

JSON to translate from {source_name} to {target_name}:
{json_str}

Return ONLY the JSON with translated VALUES and original English keys:"""

        return prompt
