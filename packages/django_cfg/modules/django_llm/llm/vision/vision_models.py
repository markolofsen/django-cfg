"""
Vision models registry - fetches and caches vision-capable models from OpenRouter.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

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
    """Vision-capable model information."""

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
        """Convert to dictionary for caching."""
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


class VisionModelsRegistry:
    """
    Registry for vision-capable models from OpenRouter.

    Fetches models from API, filters for vision capability, and caches results.
    """

    CACHE_FILENAME = "vision_models.json"
    DEFAULT_TTL = 86400  # 24 hours

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = DEFAULT_TTL,
    ):
        """
        Initialize vision models registry.

        Args:
            api_key: OpenRouter API key (optional for fetching)
            cache_dir: Directory for cache file
            cache_ttl: Cache TTL in seconds
        """
        self.api_key = api_key
        self.cache_ttl = cache_ttl

        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            from ..cache_dirs import get_models_cache_dir
            self.cache_dir = get_models_cache_dir()

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / self.CACHE_FILENAME

        # In-memory storage
        self._models: Dict[str, VisionModel] = {}
        self._last_fetch: Optional[datetime] = None

        # Load from cache on init
        self._load_from_cache()

    def _load_from_cache(self) -> bool:
        """Load models from cache file."""
        try:
            if not self.cache_file.exists():
                return False

            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check TTL
            fetch_time_str = data.get("fetch_time")
            if fetch_time_str:
                fetch_time = datetime.fromisoformat(fetch_time_str)
                if datetime.now() - fetch_time > timedelta(seconds=self.cache_ttl):
                    logger.debug("Vision models cache expired")
                    return False
                self._last_fetch = fetch_time

            # Parse models
            models_data = data.get("models", {})
            self._models = {}
            for model_id, model_data in models_data.items():
                try:
                    self._models[model_id] = VisionModel.from_dict(model_data)
                except Exception as e:
                    logger.warning(f"Failed to parse cached model {model_id}: {e}")

            logger.info(f"Loaded {len(self._models)} vision models from cache")
            return True

        except Exception as e:
            logger.warning(f"Failed to load vision models cache: {e}")
            return False

    def _save_to_cache(self) -> bool:
        """Save models to cache file."""
        try:
            data = {
                "fetch_time": self._last_fetch.isoformat() if self._last_fetch else None,
                "total_models": len(self._models),
                "models": {mid: m.to_dict() for mid, m in self._models.items()},
            }

            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            temp_file.replace(self.cache_file)
            logger.debug(f"Saved {len(self._models)} vision models to cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save vision models cache: {e}")
            return False

    async def fetch(self, force_refresh: bool = False) -> Dict[str, VisionModel]:
        """
        Fetch vision models from OpenRouter API.

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> VisionModel
        """
        # Check cache validity
        if not force_refresh and self._models and self._last_fetch:
            if datetime.now() - self._last_fetch < timedelta(seconds=self.cache_ttl):
                logger.debug("Using cached vision models")
                return self._models

        logger.info("Fetching vision models from OpenRouter API")

        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Parse and filter vision models
                    self._models = {}
                    for model_data in data.get("data", []):
                        model = self._parse_model(model_data)
                        if model and model.supports_image:
                            self._models[model.id] = model

                    self._last_fetch = datetime.now()
                    self._save_to_cache()

                    logger.info(f"Fetched {len(self._models)} vision models")
                    return self._models

        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch vision models: {e}")
            # Return cached if available
            return self._models

    def _parse_model(self, data: Dict[str, Any]) -> Optional[VisionModel]:
        """Parse model data from API response."""
        try:
            architecture = data.get("architecture", {})
            input_modalities = architecture.get("input_modalities", [])
            output_modalities = architecture.get("output_modalities", [])

            # Skip if no image input
            if "image" not in input_modalities:
                return None

            pricing_data = data.get("pricing", {})
            pricing = VisionModelPricing(
                prompt=float(pricing_data.get("prompt", 0)),
                completion=float(pricing_data.get("completion", 0)),
                image=float(pricing_data.get("image", 0)),
            )

            top_provider = data.get("top_provider", {})

            # Extract provider from model ID
            model_id = data.get("id", "")
            provider = model_id.split("/")[0] if "/" in model_id else "unknown"

            return VisionModel(
                id=model_id,
                name=data.get("name", model_id),
                description=data.get("description"),
                context_length=data.get("context_length", 0),
                pricing=pricing,
                provider=provider,
                input_modalities=input_modalities,
                output_modalities=output_modalities,
                max_completion_tokens=top_provider.get("max_completion_tokens"),
                is_moderated=top_provider.get("is_moderated", False),
            )

        except Exception as e:
            logger.warning(f"Failed to parse model: {e}")
            return None

    def get(self, model_id: str) -> Optional[VisionModel]:
        """Get model by ID."""
        return self._models.get(model_id)

    def get_all(self) -> Dict[str, VisionModel]:
        """Get all vision models."""
        return self._models.copy()

    def get_by_provider(self, provider: str) -> List[VisionModel]:
        """Get models by provider (e.g., 'google', 'qwen', 'nvidia')."""
        return [m for m in self._models.values() if m.provider.lower() == provider.lower()]

    def get_cheapest(self, limit: int = 10) -> List[VisionModel]:
        """Get cheapest vision models (sorted by input price)."""
        sorted_models = sorted(self._models.values(), key=lambda m: m.pricing.prompt)
        return sorted_models[:limit]

    def get_by_context_length(self, min_context: int = 0) -> List[VisionModel]:
        """Get models with at least specified context length."""
        return [m for m in self._models.values() if m.context_length >= min_context]

    def search(self, query: str) -> List[VisionModel]:
        """Search models by name or description."""
        query_lower = query.lower()
        results = []
        for model in self._models.values():
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
        # Filter out free models (they have rate limits)
        paid_models = [m for m in self._models.values() if not m.is_free]
        sorted_models = sorted(paid_models, key=lambda m: m.pricing.prompt)
        return sorted_models[:limit]

    @property
    def count(self) -> int:
        """Number of cached vision models."""
        return len(self._models)

    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return len(self._models) > 0

    def clear_cache(self):
        """Clear cache."""
        self._models = {}
        self._last_fetch = None
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Vision models cache cleared")
