"""
OpenRouter Models Cache - Fetch and cache available models with pricing
Originally adapted from unreal_llm; now part of modules.django_llm.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from cachetools import TTLCache

logger = logging.getLogger(__name__)

@dataclass
class ModelPricing:
    """Model pricing — the single source of truth for token cost.

    UNITS (pinned): ``prompt_price`` and ``completion_price`` are USD per
    **1M tokens** (e.g. gpt-4o-mini prompt=0.15 == $0.15/1M). OpenRouter's
    ``/models`` API returns USD **per token** as a string (e.g.
    "0.00000015"); ``_price_per_million`` multiplies by 1e6 at the
    population site so EVERYTHING downstream is per-1M. Cost math lives in
    :meth:`cost` — call it, never re-derive the ``/ 1e6`` division.
    """
    prompt_price: float  # USD per 1M input tokens
    completion_price: float  # USD per 1M output tokens
    currency: str = "USD"
    # OpenRouter's `image` field — documented as a per-IMAGE fee (schema:
    # "pricing per 1 image"), stored RAW (unscaled), unlike prompt/completion
    # which are ×1e6 → per-1M. Deliberately NOT used in `cost()`: the only
    # models that set it are Gemini, where it equals the per-token prompt rate
    # because Gemini image input is already counted in `prompt_tokens` — so
    # `cost(prompt_tokens, ...)` already bills it. Adding it would double-count.
    # See @docs/pricing-units-audit.md "Universality audit".
    image_price: float = 0.0

    def cost(self, tokens_input: int, tokens_output: int) -> float:
        """USD cost for the given token counts (per-1M pricing → USD).

        The ONE place token-cost arithmetic lives. Both the registry and
        the vision client route through this so the ``/ 1_000_000`` unit
        conversion can never drift (the bug that booked an 8.5k-token OCR
        as ~$1294 instead of ~$0.0013).
        """
        return (
            (tokens_input / 1_000_000) * self.prompt_price
            + (tokens_output / 1_000_000) * self.completion_price
        )

@dataclass
class OpenRouterModel:
    """OpenRouter model information from the /models catalogue"""
    id: str
    name: str
    description: Optional[str]
    context_length: int
    pricing: ModelPricing
    provider: str
    tags: List[str]
    is_available: bool = True
    input_modalities: List[str] = field(default_factory=list)
    output_modalities: List[str] = field(default_factory=list)
    max_completion_tokens: Optional[int] = None
    is_moderated: bool = False
    # OpenRouter `supported_parameters` — e.g. "response_format",
    # "structured_outputs", "tools", "reasoning". Drives the advisory layer.
    supported_parameters: List[str] = field(default_factory=list)
    # True when this entry came from OpenRouter's `/embeddings/models`
    # endpoint (or its output modality is "embedding"). Embedding models
    # have a prompt price but no completion price; the pricing-sync uses
    # this flag to write `capabilities.embeddings=True` rows into the DB.
    is_embedding: bool = False

    # ── Derived capability getters (centralized here so every consumer —
    #    the gateway catalog ingest, a future SDK, django — reads the SAME
    #    capability logic instead of re-deriving it from raw fields). ──

    @property
    def vendor(self) -> str:
        """Real vendor from the slug prefix (OpenRouter rarely sends `provider`).
        `anthropic/claude-3.5-haiku` → `anthropic`."""
        return self.id.split("/", 1)[0] if "/" in self.id else (self.provider or "")

    @property
    def supports_tools(self) -> bool:
        return "tools" in self.supported_parameters

    @property
    def supports_vision(self) -> bool:
        return "image" in self.input_modalities

    @property
    def supports_structured(self) -> bool:
        return any(
            p in self.supported_parameters
            for p in ("structured_outputs", "response_format")
        )

    @property
    def supports_reasoning(self) -> bool:
        return "reasoning" in self.supported_parameters

    @property
    def is_text_chat(self) -> bool:
        """Usable for a prose/tool chat turn: text in, text out (or unspecified).
        Excludes image-only / audio-only / embedding-only entries."""
        return "text" in self.input_modalities and (
            "text" in self.output_modalities or not self.output_modalities
        )

    @property
    def max_price_per_1m(self) -> float:
        """The higher of prompt/completion $/1M — the figure a price cap checks."""
        return max(self.pricing.prompt_price or 0.0, self.pricing.completion_price or 0.0)


@dataclass
class EndpointStats:
    """Per-model speed/health from OpenRouter's `/models/{slug}/endpoints`,
    computed by OpenRouter over real fleet traffic (rolling 30m). The best
    endpoint's figures — latency in ms, throughput in tok/s, uptime as a fraction.
    Any field may be None when OpenRouter hasn't measured it."""

    model_id: str
    latency_p50_ms: Optional[float] = None
    latency_p90_ms: Optional[float] = None
    throughput_tok_s: Optional[float] = None
    uptime_1d: Optional[float] = None


