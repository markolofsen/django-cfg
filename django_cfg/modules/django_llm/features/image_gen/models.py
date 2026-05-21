"""
Data models for image generation requests and responses.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# Type aliases
ImageSize = Literal[
    "256x256",
    "512x512",
    "1024x1024",
    "1792x1024",
    "1024x1792",
    "1024x768",
    "768x1024",
]
ImageQuality = Literal["standard", "hd"]
ImageStyle = Literal["vivid", "natural"]
ModelQuality = Literal["fast", "balanced", "best"]


class ImageGenRequest(BaseModel):
    """Request for image generation."""

    prompt: str = Field(
        description="Text description of the image to generate"
    )
    model: Optional[str] = Field(
        default=None,
        description="Explicit model ID to use"
    )
    model_quality: Optional[ModelQuality] = Field(
        default=None,
        description="Model quality preset (fast/balanced/best)"
    )
    n: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of images to generate"
    )
    size: ImageSize = Field(
        default="1024x1024",
        description="Image dimensions"
    )
    quality: ImageQuality = Field(
        default="standard",
        description="Image quality (standard/hd)"
    )
    style: ImageStyle = Field(
        default="vivid",
        description="Image style (vivid/natural)"
    )
    response_format: Literal["url", "b64_json"] = Field(
        default="url",
        description="Response format"
    )

    def to_api_params(self) -> Dict[str, Any]:
        """Convert to API request parameters."""
        return {
            "prompt": self.prompt,
            "n": self.n,
            "size": self.size,
            "quality": self.quality,
            "style": self.style,
            "response_format": self.response_format,
        }


class GeneratedImage(BaseModel):
    """A single generated image."""

    url: Optional[str] = Field(
        default=None,
        description="URL of generated image (if response_format='url')"
    )
    b64_json: Optional[str] = Field(
        default=None,
        description="Base64 encoded image (if response_format='b64_json')"
    )
    revised_prompt: Optional[str] = Field(
        default=None,
        description="Revised prompt used for generation (if model modified it)"
    )

    def to_data_url(self, content_type: str = "image/png") -> Optional[str]:
        """Convert b64_json to data URL."""
        if self.b64_json:
            return f"data:{content_type};base64,{self.b64_json}"
        return None


class ImageGenResponse(BaseModel):
    """Response from image generation."""

    images: List[GeneratedImage] = Field(
        default_factory=list,
        description="List of generated images"
    )
    model: str = Field(
        description="Model used for generation"
    )
    prompt: str = Field(
        description="Original prompt"
    )
    cost_usd: float = Field(
        default=0.0,
        description="Cost in USD"
    )
    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of generation"
    )

    @property
    def first_url(self) -> Optional[str]:
        """Get URL of first generated image."""
        if self.images and self.images[0].url:
            return self.images[0].url
        return None

    @property
    def first_b64(self) -> Optional[str]:
        """Get base64 of first generated image."""
        if self.images and self.images[0].b64_json:
            return self.images[0].b64_json
        return None

    @property
    def count(self) -> int:
        """Number of generated images."""
        return len(self.images)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "images": [img.model_dump() for img in self.images],
            "model": self.model,
            "prompt": self.prompt,
            "cost_usd": self.cost_usd,
            "created": self.created.isoformat(),
            "count": self.count,
        }


# Model presets for image generation
IMAGE_GEN_PRESETS: Dict[ModelQuality, Optional[str]] = {
    "fast": None,  # Auto-select cheapest
    "balanced": "google/gemini-2.0-flash-exp:free",
    "best": "black-forest-labs/flux-1.1-pro",
}

# Default model
DEFAULT_IMAGE_GEN_MODEL = "google/gemini-2.0-flash-exp:free"

# Pricing per image (approximate)
IMAGE_GEN_PRICING: Dict[str, float] = {
    "black-forest-labs/flux-1.1-pro": 0.04,
    "black-forest-labs/flux-pro": 0.05,
    "black-forest-labs/flux-dev": 0.025,
    "black-forest-labs/flux-schnell": 0.003,
    "google/gemini-2.0-flash-exp:free": 0.0,
    "openai/dall-e-3": 0.04,
    "openai/dall-e-2": 0.02,
}


def get_image_gen_price(model: str, size: str = "1024x1024") -> float:
    """
    Get price for image generation.

    Args:
        model: Model ID
        size: Image size

    Returns:
        Price per image in USD
    """
    base_price = IMAGE_GEN_PRICING.get(model, 0.04)

    # Adjust for size (larger = more expensive for some models)
    if "1792" in size:
        base_price *= 1.5
    elif "512" in size:
        base_price *= 0.5
    elif "256" in size:
        base_price *= 0.25

    return base_price
