"""
Vision models registry - a vision-filtered view over the shared OpenRouter
model catalogue (`registry.ModelsCache`).

This module does NOT fetch `/models` itself. It delegates fetch + cache to the
canonical `ModelsCache` and exposes a thin, vision-specific view: `VisionModel`
wrappers built from the shared `OpenRouterModel` catalogue, filtered to models
that accept image input.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...registry.models import ModelsCache, OpenRouterModel

logger = logging.getLogger(__name__)


@dataclass
class VisionModelPricing:
    """Pricing information for a vision model."""

    prompt: float  # Price per token (input)
    completion: float  # Price per token (output)
    image: float = 0.0  # Price per image
    currency: str = "USD"

    @property
    def is_free(self) -> bool:
        """Check if model is free."""
        return self.prompt == 0 and self.completion == 0

    @property
    def cost_per_1m_input(self) -> float:
        """Cost per 1M input tokens."""
        return self.prompt * 1_000_000

    @property
    def cost_per_1m_output(self) -> float:
        """Cost per 1M output tokens."""
        return self.completion * 1_000_000


@dataclass
class VisionModel:
    """
    Vision-capable model — a thin view over a shared catalogue
    `OpenRouterModel`, carrying vision-specific accessors.
    """

    id: str
    name: str
    description: Optional[str]
    context_length: int
    pricing: VisionModelPricing
    provider: str
    input_modalities: List[str] = field(default_factory=list)
    output_modalities: List[str] = field(default_factory=list)
    max_completion_tokens: Optional[int] = None
    is_moderated: bool = False

    @property
    def is_free(self) -> bool:
        """Check if model is free."""
        return self.pricing.is_free

    @property
    def supports_image(self) -> bool:
        """Check if model supports image input."""
        return "image" in self.input_modalities

    @property
    def supports_file(self) -> bool:
        """Check if model supports file input."""
        return "file" in self.input_modalities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "context_length": self.context_length,
            "pricing": {
                "prompt": self.pricing.prompt,
                "completion": self.pricing.completion,
                "image": self.pricing.image,
                "currency": self.pricing.currency,
            },
            "provider": self.provider,
            "input_modalities": self.input_modalities,
            "output_modalities": self.output_modalities,
            "max_completion_tokens": self.max_completion_tokens,
            "is_moderated": self.is_moderated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisionModel":
        """Create from dictionary."""
        pricing_data = data.get("pricing", {})
        pricing = VisionModelPricing(
            prompt=pricing_data.get("prompt", 0),
            completion=pricing_data.get("completion", 0),
            image=pricing_data.get("image", 0),
            currency=pricing_data.get("currency", "USD"),
        )
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            context_length=data.get("context_length", 0),
            pricing=pricing,
            provider=data.get("provider", ""),
            input_modalities=data.get("input_modalities", []),
            output_modalities=data.get("output_modalities", []),
            max_completion_tokens=data.get("max_completion_tokens"),
            is_moderated=data.get("is_moderated", False),
        )

    @classmethod
    def from_catalogue(cls, model: OpenRouterModel) -> "VisionModel":
        """Build a vision view from a shared catalogue `OpenRouterModel`."""
        pricing = VisionModelPricing(
            prompt=model.pricing.prompt_price,
            completion=model.pricing.completion_price,
            image=model.pricing.image_price,
            currency=model.pricing.currency,
        )
        # Provider is derived from the model id (OpenRouter `provider` field is
        # usually empty), matching the previous vision parser behaviour.
        provider = model.id.split("/")[0] if "/" in model.id else "unknown"
        return cls(
            id=model.id,
            name=model.name or model.id,
            description=model.description,
            context_length=model.context_length,
            pricing=pricing,
            provider=provider,
            input_modalities=model.input_modalities,
            output_modalities=model.output_modalities,
            max_completion_tokens=model.max_completion_tokens,
            is_moderated=model.is_moderated,
        )


class VisionModelsRegistry:
    """
    Vision-filtered view over the shared OpenRouter model catalogue.

    Wraps a `ModelsCache` (the single canonical `/models` fetcher) and exposes
    only image-input-capable models as `VisionModel` instances. No HTTP fetch
    or cache file of its own.
    """

    DEFAULT_TTL = 86400  # 24 hours

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = DEFAULT_TTL,
        models_cache: Optional[ModelsCache] = None,
    ):
        """
        Initialize vision models registry.

        Args:
            api_key: OpenRouter API key (used to build a ModelsCache if one is
                not injected)
            cache_dir: Directory for the shared catalogue cache file
            cache_ttl: Cache TTL in seconds
            models_cache: Optional shared ModelsCache to view (enables reuse and
                network-free testing). When omitted, one is created.
        """
        self.cache_ttl = cache_ttl
        self.models_cache = models_cache or ModelsCache(
            api_key=api_key or "",
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )

    def _vision_models(self) -> Dict[str, VisionModel]:
        """Project the shared catalogue down to image-capable models."""
        models: Dict[str, VisionModel] = {}
        for model in self.models_cache.models.values():
            vision = VisionModel.from_catalogue(model)
            if vision.supports_image:
                models[vision.id] = vision
        return models

    async def fetch(self, force_refresh: bool = False) -> Dict[str, VisionModel]:
        """
        Refresh the shared catalogue and return vision models.

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> VisionModel
        """
        await self.models_cache.fetch_models(force_refresh=force_refresh)
        return self._vision_models()

    def get(self, model_id: str) -> Optional[VisionModel]:
        """Get vision model by ID."""
        return self._vision_models().get(model_id)

    def get_all(self) -> Dict[str, VisionModel]:
        """Get all vision models."""
        return self._vision_models()

    def get_by_provider(self, provider: str) -> List[VisionModel]:
        """Get models by provider (e.g., 'google', 'qwen', 'nvidia')."""
        return [
            m for m in self._vision_models().values()
            if m.provider.lower() == provider.lower()
        ]

    def get_cheapest(self, limit: int = 10) -> List[VisionModel]:
        """Get cheapest vision models (sorted by input price)."""
        sorted_models = sorted(
            self._vision_models().values(), key=lambda m: m.pricing.prompt
        )
        return sorted_models[:limit]

    def get_by_context_length(self, min_context: int = 0) -> List[VisionModel]:
        """Get models with at least specified context length."""
        return [
            m for m in self._vision_models().values()
            if m.context_length >= min_context
        ]

    def search(self, query: str) -> List[VisionModel]:
        """Search models by name or description."""
        query_lower = query.lower()
        results = []
        for model in self._vision_models().values():
            if query_lower in model.name.lower():
                results.append(model)
            elif model.description and query_lower in model.description.lower():
                results.append(model)
        return results

    def get_cheapest_paid(self, limit: int = 1) -> List[VisionModel]:
        """
        Get cheapest paid vision models (excludes free models with rate limits).

        Args:
            limit: Maximum number of models to return

        Returns:
            List of cheapest paid VisionModel instances
        """
        paid_models = [m for m in self._vision_models().values() if not m.is_free]
        sorted_models = sorted(paid_models, key=lambda m: m.pricing.prompt)
        return sorted_models[:limit]

    @property
    def count(self) -> int:
        """Number of vision models in the shared catalogue."""
        return len(self._vision_models())

    @property
    def is_loaded(self) -> bool:
        """Check if the shared catalogue has any models loaded."""
        return len(self.models_cache.models) > 0

    def clear_cache(self):
        """Clear the shared catalogue cache."""
        self.models_cache.clear_cache()
        logger.info("Vision models registry cleared (shared catalogue)")
