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

#: Provider for a slug the catalog does not know.
#:
#: OpenRouter, deliberately: it is the AGGREGATOR — it fronts OpenAI,
#: Anthropic, Google, Meta, DeepSeek, Qwen and friends behind one
#: `vendor/model` slug namespace, which is exactly the namespace every
#: slug in this file is written in.
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
            ModelRole.REPLY: Verdict.AVOID,      # 2026-09-25: judge 5/27; 2026-09-29 archive: 26 % vs gpt-5-mini 58 %, dearer per draft
        },
        issues=(
            "tool-call args sometimes markdown-fenced over OpenRouter",
            "flattens nested objects in an output tool's args to strings; use native JSON schema output",
        ),
    ),
    "google/gemini-3.5-flash": ModelTraits(
        slug="google/gemini-3.5-flash",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.TOOL_CHAT: Verdict.GOOD,   # stable GA, strongest Flash-class reasoning for agentic chains
            ModelRole.ESCALATION: Verdict.OK,
            ModelRole.REPLY: Verdict.OK,         # 2026-09-29 archive: 12/12 drafted, judge 62.5 %, ~$0.10 a draft
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
            ModelRole.REPLY: Verdict.OK,         # 2026-09-25: judge 10/19, but no draft on 21 of 40 replies
        },
        issues=("premium cost — reserve for escalation, not the hot path",),
    ),
    # REPLY verdicts (2026-09-25): the MLS reply harness (django_cfg.modules.django_llm.agent, read
    # tools, typed output) on 40 held-out real replies of a broker, all of which
    # he answered, so a no-draft is a miss. Judge: gemini-3.1-flash-lite, blind
    # pairs; +-10 points is noise at this size. Zero-retention routing throughout.
    "openai/gpt-5-mini": ModelTraits(
        slug="openai/gpt-5-mini",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.REPLY: Verdict.GOOD,       # 31/40 drafted, judge 15/31; 2026-09-29 archive 24/24, judge 58 %, ~$0.016
        },
        issues=(
            "ZDR only through Azure on OpenRouter; strict json_schema plus ZDR found no endpoint — send require_parameters false",
        ),
    ),
    "openai/gpt-5": ModelTraits(
        slug="openai/gpt-5",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.REPLY: Verdict.AVOID,      # 26/40 drafted, judge 13/26, ~$0.027 a reply
        },
        issues=("three times gpt-5-mini's cost for no measured gain on replies; never in a chain",),
    ),
    "openai/gpt-5-nano": ModelTraits(
        slug="openai/gpt-5-nano",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.JUDGE: Verdict.GOOD,       # MLS dedup adjudicator, production since 2026-09
        },
        issues=("reasoning pass: under ~2000 max_tokens it returns empty content (floor applied by the router)",),
    ),
    "openai/gpt-6-luna": ModelTraits(
        slug="openai/gpt-6-luna",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.REPLY: Verdict.AVOID,      # 16/40 drafted, judge 4/16; never opened a knowledge entry
        },
        issues=("errors under 10 concurrent requests on the Azure ZDR endpoint",),
    ),
    "google/gemini-3.8-flash": ModelTraits(
        slug="google/gemini-3.8-flash",
        reasoning=True, reasoning_disablable=False,
        roles={
            ModelRole.REPLY: Verdict.OK,         # judge 10/20, cleanest punctuation, but no draft on 19 of 40
        },
        issues=(
            "flattens nested objects in an output tool's args to strings; use native JSON schema output",
            "$0.75/$3.75 per M",
        ),
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
        provider=PROVIDER_OPENROUTER,
        roles={
            ModelRole.EXTRACTION: Verdict.OK,
            ModelRole.CLASSIFY: Verdict.OK,
        },
    ),
}


# ── Role recommendations — ordered by preference ─────────────────────
# The first entry is the default primary; the rest form a fallback
# chain. Cross-provider on purpose: one vendor outage must not stall
# the whole role.

