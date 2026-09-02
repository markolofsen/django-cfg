"""Quality presets for image edit — mirrors ``features/image_gen``.

Apps pick an intent (``fast`` / ``balanced`` / ``premium``); the
preset resolves to a current OpenRouter model ID. When Google bumps
the Nano Banana lineup, ONE constant changes here; every caller
follows automatically.

Rates per 1M completion tokens, measured against the router catalogue
2026-08-30. Per-edit dollar figures are deliberately absent: the old
ones were measured on a SKU `fast` no longer points at, and carrying
them over would attribute one model's cost to another.
    fast      0.00150  3.1-flash-lite-image — cheapest of the nine
    balanced  0.00300  Nano Banana 2 — preview, better preserve
    premium   0.01200  Nano Banana Pro — best fidelity + 2K/4K
"""

from __future__ import annotations

from typing import Literal

from ..image_models import NANO_BANANA_MODELS, resolve_image_model


# Mirrors ``features/image_gen.ModelQuality`` (intent enum, not the
# OUTPUT resolution preset — that's ``OutputQuality`` below).
ModelQuality = Literal["fast", "balanced", "premium"]


IMAGE_EDIT_MODELS: dict[str, str] = dict(NANO_BANANA_MODELS)


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
    return resolve_image_model(model=model, quality=quality or DEFAULT_MODEL_QUALITY)
