"""Curated model catalog — the single source of truth for model
selection by role.

Seeded from three knowledge sources that previously lived as drifting
prose across two apps:

- the normalizer strict-json_schema benchmark (28 real CJK listings);
- production tool-use experience from a host CRM (insights captured
  in ``@docs/insights/tier-based-llm-routing.md`` and
  ``tool-use-hallucinations.md``);
- the external research in ``@docs/research/``.

This file holds only what OpenRouter metadata *cannot* express — the
operational verdicts and pitfalls. Price, context window,
``structured_outputs`` support and reasoning-capability come live from
``registry/`` and must not be duplicated here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .roles import ModelRole, Verdict

# ── Providers ────────────────────────────────────────────────────────
#
# Which provider actually SERVES a model is an intrinsic property of the
# model, not of the call site — so it lives here, in the catalog, with
# everything else we know about a slug.
#
# These strings are the VALUES of ``providers.LLMProvider`` and must stay
# in sync with it (``test_catalog.py`` pins that). They are kept as plain
# strings on purpose: ``providers/`` pulls in the OpenAI SDK, and the
# catalog is a pure data layer that must import cheaply and cycle-free.
# The router maps string -> ``LLMProvider`` at its own seam.

PROVIDER_OPENROUTER = "openrouter"
PROVIDER_OPENAI = "openai"
PROVIDER_GONKA = "gonkagate"

#: Provider for a slug the catalog does not know.
#:
#: OpenRouter, deliberately: it is the AGGREGATOR — it fronts OpenAI,
#: Anthropic, Google, Meta, DeepSeek, Qwen and friends behind one
#: `vendor/model` slug namespace, which is exactly the namespace every
#: slug in this file is written in. gonka, by contrast, serves only a
#: small fixed set of models (see ``providers/provider_manager.py``
#: ``_init_gonka_client``), so defaulting an unknown slug to gonka would
#: send it to a provider that has never heard of it.
DEFAULT_PROVIDER = PROVIDER_OPENROUTER


@dataclass(frozen=True)
class ModelTraits:
    """Curated operational facts for one OpenRouter model slug."""

    slug: str
    reasoning: bool                          # reasoning / thinking model
    reasoning_disablable: bool               # reasoning can be cleanly turned off
    provider: str = DEFAULT_PROVIDER         # which provider SERVES this slug
    roles: dict[ModelRole, Verdict] = field(default_factory=dict)
    issues: tuple[str, ...] = ()             # operational pitfalls

    def verdict(self, role: ModelRole) -> Verdict:
        return self.roles.get(role, Verdict.UNKNOWN)


# ── The catalog — keyed by OpenRouter slug ───────────────────────────
# Verdicts marked UNKNOWN are deliberately unassessed; do not guess.

_CATALOG: dict[str, ModelTraits] = {
    "google/gemini-2.5-flash-lite": ModelTraits(
        slug="google/gemini-2.5-flash-lite",
        reasoning=False, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.GOOD,   # $0.10/$0.40 per M, strict json_schema, non-thinking
            ModelRole.CLASSIFY: Verdict.GOOD,
        },
        issues=(
            "successor to the now-shut-down gemini-2.0-flash-lite-001 "
            "(Google retired 2.0 Flash/Flash-Lite on 2026-06-01)",
        ),
    ),
    "openai/gpt-4o-mini": ModelTraits(
        slug="openai/gpt-4o-mini",
        reasoning=False, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.GOOD,   # bench: 28/28, $0.0014/call — stable, OpenAI provider
            ModelRole.CLASSIFY: Verdict.GOOD,
            ModelRole.TOOL_CHAT: Verdict.OK,      # single-tool reliable, weak on 3+ tool chains
        },
    ),
    "deepseek/deepseek-v4-flash": ModelTraits(
        slug="deepseek/deepseek-v4-flash",
        reasoning=True, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.OK,
            ModelRole.TOOL_CHAT: Verdict.AVOID,
        },
        issues=(
            "tool-use: intent-as-completion — claims an action done without calling the tool",
            "extraction latency 20-55s — slow",
            "strict json_schema is provider-dependent — needs require_parameters",
        ),
    ),
    "qwen/qwen3.5-flash-02-23": ModelTraits(
        slug="qwen/qwen3.5-flash-02-23",
        reasoning=True, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.AVOID,
            ModelRole.CLASSIFY: Verdict.OK,
            ModelRole.TOOL_CHAT: Verdict.AVOID,
        },
        issues=(
            "extraction: reasoning-token P99 runaway — 900s+ calls observed",
            "tool-use: narrate-after-first-call — drops 2nd/3rd tool on chained turns",
        ),
    ),
    "qwen/qwen3.5-9b": ModelTraits(
        slug="qwen/qwen3.5-9b",
        reasoning=False, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.AVOID,
            ModelRole.CLASSIFY: Verdict.AVOID,
            ModelRole.TOOL_CHAT: Verdict.AVOID,
        },
        issues=("unreliable JSON even in json_object mode — returns empty / non-JSON",),
    ),
    "google/gemini-3.1-flash-lite": ModelTraits(
        slug="google/gemini-3.1-flash-lite",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.EXTRACTION: Verdict.AVOID,
            ModelRole.CLASSIFY: Verdict.OK,
        },
        issues=(
            "thinking cannot be disabled (Gemini 3.x) — truncates strict JSON ~14%",
        ),
    ),
    "google/gemini-2.5-flash": ModelTraits(
        slug="google/gemini-2.5-flash",
        reasoning=True, reasoning_disablable=True,
        roles={
            ModelRole.TOOL_CHAT: Verdict.GOOD,   # $0.30/$2.50 per M — clears multi-tool chains, thinking disablable
            ModelRole.EXTRACTION: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.GOOD,
        },
        issues=(
            "tool-call args sometimes markdown-fenced over OpenRouter",
        ),
    ),
    "google/gemini-3.5-flash": ModelTraits(
        slug="google/gemini-3.5-flash",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.TOOL_CHAT: Verdict.GOOD,   # stable GA, strongest Flash-class reasoning for agentic chains
            ModelRole.ESCALATION: Verdict.OK,
        },
        issues=(
            "premium Flash pricing — $1.50/$9.00 per M; reserve for hard tool chains",
            "thinking cannot be disabled (Gemini 3.x)",
        ),
    ),
    "openai/gpt-4.1-mini": ModelTraits(
        slug="openai/gpt-4.1-mini",
        reasoning=False, reasoning_disablable=True,
        roles={
            ModelRole.EXTRACTION: Verdict.OK,
            ModelRole.TOOL_CHAT: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.OK,
        },
        issues=(
            "$0.40/$1.60 per M — pricier PER CALL than gpt-4o-mini despite the 'mini' name",
        ),
    ),
    "anthropic/claude-sonnet-4.6": ModelTraits(
        slug="anthropic/claude-sonnet-4.6",
        reasoning=True, reasoning_disablable=True,
        roles={
            ModelRole.ESCALATION: Verdict.GOOD,
            ModelRole.TOOL_CHAT: Verdict.GOOD,
        },
        issues=("premium cost — reserve for escalation, not the hot path",),
    ),
    "meta-llama/llama-3.3-70b-instruct": ModelTraits(
        slug="meta-llama/llama-3.3-70b-instruct",
        reasoning=False, reasoning_disablable=True,
        roles={
            ModelRole.TOOL_CHAT: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.OK,
        },
        issues=("recency bias — drops tools described early in a long prompt",),
    ),
    "moonshotai/kimi-k2.6": ModelTraits(
        slug="moonshotai/kimi-k2.6",
        reasoning=False, reasoning_disablable=True,
        # THE gonka model. Verified from two places in the code, not guessed:
        #   - providers/provider_manager.py::_init_gonka_client — "serves the
        #     gonka network's chat models (e.g. minimaxai/minimax-m2.7,
        #     moonshotai/kimi-k2.6)";
        #   - providers/config_builder.py::get_default_model — gonkagate's
        #     default model IS "moonshotai/kimi-k2.6".
        # It was already the only slug any caller ever paired with
        # preferred_provider=GONKA (marketplace ingestion reviewer).
        provider=PROVIDER_GONKA,
        roles={
            ModelRole.EXTRACTION: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.OK,
        },
        issues=(
            "gonka random-host latency 11–57s — RACE it (see races()); a single "
            "leg's tail latency is the whole call's latency",
            "gonka availability is not underwritten — 502s observed for a whole "
            "run; always keep an openrouter model ahead of or behind it in the chain",
        ),
    ),
}


# ── Role recommendations — ordered by preference ─────────────────────
# The first entry is the default primary; the rest form a fallback
# chain. Cross-provider on purpose: one vendor outage must not stall
# the whole role.

_RECOMMENDED: dict[ModelRole, tuple[str, ...]] = {
    ModelRole.EXTRACTION: (
        "openai/gpt-4o-mini",         # openrouter — primary; strict json_schema reliable
        "google/gemini-2.5-flash",    # openrouter fallback
    ),
    ModelRole.TOOL_CHAT: (
        # THIS TUPLE IS THE LIVE `auto`+tools PICK. The dispatcher
        # (`dispatcher/core.py::_resolve_auto`) now takes element [0] DIRECTLY for
        # any tool-using `auto` turn — preset-first, bypassing the DB priority
        # picker (which mis-served coding turns with a cheap model). So [0] here
        # IS the model your agent codes with. Reorder to retune.
        #
        # Sonnet leads: agentic CODING is the bar here, and a Flash-class model
        # mis-reads its own tool results / loses the plan on multi-step coding
        # tasks (observed: "package.json not found" right after a glob that listed
        # it). Sonnet is the strongest tool-chat reasoner — worth the cost for the
        # `auto`+tools (coding) path. Flash stays as the cheaper fallback.
        "anthropic/claude-sonnet-4.6",    # strongest tool-chat reasoning — coding default
        "google/gemini-3.5-flash",        # strong Flash fallback for hard chains
        "google/gemini-2.5-flash",        # cheaper Flash fallback
    ),
    ModelRole.CLASSIFY: (
        "openai/gpt-4o-mini",         # openrouter — primary
        "google/gemini-2.5-flash",    # openrouter fallback
    ),
    ModelRole.ESCALATION: (
        "anthropic/claude-sonnet-4.6",
    ),
}


# ── Public API ───────────────────────────────────────────────────────

def traits(slug: str) -> ModelTraits | None:
    """Curated operational facts for ``slug``, or ``None`` if uncatalogued."""
    return _CATALOG.get(slug)


def known_issues(slug: str) -> tuple[str, ...]:
    """Operational pitfalls for ``slug`` — empty tuple if none/uncatalogued."""
    entry = _CATALOG.get(slug)
    return entry.issues if entry else ()


def provider_for(slug: str) -> str:
    """Which provider serves ``slug`` — the single source of provider truth.

    Returns an ``LLMProvider`` *value* (``"openrouter"`` / ``"openai"`` /
    ``"gonkagate"``), never an enum, so importing the catalog stays free of the
    OpenAI SDK that ``providers/`` drags in. Callers that need the enum do
    ``LLMProvider(provider_for(slug))``.

    An uncatalogued slug gets ``DEFAULT_PROVIDER`` (openrouter, the
    aggregator) — we never guess a slug onto gonka, which serves only a
    small fixed model set.
    """
    entry = _CATALOG.get(slug)
    return entry.provider if entry else DEFAULT_PROVIDER


def races(slug: str) -> bool:
    """Whether ``slug`` should be RACED (parallel legs, first clean wins).

    A property of the MODEL's provider, not of the call. gonka assigns each
    request to a random network host, so per-call latency is 11–57s with a long
    tail; two staggered legs plus first-clean-wins cuts that tail and survives an
    empty/errored leg. Every other provider serves from one endpoint at
    predictable latency — racing there would just double the bill for nothing.
    """
    return provider_for(slug) == PROVIDER_GONKA


def recommend(role: ModelRole) -> list[str]:
    """Ordered model chain for ``role`` — first is the default primary.

    Empty when the role has no curated recommendation yet; callers
    should treat that as "decide explicitly", never as "no models".
    """
    return list(_RECOMMENDED.get(role, ()))


def all_models() -> dict[str, ModelTraits]:
    """The whole catalog, keyed by slug (read-only copy)."""
    return dict(_CATALOG)
