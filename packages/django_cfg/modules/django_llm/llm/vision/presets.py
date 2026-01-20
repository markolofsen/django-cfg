"""
Model quality presets and OCR modes for vision analysis.

Provides automatic model selection based on quality/cost trade-offs.
"""

from typing import Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .vision_models import VisionModelsRegistry


# Type aliases
ModelQuality = Literal["fast", "balanced", "best"]
OCRMode = Literal["tiny", "small", "base", "gundam"]


# Vision model presets by quality level
VISION_PRESETS: dict[ModelQuality, Optional[str]] = {
    "fast": None,  # Auto-select cheapest
    "balanced": "meta-llama/llama-3.2-11b-vision-instruct",
    "best": "openai/gpt-4o",
}

# OCR model presets (same as vision for now)
OCR_PRESETS: dict[ModelQuality, Optional[str]] = {
    "fast": None,  # Auto-select cheapest
    "balanced": "meta-llama/llama-3.2-11b-vision-instruct",
    "best": "openai/gpt-4o",
}

# Image generation presets
IMAGE_GEN_PRESETS: dict[ModelQuality, Optional[str]] = {
    "fast": None,
    "balanced": "google/gemini-2.0-flash-exp:free",
    "best": "black-forest-labs/flux-1.1-pro",
}

# Fallback models when auto-selection fails
DEFAULT_VISION_MODEL = "qwen/qwen-2-vl-7b-instruct"
DEFAULT_OCR_MODEL = "qwen/qwen-2-vl-7b-instruct"


# OCR mode prompts with varying detail levels
OCR_MODE_PROMPTS: dict[OCRMode, str] = {
    "tiny": (
        "Extract text from image. Return only the text, nothing else."
    ),
    "small": (
        "Extract all visible text from this image. "
        "Return the text preserving basic structure."
    ),
    "base": (
        "Extract ALL visible text from this image exactly as written. "
        "Preserve original language, formatting, and line breaks. "
        "Return only the extracted text, no descriptions or comments."
    ),
    "gundam": (
        "You are an expert OCR system. Extract EVERY piece of text from this image "
        "with maximum accuracy. This includes:\n"
        "- Main body text\n"
        "- Headers and titles\n"
        "- Captions and labels\n"
        "- Watermarks and logos\n"
        "- Small print and footnotes\n"
        "- Text in any language\n\n"
        "Preserve exact formatting, spacing, and line breaks. "
        "If text is unclear, provide your best interpretation in [brackets]. "
        "Return ONLY the extracted text, no descriptions."
    ),
}


def select_vision_model(
    model: Optional[str] = None,
    model_quality: Optional[ModelQuality] = None,
    models_registry: Optional["VisionModelsRegistry"] = None,
) -> str:
    """
    Select vision model based on explicit model or quality preset.

    Priority:
    1. Explicit model if provided
    2. Preset model for quality level
    3. Cheapest paid model from registry
    4. Default fallback model

    Args:
        model: Explicit model ID
        model_quality: Quality preset (fast/balanced/best)
        models_registry: Optional registry for auto-selection

    Returns:
        Selected model ID
    """
    # 1. Explicit model takes priority
    if model:
        return model

    # 2. Quality preset
    if model_quality and model_quality in VISION_PRESETS:
        preset_model = VISION_PRESETS[model_quality]
        if preset_model:
            return preset_model

    # 3. Auto-select cheapest from registry
    if models_registry:
        cheapest = models_registry.get_cheapest_paid(1)
        if cheapest:
            return cheapest[0].id

    # 4. Fallback
    return DEFAULT_VISION_MODEL


def select_ocr_model(
    model: Optional[str] = None,
    model_quality: Optional[ModelQuality] = None,
    models_registry: Optional["VisionModelsRegistry"] = None,
) -> str:
    """
    Select OCR model based on explicit model or quality preset.

    Args:
        model: Explicit model ID
        model_quality: Quality preset (fast/balanced/best)
        models_registry: Optional registry for auto-selection

    Returns:
        Selected model ID
    """
    # 1. Explicit model takes priority
    if model:
        return model

    # 2. Quality preset
    if model_quality and model_quality in OCR_PRESETS:
        preset_model = OCR_PRESETS[model_quality]
        if preset_model:
            return preset_model

    # 3. Auto-select from registry
    if models_registry:
        cheapest = models_registry.get_cheapest_paid(1)
        if cheapest:
            return cheapest[0].id

    # 4. Fallback
    return DEFAULT_OCR_MODEL


def get_ocr_prompt(mode: OCRMode = "base") -> str:
    """
    Get OCR prompt for specified mode.

    Args:
        mode: OCR quality mode (tiny/small/base/gundam)

    Returns:
        Prompt string for OCR extraction
    """
    return OCR_MODE_PROMPTS.get(mode, OCR_MODE_PROMPTS["base"])


__all__ = [
    "ModelQuality",
    "OCRMode",
    "VISION_PRESETS",
    "OCR_PRESETS",
    "IMAGE_GEN_PRESETS",
    "DEFAULT_VISION_MODEL",
    "DEFAULT_OCR_MODEL",
    "OCR_MODE_PROMPTS",
    "select_vision_model",
    "select_ocr_model",
    "get_ocr_prompt",
]
