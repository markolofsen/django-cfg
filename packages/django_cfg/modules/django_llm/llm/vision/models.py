"""
Data models for vision requests and responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
    timestamp: datetime = field(default_factory=datetime.utcnow)
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
