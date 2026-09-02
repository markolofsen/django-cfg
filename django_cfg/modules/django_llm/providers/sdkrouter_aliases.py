"""Model aliases published by the sdkrouter LLM proxy (`llm.sdkrouter.com`).

One OpenAI-compatible endpoint fronting two upstreams: Cloudflare Workers AI
(the `@cf*` names) and OpenRouter (everything else). The proxy holds every
vendor credential as a Worker secret, so a caller needs one token that is
useless anywhere else.

**Why aliases rather than model ids.** `@cf-fast` is a promise about cost and
latency; `cf/openai/gpt-oss-20b` is today's way of keeping it. Naming the
promise means the upstream can be swapped centrally without every caller
learning a new id — which is the reason to route through a proxy at all.

Verified live on 2026-09-02 by calling each alias and reading back the
`model` the proxy reported. The right-hand column is what it resolved to
**that day**, recorded so drift is visible, not so anyone depends on it:

    @cf            -> cf/zai-org/glm-4.7-flash
    @cf-fast       -> cf/openai/gpt-oss-20b
    @cf-cheap      -> cf/openai/gpt-oss-20b
    @cf-balanced   -> cf/zai-org/glm-4.7-flash
    @cf-best       -> cf/moonshotai/kimi-k2.6
    @cf-smart      -> cf/moonshotai/kimi-k2.6
    @cf-coder      -> cf/zai-org/glm-4.7-flash
    @cf-reasoning  -> cf/zai-org/glm-5.2

Two things the proxy will not forgive, both found by probing it:

* **Prefixes matter.** `openai/gpt-4o-mini` routes; a bare `gpt-4o-mini`
  answers *"the proxy holds no credential for 'gpt-4o-mini'"*. Use the ids in
  `catalog/models.py`, which are already prefixed.
* **Reasoning models need room to think.** They spend part of the budget on a
  pass that never reaches `content`. Under-budget they return an empty
  `content` with `finish_reason: "length"` — which reads as a model that
  answered with nothing rather than one that was cut off, and every attempt is
  billed. `REASONING_MIN_MAX_TOKENS` is the floor; `min_max_tokens_for()`
  applies it.

  **This is not a Cloudflare property.** It was found on `@cf*` first, so the
  floor was originally gated on `is_cf_model()` — which left `openai/gpt-5-*`
  uncovered and burning a full cascade per pair. The gate is
  `is_reasoning_model()`; extend `_REASONING_MODEL_MARKERS` for new families.
"""

from __future__ import annotations

from typing import Final

#: Base URL. Also in `config_builder.PROVIDER_BASE_URLS`, which is what
#: `ProviderManager` builds clients from; this is here so a caller that only
#: wants the URL need not import the provider machinery.
SDKROUTER_BASE_URL: Final = "https://llm.sdkrouter.com/v1"

#: Floor for `max_tokens` on any model that reasons before answering. See the
#: module docstring.
#:
#: Measured 2026-09-03 on the dedup adjudicator's real payload against
#: `openai/gpt-5-nano`: 300 and 800 both returned empty `content` with
#: `finish_reason="length"`; 2000 answered. The hidden pass costs >800 tokens
#: before the first character of output.
REASONING_MIN_MAX_TOKENS: Final = 2000

#: Former name, kept so external callers keep working.
CF_MIN_MAX_TOKENS: Final = REASONING_MIN_MAX_TOKENS


class CF:
    """Cloudflare Workers AI aliases, by the job rather than the model.

    Pick by what the call needs, not by which model is fashionable:

    * :attr:`FAST` / :attr:`CHEAP` — bulk structured extraction. **This is the
      default for parsing work.** Listing normalization is a strict-JSON task
      over short text; it wants throughput and a low bill, and a bigger model
      buys nothing it can use.
    * :attr:`BALANCED` — the default when a call is not obviously bulk.
    * :attr:`BEST` / :attr:`SMART` — reach for it when a cheaper model has been
      *observed* to fail the task, not in anticipation.
    * :attr:`REASONING` — multi-step problems. Not extraction: a reasoning model
      spends its budget deliberating over a field it could have copied.
    """

    DEFAULT: Final = "@cf"
    FAST: Final = "@cf-fast"
    CHEAP: Final = "@cf-cheap"
    BALANCED: Final = "@cf-balanced"
    BEST: Final = "@cf-best"
    SMART: Final = "@cf-smart"
    CODER: Final = "@cf-coder"
    REASONING: Final = "@cf-reasoning"


#: Every alias the proxy publishes, for validation and for listing in a UI.
CF_ALIASES: Final[frozenset[str]] = frozenset(
    {
        CF.DEFAULT,
        CF.FAST,
        CF.CHEAP,
        CF.BALANCED,
        CF.BEST,
        CF.SMART,
        CF.CODER,
        CF.REASONING,
    }
)

#: The alias structured extraction WOULD use — not wired up today.
#:
#: Named separately from `CF.FAST` because this is a DECISION, not a synonym:
#: parsing listings is strict-JSON over short text, so the cheapest capable
#: model is the right one and a larger one is money spent on nothing. Change
#: this one constant to move every parsing path at once.
#:
#: `_RECOMMENDED[EXTRACTION]` does NOT reference it as of 2026-09-02, and the
#: reason is LATENCY rather than correctness. Strict JSON works: the proxy
#: rewrites `response_format` into the Workers AI shape, and `@cf` re-measured
#: 5/5 afterwards. But five distinct listings took 17.6-78.4s against
#: gpt-4o-mini's 1.0-1.3s, and ingestion runs thousands. See
#: `django_llm/CLAUDE.md`.
CF_STRUCTURED_OUTPUT: Final = CF.FAST


def is_cf_model(model: str | None) -> bool:
    """Whether ``model`` is served by Cloudflare Workers AI through the proxy.

    Accepts both the alias (`@cf-fast`) and a resolved id (`cf/openai/...`),
    with or without the leading `@` — the proxy takes all of these, so anything
    that inspects a model name has to as well.
    """
    if not model:
        return False
    name = model.lstrip("@")
    return name == "cf" or name.startswith("cf-") or name.startswith("cf/")


#: Model-name fragments that identify a reasoning family. Matched on the id, so
#: `openai/gpt-5-nano` and a bare `gpt-5-mini` both hit.
_REASONING_MODEL_MARKERS: Final = ("gpt-5", "o1-", "o3-", "o4-")


def is_reasoning_model(model: str | None) -> bool:
    """Whether ``model`` spends budget on a hidden pass before ``content``.

    CF aliases plus the OpenAI reasoning families. Not a property of the
    provider — `gpt-4o-mini` on the same endpoint needs no floor.
    """
    if not model:
        return False
    if is_cf_model(model):
        return True
    name = model.lstrip("@").lower()
    return any(marker in name for marker in _REASONING_MODEL_MARKERS)


def min_max_tokens_for(model: str | None, requested: int) -> int:
    """Raise ``requested`` to the floor when ``model`` reasons before answering.

    Unchanged for everything else — inflating a ceiling that is doing its job
    only hides genuine over-long output.
    """
    if is_reasoning_model(model):
        return max(requested, REASONING_MIN_MAX_TOKENS)
    return requested
