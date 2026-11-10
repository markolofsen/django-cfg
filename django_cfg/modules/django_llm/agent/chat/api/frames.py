"""The frames of the answer stream, as schema: one serializer per `type`, joined by a `oneOf` discriminated on `type`.

The runtime sends them from `agent/bus/events.py` (`encode_sse(event, "widget")`); these classes only describe them, so
a generated client gets a typed union. The wire page is `widgets/assistant/@docs/wire-contract.md`. They are pinned two ways
by `tests/test_api_schema.py`: the set of `type` values equals the set in the shared fixture `events.json`, and every
fixture frame validates against its serializer with no key the serializer does not declare.
"""

from __future__ import annotations

from drf_spectacular.utils import PolymorphicProxySerializer
from rest_framework import serializers

from django_cfg.modules.django_llm.agent.bus.events import WIRE_ERROR_CODES, WIRE_PHASES
from django_cfg.modules.django_llm.agent.chat.api.serializers import TraceStepSerializer


def _frame(name: str, type_: str, doc: str, **fields: serializers.Field) -> type[serializers.Serializer]:
    body = {
        "__doc__": doc,
        "Meta": type("Meta", (), {"ref_name": f"Chat{name}Frame"}),
        "type": serializers.ChoiceField(choices=[type_], help_text=f"Always `{type_}`."),
        **fields,
    }
    return type(f"{name}Frame", (serializers.Serializer,), body)


RunFrame = _frame(
    "Run", "run", "Always the first frame: names the stored rows.",
    version=serializers.IntegerField(help_text="Wire version (`WIRE_VERSION`)."),
    thread_id=serializers.UUIDField(),
    message_id=serializers.UUIDField(help_text="The assistant message being written."),
    client_id=serializers.UUIDField(allow_null=True, help_text="The user message's client-made id."),
    seq=serializers.IntegerField(allow_null=True, help_text="The assistant message's sequence number."),
)
StatusFrame = _frame(
    "Status", "status", "An ephemeral label; may repeat; never stored.",
    phase=serializers.ChoiceField(choices=list(WIRE_PHASES)),
)
TextDeltaFrame = _frame("TextDelta", "text_delta", "Appended to the answer.", delta=serializers.CharField(allow_blank=True))
ReasoningDeltaFrame = _frame("ReasoningDelta", "reasoning_delta", "The model's thinking (a kind opts in).", delta=serializers.CharField(allow_blank=True))
ReasoningEndFrame = _frame(
    "ReasoningEnd", "reasoning_end", "Seals the open thought.",
    elapsed_ms=serializers.IntegerField(required=False, allow_null=True),
    tokens=serializers.IntegerField(required=False, allow_null=True),
)
UiPayloadFrame = _frame(
    "UiPayload", "ui_payload", "Structured data the host's renderer draws by `kind`; also stored as a message part.",
    kind=serializers.CharField(),
    data=serializers.JSONField(),
)
DoneFrame = _frame(
    "Done", "done", "Terminal: the answer is stored.",
    finish_reason=serializers.CharField(),
    tokens_in=serializers.IntegerField(allow_null=True),
    tokens_out=serializers.IntegerField(allow_null=True),
    cost_usd=serializers.FloatField(allow_null=True, help_text="Null: the run could not be priced."),
    replayed=serializers.BooleanField(required=False, help_text="Present (true) when the stored answer was replayed for a resent `client_id`."),
)
TraceStepFrame = _frame(
    "TraceStep", "trace_step",
    "Optional: one step of the answer's trace, sent at start (`status: running`) and again when it settles; upsert by `step.step_id`. "
    "Only a kind with `trace_level` > 0 sends it. `event_seq` equals the frame's SSE `id:`.",
    event_seq=serializers.IntegerField(required=False),
    step=TraceStepSerializer(),
)
ErrorFrame = _frame(
    "Error", "error", "Terminal: the answer failed; partial text is kept.",
    code=serializers.ChoiceField(choices=list(WIRE_ERROR_CODES)),
    message=serializers.CharField(),
    retryable=serializers.BooleanField(),
)

#: `type` -> serializer: the whole vocabulary of a stream.
FRAMES: dict[str, type[serializers.Serializer]] = {
    "run": RunFrame,
    "status": StatusFrame,
    "text_delta": TextDeltaFrame,
    "reasoning_delta": ReasoningDeltaFrame,
    "reasoning_end": ReasoningEndFrame,
    "ui_payload": UiPayloadFrame,
    "trace_step": TraceStepFrame,
    "done": DoneFrame,
    "error": ErrorFrame,
}

#: One frame of the stream: `oneOf` with `discriminator: type`.
FRAME = PolymorphicProxySerializer(component_name="ChatFrame", serializers=FRAMES, resource_type_field_name="type")
