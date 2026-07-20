"""Turn a use-case into a ready pydantic-ai ``Model`` with a fallback chain.

The agent plane needs a ``pydantic_ai.models.Model`` — the transport library
(`django_cfg.modules.django_llm` root) returns ``(text, model_id)`` and runs no tool loop, so
the two layers stay separate and this is the seam between them. This module owns the
*machinery*: reading the provider/key/endpoint from `django_cfg.modules.django_llm`, building an
``OpenAIChatModel`` per slug, and wrapping them in a ``FallbackModel`` with the
right fall-over predicate.

It owns none of the *policy*. Which slug is primary and which are fallbacks for a
given use case is the host's — a CRM tier map, a django-cfg default, whatever — and
arrives through the `AgentConfig` seam (`agent/protocols.py`). A per-run override
(one project pinning its own model) arrives the same way, as an optional pair the
caller resolves before calling in.

## Why the fall-over predicate is not the library default

``FallbackModel`` defaults to ``fallback_on=(ModelAPIError,)`` — a 5xx or a timeout.
But a 200 whose body is not the JSON the SDK expects is raised as
``UnexpectedModelBehavior``, a **sibling** of ``ModelAPIError`` under
``AgentRunError``, not a child. So a naive fallback chain never fires for it: the
provider hands back a garbage body, the run dies, and the fallback model sits idle.

That single gap once made an e2e suite unmeasurable — failure counts tracked
provider errors nearly 1:1, and a good change looked like a regression because its
run simply drew more bad bodies. A run is only worth reading when the transport is
not the variable.

``UnexpectedModelBehavior`` is too broad to retry wholesale: it is also the parent
of ``ContentFilterError`` (the model *refused* — a real signal) and
``IncompleteToolCall`` (a real bug in the tool surface). Falling over on those would
paper over the exact failures a suite exists to catch. So the predicate matches the
malformed-body case and nothing else.
"""

from __future__ import annotations

import logging

from pydantic_ai.exceptions import ModelAPIError, UnexpectedModelBehavior
from pydantic_ai.models import Model
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)


def is_malformed_response(exc: Exception) -> bool:
    """Should this failure fall over to the next model in the chain?

    True for upstream API errors (the library default) AND for the one
    ``UnexpectedModelBehavior`` shape that means "provider returned a garbage body"
    — matched narrowly, by exact type + message, so a refusal or a tool-call bug
    stays as loud as it was. See the module docstring for the full rationale.
    """
    if isinstance(exc, ModelAPIError):
        return True  # upstream's default: 5xx, timeouts, connection resets
    return (
        type(exc) is UnexpectedModelBehavior  # exactly this — not its subclasses
        and "Invalid response from" in str(exc)
    )


def resolve_provider() -> tuple[str, str, str | None]:
    """Return ``(provider_name, api_key, base_url)`` from ``django_cfg.modules.django_llm``.

    Preference order matches ``ProviderManager._determine_primary_provider``:
    OpenRouter first (it fronts every model most tier configs name), then OpenAI,
    then gonka.

    ``base_url`` is ``None`` only for stock OpenAI, where the SDK's own default is
    correct. It must NOT fall back to ``None`` when the OpenRouter key is missing
    while still sending the OpenRouter key — that silently points OpenRouter slugs
    at ``api.openai.com``.
    """
    # Import the transport from THIS package's own root, not through a host shim.
    # `django_cfg.modules.django_llm` was cmdop's sandbox/djangocfg switch — a host module that
    # does not exist in django-cfg, so reaching for it broke the harness there. The
    # transport root (`django_cfg.modules.django_llm` → `django_cfg.django_cfg.modules.django_llm` under the
    # sync's rewrite) is the portable path, and both symbols are on its public surface.
    from django_cfg.modules.django_llm import get_api_keys, PROVIDER_BASE_URLS

    keys = get_api_keys()
    urls = PROVIDER_BASE_URLS

    for name in ("openrouter", "openai", "gonkagate"):
        key = keys.get(name)
        if key:
            base_url = None if name == "openai" else urls[name]
            return name, str(key), base_url

    logger.error(
        "[model_builder] no LLM provider key found — checked %s via "
        "django_cfg.modules.django_llm.get_api_keys(). The agent will fail on first call.",
        ", ".join(urls),
    )
    return "openrouter", "api-key-not-set", urls["openrouter"]


def build_chat_model(model_name: str) -> OpenAIChatModel:
    """Build one chat model on whichever provider ``django_cfg.modules.django_llm`` resolves."""
    _, api_key, base_url = resolve_provider()
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    return OpenAIChatModel(model_name, provider=provider)


def parse_fallbacks(raw: str) -> tuple[str, ...]:
    """Parse a comma-/semicolon-/whitespace-separated list of model slugs.

    Blank → empty tuple (the caller falls back to the config's own chain).
    """
    if not raw:
        return ()
    parts = [p.strip() for p in raw.replace(";", ",").split(",")]
    return tuple(p for p in parts if p)


def build_fallback_model(primary_name: str, fallback_names: tuple[str, ...]) -> Model:
    """Compose a ``FallbackModel`` (or a plain model if nothing distinct follows).

    The fallback chain retries the next slug on an upstream API error AND on a
    malformed response body — see ``is_malformed_response`` for why the latter must
    be said explicitly.
    """
    primary = build_chat_model(primary_name)
    fallbacks = tuple(
        build_chat_model(name)
        for name in fallback_names
        if name and name != primary_name
    )
    if not fallbacks:
        return primary
    return FallbackModel(primary, *fallbacks, fallback_on=is_malformed_response)


def resolve_model(
    config,
    use_case: str,
    *,
    primary_override: str | None = None,
    fallbacks_override: tuple[str, ...] = (),
) -> Model:
    """Resolve a use-case to a ``Model``, letting a host override the slugs.

    Args:
        config: satisfies `AgentConfig` — ``resolve_primary(use_case)`` and
            ``resolve_fallbacks(use_case)`` supply the host's tier defaults.
        use_case: the key the config maps (e.g. ``"admin_chat"``).
        primary_override: a per-run primary that wins over the tier default —
            e.g. a single project pinning its own model. Blank/None → use the config.
        fallbacks_override: per-run fallbacks that win over the tier chain. Empty →
            use the config.

    An override wins so an operator tuning one project need not know about tiers.
    """
    primary_name = primary_override or config.resolve_primary(use_case)
    fallback_names = tuple(fallbacks_override) or tuple(config.resolve_fallbacks(use_case))
    return build_fallback_model(primary_name, fallback_names)
