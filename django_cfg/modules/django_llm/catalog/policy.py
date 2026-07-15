"""Model-selection POLICY — the pure decision layer for `auto`.

This is the single source of truth for *which kind of model* an `auto` request
should get, expressed only in terms of the request's intrinsic features
(does it use tools? vision?). It is deliberately PURE:

  - no database, no session, no HTTP, no keys, no quota
  - inputs are plain flags; output is a role + its preset model chain
  - trivially unit-testable without any infrastructure

The gateway is the EXECUTION layer: it takes the plan returned here and turns the
preset slugs into a concrete dispatchable model (resolve_model → resolve_key →
dispatch) against the DB. Policy decides WHAT; the gateway decides HOW. The
dependency points one way: the gateway imports this module; this module imports
nothing from the gateway. (Clean/hexagonal split — keeps the routing rule
auditable in one place instead of smeared across the dispatcher.)
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import recommend
from .roles import ModelRole


@dataclass(frozen=True)
class RequestFeatures:
    """The intrinsic properties of a request that drive model selection."""

    has_tools: bool
    has_vision: bool = False


@dataclass(frozen=True)
class ModelPlan:
    """The policy's decision: which role, and the preset chain for it.

    `preset` is the verdict-ranked model chain (`recommend(role)`); `preset[0]` is
    the default pick. `role` and `reason` are carried for logging/telemetry so the
    gateway can record WHY this plan was chosen. Empty `preset` means the catalog
    has no recommendation for the role — the gateway should fall back to its DB
    picker rather than 503.
    """

    role: ModelRole
    preset: tuple[str, ...]
    reason: str


def select_model_plan(features: RequestFeatures) -> ModelPlan:
    """Pick the model ROLE for an `auto` request from its features alone.

    Rules (the routing policy — change here, in one place):
      - tool-using (agentic CODING) → TOOL_CHAT: a strong, tool-reliable model.
        A Flash/mini-class model mis-reads its own tool output and loops on
        multi-step coding, so this path must get the curated TOOL_CHAT preset.
      - everything else (prose-only `auto`) → CLASSIFY-tier cheap chat is fine;
        we leave the concrete cheap pick to the gateway's DB picker by returning
        an empty preset for this branch (no dedicated prose-chat preset role
        exists, and cheap prose was never the failure mode).
    """
    if features.has_tools:
        return ModelPlan(
            role=ModelRole.TOOL_CHAT,
            preset=tuple(recommend(ModelRole.TOOL_CHAT)),
            reason="agentic (tool-using) turn → strong tool-reliable preset",
        )
    # Prose-only: empty preset → gateway uses its cheap DB pick.
    return ModelPlan(
        role=ModelRole.TOOL_CHAT,
        preset=(),
        reason="prose-only turn → defer to gateway's cheap pick",
    )
