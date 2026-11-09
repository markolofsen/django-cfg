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


class AckSerializer(serializers.Serializer):
    """What the browser told the server about a part: it was applied, or refused and why."""

    class Meta:
        ref_name = "ChatPartAck"

    applied = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True, required=False, max_length=200, default="", help_text="Why it was refused (a short code of the client's); empty when applied.")


class PartSerializer(serializers.Serializer):
    """A structured part of an answer, by the same `kind` a live `ui_payload` carries."""

    class Meta:
        ref_name = "ChatPart"

    kind = serializers.CharField()
    data = serializers.JSONField()
    ack = AckSerializer(required=False, help_text="Present once the browser reported the part (`POST .../parts/<n>/ack`).")


class ToolCallSerializer(serializers.Serializer):
    """One step of how an answer was reached: compact and safe (see `chat.trace`), never the raw output."""

    class Meta:
        ref_name = "ChatToolCall"

    name = serializers.CharField()
    input = serializers.JSONField(help_text="The tool's arguments, trimmed: long text and lists are cut.")
    summary = serializers.CharField(allow_blank=True, help_text="One line about the outcome, in English.")


class AttachmentSerializer(serializers.Serializer):
    """A file on a message. `url` is minted fresh on every read and expires: refetch the thread for a new one, never store it."""

    class Meta:
        ref_name = "ChatAttachment"

    id = serializers.UUIDField()
    name = serializers.CharField(help_text="The user's file name: a label, never a path.")
    mime = serializers.CharField(help_text="Sniffed from the bytes on upload, not the client's claim.")
    size = serializers.IntegerField()
    kind = serializers.CharField(source="media_kind", help_text="image | audio | video | text | document.")
    url = serializers.SerializerMethodField(help_text="Where the browser may fetch the bytes; short-lived.")
    expired = serializers.SerializerMethodField(help_text="True once the file was deleted by the kind's retention: `url` is empty, the chat remembers its name and what was read from it.")
    created_at = serializers.DateTimeField()

    def get_expired(self, obj) -> bool:
        return obj.status == "expired"

    def get_url(self, obj) -> str:
        if obj.status == "expired":
            return ""
        make = self.context.get("attachment_url")
        return make(obj) if make is not None else ""


class AttachmentRefSerializer(serializers.Serializer):
    """A file named on send. Only the id is read: the server knows the rest, a client's url or size is never believed."""

    class Meta:
        ref_name = "ChatAttachmentRef"

    id = serializers.UUIDField()


class AttachmentUploadSerializer(serializers.Serializer):
    """Multipart body of an upload."""

    class Meta:
        ref_name = "ChatAttachmentUpload"

    file = serializers.FileField(help_text="The file. Its type is decided from its bytes.")
    kind = serializers.CharField(max_length=40, required=False, help_text="The chat kind the file is for; may be left out where the host named a default kind.")


class AttachmentLimitsSerializer(serializers.Serializer):
    """What a chat kind accepts as files, for the picker and the tray."""

    class Meta:
        ref_name = "ChatAttachmentLimits"

    enabled = serializers.BooleanField(help_text="False: this kind takes no files; show no attach control.")
    kinds = serializers.ListField(child=serializers.CharField())
    accept = serializers.ListField(child=serializers.CharField(), help_text="Mime types for the file picker.")
    max_files = serializers.IntegerField()
    max_bytes = serializers.IntegerField(help_text="Per file.")
    max_total_bytes = serializers.IntegerField(help_text="Per message.")


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
    attachments = serializers.SerializerMethodField(help_text="Files of a user message, with fresh short-lived urls; empty otherwise.")
    created_at = serializers.DateTimeField()

    @extend_schema_field(AttachmentSerializer(many=True))
    def get_attachments(self, obj) -> list[dict]:
        rows = getattr(obj, "attached", None)
        return AttachmentSerializer(rows or [], many=True, context=self.context).data

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

    text = serializers.CharField(trim_whitespace=False, allow_blank=True, max_length=100_000, help_text="The user's message (the policy's `max_text_chars` applies). May be empty only when the context carries a key the kind lists in `empty_text_with` (a hidden feedback turn); any other empty text is refused as `invalid` / `empty`.")
    client_id = serializers.UUIDField(required=False, allow_null=True, help_text="Client-made id: a resend is answered from storage, not asked twice.")
    context = serializers.DictField(required=False, help_text="What the host says about this turn only; the kind validates it.")
    attachments = AttachmentRefSerializer(many=True, required=False, help_text="Files uploaded earlier (`attachments_create`), by id. Empty text is allowed when at least one is sent.")


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
