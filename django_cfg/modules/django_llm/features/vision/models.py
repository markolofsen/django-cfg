"""
Data models for vision requests and responses.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

# Type aliases
ModelQuality = Literal["fast", "balanced", "best"]
OCRMode = Literal["tiny", "small", "base", "gundam"]


class ImageAnalysisResult(BaseModel):
    """
    Structured result from image analysis.

    Contains extracted text (OCR), description, and language detection.
    """

    extracted_text: str = Field(
        default="",
        description="All text found in the image (OCR). Empty string if no text visible."
    )
    description: str = Field(
        default="",
        description="Brief description of what's in the image."
    )
    language: str = Field(
        default="",
        description="Language code of text in image (e.g., 'ru', 'en', 'ko'). Empty if no text."
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


@dataclass
class VisionRequest:
    """Request for vision analysis."""

    image_url: str  # URL or base64 data URL
    query: str  # Question about the image
    model: str = "qwen/qwen2.5-vl-32b-instruct:free"
    max_tokens: int = 1024
    temperature: float = 0.2

    def to_messages(self) -> List[Dict[str, Any]]:
        """Convert to OpenAI-compatible messages format."""
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": self.image_url},
                    },
                    {
                        "type": "text",
                        "text": self.query,
                    },
                ],
            }
        ]


@dataclass
class VisionResponse:
    """Response from vision analysis."""

    content: str
    model: str
    query: str
    image_url: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def tokens_total(self) -> int:
        """Total tokens used."""
        return self.tokens_input + self.tokens_output

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "query": self.query,
            "image_url": self.image_url[:100] + "..." if len(self.image_url) > 100 else self.image_url,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_total,
            },
            "cost_usd": self.cost_usd,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "cached": self.cached,
        }


class VisionAnalyzeRequest(BaseModel):
    """
    Request for vision analysis with model quality support.

    Either image (base64) or image_url must be provided.
    """

    image: Optional[str] = Field(
        default=None,
        description="Base64 encoded image data"
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL of image to analyze"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Analysis prompt/question"
    )
    model: Optional[str] = Field(
        default=None,
        description="Explicit model ID to use"
    )
    model_quality: Optional[ModelQuality] = Field(
        default=None,
        description="Model quality preset (fast/balanced/best)"
    )
    ocr_mode: OCRMode = Field(
        default="base",
        description="OCR extraction mode (tiny/small/base/gundam)"
    )
    fetch_image: bool = Field(
        default=True,
        description="Whether to fetch image from URL"
    )

    @model_validator(mode="after")
    def validate_image_source(self) -> "VisionAnalyzeRequest":
        """Ensure either image or image_url is provided."""
        if not self.image and not self.image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")
        return self


class VisionAnalyzeResponse(BaseModel):
    """
    Enhanced response from vision analysis.

    Includes full cost and token tracking.
    """

    extracted_text: str = Field(
        default="",
        description="OCR text from image"
    )
    description: str = Field(
        default="",
        description="Image description"
    )
    language: Optional[str] = Field(
        default=None,
        description="Detected language code"
    )
    model: str = Field(
        description="Model used for analysis"
    )
    cost_usd: float = Field(
        default=0.0,
        description="Cost in USD"
    )
    tokens_input: int = Field(
        default=0,
        description="Input tokens used"
    )
    tokens_output: int = Field(
        default=0,
        description="Output tokens used"
    )

    @property
    def tokens_total(self) -> int:
        """Total tokens used."""
        return self.tokens_input + self.tokens_output

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **self.model_dump(),
            "tokens_total": self.tokens_total,
        }


class OCRRequest(BaseModel):
    """Request for OCR text extraction."""

    image: Optional[str] = Field(
        default=None,
        description="Base64 encoded image data"
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL of image to process"
    )
    model: Optional[str] = Field(
        default=None,
        description="Explicit model ID"
    )
    model_quality: Optional[ModelQuality] = Field(
        default=None,
        description="Model quality preset"
    )
    mode: OCRMode = Field(
        default="base",
        description="OCR mode (tiny/small/base/gundam)"
    )
    fetch_image: bool = Field(
        default=True,
        description="Whether to fetch image from URL"
    )

    @model_validator(mode="after")
    def validate_image_source(self) -> "OCRRequest":
        """Ensure either image or image_url is provided."""
        if not self.image and not self.image_url:
            raise ValueError("Either 'image' or 'image_url' must be provided")
        return self


class OCRResponse(BaseModel):
    """Response from OCR extraction."""

    text: str = Field(
        description="Extracted text from image"
    )
    model: str = Field(
        description="Model used for extraction"
    )
    cost_usd: float = Field(
        default=0.0,
        description="Cost in USD"
    )
    tokens_input: int = Field(
        default=0,
        description="Input tokens used"
    )
    tokens_output: int = Field(
        default=0,
        description="Output tokens used"
    )

    @property
    def tokens_total(self) -> int:
        """Total tokens used."""
        return self.tokens_input + self.tokens_output

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **self.model_dump(),
            "tokens_total": self.tokens_total,
        }
