"""
Vision client for image analysis using multimodal LLMs.

Uses OpenRouter API with vision models like Qwen2.5 VL, Gemma 3, NVIDIA Nemotron.
Supports structured output with Pydantic schemas.
Includes automatic image resizing for token optimization.
"""

import base64
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union, cast

from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel

from ....base import BaseCfgModule
from .image_encoder import ImageEncoder
from .image_fetcher import ImageFetcher, ImageFetchError
from .image_resizer import DetailMode
from .models import (
    VisionRequest,
    VisionResponse,
    ImageAnalysisResult,
    VisionAnalyzeResponse,
    OCRResponse,
)
from .presets import (
    ModelQuality,
    OCRMode,
    select_vision_model,
    select_ocr_model,
    get_ocr_prompt,
)
from .tokens import estimate_image_tokens
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
        auto_resize: bool = True,
        default_detail: DetailMode = "low",
    ):
        """
        Initialize vision client.

        Args:
            api_key: OpenRouter API key (auto-detected from config if not provided)
            default_model: Default model for vision tasks (auto-selected if None)
            max_tokens: Default max tokens for responses
            temperature: Default temperature for generation
            cache_dir: Directory for models cache
            auto_resize: Whether to auto-resize images for token optimization (default True)
            default_detail: Default detail mode for resize (low/high/auto, default "low")
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
        self.auto_resize = auto_resize
        self.default_detail = default_detail

        self._client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None
        self.image_encoder = ImageEncoder()
        self.image_fetcher = ImageFetcher(resize=auto_resize, detail=default_detail)

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
        """Initialize OpenAI clients for OpenRouter."""
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self._async_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        logger.info("VisionClient initialized with OpenRouter")

    @property
    def client(self) -> OpenAI:
        """Get sync OpenAI client, raising error if not initialized."""
        if self._client is None:
            raise RuntimeError("VisionClient not initialized. Provide API key.")
        return self._client

    @property
    def async_client(self) -> AsyncOpenAI:
        """Get async OpenAI client, raising error if not initialized."""
        if self._async_client is None:
            raise RuntimeError("VisionClient not initialized. Provide API key.")
        return self._async_client

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
        resize: Optional[bool] = None,
        detail: Optional[DetailMode] = None,
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
            resize: Override auto_resize setting (None uses instance default)
            detail: Override default_detail setting (None uses instance default)

        Returns:
            VisionResponse with analysis result
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature

        # Use instance defaults if not overridden
        should_resize = resize if resize is not None else self.auto_resize
        detail_mode = detail if detail is not None else self.default_detail

        # Prepare image URL
        image_url = self.image_encoder.prepare_image_url(
            image_source, resize=should_resize, detail=cast(DetailMode, detail_mode)
        )

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

    async def aanalyze(
        self,
        image_source: str,
        query: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        resize: Optional[bool] = None,
        detail: Optional[DetailMode] = None,
    ) -> VisionResponse:
        """
        Async version of analyze().

        Args:
            image_source: Image URL, base64 data URL, or file path
            query: Question/prompt about the image
            model: Vision model to use
            max_tokens: Maximum tokens in response
            temperature: Generation temperature
            system_prompt: Optional system prompt
            resize: Override auto_resize setting (None uses instance default)
            detail: Override default_detail setting (None uses instance default)

        Returns:
            VisionResponse with analysis result
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature

        # Use instance defaults if not overridden
        should_resize = resize if resize is not None else self.auto_resize
        detail_mode = detail if detail is not None else self.default_detail

        # Prepare image URL
        image_url = self.image_encoder.prepare_image_url(
            image_source, resize=should_resize, detail=cast(DetailMode, detail_mode)
        )

        # Build messages
        messages: List[Dict[str, Any]] = []

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
            response = await self.async_client.chat.completions.create(
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
            logger.error(f"Async vision analysis failed: {e}")
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
    # Enhanced Vision API with Model Quality Presets
    # =========================================================================

    def analyze_with_quality(
        self,
        *,
        image: Optional[str] = None,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        ocr_mode: OCRMode = "base",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> VisionAnalyzeResponse:
        """
        Analyze image with model quality presets.

        Args:
            image: Base64 encoded image data
            image_url: URL of image to analyze
            prompt: Analysis prompt/question (default: describe + OCR)
            model: Explicit model ID (overrides model_quality)
            model_quality: Quality preset (fast/balanced/best)
            ocr_mode: OCR extraction mode (tiny/small/base/gundam)
            max_tokens: Maximum tokens in response
            temperature: Generation temperature

        Returns:
            VisionAnalyzeResponse with description, extracted_text, cost, tokens

        Example:
            result = client.analyze_with_quality(
                image_url="https://example.com/image.jpg",
                model_quality="balanced",
                ocr_mode="base",
            )
            print(result.description)
            print(result.extracted_text)
            print(f"Cost: ${result.cost_usd}")
        """
        # Validate input
        if not image and not image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Select model based on quality preset
        selected_model = select_vision_model(
            model=model,
            model_quality=model_quality,
            models_registry=self.models_registry,
        )

        # Prepare image source (we know one of them is set due to validation above)
        image_source: str
        if image:
            # Build data URL from base64
            image_source = self.image_fetcher.build_data_url(image)
        elif image_url:
            image_source = image_url
        else:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Build prompt with OCR mode
        ocr_prompt = get_ocr_prompt(ocr_mode)

        if prompt:
            full_prompt = f"""{prompt}

Additionally, {ocr_prompt}

Respond with JSON:
{{
  "description": "your analysis based on the prompt",
  "extracted_text": "all text found in image",
  "language": "detected language code (en/ru/ko/etc) or null"
}}"""
        else:
            full_prompt = f"""Analyze this image.

1. Provide a brief description of what you see
2. {ocr_prompt}
3. Detect the language of any text

Respond with JSON only:
{{
  "description": "brief description of image content",
  "extracted_text": "all text found in image",
  "language": "detected language code (en/ru/ko/etc) or null"
}}"""

        # Make request
        response = self.analyze(
            image_source=image_source,
            query=full_prompt,
            model=selected_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Parse JSON response
        import re
        content = response.content.strip()

        # Extract JSON from markdown if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1).strip()

        try:
            data = json.loads(content)
            return VisionAnalyzeResponse(
                description=data.get("description", "") or "",
                extracted_text=data.get("extracted_text", "") or "",
                language=data.get("language"),
                model=selected_model,
                cost_usd=response.cost_usd,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
            )
        except json.JSONDecodeError:
            # Fallback: use raw content as description
            return VisionAnalyzeResponse(
                description=content,
                extracted_text="",
                language=None,
                model=selected_model,
                cost_usd=response.cost_usd,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
            )

    def ocr(
        self,
        *,
        image: Optional[str] = None,
        image_url: Optional[str] = None,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        mode: OCRMode = "base",
        max_tokens: Optional[int] = None,
    ) -> OCRResponse:
        """
        Extract text from image using OCR.

        Args:
            image: Base64 encoded image data
            image_url: URL of image to process
            model: Explicit model ID (overrides model_quality)
            model_quality: Quality preset (fast/balanced/best)
            mode: OCR mode (tiny/small/base/gundam)
            max_tokens: Maximum tokens in response

        Returns:
            OCRResponse with extracted text and cost info

        Example:
            result = client.ocr(
                image_url="https://example.com/document.png",
                mode="gundam",
                model_quality="best",
            )
            print(result.text)
            print(f"Cost: ${result.cost_usd}")
        """
        # Validate input
        if not image and not image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Select model
        selected_model = select_ocr_model(
            model=model,
            model_quality=model_quality,
            models_registry=self.models_registry,
        )

        # Prepare image source (we know one of them is set due to validation above)
        image_source: str
        if image:
            image_source = self.image_fetcher.build_data_url(image)
        elif image_url:
            image_source = image_url
        else:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Get OCR prompt for mode
        ocr_prompt = get_ocr_prompt(mode)

        # Make request
        response = self.analyze(
            image_source=image_source,
            query=ocr_prompt,
            model=selected_model,
            max_tokens=max_tokens,
        )

        return OCRResponse(
            text=response.content.strip(),
            model=selected_model,
            cost_usd=response.cost_usd,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
        )

    async def aanalyze_with_quality(
        self,
        *,
        image: Optional[str] = None,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        ocr_mode: OCRMode = "base",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> VisionAnalyzeResponse:
        """Async version of analyze_with_quality()."""
        # Validate input
        if not image and not image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Select model
        selected_model = select_vision_model(
            model=model,
            model_quality=model_quality,
            models_registry=self.models_registry,
        )

        # Prepare image source
        image_source: str
        if image:
            image_source = self.image_fetcher.build_data_url(image)
        elif image_url:
            image_source = image_url
        else:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Build prompt
        ocr_prompt = get_ocr_prompt(ocr_mode)
        if prompt:
            full_prompt = f"""{prompt}

Additionally, {ocr_prompt}

Respond with JSON:
{{
  "description": "your analysis based on the prompt",
  "extracted_text": "all text found in image",
  "language": "detected language code (en/ru/ko/etc) or null"
}}"""
        else:
            full_prompt = f"""Analyze this image.

1. Provide a brief description of what you see
2. {ocr_prompt}
3. Detect the language of any text

Respond with JSON only:
{{
  "description": "brief description of image content",
  "extracted_text": "all text found in image",
  "language": "detected language code (en/ru/ko/etc) or null"
}}"""

        # Make async request
        response = await self.aanalyze(
            image_source=image_source,
            query=full_prompt,
            model=selected_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Parse JSON response
        import re
        content = response.content.strip()
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1).strip()

        try:
            data = json.loads(content)
            return VisionAnalyzeResponse(
                description=data.get("description", "") or "",
                extracted_text=data.get("extracted_text", "") or "",
                language=data.get("language"),
                model=selected_model,
                cost_usd=response.cost_usd,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
            )
        except json.JSONDecodeError:
            return VisionAnalyzeResponse(
                description=content,
                extracted_text="",
                language=None,
                model=selected_model,
                cost_usd=response.cost_usd,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
            )

    async def aocr(
        self,
        *,
        image: Optional[str] = None,
        image_url: Optional[str] = None,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        mode: OCRMode = "base",
        max_tokens: Optional[int] = None,
    ) -> OCRResponse:
        """Async version of ocr()."""
        # Validate input
        if not image and not image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Select model
        selected_model = select_ocr_model(
            model=model,
            model_quality=model_quality,
            models_registry=self.models_registry,
        )

        # Prepare image source
        image_source: str
        if image:
            image_source = self.image_fetcher.build_data_url(image)
        elif image_url:
            image_source = image_url
        else:
            raise ValueError("Either 'image' or 'image_url' must be provided")

        # Get OCR prompt
        ocr_prompt = get_ocr_prompt(mode)

        # Make async request
        response = await self.aanalyze(
            image_source=image_source,
            query=ocr_prompt,
            model=selected_model,
            max_tokens=max_tokens,
        )

        return OCRResponse(
            text=response.content.strip(),
            model=selected_model,
            cost_usd=response.cost_usd,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
        )

    def estimate_tokens(
        self,
        image_source: str,
        detail: Literal["low", "high", "auto"] = "high",
    ) -> int:
        """
        Estimate tokens for an image.

        Args:
            image_source: Image URL, data URL, or file path
            detail: Detail mode (low/high/auto)

        Returns:
            Estimated token count
        """
        try:
            info = self.image_encoder.get_image_info(image_source)
            return estimate_image_tokens(
                width=info["width"],
                height=info["height"],
                detail=detail,
            )
        except Exception as e:
            logger.warning(f"Failed to estimate tokens: {e}, using default")
            return estimate_image_tokens(detail=detail)

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
