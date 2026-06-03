"""
LLMRouter — universal multi-model retry client.

A high-level facade over `LLMClient` + `pipeline.ModelRouter`: it runs a
cascading model chain (primary → secondary → tertiary), one classified
attempt per model with its own circuit breaker, falling through on
failure. When every model is exhausted it raises `LLMRouterError`.

This is the convenience layer most callers want — `pipeline/` holds the
mechanism (retry, circuit breaker, cost), `llm_router` is the ergonomic
API on top.

Configuration (model chain, delays, attempt cap) is passed in by the
caller — this module reads no host/project config of its own.

Usage — structured output (Pydantic schema):

    router = LLMRouter(model_chain=["openai/gpt-4o-mini", "google/gemini-2.0-flash-lite"])
    result, model_used, usage = router.parse(
        schema=MySchema,
        messages=[{"role": "user", "content": "..."}],
    )

Usage — raw text completion:

    text, model_used = router.complete(
        messages=[{"role": "user", "content": "..."}],
        max_tokens=1024,
    )
"""

from __future__ import annotations

import asyncio
import logging
from typing import TypeVar

from pydantic import BaseModel

from ..client.client import LLMClient
from ..providers import LLMProvider
from ..pipeline import ModelRouter, alert_wasted_call
from ..core import AllProvidersFailedError
from ..core.errors import LLMTruncationError, LLMValidationError
from ..catalog import ModelRole, check, recommend
from ..structured import parse_into_schema

logger = logging.getLogger("django_cfg.django_llm.router")

T = TypeVar("T", bound=BaseModel)

# Defaults — callers may override every one via the constructor.
DEFAULT_MAX_TOTAL_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 1.0


class LLMRouterError(Exception):
    """All models in the chain failed."""

    def __init__(self, message: str, attempts: list[dict]) -> None:
        self.attempts = attempts  # [{"model": ..., "error": ...}, ...]
        super().__init__(message)


def _attempts_from_error(exc: AllProvidersFailedError) -> list[dict]:
    """Flatten ModelRouter's per-model attempt records into the public shape."""
    attempts: list[dict] = []
    for record in exc.attempts:
        error = record.get("error")
        if error is None:
            detail = record.get("reason") or "skipped"
        else:
            detail = str(getattr(error, "message", None) or error)
        attempts.append({"model": record.get("model"), "error": detail})
    return attempts


def _raise_router_error(exc: AllProvidersFailedError) -> LLMRouterError:
    """Convert ModelRouter's AllProvidersFailedError to the public LLMRouterError."""
    attempts = _attempts_from_error(exc)
    return LLMRouterError(
        f"All LLM models failed after {len(attempts)} attempt(s): "
        + "; ".join(f"{a['model']}: {a['error']}" for a in attempts),
        attempts=attempts,
    )


