"""Curated model catalog — the single source of truth for model
selection by role.

Seeded from three knowledge sources that previously lived as drifting
prose across two apps:

- the normalizer strict-json_schema benchmark (28 real CJK listings);
- carapis CRM tool-use production experience
  (``apps/crm/@docs/insights/tier-based-llm-routing.md`` and
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


@dataclass(frozen=True)
class ModelTraits:
    """Curated operational facts for one OpenRouter model slug."""

    slug: str
    reasoning: bool                          # reasoning / thinking model
    reasoning_disablable: bool               # reasoning can be cleanly turned off
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
}


# ── Role recommendations — ordered by preference ─────────────────────
# The first entry is the default primary; the rest form a fallback
# chain. Cross-provider on purpose: one vendor outage must not stall
# the whole role.

_RECOMMENDED: dict[ModelRole, tuple[str, ...]] = {
    ModelRole.EXTRACTION: (
        "google/gemini-2.5-flash-lite",   # $0.10/$0.40 — cheapest reliable strict-json
        "openai/gpt-4o-mini",             # cross-provider fallback (OpenAI), 28/28 strict
        "deepseek/deepseek-v4-flash",
    ),
    ModelRole.TOOL_CHAT: (
        "google/gemini-2.5-flash",        # $0.30/$2.50 — clears multi-tool chains, thinking off
        "google/gemini-3.5-flash",        # stronger reasoning for hard chains (pricier)
        "anthropic/claude-sonnet-4.6",    # premium escalation fallback
    ),
    ModelRole.CLASSIFY: (
        "google/gemini-2.5-flash-lite",
        "openai/gpt-4o-mini",
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


def recommend(role: ModelRole) -> list[str]:
    """Ordered model chain for ``role`` — first is the default primary.

    Empty when the role has no curated recommendation yet; callers
    should treat that as "decide explicitly", never as "no models".
    """
    return list(_RECOMMENDED.get(role, ()))


def all_models() -> dict[str, ModelTraits]:
    """The whole catalog, keyed by slug (read-only copy)."""
    return dict(_CATALOG)
