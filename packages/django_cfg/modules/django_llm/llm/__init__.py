"""
LLM Client, Cache, Models Cache, Vision, and Image Generation

Enhanced Vision API (v2.0):
- Model quality presets (fast/balanced/best)
- OCR modes (tiny/small/base/gundam)
- Image fetcher with URL validation
- Token estimation for images
- Async support
- Image caching with TTL

Image Generation (v2.0):
- FLUX, Gemini, DALL-E support
- Model quality presets
- Async support
"""

from .cache import LLMCache
from .client import LLMClient
from .models_cache import ModelsCache
from .cache_dirs import (
    CacheDirectoryBuilder,
    get_default_llm_cache_dir,
    get_models_cache_dir,
    get_translator_cache_dir,
)
from .config import (
    VisionConfig,
    ImageGenConfig,
    LLMVisionConfig,
)
from .vision import (
    # Client
    VisionClient,
    # Encoding
    ImageEncoder,
    ImageFetcher,
    ImageFetchError,
    # Models - Legacy
    VisionRequest,
    VisionResponse,
    ImageAnalysisResult,
    # Models - New
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    OCRRequest,
    OCRResponse,
    # Types
    ModelQuality,
    OCRMode,
    # Presets
    VISION_PRESETS,
    OCR_PRESETS,
    select_vision_model,
    select_ocr_model,
    get_ocr_prompt,
    # Tokens
    estimate_image_tokens,
    # Cache
    ImageCache,
    get_image_cache,
    # Registry
    VisionModel,
    VisionModelPricing,
    VisionModelsRegistry,
)
from .image_gen import (
    ImageGenClient,
    ImageGenRequest,
    ImageGenResponse,
    GeneratedImage,
    ImageSize,
    ImageQuality,
    ImageStyle,
)

__all__ = [
    # Core LLM
    'LLMClient',
    'LLMCache',
    'ModelsCache',
    'CacheDirectoryBuilder',
    'get_default_llm_cache_dir',
    'get_models_cache_dir',
    'get_translator_cache_dir',
    # Config
    'VisionConfig',
    'ImageGenConfig',
    'LLMVisionConfig',
    # Vision - Client
    'VisionClient',
    # Vision - Encoding
    'ImageEncoder',
    'ImageFetcher',
    'ImageFetchError',
    # Vision - Models (Legacy)
    'VisionRequest',
    'VisionResponse',
    'ImageAnalysisResult',
    # Vision - Models (New)
    'VisionAnalyzeRequest',
    'VisionAnalyzeResponse',
    'OCRRequest',
    'OCRResponse',
    # Vision - Types
    'ModelQuality',
    'OCRMode',
    # Vision - Presets
    'VISION_PRESETS',
    'OCR_PRESETS',
    'select_vision_model',
    'select_ocr_model',
    'get_ocr_prompt',
    # Vision - Tokens
    'estimate_image_tokens',
    # Vision - Cache
    'ImageCache',
    'get_image_cache',
    # Vision - Registry
    'VisionModel',
    'VisionModelPricing',
    'VisionModelsRegistry',
    # Image Generation
    'ImageGenClient',
    'ImageGenRequest',
    'ImageGenResponse',
    'GeneratedImage',
    'ImageSize',
    'ImageQuality',
    'ImageStyle',
]
