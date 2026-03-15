"""
Configuration classes for LLM vision and image generation.
"""

from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class VisionConfig(BaseModel):
    """Configuration for vision analysis."""

    # Enable/disable vision
    enabled: bool = Field(
        default=True,
        description="Whether vision analysis is enabled"
    )

    # Model settings
    default_model: str = Field(
        default="qwen/qwen-2-vl-7b-instruct",
        description="Default vision model"
    )
    default_model_quality: Literal["fast", "balanced", "best"] = Field(
        default="balanced",
        description="Default model quality preset"
    )
    default_ocr_mode: Literal["tiny", "small", "base", "gundam"] = Field(
        default="base",
        description="Default OCR extraction mode"
    )

    # Request settings
    default_max_tokens: int = Field(
        default=1024,
        ge=1,
        le=128000,
        description="Default max tokens for responses"
    )
    default_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Default temperature for generation"
    )

    # Image fetching
    fetch_enabled: bool = Field(
        default=True,
        description="Whether to fetch images from URLs"
    )
    fetch_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Timeout for image fetching in seconds"
    )
    max_image_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum image size in megabytes"
    )
    allowed_domains: Optional[List[str]] = Field(
        default=None,
        description="Allowed domains for image URLs (None = all)"
    )

    # Caching
    cache_enabled: bool = Field(
        default=True,
        description="Whether to cache images and responses"
    )
    cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=720,
        description="Cache TTL in hours"
    )
    cache_dir: Optional[str] = Field(
        default=None,
        description="Custom cache directory path"
    )

    @property
    def cache_path(self) -> Optional[Path]:
        """Get cache directory as Path."""
        return Path(self.cache_dir) if self.cache_dir else None


class ImageGenConfig(BaseModel):
    """Configuration for image generation."""

    # Enable/disable
    enabled: bool = Field(
        default=True,
        description="Whether image generation is enabled"
    )

    # Model settings
    default_model: str = Field(
        default="google/gemini-2.0-flash-exp:free",
        description="Default image generation model"
    )
    default_model_quality: Literal["fast", "balanced", "best"] = Field(
        default="balanced",
        description="Default model quality preset"
    )

    # Generation settings
    default_size: str = Field(
        default="1024x1024",
        description="Default image size"
    )
    default_quality: Literal["standard", "hd"] = Field(
        default="standard",
        description="Default image quality"
    )
    default_style: Literal["vivid", "natural"] = Field(
        default="vivid",
        description="Default image style"
    )

    # Caching
    cache_enabled: bool = Field(
        default=True,
        description="Whether to cache generated images"
    )
    cache_ttl_hours: int = Field(
        default=168,  # 7 days
        ge=1,
        le=720,
        description="Cache TTL in hours"
    )
    cache_max_size_mb: int = Field(
        default=1024,
        ge=100,
        le=10240,
        description="Maximum cache size in megabytes"
    )
    cache_dir: Optional[str] = Field(
        default=None,
        description="Custom cache directory path"
    )

    @property
    def cache_path(self) -> Optional[Path]:
        """Get cache directory as Path."""
        return Path(self.cache_dir) if self.cache_dir else None


class LLMVisionConfig(BaseModel):
    """Combined configuration for LLM vision module."""

    vision: VisionConfig = Field(
        default_factory=VisionConfig,
        description="Vision analysis configuration"
    )
    image_gen: ImageGenConfig = Field(
        default_factory=ImageGenConfig,
        description="Image generation configuration"
    )

    @classmethod
    def from_dict(cls, data: dict) -> "LLMVisionConfig":
        """Create config from dictionary."""
        return cls(
            vision=VisionConfig(**data.get("vision", {})),
            image_gen=ImageGenConfig(**data.get("image_gen", {})),
        )


# Default configuration
DEFAULT_VISION_CONFIG = VisionConfig()
DEFAULT_IMAGE_GEN_CONFIG = ImageGenConfig()


__all__ = [
    "VisionConfig",
    "ImageGenConfig",
    "LLMVisionConfig",
    "DEFAULT_VISION_CONFIG",
    "DEFAULT_IMAGE_GEN_CONFIG",
]
