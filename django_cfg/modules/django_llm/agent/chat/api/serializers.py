"""Wire shapes of the JSON half of the chat API. Allow-lists (`Serializer`, never `ModelSerializer`): a new column on the
host's table reaches no client until it is added here. The vocabulary (`thread_id`, `client_id`, `parts`) is the one the
SSE frames and the widget's stored parts carry."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from django_cfg.modules.django_llm.agent.chat import kind as kinds
from django_cfg.modules.django_llm.agent.chat import trace
from django_cfg.modules.django_llm.agent.chat.models import choices
from django_cfg.modules.django_llm.agent.chat.turn import ErrorCode, Role, Status


class PartSerializer(serializers.Serializer):
    """A structured part of an answer, by the same `kind` a live `ui_payload` carries."""

    class Meta:
        ref_name = "ChatPart"

    kind = serializers.CharField()
    data = serializers.JSONField()


class ToolCallSerializer(serializers.Serializer):
    """One step of how an answer was reached: compact and safe (see `chat.trace`), never the raw output."""

    class Meta:
        ref_name = "ChatToolCall"

    name = serializers.CharField()
    input = serializers.JSONField(help_text="The tool's arguments, trimmed: long text and lists are cut.")
    summary = serializers.CharField(allow_blank=True, help_text="One line about the outcome, in English.")


class MessageSerializer(serializers.Serializer):
    """Give the serializer `context={"kind": thread.kind}` so the kind's `summarize_call` writes the trace."""

    class Meta:
        ref_name = "ChatMessage"

    id = serializers.UUIDField()
    seq = serializers.IntegerField()
    role = serializers.ChoiceField(choices=choices(Role))
    text = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=choices(Status))
    error_code = serializers.ChoiceField(choices=choices(ErrorCode), allow_blank=True)
    parts = PartSerializer(many=True)
    tool_calls = serializers.SerializerMethodField(help_text="How the answer was reached; empty for a user message.")
    created_at = serializers.DateTimeField()

    @extend_schema_field(ToolCallSerializer(many=True))
    def get_tool_calls(self, obj) -> list[dict]:
        if obj.role != Role.ASSISTANT.value:
            return []
        try:
            summarize = kinds.get(self.context.get("kind", "")).summarize_call
        except kinds.UnknownKind:
            summarize = None
        return trace.compact(obj.tool_calls, summarize)


class ThreadSerializer(serializers.Serializer):
    class Meta:
        ref_name = "ChatThread"

    id = serializers.UUIDField()
    kind = serializers.CharField()
    title = serializers.CharField(allow_blank=True)
    context = serializers.JSONField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        """The kind's `private_context` keys (e.g. a whole document) stay on the server."""
        data = super().to_representation(instance)
        try:
            hidden = kinds.get(instance.kind).private_context
        except kinds.UnknownKind:
            hidden = frozenset()
        data["context"] = {k: v for k, v in (data["context"] or {}).items() if k not in hidden}
        return data


class ThreadListItemSerializer(ThreadSerializer):
    class Meta:
        ref_name = "ChatThreadListItem"

    message_count = serializers.IntegerField()
    last_message_at = serializers.DateTimeField(allow_null=True)


class ThreadDetailSerializer(ThreadSerializer):
    class Meta:
        ref_name = "ChatThreadDetail"

    messages = MessageSerializer(many=True)


class NewThreadSerializer(serializers.Serializer):
    class Meta:
        ref_name = "ChatNewThread"

    kind = serializers.CharField(max_length=40, required=False, help_text="A chat kind the server knows. May be left out only where the host named a default kind.")
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    context = serializers.JSONField(required=False, help_text="The kind's context for this thread; the kind validates it.")


class SendSerializer(serializers.Serializer):
    class Meta:
        ref_name = "ChatSend"

    text = serializers.CharField(trim_whitespace=False, max_length=100_000, help_text="The user's message (the policy's `max_text_chars` applies).")
    client_id = serializers.UUIDField(required=False, allow_null=True, help_text="Client-made id: a resend is answered from storage, not asked twice.")
    context = serializers.DictField(required=False, help_text="What the host says about this turn only; the kind validates it.")


class SearchHitSerializer(serializers.Serializer):
    """A run of consecutive messages of one of your chats that is close in meaning to the query, in any language."""

    class Meta:
        ref_name = "ChatSearchHit"

    thread_id = serializers.UUIDField()
    title = serializers.CharField(allow_blank=True)
    kind = serializers.CharField()
    first_seq = serializers.IntegerField()
    last_seq = serializers.IntegerField()
    score = serializers.FloatField(help_text="Cosine similarity, 0..1; only comparable within one response.")
    snippet = serializers.CharField(allow_blank=True)
