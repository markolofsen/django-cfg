"""
Vision client for image analysis using multimodal LLMs.

Uses OpenRouter API with vision models like Qwen2.5 VL, Gemma 3, NVIDIA Nemotron.
Supports structured output with Pydantic schemas.
"""

import base64
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from openai import OpenAI
from pydantic import BaseModel

from ....base import BaseCfgModule
from .image_encoder import ImageEncoder
from .models import VisionRequest, VisionResponse, ImageAnalysisResult
from .vision_models import VisionModelsRegistry

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class VisionClient(BaseCfgModule):
    """
    Client for image analysis using vision-language models.

    Uses OpenRouter API for access to multiple vision models.
    Auto-detects API key from django-cfg config if not provided.
    """

    # Default model (fallback if registry not loaded)
    # Use cheap paid model - free models have rate limits
    DEFAULT_MODEL = "qwen/qwen-2-vl-7b-instruct"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize vision client.

        Args:
            api_key: OpenRouter API key (auto-detected from config if not provided)
            default_model: Default model for vision tasks (auto-selected if None)
            max_tokens: Default max tokens for responses
            temperature: Default temperature for generation
            cache_dir: Directory for models cache
        """
        super().__init__()

        # Auto-detect API key from config if not provided
        if api_key is None:
            django_config = self.get_config()
            if django_config and hasattr(django_config, 'api_keys') and django_config.api_keys:
                api_key = django_config.api_keys.get_openrouter_key()

        self.api_key = api_key
        self._default_model = default_model
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature

        self._client: Optional[OpenAI] = None
        self.image_encoder = ImageEncoder()

        # Models registry
        self.models_registry = VisionModelsRegistry(
            api_key=api_key,
            cache_dir=cache_dir,
        )

        if api_key:
            self._init_client()
        else:
            logger.warning("VisionClient: No API key provided or found in config")

    def _init_client(self):
        """Initialize OpenAI client for OpenRouter."""
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        logger.info("VisionClient initialized with OpenRouter")

    @property
    def client(self) -> OpenAI:
        """Get OpenAI client, raising error if not initialized."""
        if self._client is None:
            raise RuntimeError("VisionClient not initialized. Provide API key.")
        return self._client

    @property
    def default_model(self) -> str:
        """Get default model, using cheapest paid from registry if not set."""
        if self._default_model:
            return self._default_model

        # Try to get cheapest paid from registry (free models have rate limits)
        cheapest = self.models_registry.get_cheapest_paid(1)
        if cheapest:
            return cheapest[0].id

        return self.DEFAULT_MODEL

    def analyze(
        self,
        image_source: str,
        query: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
    ) -> VisionResponse:
        """
        Analyze an image with a text query.

        Args:
            image_source: Image URL, base64 data URL, or file path
            query: Question/prompt about the image
            model: Vision model to use (default: qwen2.5-vl-32b)
            max_tokens: Maximum tokens in response
            temperature: Generation temperature
            system_prompt: Optional system prompt

        Returns:
            VisionResponse with analysis result
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature

        # Prepare image URL
        image_url = self.image_encoder.prepare_image_url(image_source)

        # Build messages
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": query},
            ],
        })

        # Make API call
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            processing_time = (time.time() - start_time) * 1000

            # Extract response data
            content = response.choices[0].message.content or ""
            usage = response.usage

            tokens_input = usage.prompt_tokens if usage else 0
            tokens_output = usage.completion_tokens if usage else 0

            # Calculate cost from registry pricing
            cost_usd = self._calculate_cost(model, tokens_input, tokens_output)

            return VisionResponse(
                content=content,
                model=model,
                query=query,
                image_url=image_source[:100] + "..." if len(image_source) > 100 else image_source,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=cost_usd,
                processing_time_ms=processing_time,
                cached=False,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            raise

    def describe(
        self,
        image_source: str,
        model: Optional[str] = None,
    ) -> VisionResponse:
        """
        Get a general description of an image.

        Args:
            image_source: Image URL, data URL, or file path
            model: Vision model to use

        Returns:
            VisionResponse with image description
        """
        return self.analyze(
            image_source=image_source,
            query="Describe this image in detail. What do you see?",
            model=model,
        )

    def extract_text(
        self,
        image_source: str,
        model: Optional[str] = None,
    ) -> VisionResponse:
        """
        Extract text/OCR from an image.

        Args:
            image_source: Image URL, data URL, or file path
            model: Vision model to use

        Returns:
            VisionResponse with extracted text
        """
        return self.analyze(
            image_source=image_source,
            query="Extract all visible text from this image. Return only the text, preserving layout where possible.",
            model=model or self.default_model,
        )

    def analyze_structured(
        self,
        image_source: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[ImageAnalysisResult, VisionResponse]:
        """
        Analyze image and return structured result with OCR text and description.

        Args:
            image_source: Image URL, data URL, or file path
            context: Optional context (e.g., message text, channel name)
            model: Vision model to use

        Returns:
            Tuple of (ImageAnalysisResult, VisionResponse)
            - ImageAnalysisResult contains: extracted_text, description, language
            - VisionResponse contains: cost, tokens, model info
        """
        import re

        # Build prompt for structured output
        json_format = '''{
  "extracted_text": "all text found in image exactly as written, preserve original language",
  "description": "brief description of image content",
  "language": "language code of text (ru/en/ko/zh/ja/etc) or empty string if no text"
}'''

        if context:
            prompt = f"""Analyze this image.

<context>
{context}
</context>

1. Extract ALL visible text exactly as written (preserve original language, formatting, line breaks)
2. Provide brief description of image content
3. Detect language of text

Respond ONLY with valid JSON:
{json_format}

No preamble. No markdown. Just JSON."""
        else:
            prompt = f"""Analyze this image.

1. Extract ALL visible text exactly as written (preserve original language, formatting, line breaks)
2. Provide brief description of image content
3. Detect language of text

Respond ONLY with valid JSON:
{json_format}

No preamble. No markdown. Just JSON."""

        response = self.analyze(
            image_source=image_source,
            query=prompt,
            model=model,
        )

        # Parse JSON from response
        content = response.content.strip()

        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1).strip()

        # Parse JSON
        try:
            data = json.loads(content)
            result = ImageAnalysisResult(
                extracted_text=data.get("extracted_text", "") or "",
                description=data.get("description", "") or "",
                language=data.get("language", "") or "",
            )
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from vision response, using raw content as description")
            result = ImageAnalysisResult(
                extracted_text="",
                description=content,
                language="",
            )

        return result, response

    def ask(
        self,
        image_source: str,
        questions: List[str],
        model: Optional[str] = None,
    ) -> List[VisionResponse]:
        """
        Ask multiple questions about an image.

        Args:
            image_source: Image URL, data URL, or file path
            questions: List of questions to ask
            model: Vision model to use

        Returns:
            List of VisionResponse for each question
        """
        responses = []
        for question in questions:
            response = self.analyze(
                image_source=image_source,
                query=question,
                model=model,
            )
            responses.append(response)
        return responses

    def _calculate_cost(self, model: str, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost from registry pricing.

        Args:
            model: Model ID
            tokens_input: Input tokens
            tokens_output: Output tokens

        Returns:
            Cost in USD
        """
        model_info = self.models_registry.get(model)

        # If model not in cache, fetch models from API
        if not model_info and not self.models_registry.is_loaded:
            logger.debug("Models registry empty, fetching from API...")
            self.fetch_models_sync()
            model_info = self.models_registry.get(model)

        if not model_info:
            logger.warning(f"Model {model} not found in registry, using 0 cost")
            return 0.0

        pricing = model_info.pricing
        input_cost = tokens_input * pricing.prompt
        output_cost = tokens_output * pricing.completion

        total_cost = input_cost + output_cost
        logger.debug(f"Vision cost for {model}: ${total_cost:.6f} ({tokens_input} in, {tokens_output} out)")
        return total_cost

    def get_model(self, model_id: str):
        """Get model info from registry."""
        return self.models_registry.get(model_id)

    def get_cheapest_paid(self, limit: int = 10):
        """Get cheapest paid vision models (excludes free models with rate limits)."""
        return self.models_registry.get_cheapest_paid(limit)

    async def fetch_models(self, force_refresh: bool = False):
        """
        Fetch vision models from OpenRouter API.

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dict of model_id -> VisionModel
        """
        return await self.models_registry.fetch(force_refresh=force_refresh)

    def fetch_models_sync(self, force_refresh: bool = False):
        """Sync version of fetch_models()."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.fetch_models(force_refresh=force_refresh))
        finally:
            loop.close()

    # =========================================================================
    # Django Model Integration
    # =========================================================================

    def analyze_model(
        self,
        instance: Any,
        image_field: str = "file",
        prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        model: Optional[str] = None,
    ) -> Union[T, str, None]:
        """
        Analyze image from Django model field.

        Args:
            instance: Django model instance with image field
            image_field: Name of the field containing image (FileField, ImageField, or URLField)
            prompt: Query/prompt for analysis (default: "Describe this image")
            schema: Optional Pydantic model for structured output
            model: Vision model to use

        Returns:
            - If schema provided: Populated Pydantic model instance
            - If no schema: Raw text response
            - None if analysis failed

        Example:
            class ChartAnalysis(BaseModel):
                trend: str
                confidence: float
                summary: str

            result = client.analyze_model(
                media,
                image_field="file",
                prompt=media.message.message_text,
                schema=ChartAnalysis,
            )
            media.image_analysis = result.model_dump()
            media.save()
        """
        # Get image source from model field
        image_source = self._get_image_source(instance, image_field)
        if not image_source:
            logger.warning(f"No image source found in {instance.__class__.__name__}.{image_field}")
            return None

        # Default prompt
        if not prompt:
            prompt = "Describe this image in detail. What do you see?"

        # Build system prompt with schema if provided
        system_prompt = None
        if schema:
            json_schema = schema.model_json_schema()
            system_prompt = (
                "You are an image analysis assistant. "
                "Analyze the image and respond with valid JSON matching this schema:\n"
                f"```json\n{json.dumps(json_schema, indent=2)}\n```\n"
                "Respond ONLY with valid JSON, no other text."
            )

        try:
            response = self.analyze(
                image_source=image_source,
                query=prompt,
                model=model,
                system_prompt=system_prompt,
            )

            content = response.content

            # Parse to Pydantic model if schema provided
            if schema:
                return self._parse_to_schema(content, schema)

            return content

        except Exception as e:
            logger.error(f"analyze_model failed: {e}")
            return None

    def _get_image_source(self, instance: Any, image_field: str) -> Optional[str]:
        """Extract image source from Django model field."""
        try:
            field_value = getattr(instance, image_field, None)
            if not field_value:
                return None

            # FileField / ImageField
            if hasattr(field_value, 'read'):
                try:
                    file_bytes = field_value.read()
                    field_value.seek(0)

                    # Detect mime type
                    mime_type = "image/jpeg"
                    if hasattr(instance, 'mime_type') and instance.mime_type:
                        mime_type = instance.mime_type
                    elif hasattr(field_value, 'name'):
                        name = field_value.name.lower()
                        if name.endswith('.png'):
                            mime_type = "image/png"
                        elif name.endswith('.webp'):
                            mime_type = "image/webp"
                        elif name.endswith('.gif'):
                            mime_type = "image/gif"

                    b64_data = base64.b64encode(file_bytes).decode('utf-8')
                    return f"data:{mime_type};base64,{b64_data}"
                except Exception as e:
                    logger.warning(f"Failed to read file field: {e}")
                    return None

            # URL string
            if isinstance(field_value, str):
                if field_value.startswith(('http://', 'https://', 'data:')):
                    return field_value

            # URLField with .url property
            if hasattr(field_value, 'url'):
                return field_value.url

            return None

        except Exception as e:
            logger.error(f"Failed to get image source: {e}")
            return None

    def _parse_to_schema(self, content: str, schema: Type[T]) -> Optional[T]:
        """Parse LLM response to Pydantic model."""
        try:
            # Try to extract JSON from response
            text = content.strip()

            # Remove markdown code blocks if present
            if text.startswith("```"):
                lines = text.split("\n")
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = "\n".join(lines)

            # Parse JSON
            data = json.loads(text)

            # Validate with Pydantic
            return schema.model_validate(data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}\nContent: {content[:200]}")
            return None
        except Exception as e:
            logger.error(f"Failed to validate schema: {e}")
            return None
