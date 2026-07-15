"""UI payloads — typed structured data attached to tool returns
for the frontend to render product widgets.

This is the public 'UI side channel' that streaming.py drains and
emits as `ui_payload` SSE frames. Tool functions populate it via the
``ToolReturnPart.metadata`` field (pydantic-ai convention — same
pattern used by Vercel AI SDK's Generative UI adapter, see
``pydantic_ai/ui/vercel_ai/_utils.py:iter_metadata_chunks``).

Decoupled from the ``tool_call`` / ``tool_result`` debug events:
- Tool events leak tool names + raw args + raw results — gated to
  admin / dev (see ``streaming.py:expose_tool_events``).
- UI payloads carry **only** what the frontend needs to render a
  widget — safe to ship on prod public chat unconditionally.

To add a new widget:
1. Define a Pydantic model below with a ``kind: Literal["..."]``
   discriminator and the minimal fields the frontend needs.
2. Add it to the ``UIPayload`` union and the ``UI_PAYLOAD_TYPES``
   tuple (used by ``streaming.py:_iter_ui_payloads`` for isinstance
   checks).
3. Attach it to a tool's return via
   ``ToolReturn(return_value=..., metadata=YourPayload(...))``.
4. Frontend matches on ``data.kind`` in the ``ui_payload`` SSE event.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class VehicleCardsPayload(BaseModel):
    """Render a horizontally-scrolling list of vehicle cards.

    The frontend hydrates each card from
    ``GET /apix/catalog/vehicles/{id}`` — we deliberately do NOT push
    full vehicle objects through SSE. Keeps the wire light and gives
    the catalog API a single point of cache / permissions / throttling.

    Capped at 20 ids to bound payload size and avoid runaway prompts
    asking the agent to "show me every Toyota".
    """

    kind: Literal["vehicle_cards"] = "vehicle_cards"
    ids: list[str] = Field(..., max_length=20)


class TaxBreakdownPayload(BaseModel):
    """Inline cost-breakdown table for a Korean-import tax estimate.

    Mirrors the line items the ``calculate_tax`` tool returns so the
    frontend can render the same numbers the agent quoted in chat as
    a clean table without re-parsing the prose.

    Currency is USD throughout. Values are rounded integers — the
    backend rounds at calculation time; we don't carry decimals.
    """

    kind: Literal["tax_breakdown"] = "tax_breakdown"
    vehicle_price_usd: int
    customs_duty_usd: int
    excise_tax_usd: int
    vat_usd: int
    recycling_fee_usd: int
    total_tax_usd: int
    total_landed_usd: int


# ---------------------------------------------------------------------------
# Discriminated union — extend here AND in ``UI_PAYLOAD_TYPES`` below when
# adding new kinds.
# ---------------------------------------------------------------------------

UIPayload = Annotated[
    Union[VehicleCardsPayload, TaxBreakdownPayload],
    Field(discriminator="kind"),
]


# Tuple form for ``isinstance`` checks in the streaming runtime — kept
# in sync with the union manually because Python's typing utilities
# can't reflect a discriminated union into a tuple at import time.
UI_PAYLOAD_TYPES: tuple[type[BaseModel], ...] = (
    VehicleCardsPayload,
    TaxBreakdownPayload,
)


# ---------------------------------------------------------------------------
# Directive side channel
# ---------------------------------------------------------------------------
#
# Distinct from the UI-payload union above: a directive does not render a
# product widget, it points the user at an on-screen element. It rides the
# SAME ``ToolReturnPart.metadata`` plumbing — the streaming runtime drains
# it the same way ``_iter_ui_payloads`` drains widgets — but is emitted as
# a ``directive`` SSE frame, not a ``ui_payload`` one.
#
# Why a tool, not a free-text marker: the ``point_at_elements`` tool gets
# schema-validated args from pydantic-ai's constrained tool-call decoding,
# so the model can no longer hallucinate malformed JSON in prose. And
# because the directive is a tool call (never reply text), nothing leaks
# into persisted history — the model cannot copy a prior bad example.


class DirectivePayload(BaseModel):
    """A validated batch of ``point`` directives for the user's screen.

    Carried on ``ToolReturnPart.metadata`` by the ``point_at_elements``
    tool. ``directives`` holds clean dicts already validated against the
    page snapshot's known refs — the streaming runtime ships them
    verbatim inside a ``DirectiveEvent`` (wire shape unchanged, so the
    frontend directive overlay needs no change).
    """

    directives: list[dict]


__all__ = [
    "UIPayload",
    "UI_PAYLOAD_TYPES",
    "VehicleCardsPayload",
    "TaxBreakdownPayload",
    "DirectivePayload",
]
