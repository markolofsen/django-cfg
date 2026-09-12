"""Fusion presets — the source-of-truth model combos for the "AI council".

This sits in the catalog (next to ``roles`` / ``models`` verdicts) so the council
lineup lives in ONE place alongside the rest of the curated model knowledge —
not duplicated in the gateway. Consumers (the gateway's ``fusion`` service, a
future SDK, django) read ``DEFAULT_PRESETS`` from here and may OVERRIDE locally
when they need a runtime/per-fleet customization.

Each preset is a cost tier: a panel of proposers + a frontier synthesizer. Slugs
are concrete OpenRouter ids (verified live). The synthesizer is ALWAYS a frontier
model — a cheap evaluator fails (style bias, picks the longest answer, can't
resolve contradictions). Source: cmdop fusion research (OpenRouter DRACO bench).

Why fusion is worth it (the concept, not a benchmark number): several CHEAP
panel models proposing in parallel + ONE frontier synth tends to BEAT a single
frontier model on quality AND come out CHEAPER overall — the panel's combined
cost stays below one solo frontier call. So fusion is a SAVING, not a premium;
treat it as the high-quality default for prose/reasoning, never as a costly
extra to ration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: The frontier synthesizer shared by every preset — one constant so the price
#: ceiling (<= Opus-4.8-class) lives in one place.
_OPUS = "openrouter/anthropic/claude-opus-4.8"

DEFAULT_PRESET = "budget"

#: Default provider routing for PANEL legs: prefer the fastest upstream provider
#: of each model (OpenRouter ``sort=throughput``). The council waits on its
#: SLOWEST node, so a slow provider of one panelist (e.g. a laggy Kimi endpoint)
#: stalls the whole turn — speed dominates price here. Kept as a plain dict so
#: the catalog stays free of a routing-package import; mirrors
#: ``django_cfg.modules.django_llm.routing.providers.THROUGHPUT.to_dict()``.
_PANEL_FAST: dict[str, Any] = {"sort": "throughput", "allow_fallbacks": True}


@dataclass(frozen=True)
class FusionCombo:
    """A cost-tiered council combo: panel of proposers + frontier synthesizer.

    ``label`` / ``hint`` are the picker presentation (one source of truth so the
    desktop ``/v1/tiers`` view and any SDK show the same names). ``order`` is the
    display rank — lower first; the default preset leads. ``panel_provider`` is
    the OpenRouter provider-routing policy applied to each PANEL leg (default:
    fastest provider — the council bottlenecks on its slowest node). The synth
    leg keeps the default balanced policy.
    """

    panel: tuple[str, ...]
    synth: str
    label: str = ""
    hint: str = ""
    order: int = 100
    panel_provider: dict[str, Any] = field(default_factory=lambda: dict(_PANEL_FAST))


#: The research-backed lineup. Edit THIS to retune the council.
DEFAULT_PRESETS: dict[str, FusionCombo] = {
    # 64.7% on DRACO at ~half a frontier model's cost — the default.
    "budget": FusionCombo(
        panel=(
            "openrouter/google/gemini-3-flash-preview",
            "openrouter/moonshotai/kimi-k2.6",
            "openrouter/deepseek/deepseek-v4-pro",
        ),
        synth=_OPUS,
        label="Council · Budget",
        hint="3-model panel → Opus synthesis. Best value (~½ frontier cost).",
        order=10,
    ),
    # Cross-family fallback when baselines are comparable.
    "balanced": FusionCombo(
        panel=(
            "openrouter/google/gemini-3-flash-preview",
            "openrouter/qwen/qwen3.6-flash",
            "openrouter/meta-llama/llama-3.3-70b-instruct",
        ),
        synth=_OPUS,
        label="Council · Balanced",
        hint="Cross-family panel (Gemini/Qwen/Llama) → Opus synthesis.",
        order=20,
    ),
    # Frontier panel, synthesized by Opus 4.8.
    "premium": FusionCombo(
        panel=(
            _OPUS,
            "openrouter/openai/gpt-5.5",
            "openrouter/google/gemini-3.1-pro-preview",
        ),
        synth=_OPUS,
        label="Council · Premium",
        hint="Frontier panel (Opus/GPT-5.5/Gemini-Pro) → Opus synthesis.",
        order=30,
    ),
    # Top DRACO score (69.0%): Fable 5 + GPT-5.5 -> Opus 4.8.
    "frontier": FusionCombo(
        panel=("openrouter/anthropic/claude-fable-5", "openrouter/openai/gpt-5.5"),
        synth=_OPUS,
        label="Council · Frontier",
        hint="Highest quality (Fable-5 + GPT-5.5 → Opus). Top benchmark score.",
        order=40,
    ),
    # Self-fusion: one strong model with itself (58.8%->65.5%) — the synthesis
    # phase itself, not just family diversity, drives the gain.
    "self": FusionCombo(
        panel=(_OPUS, _OPUS),
        synth=_OPUS,
        label="Council · Self",
        hint="Opus debating itself → Opus synthesis. Single-vendor.",
        order=50,
    ),
}


def default_presets() -> dict[str, FusionCombo]:
    """A fresh copy of the source-of-truth presets (callers may mutate/override)."""
    return dict(DEFAULT_PRESETS)