def _price_per_million(raw: Any) -> float:
    """Convert an OpenRouter per-token price (a string like "0.00000015")
    to a per-1M-token float — the unit ModelPricing and the cost math use."""
    try:
        return float(raw or 0.0) * 1_000_000
    except (TypeError, ValueError):
        return 0.0

class ModelsCache:
    """Cache for OpenRouter models with pricing information"""

    DEFAULT_TTL = 86400  # 24 hours default
    DEFAULT_CACHE_SIZE = 100
    # v3: includes the 26 embedding models merged from OpenRouter's
    # /api/v1/embeddings/models endpoint (is_embedding flag). The version bump
    # invalidates a pre-fix v2 cache automatically, so a deployed node picks up
    # embeddings on its next fetch instead of serving a stale chat-only cache for
    # up to the 24h TTL.
    CACHE_FILENAME = "openrouter_models_v3.json"

    def __init__(self,
                 api_key: Optional[str] = None,
                 cache_dir: Optional[Path] = None,
                 cache_ttl: int = DEFAULT_TTL,
                 max_cache_size: int = DEFAULT_CACHE_SIZE):
        """
        Initialize models cache

        Args:
            api_key: OpenRouter API key — defaults to the central
                     `_integration.get_api_keys()` accessor when omitted.
            cache_dir: Directory for persistent cache files
            cache_ttl: Cache TTL in seconds (default: 24 hours)
            max_cache_size: Maximum cache size
        """
        if not api_key:
            from .._integration import get_api_keys
            api_key = get_api_keys()["openrouter"]
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size

        # Determine cache directory using builder
        from ..storage.dirs import get_models_cache_dir
        self.cache_dir = get_models_cache_dir(cache_dir)
        self.cache_file = self.cache_dir / self.CACHE_FILENAME

        # Memory cache
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)
        self.last_fetch_time: Optional[datetime] = None
        self.models: Dict[str, OpenRouterModel] = {}
        self._sync_fetch_done = False

        # Cache key for models list
        self.models_cache_key = "openrouter_models"

        # Load from file cache on initialization
        self._load_from_file()

    def _load_from_file(self) -> bool:
        """Load models from file cache"""
        try:
            if not self.cache_file.exists():
                return False

            with open(self.cache_file, encoding='utf-8') as f:
                data = json.load(f)

            # Check if cache is still valid
            fetch_time_str = data.get('fetch_time')
            if fetch_time_str:
                fetch_time = datetime.fromisoformat(fetch_time_str)
                if datetime.now() - fetch_time > timedelta(seconds=self.cache_ttl):
                    logger.debug("File cache expired")
                    return False

            # Parse models
            models_data = data.get('models', {})
            self.models = {}

            for model_id, model_data in models_data.items():
                try:
                    pricing = ModelPricing(
                        prompt_price=float(model_data['pricing'].get('prompt_price') or 0.0),
                        completion_price=float(model_data['pricing'].get('completion_price') or 0.0),
                        currency=model_data['pricing']['currency'],
                        image_price=model_data['pricing'].get('image_price', 0.0)
                    )

                    model_info = OpenRouterModel(
                        id=model_data['id'],
                        name=model_data['name'],
                        description=model_data.get('description'),
                        context_length=model_data['context_length'],
                        pricing=pricing,
                        provider=model_data['provider'],
                        tags=model_data.get('tags', []),
                        is_available=model_data.get('is_available', True),
                        input_modalities=model_data.get('input_modalities', []),
                        output_modalities=model_data.get('output_modalities', []),
                        max_completion_tokens=model_data.get('max_completion_tokens'),
                        is_moderated=model_data.get('is_moderated', False),
                        supported_parameters=model_data.get('supported_parameters', []),
                        is_embedding=model_data.get('is_embedding', False)
                    )

                    self.models[model_id] = model_info

                except Exception as e:
                    logger.warning(f"Failed to parse cached model {model_id}: {e}")
                    continue

            if fetch_time_str:
                self.last_fetch_time = datetime.fromisoformat(fetch_time_str)

            # Also update memory cache
            self.cache[self.models_cache_key] = {
                "models": self.models,
                "fetch_time": self.last_fetch_time
            }

            logger.info(f"Loaded {len(self.models)} models from file cache")
            return True

        except Exception as e:
            logger.warning(f"Failed to load models from file cache: {e}")
            return False

    def _save_to_file(self) -> bool:
        """Save models to file cache"""
        try:
            # Prepare data for serialization
            models_data = {}
            for model_id, model_info in self.models.items():
                models_data[model_id] = {
                    'id': model_info.id,
                    'name': model_info.name,
                    'description': model_info.description,
                    'context_length': model_info.context_length,
                    'pricing': {
                        'prompt_price': model_info.pricing.prompt_price,
                        'completion_price': model_info.pricing.completion_price,
                        'currency': model_info.pricing.currency,
                        'image_price': model_info.pricing.image_price
                    },
                    'provider': model_info.provider,
                    'tags': model_info.tags,
                    'is_available': model_info.is_available,
                    'input_modalities': model_info.input_modalities,
                    'output_modalities': model_info.output_modalities,
                    'max_completion_tokens': model_info.max_completion_tokens,
                    'is_moderated': model_info.is_moderated,
                    'supported_parameters': model_info.supported_parameters,
                    'is_embedding': model_info.is_embedding
                }

            data = {
                'models': models_data,
                'fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
                'cache_ttl': self.cache_ttl,
                'total_models': len(self.models)
            }

            # Write to file atomically
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            temp_file.replace(self.cache_file)
            logger.debug(f"Saved {len(self.models)} models to file cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save models to file cache: {e}")
            return False

    async def fetch_models(self, force_refresh: bool = False) -> Dict[str, OpenRouterModel]:
        """
        Fetch models from OpenRouter API

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> OpenRouterModel
        """
        # Check memory cache first
        if not force_refresh and self.models_cache_key in self.cache:
            logger.debug("Using cached models from memory")
            cached_data = self.cache[self.models_cache_key]
            self.models = cached_data["models"]
            self.last_fetch_time = cached_data["fetch_time"]
            return self.models

        # Check if we have models from file cache and they're still valid
        if not force_refresh and self.models and self.last_fetch_time:
            if datetime.now() - self.last_fetch_time < timedelta(seconds=self.cache_ttl):
                logger.debug("Using models from file cache")
                # Update memory cache
                self.cache[self.models_cache_key] = {
                    "models": self.models,
                    "fetch_time": self.last_fetch_time
                }
                return self.models

        logger.info("Fetching models from OpenRouter API")

        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Parse models
                    self.models = {}
                    for model_data in data.get("data", []):
                        model_info = self._parse_model_data(model_data)
                        if model_info:
                            self.models[model_info.id] = model_info

                    # Merge the dedicated embeddings catalogue. OpenRouter
                    # exposes embedding models on a SEPARATE endpoint that the
                    # chat `/models` list omits; without this the DB has no
                    # embedding prices and the gateway bills `DEFAULT_PRICING`.
                    await self._fetch_embedding_models(session)

                    # Update cache
                    self.last_fetch_time = datetime.now()
                    self.cache[self.models_cache_key] = {
                        "models": self.models,
                        "fetch_time": self.last_fetch_time
                    }

                    # Save to file
                    self._save_to_file()

                    logger.info(f"Fetched {len(self.models)} models from OpenRouter")
                    return self.models

        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch models: {e}")
            # Return cached models if available
            if self.models:
                logger.info(f"Using stale cached models ({len(self.models)} models)")
                return self.models
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching models: {e}")
            # Return cached models if available
            if self.models:
                logger.info(f"Using stale cached models ({len(self.models)} models)")
                return self.models
            raise

    async def _fetch_embedding_models(
        self, session: "aiohttp.ClientSession"
    ) -> None:
        """Merge OpenRouter's embeddings catalogue into ``self.models``.

        OpenRouter lists embedding models on a SEPARATE endpoint
        (``/api/v1/embeddings/models``) that the chat ``/models`` response
        does NOT include. Each entry has the same object shape (per-token
        string ``pricing.prompt``), so it reuses ``_parse_model_data`` with
        ``is_embedding=True``. The merged entry keeps OpenRouter's id (e.g.
        ``openai/text-embedding-3-small``), which is exactly the model_id the
        gateway charges on.

        Best-effort: any failure logs and leaves the chat models intact — an
        embeddings outage must never break the whole sync.
        """
        try:
            async with session.get(
                "https://openrouter.ai/api/v1/embeddings/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                data = await response.json()
        except Exception as e:  # noqa: BLE001 — embeddings are additive
            logger.warning(f"Failed to fetch embedding models: {e}")
            return

        added = 0
        for model_data in data.get("data", []):
            model_info = self._parse_model_data(model_data, is_embedding=True)
            if model_info:
                self.models[model_info.id] = model_info
                added += 1
        logger.info(f"Merged {added} embedding models from OpenRouter")

    def _ensure_models(self) -> None:
        """Lazily populate the catalogue on first real use.

        ``__init__`` already tried the on-disk cache; if that was cold,
        do one synchronous OpenRouter fetch. Attempted at most once per
        instance so a failed fetch never hammers the API.
        """
        if self.models or self._sync_fetch_done:
            return
        self._sync_fetch_done = True
        self._fetch_models_sync()

    def _fetch_models_sync(self) -> None:
        """Synchronous catalogue fetch — urllib, no event loop, callable
        from any context (sync view, async threadpool). Best-effort: a
        failure leaves models empty, so cost estimation returns 0.0 + a
        warning (there is no static fallback price table — the catalogue is
        the single source of truth).
        """
        if not self.api_key:
            return
        import urllib.request
        try:
            request = urllib.request.Request(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            models: Dict[str, OpenRouterModel] = {}
            for model_data in payload.get("data", []):
                model_info = self._parse_model_data(model_data)
                if model_info:
                    models[model_info.id] = model_info
            # Merge embedding catalogue (separate endpoint). Best-effort.
            try:
                emb_request = urllib.request.Request(
                    "https://openrouter.ai/api/v1/embeddings/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                with urllib.request.urlopen(emb_request, timeout=20) as emb_response:
                    emb_payload = json.loads(emb_response.read().decode("utf-8"))
                for model_data in emb_payload.get("data", []):
                    model_info = self._parse_model_data(model_data, is_embedding=True)
                    if model_info:
                        models[model_info.id] = model_info
            except Exception as e:  # noqa: BLE001 — embeddings are additive
                logger.warning("Sync embedding fetch failed: %s", e)
            if models:
                self.models = models
                self.last_fetch_time = datetime.now()
                self.cache[self.models_cache_key] = {
                    "models": self.models,
                    "fetch_time": self.last_fetch_time,
                }
                self._save_to_file()
                logger.info("Fetched %d models from OpenRouter (sync)", len(models))
        except Exception as e:
            logger.warning("Sync model fetch failed: %s", e)

    def _parse_model_data(
        self, model_data: Dict[str, Any], *, is_embedding: bool = False
    ) -> Optional[OpenRouterModel]:
        """Parse model data from an OpenRouter `/models` or
        `/embeddings/models` entry.

        Both endpoints share the same object shape (``id``, ``name``,
        ``pricing`` with per-token string prices, ``architecture``), so the
        embedding path reuses this parser. ``is_embedding`` marks rows that
        came from the embeddings endpoint; it is OR-ed with an
        ``"embedding"`` output modality so either signal flags the model.
        Embedding models have a prompt price but no completion price.
        """
        try:
            # Check required fields
            if not model_data.get("id") or not model_data.get("name"):
                return None

            # Extract pricing — OpenRouter sends per-token strings; store
            # per-1M-token floats so cost math never trips on a str.
            pricing_data = model_data.get("pricing", {})
            pricing = ModelPricing(
                prompt_price=_price_per_million(pricing_data.get("prompt")),
                completion_price=_price_per_million(pricing_data.get("completion")),
                currency=pricing_data.get("currency", "USD"),
                image_price=float(pricing_data.get("image", 0.0) or 0.0)
            )

            # Capabilities from architecture / top_provider blocks
            architecture = model_data.get("architecture", {})
            top_provider = model_data.get("top_provider", {})
            output_modalities = architecture.get("output_modalities", [])
            embedding = is_embedding or ("embedding" in output_modalities)

            # Create model info
            model_info = OpenRouterModel(
                id=model_data.get("id", ""),
                name=model_data.get("name", ""),
                description=model_data.get("description"),
                context_length=model_data.get("context_length", 0),
                pricing=pricing,
                provider=model_data.get("provider", ""),
                tags=model_data.get("tags", []),
                is_available=model_data.get("available", True),
                input_modalities=architecture.get("input_modalities", []),
                output_modalities=output_modalities,
                max_completion_tokens=top_provider.get("max_completion_tokens"),
                is_moderated=top_provider.get("is_moderated", False),
                supported_parameters=model_data.get("supported_parameters", []),
                is_embedding=embedding
            )

            return model_info

        except Exception as e:
            logger.warning(f"Failed to parse model data: {e}")
            return None

    async def fetch_endpoint_stats(self, slug: str) -> Optional[EndpointStats]:
        """Fetch per-model speed/health from OpenRouter's
        `/models/{slug}/endpoints` (latency/throughput/uptime percentiles, computed
        over real fleet traffic — far more representative than a self-probe, and
        free on the same key). Returns the BEST endpoint's figures (lowest p50
        latency), or None on any failure. Percentiles are only visible when
        authenticated, which we are.

        `slug` is the OpenRouter id WITHOUT any local prefix, e.g.
        "anthropic/claude-3.5-haiku" (strip a leading "openrouter/" first)."""
        slug = slug.removeprefix("openrouter/")
        url = f"https://openrouter.ai/api/v1/models/{slug}/endpoints"
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
        except Exception as e:  # noqa: BLE001 — best-effort signal
            logger.warning(f"Failed to fetch endpoint stats for {slug}: {e}")
            return None

        endpoints = (data.get("data") or {}).get("endpoints") or []
        if not endpoints:
            return None

        def _p50(ep: dict) -> float:
            lat = ep.get("latency_last_30m") or {}
            return float(lat.get("p50") or float("inf"))

        best = min(endpoints, key=_p50)
        lat = best.get("latency_last_30m") or {}
        tp = best.get("throughput_last_30m") or {}

        def _f(v: Any) -> Optional[float]:
            try:
                return float(v) if v is not None else None
            except (TypeError, ValueError):
                return None

        return EndpointStats(
            model_id=slug,
            latency_p50_ms=_f(lat.get("p50")),
            latency_p90_ms=_f(lat.get("p90")),
            throughput_tok_s=_f(tp.get("p50")),
            uptime_1d=_f(best.get("uptime_last_1d")),
        )

    def get_model(self, model_id: str) -> Optional[OpenRouterModel]:
        """Get model information by ID — lazily populates the catalogue."""
        self._ensure_models()
        return self.models.get(model_id)

    def get_models_by_provider(self, provider: str) -> List[OpenRouterModel]:
        """Get all models from a specific provider"""
        return [model for model in self.models.values() if model.provider == provider]

    def get_models_by_price_range(self,
                                 min_price: float = 0.0,
                                 max_price: float = float('inf'),
                                 price_type: str = "prompt") -> List[OpenRouterModel]:
        """
        Get models within a price range
        
        Args:
            min_price: Minimum price per 1M tokens
            max_price: Maximum price per 1M tokens
            price_type: "prompt" or "completion"
            
        Returns:
            List of models in price range
        """
        filtered_models = []

        for model in self.models.values():
            if not model.is_available:
                continue

            price = model.pricing.prompt_price if price_type == "prompt" else model.pricing.completion_price

            if min_price <= price <= max_price:
                filtered_models.append(model)

        # Sort by price
        filtered_models.sort(key=lambda m: m.pricing.prompt_price if price_type == "prompt" else m.pricing.completion_price)

        return filtered_models

    def get_free_models(self) -> List[OpenRouterModel]:
        """Get all free models (price = 0)"""
        return self.get_models_by_price_range(0.0, 0.0)

    def get_budget_models(self, max_price: float = 1.0) -> List[OpenRouterModel]:
        """Get budget models (price <= max_price)"""
        return self.get_models_by_price_range(0.0, max_price)

    def get_premium_models(self, min_price: float = 10.0) -> List[OpenRouterModel]:
        """Get premium models (price >= min_price)"""
        return self.get_models_by_price_range(min_price, float('inf'))

    def eligible_models(
        self,
        *,
        max_price_per_1m: float = float('inf'),
        require_tools: bool = False,
        require_vision: bool = False,
        text_chat_only: bool = True,
        available_only: bool = True,
    ) -> List[OpenRouterModel]:
        """The CENTRAL model-selection surface: live catalogue filtered by the
        policies every consumer needs (price cap, capability requirements, chat
        usability). Sorted cheapest-first. The gateway catalog ingest, the coding
        picker, and a future SDK all call THIS instead of re-deriving filters.

        - max_price_per_1m: drop "ugly-expensive" models above this $/1M ceiling.
        - require_tools / require_vision: keep only capable models.
        - text_chat_only: exclude image/audio/embedding-only entries.
        """
        out = [
            m
            for m in self.models.values()
            if (not available_only or m.is_available)
            and (not text_chat_only or m.is_text_chat)
            and (not require_tools or m.supports_tools)
            and (not require_vision or m.supports_vision)
            and m.max_price_per_1m <= max_price_per_1m
        ]
        out.sort(key=lambda m: m.pricing.prompt_price or 0.0)
        return out

    def embedding_models(self, *, available_only: bool = True) -> List[OpenRouterModel]:
        """All embedding models in the catalogue (from OpenRouter's
        ``/embeddings/models`` endpoint). These are excluded from
        ``eligible_models`` (which is text-chat-only) so the pricing-sync
        pulls them through THIS accessor to write embedding rows to the DB.
        Sorted cheapest-first by prompt price."""
        out = [
            m
            for m in self.models.values()
            if m.is_embedding and (not available_only or m.is_available)
        ]
        out.sort(key=lambda m: m.pricing.prompt_price or 0.0)
        return out

    def coding_models(
        self, *, max_price_per_1m: float = float('inf')
    ) -> List[OpenRouterModel]:
        """Tool-capable text-chat models under a price cap, cheapest-first — the
        ready coding/agent picker surface. Quality ranking (e.g. an Artificial
        Analysis coding index) is layered by the caller when available."""
        return self.eligible_models(
            max_price_per_1m=max_price_per_1m, require_tools=True
        )

    def search_models(self, query: str) -> List[OpenRouterModel]:
        """Search models by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for model in self.models.values():
            # Search in name
            if query_lower in model.name.lower():
                results.append(model)
                continue

            # Search in description
            if model.description and query_lower in model.description.lower():
                results.append(model)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in model.tags):
                results.append(model)
                continue

        return results

    def get_model_cost_estimate(self,
                               model_id: str,
                               input_tokens: int,
                               output_tokens: int) -> Optional[float]:
        """
        Estimate cost for a model
        
        Args:
            model_id: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        model = self.get_model(model_id)
        if not model:
            return None

        return model.pricing.cost(input_tokens, output_tokens)

    def calculate_cost_from_usage(self, model_id: str, usage: Dict[str, int]) -> Optional[float]:
        """
        Calculate cost from OpenAI usage object
        
        Args:
            model_id: Model ID
            usage: Usage dict with prompt_tokens, completion_tokens, total_tokens
            
        Returns:
            Calculated cost in USD
        """
        model = self.get_model(model_id)
        if not model:
            return None

        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)

        return model.pricing.cost(prompt_tokens, completion_tokens)

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            "cache_size": len(self.cache),
            "models_count": len(self.models),
            "last_fetch": self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            "cache_ttl": self.cache.ttl,
            "max_cache_size": self.cache.maxsize,
            "cache_file": str(self.cache_file),
            "cache_file_exists": self.cache_file.exists()
        }

    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.models.clear()
        self.last_fetch_time = None

        # Also remove file cache
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Removed file cache")
        except Exception as e:
            logger.warning(f"Failed to remove file cache: {e}")

        logger.info("Models cache cleared")

    def get_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models"""
        if not self.models:
            return {"error": "No models loaded"}

        # Count by provider
        provider_counts = {}
        for model in self.models.values():
            provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1

        # Price ranges
        prices = [model.pricing.prompt_price for model in self.models.values() if model.is_available]

        # Count free models (both prompt and completion prices are 0)
        free_models = [m for m in self.models.values()
                      if m.is_available and m.pricing.prompt_price == 0.0 and m.pricing.completion_price == 0.0]

        return {
            "total_models": len(self.models),
            "available_models": len([m for m in self.models.values() if m.is_available]),
            "providers": provider_counts,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            },
            "free_models_count": len(free_models),
            "budget_models_count": len(self.get_budget_models()),
            "premium_models_count": len(self.get_premium_models()),
            "last_updated": self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }

# Example usage
async def example_models_cache():
    """Example usage of ModelsCache"""
    import os

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Please set OPENROUTER_API_KEY environment variable")
        return

    # Initialize cache
    cache = ModelsCache(api_key=api_key, cache_ttl=86400)  # 24 hours

    try:
        # Fetch models
        models = await cache.fetch_models()
        print(f"Fetched {len(models)} models")

        # Get summary
        summary = cache.get_models_summary()
        print(f"Summary: {summary}")

        # Get free models
        free_models = cache.get_free_models()
        print(f"Free models: {len(free_models)}")
        for model in free_models[:5]:  # Show first 5
            print(f"  - {model.name} ({model.provider})")

        # Get budget models
        budget_models = cache.get_budget_models(max_price=0.5)
        print(f"Budget models (≤$0.5/1M tokens): {len(budget_models)}")

        # Search for coding models
        coding_models = cache.search_models("code")
        print(f"Coding models: {len(coding_models)}")
        for model in coding_models[:3]:
            print(f"  - {model.name}: ${model.pricing.prompt_price}/1M tokens")

        # Estimate cost
        model_id = "openai/gpt-4o-mini"
        cost = cache.get_model_cost_estimate(model_id, 1000, 500)
        print(f"Cost for {model_id} (1000 input + 500 output tokens): ${cost:.6f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(example_models_cache())
