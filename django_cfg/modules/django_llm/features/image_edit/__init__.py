"""Image edit — image-in, prompt-in, image-out via multimodal models.

Pure image generation lives in ``features/image_gen`` (text → image).
This module is the missing third corner: image + prompt → edited
image. Backed by Nano Banana family models on OpenRouter, which
accept multimodal inputs AND multimodal outputs via
``modalities=["image","text"]``.

Cost is calculated through the same registry every other django_llm
client uses, so AIPhoto / future apps don't need their own pricing
math.

Model selection mirrors ``features/image_gen``:

    client = ImageEditClient()
    # By preset (recommended):
    r = client.edit_premium(image_bytes, "Brighten the room.")
    r = client.edit_fast(image_bytes, "Remove the corner overlay.")
    # Or via the typed request with ``model_quality``:
    r = client.edit(ImageEditRequest(..., model_quality="balanced"))
    # Or explicit SKU override:
    r = client.edit(ImageEditRequest(..., model="google/..."))
"""

from .client import ImageEditClient
from .errors import ImageEditError, NoImageReturnedError
from .fanout import edit_many
from .models import (
    DEFAULT_EDIT_MODEL,
    AspectRatio,
    ImageEditRequest,
    ImageEditResponse,
    OutputQuality,
)
from .payload import build_payload
from .presets import (
    DEFAULT_MODEL_QUALITY,
    IMAGE_EDIT_MODELS,
    ModelQuality,
    resolve_model,
)
from .prompt_safety import sanitize_edit_prompt
from .response_parser import extract_image_bytes, extract_text

__all__ = [
    "ImageEditClient",
    "ImageEditError",
    "NoImageReturnedError",
    "ImageEditRequest",
    "ImageEditResponse",
    "OutputQuality",
    "AspectRatio",
    "ModelQuality",
    "DEFAULT_EDIT_MODEL",
    "DEFAULT_MODEL_QUALITY",
    "IMAGE_EDIT_MODELS",
    "resolve_model",
    "sanitize_edit_prompt",
    "edit_many",
]
