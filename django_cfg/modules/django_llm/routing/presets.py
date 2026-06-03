"""Task presets — call an LLM by *job*, not by model.

These are thin, ergonomic wrappers over ``LLMRouter.for_role(...)``. Each
preset picks the curated model chain for its role from the catalog
(``catalog.recommend``), so callers never pass a model slug and never repeat
the cascade/structured-output wiring:

    from django_cfg.modules.django_llm import extract, classify, chat_with_tools, escalate

    car, model, usage = extract(CarListing, "2021 Hyundai Grandeur, 41k km, ...")
    label, model = classify(Sentiment, "the dealer never called back")

``extract`` / ``classify`` return ``(parsed_pydantic, model_used, usage)`` via
the strict-json_schema path (the provider enforces the schema during
generation). ``chat_with_tools`` / ``escalate`` / ``complete_text`` return raw
text. Every preset cascades primary→fallback and raises ``LLMRouterError`` only
when the whole chain is exhausted.

Override the model choice when you must: pass ``models=[...]`` to use an
explicit chain instead of the role default, or ``extra_models=[...]`` to append
last-resort fallbacks after the curated chain.
"""

from __future__ import annotations

import asyncio
import functools
from typing import Sequence, TypeVar

from pydantic import BaseModel

from ..catalog import ModelRole
from .llm_router import LLMRouter

T = TypeVar("T", bound=BaseModel)


def _router(role: ModelRole, models: list[str] | None, extra_models: list[str] | None) -> LLMRouter:
    """A router for ``role`` — explicit ``models`` win over the role default."""
    if models:
        return LLMRouter(models)
    return LLMRouter.for_role(role, extra_models=extra_models)