_RECOMMENDED: dict[ModelRole, tuple[str, ...]] = {
    ModelRole.EXTRACTION: (
        # OpenRouter only (sdkrouter proxy retired 2026-11-10, see
        # @docs/sdkrouter-retirement.md). Latency bench, five DISTINCT listings
        # in five languages (KR/DE/JP/PL/CN), 2026-09-14:
        #
        #     google/gemini-2.5-flash-lite  1.7 1.2 1.2 1.2 1.2  (s)
        #     openai/gpt-4o-mini            2.4 3.5 1.0 2.7 1.2
        #
        # Both 5/5 on the `anyOf: [integer, null]` shape that degrades worst.
        # gemini-2.5-flash-lite leads: fastest and steadiest. gpt-4o-mini
        # (28/28 on the strict-JSON bench) is the stronger-on-schema fallback;
        # gemini-2.5-flash stays last as the operator-trusted heavier model
        # (thinking is disablable, which makes its determinism caution
        # survivable).
        "google/gemini-2.5-flash-lite",
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash",
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
        # Same reasoning as EXTRACTION above — this role wants strict JSON too,
        # so it waits on the same proxy fix.
        "openai/gpt-4o-mini",         # openrouter — primary
        "google/gemini-2.5-flash",    # openrouter fallback
    ),
    ModelRole.ESCALATION: (
        "anthropic/claude-sonnet-4.6",
    ),
    ModelRole.TRANSLATE: (
        # ADDED 2026-11-10. gpt-4o-mini is what Carapis translated with in
        # production (TRANSLATION_MODEL); the Gemini pair is the cross-vendor net.
        # Plain-text role: no strict schema, so a thinking model buys nothing.
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash-lite",
        "google/gemini-2.5-flash",
    ),
    ModelRole.JUDGE: (
        # ADDED 2026-11-10 from the MLS dedup adjudicator (catalog/services/projects/
        # judge.py): gpt-5-nano leads (reasoning model - the router's reasoning
        # floor lifts max_tokens to 2000 for it), gemini-2.5-flash-lite is the
        # non-reasoning net on another vendor.
        "openai/gpt-5-nano",
        "google/gemini-2.5-flash-lite",
    ),
    ModelRole.REPLY: (
        # ADDED 2026-09-25 from a 40-reply evaluation (verdicts in openrouter.py).
        # Every entry must have a zero-retention endpoint on OpenRouter: the
        # input is a client's private correspondence. Same family on purpose —
        # the fallback takes the same tool and output shape without a second
        # output mode.
        # gpt-5 left the chain 2026-09-29: three times the cost for no measured
        # gain, and as a fallback it billed every upstream hiccup at that price.
        # gemini-3.5-flash is the fallback: judge 62.5 % vs gpt-5-mini 58.3 % on
        # the same CarAPIs archive cases, but ~6x the cost, so it runs only
        # when gpt-5-mini fails upstream.
        "openai/gpt-5-mini",
        "google/gemini-3.5-flash",
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

    Returns an ``LLMProvider`` *value* (``"openrouter"`` / ``"openai"``), never an enum, so importing the catalog stays free of the
    OpenAI SDK that ``providers/`` drags in. Callers that need the enum do
    ``LLMProvider(provider_for(slug))``.

    An uncatalogued slug gets ``DEFAULT_PROVIDER`` (openrouter, the aggregator).
    """
    entry = _CATALOG.get(slug)
    return entry.provider if entry else DEFAULT_PROVIDER


def races(slug: str) -> bool:
    """Whether ``slug`` should be RACED (parallel legs, first clean wins).

    A property of the MODEL's provider, not of the call.

    **Nothing races today, and that is the correct answer, not an oversight.**
    Racing existed for a since-retired provider, which assigned each request to a random
    network host and so had an 11–57s latency spread with a long tail; two
    staggered legs cut it. Every remaining provider serves from one endpoint at predictable latency,
    where a second leg doubles the bill and buys nothing.

    Kept as a function rather than deleted: it is the one place that decides,
    and a provider with a latency tail may appear again.
    """
    return False


def recommend(role: ModelRole) -> list[str]:
    """Ordered model chain for ``role`` — first is the default primary.

    Empty when the role has no curated recommendation yet; callers
    should treat that as "decide explicitly", never as "no models".
    """
    return list(_RECOMMENDED.get(role, ()))


def all_models() -> dict[str, ModelTraits]:
    """The whole catalog, keyed by slug (read-only copy)."""
    return dict(_CATALOG)