class LLMRouter:
    """
    Cascading multi-model LLM client backed by `LLMClient`.

    The model cascade is delegated to `pipeline.ModelRouter`: each model in
    the chain gets its own circuit breaker and one classified attempt; on
    failure the router falls through to the next model. The chain length
    (capped at ``max_total_attempts``) bounds the total work.

    Args:
        model_chain: Ordered list of model ids to try, primary first.
        max_total_attempts: Hard cap on chain length — the chain is sliced
            to this many models so total work stays bounded.
        retry_delay_seconds: Base delay for any within-model retry. Unused
            at the default ``max_attempts=1``, kept for future cadence.
        preferred_provider: Provider the underlying LLMClient prefers.
    """

    def __init__(
        self,
        model_chain: list[str],
        *,
        max_total_attempts: int = DEFAULT_MAX_TOTAL_ATTEMPTS,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        preferred_provider: LLMProvider = LLMProvider.OPENROUTER,
    ) -> None:
        if not model_chain:
            raise ValueError("LLMRouter requires a non-empty model_chain")
        self._chain = list(model_chain)
        self._max_total_attempts = max_total_attempts
        self._retry_delay = retry_delay_seconds
        self._client = LLMClient(preferred_provider=preferred_provider)

    # ── Construction by role ────────────────────────────────────────────────────

    @classmethod
    def for_role(
        cls,
        role: ModelRole,
        *,
        max_total_attempts: int = DEFAULT_MAX_TOTAL_ATTEMPTS,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        preferred_provider: LLMProvider = LLMProvider.OPENROUTER,
        extra_models: list[str] | None = None,
    ) -> "LLMRouter":
        """Build a router from the catalog's recommended chain for ``role``.

        The chain comes from ``catalog.recommend(role)`` — the curated,
        cross-provider primary→fallback order for that job — so callers pick a
        *task*, not a model. ``extra_models`` are appended to the end as
        last-resort fallbacks (deduped, order preserved).

        Raises ``ValueError`` if the role has no curated recommendation and no
        ``extra_models`` were supplied — never silently invents a model.
        """
        chain = recommend(role)
        if extra_models:
            seen = set(chain)
            chain = [*chain, *(m for m in extra_models if not (m in seen or seen.add(m)))]
        if not chain:
            raise ValueError(
                f"No recommended models for role {role.value!r}; pass extra_models=[...] "
                f"to choose explicitly."
            )
        return cls(
            chain,
            max_total_attempts=max_total_attempts,
            retry_delay_seconds=retry_delay_seconds,
            preferred_provider=preferred_provider,
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def parse(
        self,
        schema: type[T],
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> tuple[T, str, dict]:
        """
        Structured output: parse LLM response into a Pydantic model.

        Returns:
            (parsed_instance, model_id_used, usage_dict)
            usage_dict keys: "tokens" (int), "cost_usd" (float)

        Raises:
            LLMRouterError: all attempts failed.
        """
        # Advisory (best-effort, deduped, never blocks) — flag any chain
        # model the catalog grades a poor fit for structured extraction.
        for chain_model in self._chain[: self._max_total_attempts]:
            check(chain_model, role=ModelRole.EXTRACTION, response_format=schema)

        full_messages = self._build_messages(messages, system)

        def call(model: str) -> tuple[T, str, dict]:
            # Per-model validate-and-repair ladder (one bounded recovery each):
            #   strict json_schema → parse_into_schema (json-repair on syntax)
            #     finish_reason==length → bump max_tokens, ONE retry
            #     validation failure    → ONE bounded re-ask with the error
            # Any remaining failure propagates so ModelRouter cascades to the
            # next model. Each attempt is billed → wasted spend is surfaced.
            attempt_messages = list(full_messages)
            attempt_max_tokens = max_tokens
            did_bump = False
            did_reask = False

            while True:
                resp = None
                try:
                    # Pass the Pydantic schema itself: django_llm renders it as a
                    # strict json_schema block and (on OpenRouter) sets
                    # provider.require_parameters, so the provider enforces the
                    # schema during generation. parse_into_schema is the backstop
                    # for any provider that falls through to plain json_object.
                    resp = self._client.chat_completion(
                        messages=attempt_messages,
                        model=model,
                        max_tokens=attempt_max_tokens,
                        response_format=schema,
                    )
                    result = parse_into_schema(
                        resp.content, schema, finish_reason=resp.finish_reason
                    )
                    usage_dict = {"tokens": resp.tokens_used, "cost_usd": resp.cost_usd}
                    logger.debug(
                        "LLMRouter.parse: success model=%s tokens=%d cost=$%.6f%s%s",
                        model, resp.tokens_used, resp.cost_usd,
                        " (after max_tokens bump)" if did_bump else "",
                        " (after re-ask)" if did_reask else "",
                    )
                    return result, model, usage_dict

                except LLMTruncationError as exc:
                    # Output cut off — bump max_tokens once and retry (do NOT
                    # repair a truncation; the data is genuinely missing).
                    if resp is not None:
                        alert_wasted_call(
                            model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                        )
                    if did_bump:
                        logger.warning(
                            "LLMRouter.parse: model=%s truncated again after bump", model
                        )
                        raise
                    did_bump = True
                    attempt_max_tokens = min(attempt_max_tokens * 2, 32768)
                    logger.info(
                        "LLMRouter.parse: model=%s truncated; bumping max_tokens → %d",
                        model, attempt_max_tokens,
                    )
                    continue

                except LLMValidationError as exc:
                    # Parsed but wrong shape — one bounded re-ask with the
                    # validation error injected so the model self-corrects.
                    if resp is not None:
                        alert_wasted_call(
                            model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                        )
                    if did_reask:
                        logger.warning(
                            "LLMRouter.parse: model=%s still invalid after re-ask", model
                        )
                        raise
                    did_reask = True
                    attempt_messages = [
                        *attempt_messages,
                        {"role": "assistant", "content": resp.content if resp else ""},
                        {
                            "role": "user",
                            "content": (
                                "Your previous response did not match the required "
                                f"schema. Error: {exc}. Return ONLY corrected JSON "
                                "that satisfies the schema — no prose, no fences."
                            ),
                        },
                    ]
                    logger.info("LLMRouter.parse: model=%s re-asking after validation error", model)
                    continue

                except Exception as exc:
                    logger.warning("LLMRouter.parse: model=%s failed: %s", model, exc)
                    if resp is not None:
                        alert_wasted_call(
                            model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                        )
                    raise

        try:
            return self._router().run(call)
        except AllProvidersFailedError as exc:
            raise _raise_router_error(exc) from exc

    def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> tuple[str, str]:
        """
        Raw text completion.

        Returns:
            (text_content, model_id_used)

        Raises:
            LLMRouterError: all attempts failed.
        """
        full_messages = self._build_messages(messages, system)

        def call(model: str) -> tuple[str, str]:
            resp = self._client.chat_completion(
                messages=full_messages,
                model=model,
                max_tokens=max_tokens,
            )
            logger.debug("LLMRouter.complete: success model=%s", model)
            return resp.content, model

        try:
            return self._router().run(call)
        except AllProvidersFailedError as exc:
            raise _raise_router_error(exc) from exc

    # ── Async twins ─────────────────────────────────────────────────────────────
    #
    # Deliberately thin: the sync cascade + validate-and-repair ladder are run in
    # a worker thread via asyncio.to_thread. The GIL is released during the
    # network wait, so this gives real concurrency (and a freed event loop) with
    # ZERO duplicated cascade/ladder logic — there is exactly one of each.

    async def aparse(
        self,
        schema: type[T],
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> tuple[T, str, dict]:
        """Async ``parse`` — awaits the sync cascade on a worker thread."""
        return await asyncio.to_thread(
            self.parse, schema, messages, system, max_tokens
        )

    async def acomplete(
        self,
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> tuple[str, str]:
        """Async ``complete`` — awaits the sync cascade on a worker thread."""
        return await asyncio.to_thread(
            self.complete, messages, system, max_tokens
        )

    # ── Internals ──────────────────────────────────────────────────────────────

    def _router(self) -> ModelRouter:
        """A fresh ModelRouter over the chain — one attempt per model, then cascade.

        The chain is capped at ``max_total_attempts`` so total work stays
        bounded even if a longer chain is supplied. ``base_delay`` maps to
        the configured retry cadence (unused at max_attempts=1, but kept so
        any future within-model retry honours it).
        """
        return ModelRouter(
            self._chain[: self._max_total_attempts],
            max_attempts=1,
            base_delay=self._retry_delay,
        )

    @staticmethod
    def _build_messages(messages: list[dict], system: str | None) -> list[dict]:
        if system:
            return [{"role": "system", "content": system}, *messages]
        return messages