def extract(
    schema: type[T],
    text: str,
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Structured extraction: pull ``schema`` out of ``text`` (EXTRACTION role).

    Returns ``(parsed_instance, model_id_used, usage_dict)``. Uses the strict
    json_schema path so the provider enforces the schema during generation.
    """
    return _router(ModelRole.EXTRACTION, models, extra_models).parse(
        schema=schema,
        messages=[{"role": "user", "content": text}],
        system=system,
        max_tokens=max_tokens,
    )


def classify(
    schema: type[T],
    text: str,
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Cheap structured classification of ``text`` into ``schema`` (CLASSIFY role).

    Same return shape as ``extract``. Use a small enum/Literal schema (e.g. a
    single ``label`` field) — the role is tuned for the cheapest reliable
    strict-json models, with a tighter ``max_tokens`` default.
    """
    return _router(ModelRole.CLASSIFY, models, extra_models).parse(
        schema=schema,
        messages=[{"role": "user", "content": text}],
        system=system,
        max_tokens=max_tokens,
    )


def chat_with_tools(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[str, str]:
    """Agentic chat tuned for multi-tool chains (TOOL_CHAT role).

    Returns ``(text_content, model_id_used)``. The role chain favours the
    Flash-class models that clear multi-tool chains; pass tool definitions and
    handle tool calls in your own loop on top of this.
    """
    return _router(ModelRole.TOOL_CHAT, models, extra_models).complete(
        messages=messages,
        system=system,
        max_tokens=max_tokens,
    )


def escalate(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[str, str]:
    """Quality-over-cost completion for hard / customer-facing turns (ESCALATION role).

    Returns ``(text_content, model_id_used)``. Reserve for the cases a cheap
    model got wrong — this role maps to premium models.
    """
    return _router(ModelRole.ESCALATION, models, extra_models).complete(
        messages=messages,
        system=system,
        max_tokens=max_tokens,
    )


def extract_chat(
    schema: type[T],
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Like ``extract`` but takes a full ``messages`` list instead of one string.

    For multi-turn or role-tagged inputs where a single ``text`` won't do.
    """
    return _router(ModelRole.EXTRACTION, models, extra_models).parse(
        schema=schema,
        messages=messages,
        system=system,
        max_tokens=max_tokens,
    )


# ── Async twins ──────────────────────────────────────────────────────────────
#
# Each async preset just awaits its sync counterpart on a worker thread
# (asyncio.to_thread). The GIL is released during the network wait, so this is
# real concurrency with ZERO duplicated logic — the sync cascade + repair ladder
# are the single source of truth. Use from adrf async views, or as the unit of
# work in the fan-out helpers below.


async def aextract(
    schema: type[T],
    text: str,
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Async ``extract`` — awaits the sync preset on a worker thread."""
    return await asyncio.to_thread(
        extract, schema, text,
        system=system, max_tokens=max_tokens, models=models, extra_models=extra_models,
    )


async def aextract_chat(
    schema: type[T],
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Async ``extract_chat``."""
    return await asyncio.to_thread(
        extract_chat, schema, messages,
        system=system, max_tokens=max_tokens, models=models, extra_models=extra_models,
    )


async def aclassify(
    schema: type[T],
    text: str,
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[T, str, dict]:
    """Async ``classify``."""
    return await asyncio.to_thread(
        classify, schema, text,
        system=system, max_tokens=max_tokens, models=models, extra_models=extra_models,
    )


async def achat_with_tools(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[str, str]:
    """Async ``chat_with_tools``."""
    return await asyncio.to_thread(
        chat_with_tools, messages,
        system=system, max_tokens=max_tokens, models=models, extra_models=extra_models,
    )


async def aescalate(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
) -> tuple[str, str]:
    """Async ``escalate``."""
    return await asyncio.to_thread(
        escalate, messages,
        system=system, max_tokens=max_tokens, models=models, extra_models=extra_models,
    )


# ── Fan-out ──────────────────────────────────────────────────────────────────


async def extract_many(
    schema: type[T],
    texts: Sequence[str],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
    max_at_once: int = 8,
    max_per_second: float | None = None,
) -> list[tuple[T, str, dict]]:
    """Extract ``schema`` from many ``texts`` concurrently (the headline async win).

    Runs each text through ``aextract`` with bounded concurrency via aiometer:
    ``max_at_once`` caps simultaneous in-flight calls; ``max_per_second`` (optional)
    caps the spawn rate to respect provider RPM limits. Results are returned in
    input order.

    A per-item failure raises out of ``extract_many`` (aiometer propagates the
    first exception and cancels the rest). Wrap a per-item try in your own
    coroutine and pass it instead if you need partial results — this preset
    keeps the simple all-or-nothing contract.
    """
    import aiometer  # local import: only the fan-out helpers need it

    async def _one(text: str) -> tuple[T, str, dict]:
        return await aextract(
            schema, text, system=system, max_tokens=max_tokens,
            models=models, extra_models=extra_models,
        )

    return await aiometer.run_all(
        [functools.partial(_one, t) for t in texts],
        max_at_once=max_at_once,
        max_per_second=max_per_second,
    )


async def classify_many(
    schema: type[T],
    texts: Sequence[str],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    models: list[str] | None = None,
    extra_models: list[str] | None = None,
    max_at_once: int = 8,
    max_per_second: float | None = None,
) -> list[tuple[T, str, dict]]:
    """Classify many ``texts`` concurrently — fan-out twin of ``classify``."""
    import aiometer

    async def _one(text: str) -> tuple[T, str, dict]:
        return await aclassify(
            schema, text, system=system, max_tokens=max_tokens,
            models=models, extra_models=extra_models,
        )

    return await aiometer.run_all(
        [functools.partial(_one, t) for t in texts],
        max_at_once=max_at_once,
        max_per_second=max_per_second,
    )


__all__ = [
    "extract",
    "extract_chat",
    "classify",
    "chat_with_tools",
    "escalate",
    # async twins
    "aextract",
    "aextract_chat",
    "aclassify",
    "achat_with_tools",
    "aescalate",
    # fan-out
    "extract_many",
    "classify_many",
]
