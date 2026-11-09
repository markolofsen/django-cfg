"""Admin mixins for a host's Thread and Message models: readonly JSON, filters, cost and token totals. Text-free by default.

    @admin.register(Thread)
    class ThreadAdmin(ThreadAdminMixin, admin.ModelAdmin): ...

    @admin.register(Message)
    class MessageAdmin(MessageAdminMixin, admin.ModelAdmin): ...

Nothing here is editable: the tables are the transcript. A user's words are private, so the pages show no `text`, no tool
arguments and no tool outputs unless the class sets `show_text = True`; what stays is who, when, which kind and model, tokens,
cost, latency, the tool names and the payload kinds. Import this module only in an `admin.py` (it needs `django.contrib.admin`).
"""

from __future__ import annotations

import json
from typing import Any

from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.utils.html import format_html


def pretty(value: Any) -> str:
    return format_html("<pre style='white-space:pre-wrap;margin:0'>{}</pre>", json.dumps(value, ensure_ascii=False, indent=2, default=str))


class _ReadOnly:
    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class ThreadAdminMixin(_ReadOnly):
    """Sessions: kind, owner, messages, tokens and cost per thread; filters by kind and day; context as readonly JSON."""

    list_display = ("id", "kind", "owner", "title_short", "messages_count", "tokens_total", "cost_total", "updated_at")
    list_filter = ("kind", "created_at", "updated_at")
    search_fields = ("id", "owner__email", "owner__username")
    date_hierarchy = "created_at"
    ordering = ("-updated_at",)
    show_text = False  # True shows the title (it is the first words of the user's message)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _messages=Count("messages"), _tokens=Sum("messages__tokens_in") + Sum("messages__tokens_out"), _cost=Sum("messages__cost_usd")
        )

    def get_fields(self, request, obj=None):
        fields = ["id", "kind", "owner", "context_json", "last_seq", "created_at", "updated_at"]
        return ["title", *fields] if self.show_text else fields

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)

    @admin.display(description="title")
    def title_short(self, obj) -> str:
        return obj.title[:60] if self.show_text else "(hidden)"

    @admin.display(description="messages", ordering="_messages")
    def messages_count(self, obj) -> int:
        return obj._messages

    @admin.display(description="tokens", ordering="_tokens")
    def tokens_total(self, obj) -> int:
        return obj._tokens or 0

    @admin.display(description="cost USD", ordering="_cost")
    def cost_total(self, obj) -> str:
        return f"{obj._cost:.4f}" if obj._cost is not None else "-"

    @admin.display(description="context")
    def context_json(self, obj):
        return pretty(obj.context)


class MessageAdminMixin(_ReadOnly):
    """Messages and answers: status, model, prompt version, tokens, cost, latency; parts and tool calls as readonly JSON.

    The changelist announces the totals of what the filters select (messages, tokens, cost) in a banner.
    """

    list_display = ("id", "thread", "seq", "role", "status", "error_code", "model", "prompt_version", "tokens_in", "tokens_out", "cost_usd", "latency_ms", "tools_used", "created_at")
    list_filter = ("role", "status", "error_code", "model", "prompt_version", "created_at")
    search_fields = ("id", "thread__id")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("thread",)
    show_text = False  # True shows `text` and the tool calls with their arguments and outputs

    def get_fields(self, request, obj=None):
        fields = ["thread", "seq", "role", "status", "error_code", "model", "prompt_version", "tokens_in", "tokens_out", "cost_usd", "latency_ms", "client_id", "created_at", "tools_used", "parts_json"]
        return [*fields, "text", "tool_calls_json"] if self.show_text else fields

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)

    @admin.display(description="tools")
    def tools_used(self, obj) -> str:
        return ", ".join(str(c.get("name", "?")) for c in (obj.tool_calls or []) if isinstance(c, dict))

    @admin.display(description="parts")
    def parts_json(self, obj):
        return pretty(obj.parts)

    @admin.display(description="tool calls")
    def tool_calls_json(self, obj):
        return pretty(obj.tool_calls)

    def totals_line(self, queryset) -> str:
        total = queryset.aggregate(n=Count("pk"), tin=Sum("tokens_in"), tout=Sum("tokens_out"), cost=Sum("cost_usd"))
        return f"{total['n']} messages, {(total['tin'] or 0) + (total['tout'] or 0)} tokens, {total['cost'] or 0:.4f} USD (all pages of this filter)"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        cl = response.context_data.get("cl") if hasattr(response, "context_data") else None
        if cl is not None:
            self.message_user(request, self.totals_line(cl.queryset), level=messages.INFO)
        return response


class AttachmentAdminMixin(_ReadOnly):
    """Files on messages: who, kind, type, size, status, when. Text-free: no file name and no derived (OCR, transcript) text, unless `show_text = True`."""

    list_display = ("id", "owner", "chat_kind", "media_kind", "mime", "size", "status", "created_at")
    list_filter = ("chat_kind", "media_kind", "status", "created_at")
    search_fields = ("id", "owner__email", "owner__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    show_text = False  # True shows the file name and the text read from the file

    def get_fields(self, request, obj=None):
        fields = ["owner", "message", "chat_kind", "media_kind", "mime", "size", "sha256", "storage", "status", "created_at"]
        return [*fields, "name", "derived_json"] if self.show_text else fields

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)

    @admin.display(description="derived")
    def derived_json(self, obj):
        return pretty(obj.derived)

    def has_delete_permission(self, request, obj=None) -> bool:
        return False  # a row deleted here would strand its file: files go with their thread (`chat_prune`) or their TTL (`chat_reap`)
