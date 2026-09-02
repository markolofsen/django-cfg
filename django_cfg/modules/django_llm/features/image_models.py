"""Single source of truth for OpenRouter image-capable model intents."""
from __future__ import annotations


#: `fast` is the DEFAULT every caller lands on, so it has to be the cheapest
#: model that still produces an image — not merely a fast one. Measured against
#: the router catalogue 2026-08-30: lite bills 0.00150/1M completion against
#: 2.5-flash-image's 0.00250, and carries double the context (65536 vs 32768).
#: An image already costs ~44 chat turns, so the default tier is where the
#: money is; anything better is a deliberate ask by the caller.
NANO_BANANA_MODELS: dict[str, str] = {
    "fast": "google/gemini-3.1-flash-lite-image",
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
