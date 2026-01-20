"""
Vision module for image analysis using multimodal LLMs.

Supports OpenRouter vision models (Qwen2.5 VL, Gemma 3, NVIDIA Nemotron, etc.)

New in v2.0:
- Model quality presets (fast/balanced/best)
- OCR modes (tiny/small/base/gundam)
- Image fetcher with URL validation
- Token estimation for images
"""

from .client import VisionClient
from .image_encoder import ImageEncoder
from .image_fetcher import ImageFetcher, ImageFetchError
from .models import (
    VisionRequest,
    VisionResponse,
    ImageAnalysisResult,
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    OCRRequest,
    OCRResponse,
    ModelQuality,
    OCRMode,
)
from .presets import (
    VISION_PRESETS,
    OCR_PRESETS,
    IMAGE_GEN_PRESETS,
    select_vision_model,
    select_ocr_model,
    get_ocr_prompt,
)
from .tokens import (
    estimate_image_tokens,
    estimate_cost_from_tokens,
    get_tile_count,
    get_optimal_detail_mode,
)
from .cache import ImageCache, get_image_cache
from .vision_models import VisionModel, VisionModelPricing, VisionModelsRegistry

__all__ = [
    # Client
    "VisionClient",
    # Encoding
    "ImageEncoder",
    "ImageFetcher",
    "ImageFetchError",
    # Models - Legacy
    "VisionRequest",
    "VisionResponse",
    "ImageAnalysisResult",
    # Models - New
    "VisionAnalyzeRequest",
    "VisionAnalyzeResponse",
    "OCRRequest",
    "OCRResponse",
    # Types
    "ModelQuality",
    "OCRMode",
    # Presets
    "VISION_PRESETS",
    "OCR_PRESETS",
    "IMAGE_GEN_PRESETS",
    "select_vision_model",
    "select_ocr_model",
    "get_ocr_prompt",
    # Tokens
    "estimate_image_tokens",
    "estimate_cost_from_tokens",
    "get_tile_count",
    "get_optimal_detail_mode",
    # Cache
    "ImageCache",
    "get_image_cache",
    # Vision Models Registry
    "VisionModel",
    "VisionModelPricing",
    "VisionModelsRegistry",
]
