"""Quality presets for image edit — mirrors ``features/image_gen``.

Apps pick an intent (``fast`` / ``balanced`` / ``premium``); the
preset resolves to a current OpenRouter model ID. When Google bumps
the Nano Banana lineup, ONE constant changes here; every caller
follows automatically.

Cost ballpark (June 2026 OpenRouter pricing, per typical real-estate
photo edit at HD output):
    fast      ≈ $0.07     Nano Banana GA — cheapest, stable
    balanced  ≈ $0.07-0.10 Nano Banana 2 — preview, better preserve
    premium   ≈ $0.30-0.50 Nano Banana Pro — best fidelity + 2K/4K
"""

from __future__ import annotations

from typing import Literal


# Mirrors ``features/image_gen.ModelQuality`` (intent enum, not the
# OUTPUT resolution preset — that's ``OutputQuality`` below).
ModelQuality = Literal["fast", "balanced", "premium"]


IMAGE_EDIT_MODELS: dict[str, str] = {
    "fast":     "google/gemini-2.5-flash-image",
    "balanced": "google/gemini-3.1-flash-image-preview",
    "premium":  "google/gemini-3-pro-image-preview",
}


# Default when no explicit model and no quality preset is given.
# Picking PREMIUM (Nano Banana Pro) — production listing photos need
# faithful interpretation of nuanced prompt directives (directional
# light, material textures, micro-contrast) that Flash struggles
# with. Real cost data (June 2026) shows ~$0.13/edit Pro vs ~$0.04
# Fast — $0.09 difference is negligible per photo for assets shown
# to hundreds of buyers. Apps that want cheap iteration override
# per-call via ``ImageEditRequest(model_quality="fast")``.
DEFAULT_MODEL_QUALITY: ModelQuality = "premium"


def resolve_model(
    *,
    model: str | None = None,
    quality: ModelQuality | None = None,
) -> str:
    """Pick the final OpenRouter model id.

    Priority:
        explicit ``model`` (full id) > ``quality`` preset > default.
    """
    if model:
        return model
    if quality:
        if quality not in IMAGE_EDIT_MODELS:
            raise ValueError(
                f"unknown image-edit quality preset {quality!r}; "
                f"expected one of {list(IMAGE_EDIT_MODELS)}"
            )
        return IMAGE_EDIT_MODELS[quality]
    return IMAGE_EDIT_MODELS[DEFAULT_MODEL_QUALITY]
