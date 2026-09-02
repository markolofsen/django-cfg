"""
LLMRouter — universal multi-model retry client.

A high-level facade over `LLMClient` + `pipeline.ModelRouter`: it runs a
cascading model chain (primary → secondary → tertiary), one classified
attempt per model with its own circuit breaker, falling through on
failure. When every model is exhausted it raises `LLMRouterError`.

This is the convenience layer most callers want — `pipeline/` holds the
mechanism (retry, circuit breaker, cost), `llm_router` is the ergonomic
API on top.

Providers are NOT a caller concern. Which provider serves a model is an
intrinsic property OF THE MODEL, and `catalog.provider_for` is the single
source of that truth; the router resolves it per model as it walks the chain.
So a chain may freely mix providers — which is exactly what
`catalog.recommend()` builds, on purpose, so one vendor's outage cannot stall a
whole role — and every leg still lands on the provider that actually serves it.
Racing follows the same rule (`catalog.races`).

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
import concurrent.futures as _futures
import logging
import time
from typing import Callable, TypeVar

from pydantic import BaseModel

from ..client.client import LLMClient
from ..providers import LLMProvider, min_max_tokens_for
from ..pipeline import ModelRouter, alert_wasted_call
from ..core import AllProvidersFailedError
from ..core.errors import LLMTruncationError, LLMValidationError
from ..catalog import ModelRole, check, provider_for, recommend
from ..structured import parse_into_schema

logger = logging.getLogger("modules.django_llm.routing.router")

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

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

    The provider each model runs on is NOT a router-level setting — it is an
    intrinsic property of the MODEL, and the catalog owns it
    (``catalog.provider_for``). The router resolves it per model as it walks the
    chain, so a genuinely cross-provider chain — which is what
    ``catalog.recommend()`` deliberately builds, precisely so one vendor outage
    cannot stall a whole role — reaches each leg on the provider that actually
    serves it. Racing is derived the same way (``catalog.races``): gonka models
    are raced because gonka's random-host assignment gives an 11–57s latency
    tail; openrouter models are not, because racing them would just double the
    bill.

    Args:
        model_chain: Ordered list of model ids to try, primary first.
        max_total_attempts: Hard cap on chain length — the chain is sliced
            to this many models so total work stays bounded.
        retry_delay_seconds: Base delay for any within-model retry. Unused
            at the default ``max_attempts=1``, kept for future cadence.
        preferred_provider: DEPRECATED. Pin EVERY model in the chain to this one
            provider, overriding the catalog. It used to default to GONKA, which
            silently sent openrouter-only models (claude, gpt-4o-mini, gemini) to
            gonka — a provider that has never heard of them. It now defaults to
            ``None`` = "derive from the model", which is the only correct answer
            for a cross-provider chain. Kept solely so existing callers keep
            working; pass it only for a deliberate, documented override (e.g. a
            model too new to be catalogued). New code should not pass it at all.
        race_size: DEPRECATED as a blanket setting — derived per model from
            one leg when left ``None`` — racing went with gonka. An explicit value
            overrides that for every model in the chain.
    """

    def __init__(
        self,
        model_chain: list[str],
        *,
        max_total_attempts: int = DEFAULT_MAX_TOTAL_ATTEMPTS,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        preferred_provider: LLMProvider | str | None = None,
        race_size: int | None = None,
        race_rounds: int = 2,
        race_stagger_seconds: float = 0.2,
    ) -> None:
        if not model_chain:
            raise ValueError("LLMRouter requires a non-empty model_chain")
        self._chain = list(model_chain)
        # Set once the proxy refuses our credential; see provider_for_model.
        self._sdkrouter_rejected = False
        self._max_total_attempts = max_total_attempts
        self._retry_delay = retry_delay_seconds

        # The explicit override, normalized to a provider VALUE string
        # ("openrouter" / "openai" / "gonkagate"), or None = derive per model.
        if isinstance(preferred_provider, LLMProvider):
            self._provider_override: str | None = preferred_provider.value
        elif preferred_provider:
            self._provider_override = str(preferred_provider)
        else:
            self._provider_override = None

        # ONE client, all providers. The provider is chosen per CALL
        # (LLMClient.chat_completion(provider=...)), not baked into the client —
        # so a cross-provider chain needs exactly one client, and two concurrent
        # race legs can target different providers without mutating shared state.
        # preferred_provider is still handed over so it decides the client's
        # PRIMARY (i.e. the fallback when a model's provider has no key).
        self._client = LLMClient(preferred_provider=self._provider_override)

        # None = derive per model (gonka races, others don't). An explicit value
        # pins every model in the chain — kept for callers that must force it.
        self._race_size_override = max(1, race_size) if race_size is not None else None
        self._race_rounds = max(1, race_rounds)
        self._race_stagger = max(0.0, race_stagger_seconds)

    # ── Per-model resolution — the catalog is the source of truth ───────────────

    def provider_for_model(self, model: str) -> str:
        """Which TRANSPORT serves ``model``: explicit override, else edge, else catalog.

        THE EDGE PROXY SHORT-CIRCUITS THE CATALOG, and it has to. Everywhere
        else a provider is an intrinsic property of the model — the docstring at
        the top of this module says so and it is still true of VENDORS. The edge
        proxy is not a vendor: it fronts the same upstreams under the same
        slugs, so asking "which vendor serves gpt-4o-mini" is the wrong
        question when the answer is "we no longer talk to vendors directly".

        Without this the migration would silently not happen. `_determine_
        primary_provider` only picks the client used when a model's own provider
        has no key, but the router names a provider PER CALL — so every call
        would resolve to "openrouter" and go direct, while the edge client sat
        initialised and unused.

        A chain may still mix providers when the edge is not configured; that
        path is unchanged.

        **The proxy drops out if it rejects our credential.** "Configured"
        used to mean "a token exists", which is not the same as "the token
        works": on 2026-09-02 production held a token belonging to a different
        service, so every model resolved to the proxy, every call came back
        `401 invalid cmdop token`, and ingestion failed wholesale — with valid
        OpenRouter and OpenAI keys sitting right there, unused. A transport
        that cannot authenticate is not a transport.
        """
        if self._provider_override:
            return self._provider_override
        if not self._sdkrouter_rejected and self._client.provider_manager.has_provider(
            LLMProvider.SDKROUTER.value
        ):
            return LLMProvider.SDKROUTER.value
        return provider_for(model)

    def note_provider_failure(self, provider: str, exc: BaseException) -> None:
        """Retire the proxy for this router once it refuses our credential.

        Scoped to auth failures (401/403) on purpose. A 5xx or a timeout is the
        proxy having a bad minute and the normal cascade handles it; a rejected
        credential will be rejected identically on every subsequent call, so
        continuing to route through it turns one bad secret into a total
        outage rather than a degraded one.
        """
        if provider != LLMProvider.SDKROUTER.value or self._sdkrouter_rejected:
            return
        status = getattr(exc, "status_code", None)
        if status is None:
            # openai.APIStatusError carries it on .response; fall back to the
            # message, which is what a wrapped error leaves us.
            status = getattr(getattr(exc, "response", None), "status_code", None)
        text = str(exc)
        if status in (401, 403) or "401" in text or "403" in text:
            self._sdkrouter_rejected = True
            logger.warning(
                "sdkrouter rejected our credential (%s) — falling back to the "
                "vendors the catalogue names for each model",
                status or "auth error",
            )

    def race_size_for_model(self, model: str) -> int:
        """How many parallel legs to run for ``model``.

        Derived from the MODEL (gonka's latency tail is a gonka fact, not a
        call-site fact), unless a ``race_size`` override was passed. When a
        provider override IS in force the racing decision follows THAT provider,
        not the model's catalogued one — otherwise pinning a chain to gonka
        would leave it un-raced.
        """
        if self._race_size_override is not None:
            return self._race_size_override
        # ONE LEG unless a caller asks otherwise. Racing existed for gonka's
        # 8-55s random-host tail; that network went on 2026-08-15 and every
        # remaining provider serves from a single endpoint, where a second leg
        # buys nothing and pays for two prompts.
        return 1

    # ── Construction by role ────────────────────────────────────────────────────

    @classmethod
    def for_role(
        cls,
        role: ModelRole,
        *,
        max_total_attempts: int = DEFAULT_MAX_TOTAL_ATTEMPTS,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        preferred_provider: LLMProvider | str | None = None,
        extra_models: list[str] | None = None,
    ) -> "LLMRouter":
        """Build a router from the catalog's recommended chain for ``role``.

        The chain comes from ``catalog.recommend(role)`` — the curated,
        cross-provider primary→fallback order for that job — so callers pick a
        *task*, not a model, and never a provider: each model's provider is
        resolved from the catalog as the chain is walked. ``extra_models`` are
        appended to the end as last-resort fallbacks (deduped, order preserved).

        ``preferred_provider`` is a DEPRECATED override — see ``__init__``.

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

    # ── Execution: cascade, racing per model ────────────────────────────────────

    def _run(self, call: "Callable[[str], R]") -> "R":
        """Execute ``call`` over the chain, one model at a time.

        The cascade itself (per-model circuit breaker, fall through on failure)
        belongs to ``pipeline.ModelRouter``. All this layer adds is that a model
        whose provider warrants it (``race_size_for_model`` >= 2 — i.e. gonka) is
        RACED across parallel legs before it is declared failed. Racing is thus a
        per-MODEL decision made as the chain is walked, not a chain-wide flag: a
        chain of [claude (openrouter), kimi (gonka)] runs claude once and, only if
        it fails, races kimi.

        A model whose race is fully exhausted has simply failed — ModelRouter then
        cascades to the next model, exactly as for a non-raced failure.
        """
        return self._router().run(lambda model: self._attempt(call, model))

    def _attempt(self, call: "Callable[[str], R]", model: str) -> "R":
        """One model's turn: race it if its provider warrants it, else call once.

        A failure is reported to `note_provider_failure` before it propagates,
        so a proxy that rejects our credential is retired for the rest of this
        router rather than being re-tried for every remaining model in the
        chain. The provider is resolved BEFORE the call: afterwards the flag
        may already have flipped and we would attribute the failure to whoever
        comes next.
        """
        provider = self.provider_for_model(model)
        try:
            race_size = self.race_size_for_model(model)
            if race_size >= 2:
                return self._race(call, model, race_size)
            return call(model)
        except Exception as exc:
            self.note_provider_failure(provider, exc)
            raise

    def _race(self, call: "Callable[[str], R]", model: str, race_size: int) -> "R":
        """Parallel race of ``race_size`` legs on ONE model.

        Staggered starts dodge gonka's near-identical-burst guard. The first leg
        that returns (no exception) wins; remaining legs are abandoned via
        ``shutdown(wait=False)`` so wall-clock == the fastest leg. A round where
        every leg raises (error / empty / validation) is retried up to
        ``race_rounds`` before the model is given up on (and the caller — the
        cascade — moves to the next model).
        """
        last_exc: Exception | None = None
        for round_idx in range(self._race_rounds):
            executor = _futures.ThreadPoolExecutor(max_workers=race_size)
            futures: list[_futures.Future] = []
            try:
                for leg in range(race_size):
                    if leg and self._race_stagger:
                        time.sleep(self._race_stagger)
                    futures.append(executor.submit(call, model))
                for fut in _futures.as_completed(futures):
                    try:
                        result = fut.result()
                        logger.debug(
                            "LLMRouter race: winner model=%s round=%d legs=%d",
                            model, round_idx, race_size,
                        )
                        executor.shutdown(wait=False, cancel_futures=True)
                        return result
                    except Exception as exc:  # this leg lost; keep waiting
                        last_exc = exc
            finally:
                executor.shutdown(wait=False)
            logger.warning(
                "LLMRouter race round %d: model=%s all %d legs failed (last: %s)",
                round_idx, model, race_size, last_exc,
            )
        raise last_exc or RuntimeError(f"race produced no result for {model}")

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
            # A `@cf*` model spends part of its budget on a reasoning pass that
            # never reaches `content`; under the floor it returns an empty
            # `content` with finish_reason=length, which reads as a model that
            # answered with nothing rather than one that was cut off. Applied
            # here so no caller has to know — non-CF models pass through
            # untouched, since inflating their ceiling only loosens a limit
            # that is doing its job.
            attempt_max_tokens = min_max_tokens_for(model, max_tokens)
            did_bump = False
            did_reask = False

            while True:
                resp = None
                try:
                    # Pass the Pydantic schema itself: the client renders it as a
                    # strict json_schema block and (on OpenRouter) sets
                    # provider.require_parameters, so the provider enforces the
                    # schema during generation. parse_into_schema is the backstop
                    # for any provider that falls through to plain json_object.
                    resp = self._client.chat_completion(
                        messages=attempt_messages,
                        model=model,
                        max_tokens=attempt_max_tokens,
                        response_format=schema,
                        # The provider is a property of THIS model, not of the
                        # router — so a cross-provider chain hits the right one
                        # on every leg.
                        provider=self.provider_for_model(model),
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
                    # Alert only on terminal failure (recovery exhausted);
                    # the first cut-off plus successful retry is logged but
                    # does not Telegram-spam — the call is "wasted" in cost
                    # but the listing still gets normalized.
                    if did_bump:
                        if resp is not None:
                            alert_wasted_call(
                                model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                            )
                        logger.warning(
                            "LLMRouter.parse: model=%s truncated again after bump", model
                        )
                        raise
                    did_bump = True
                    attempt_max_tokens = min(attempt_max_tokens * 2, 32768)
                    if resp is not None:
                        logger.warning(
                            "LLMRouter.parse: model=%s truncated (billed $%.6f, tokens=%d); "
                            "bumping max_tokens → %d and retrying",
                            model, resp.cost_usd or 0.0, resp.tokens_used, attempt_max_tokens,
                        )
                    else:
                        logger.info(
                            "LLMRouter.parse: model=%s truncated; bumping max_tokens → %d",
                            model, attempt_max_tokens,
                        )
                    continue

                except LLMValidationError as exc:
                    # Parsed but wrong shape — one bounded re-ask with the
                    # validation error injected so the model self-corrects.
                    # Alert only on terminal failure (re-ask exhausted); the
                    # first invalid response plus successful re-ask is logged
                    # but does not Telegram-spam.
                    if did_reask:
                        if resp is not None:
                            alert_wasted_call(
                                model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                            )
                        logger.warning(
                            "LLMRouter.parse: model=%s still invalid after re-ask", model
                        )
                        raise
                    did_reask = True
                    if resp is not None:
                        # The validation error belongs in this line. Without it
                        # a recurring shape problem is invisible: you see the
                        # re-ask rate and the wasted spend, but never which
                        # field the model keeps getting wrong, so there is
                        # nothing to act on short of reproducing by hand.
                        logger.warning(
                            "LLMRouter.parse: model=%s invalid (billed $%.6f, tokens=%d); "
                            "re-asking with error injected: %s",
                            model, resp.cost_usd or 0.0, resp.tokens_used,
                            str(exc).replace("\n", " ")[:300],
                        )
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
                    continue

                except Exception as exc:
                    # No recovery for these — always terminal, always alert.
                    logger.warning("LLMRouter.parse: model=%s failed: %s", model, exc)
                    if resp is not None:
                        alert_wasted_call(
                            model, resp.tokens_used, resp.cost_usd or 0.0, str(exc)
                        )
                    raise

        try:
            return self._run(call)
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
                # Same CF floor `parse` applies: a `@cf*` model under it returns
                # empty content with finish_reason=length. `complete` has no
                # repair ladder to notice that, so the floor matters MORE here.
                max_tokens=min_max_tokens_for(model, max_tokens),
                provider=self.provider_for_model(model),
            )
            logger.debug("LLMRouter.complete: success model=%s", model)
            return resp.content, model

        try:
            return self._run(call)
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
