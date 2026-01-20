"""
Image generation client using OpenRouter API.

Supports FLUX, Gemini, DALL-E and other image generation models.
"""

import logging
from typing import Optional

from openai import OpenAI, AsyncOpenAI

from ....base import BaseCfgModule
from typing import Literal

from .models import (
    ImageGenResponse,
    GeneratedImage,
    ImageSize,
    ImageQuality,
    ImageStyle,
    ModelQuality,
    IMAGE_GEN_PRESETS,
    DEFAULT_IMAGE_GEN_MODEL,
    get_image_gen_price,
)

ResponseFormat = Literal["url", "b64_json"]

logger = logging.getLogger(__name__)


class ImageGenClient(BaseCfgModule):
    """
    Client for image generation using AI models.

    Uses OpenRouter API for access to multiple image generation models.
    Auto-detects API key from django-cfg config if not provided.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        """
        Initialize image generation client.

        Args:
            api_key: OpenRouter API key (auto-detected from config if not provided)
            default_model: Default model for generation (auto-selected if None)
        """
        super().__init__()

        # Auto-detect API key from config
        if api_key is None:
            django_config = self.get_config()
            if django_config and hasattr(django_config, 'api_keys') and django_config.api_keys:
                api_key = django_config.api_keys.get_openrouter_key()

        self.api_key = api_key
        self._default_model = default_model

        self._client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None

        if api_key:
            self._init_client()
        else:
            logger.warning("ImageGenClient: No API key provided or found in config")

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
        logger.info("ImageGenClient initialized with OpenRouter")

    @property
    def client(self) -> OpenAI:
        """Get sync OpenAI client."""
        if self._client is None:
            raise RuntimeError("ImageGenClient not initialized. Provide API key.")
        return self._client

    @property
    def async_client(self) -> AsyncOpenAI:
        """Get async OpenAI client."""
        if self._async_client is None:
            raise RuntimeError("ImageGenClient not initialized. Provide API key.")
        return self._async_client

    @property
    def default_model(self) -> str:
        """Get default model."""
        return self._default_model or DEFAULT_IMAGE_GEN_MODEL

    def _select_model(
        self,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
    ) -> str:
        """Select model based on explicit model or quality preset."""
        if model:
            return model

        if model_quality and model_quality in IMAGE_GEN_PRESETS:
            preset = IMAGE_GEN_PRESETS[model_quality]
            if preset:
                return preset

        return self.default_model

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        n: int = 1,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        style: ImageStyle = "vivid",
        response_format: ResponseFormat = "url",
    ) -> ImageGenResponse:
        """
        Generate images from text prompt.

        Args:
            prompt: Text description of the image to generate
            model: Explicit model ID (overrides model_quality)
            model_quality: Quality preset (fast/balanced/best)
            n: Number of images to generate (1-10)
            size: Image dimensions
            quality: Image quality (standard/hd)
            style: Image style (vivid/natural)
            response_format: Response format (url/b64_json)

        Returns:
            ImageGenResponse with generated images

        Example:
            result = client.generate(
                "A beautiful sunset over mountains",
                model_quality="balanced",
                size="1024x1024",
            )
            print(result.first_url)
        """
        selected_model = self._select_model(model, model_quality)

        try:
            response = self.client.images.generate(
                model=selected_model,
                prompt=prompt,
                n=n,
                size=size,
                quality=quality,
                style=style,
                response_format=response_format,
            )

            # Build response
            images = []
            for img_data in response.data or []:
                images.append(GeneratedImage(
                    url=getattr(img_data, 'url', None),
                    b64_json=getattr(img_data, 'b64_json', None),
                    revised_prompt=getattr(img_data, 'revised_prompt', None),
                ))

            # Calculate cost
            cost_usd = get_image_gen_price(selected_model, size) * n

            return ImageGenResponse(
                images=images,
                model=selected_model,
                prompt=prompt,
                cost_usd=cost_usd,
            )

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def agenerate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        model_quality: Optional[ModelQuality] = None,
        n: int = 1,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        style: ImageStyle = "vivid",
        response_format: ResponseFormat = "url",
    ) -> ImageGenResponse:
        """
        Async version of generate().

        Args:
            prompt: Text description of the image to generate
            model: Explicit model ID (overrides model_quality)
            model_quality: Quality preset (fast/balanced/best)
            n: Number of images to generate (1-10)
            size: Image dimensions
            quality: Image quality (standard/hd)
            style: Image style (vivid/natural)
            response_format: Response format (url/b64_json)

        Returns:
            ImageGenResponse with generated images
        """
        selected_model = self._select_model(model, model_quality)

        try:
            response = await self.async_client.images.generate(
                model=selected_model,
                prompt=prompt,
                n=n,
                size=size,
                quality=quality,
                style=style,
                response_format=response_format,
            )

            # Build response
            images = []
            for img_data in response.data or []:
                images.append(GeneratedImage(
                    url=getattr(img_data, 'url', None),
                    b64_json=getattr(img_data, 'b64_json', None),
                    revised_prompt=getattr(img_data, 'revised_prompt', None),
                ))

            # Calculate cost
            cost_usd = get_image_gen_price(selected_model, size) * n

            return ImageGenResponse(
                images=images,
                model=selected_model,
                prompt=prompt,
                cost_usd=cost_usd,
            )

        except Exception as e:
            logger.error(f"Async image generation failed: {e}")
            raise

    def generate_quick(
        self,
        prompt: str,
        size: ImageSize = "1024x1024",
    ) -> Optional[str]:
        """
        Quick image generation with default settings.

        Returns URL of generated image or None on failure.

        Args:
            prompt: Text description
            size: Image dimensions

        Returns:
            URL of generated image or None
        """
        try:
            result = self.generate(
                prompt=prompt,
                model_quality="fast",
                size=size,
            )
            return result.first_url
        except Exception as e:
            logger.error(f"Quick generation failed: {e}")
            return None

    async def agenerate_quick(
        self,
        prompt: str,
        size: ImageSize = "1024x1024",
    ) -> Optional[str]:
        """Async version of generate_quick()."""
        try:
            result = await self.agenerate(
                prompt=prompt,
                model_quality="fast",
                size=size,
            )
            return result.first_url
        except Exception as e:
            logger.error(f"Async quick generation failed: {e}")
            return None
