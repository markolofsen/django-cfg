"""Single source of truth for OpenRouter image-capable model intents."""
from __future__ import annotations


NANO_BANANA_MODELS: dict[str, str] = {
    "fast": "google/gemini-2.5-flash-image",
    "balanced": "google/gemini-3.1-flash-image-preview",
    "premium": "google/gemini-3-pro-image-preview",
}


def resolve_image_model(*, model: str | None = None, quality: str | None = None) -> str:
    if model:
        return model
    selected = quality or "balanced"
    selected = "premium" if selected == "best" else selected
    if selected not in NANO_BANANA_MODELS:
        raise ValueError(
            f"unknown image quality {quality!r}; expected fast, balanced, premium/best"
        )
    return NANO_BANANA_MODELS[selected]
