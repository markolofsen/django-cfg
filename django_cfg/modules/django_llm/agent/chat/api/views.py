"""The views of the chat API. Thin over `ChatService`; mounted by `urls()` with the service and the host's names as initkwargs.

Someone else's thread is the same 404 as a missing one. The answer is `text/event-stream` (the widget wire); it is declared in
the schema as a `oneOf` of frame schemas, and every refusal before it is problem+json (`problems.py`).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.http import FileResponse, StreamingHttpResponse
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import status
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cfg.modules.django_llm.agent.bus.events import SSE_HEADERS
from django_cfg.modules.django_llm.agent.chat.api import serializers as s
from django_cfg.modules.django_llm.agent.chat.api.frames import FRAME
from django_cfg.modules.django_llm.agent.chat.api.problems import Problem, ProblemMixin
from django_cfg.modules.django_llm.agent.chat.api.schema import RETRY_AFTER, ChatSchema, Doc, problems
from django_cfg.modules.django_llm.agent.chat.attachments.store import is_inline, policy_of
from django_cfg.modules.django_llm.agent.chat.errors import InvalidKind, NotFound
from django_cfg.modules.django_llm.agent.chat.service import ChatService
from django_cfg.modules.django_llm.agent.chat.tail import Cursor

STREAM_MEDIA_TYPE = "text/event-stream"


class JsonNegotiation(DefaultContentNegotiation):
    """Always answer in JSON: the stream route is called with `Accept: text/event-stream`, which no DRF renderer serves,
    and a refusal before the stream must still be readable (the default would be a 406)."""

    def select_renderer(self, request, renderers, format_suffix=None):
        return renderers[0], renderers[0].media_type


class ChatView(ProblemMixin, APIView):
    """Base of the kit's views. The host never subclasses it: `urls()` sets the attributes."""

    service: ChatService | None = None
    operation_id_prefix = "chat"
    tag = "chat"
    default_kind: str | None = None
    gate: Callable[[Any], None] | None = None  # called after authentication and throttles; may raise `ServiceUnavailable` or any chat error
    docs: dict[str, Doc] = {}

    schema = ChatSchema()
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    content_negotiation_class = JsonNegotiation

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.gate is not None:
            self.gate(request)

    def thread_of(self, request, thread_id):
        return self.service.get(request.user, thread_id)

    def attachment_store(self):
        """The service's attachment store, or `NotFound`: a host without the table has no such routes to answer."""
        store = self.service.attachment_store
        if store is None:
            raise NotFound("attachments")
        return store

    def signed_url(self, request, row, token: str) -> str:
        namespace = request.resolver_match.namespace if request.resolver_match else ""
        name = f"{namespace}:attachment-content" if namespace else "attachment-content"
        return request.build_absolute_uri(f"{reverse(name, kwargs={'attachment_id': row.pk})}?t={token}")

    def message_context(self, request, kind: str) -> dict:
        """Context of `MessageSerializer`: the kind (for the trace) and the minting of fresh attachment links for this reader."""
        context: dict[str, Any] = {"kind": kind}
        store = self.service.attachment_store
        if store is not None:
            def make(row) -> str:
                try:
                    policy = policy_of(row.chat_kind)
                except NotFound:
                    return ""  # the kind lost its policy: the chip stays, the link does not
                return store.url(row, request.user.pk, policy, lambda r, token: self.signed_url(request, r, token))

            context["attachment_url"] = make
        return context


class ThreadsView(ChatView):
    """Your sessions: the list (only those with messages, newest activity first) and a new empty one."""

    docs = {
        "GET": Doc(
            "threads_list", "List your chats",
            {200: s.ThreadListItemSerializer(many=True), **problems(401)},
            parameters=(OpenApiParameter("kind", str, OpenApiParameter.QUERY, required=False, description="Only chats of this kind."),),
        ),
        "POST": Doc("threads_create", "Start a chat", {201: s.ThreadSerializer, **problems(400, 401)}, request=s.NewThreadSerializer),
    }

    def get(self, request):
        found = self.service.list_for(request.user, kind=request.query_params.get("kind"), only_with_messages=True)
        return Response(s.ThreadListItemSerializer(found, many=True).data)

    def post(self, request):
        body = s.NewThreadSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = dict(body.validated_data)
        kind = data.pop("kind", None) or self.default_kind
        if not kind:
            raise InvalidKind("")
        thread = self.service.create(request.user, kind, **data)
        return Response(s.ThreadSerializer(thread).data, status=status.HTTP_201_CREATED)


class ThreadView(ChatView):
    """One session with its messages (the newest page, oldest first)."""

    docs = {"GET": Doc("threads_retrieve", "Load a chat", {200: s.ThreadDetailSerializer, **problems(401, 404)})}

    def get(self, request, thread_id):
        thread = self.thread_of(request, thread_id)
        messages = s.MessageSerializer(self.service.page(thread), many=True, context=self.message_context(request, thread.kind))
        return Response({**s.ThreadSerializer(thread).data, "messages": messages.data})


class MessagesView(ChatView):
    """Send a message and stream the answer (`text/event-stream`, the widget wire)."""

    docs = {
        "POST": Doc(
            "messages_create", "Send a message, stream the answer",
            {(200, STREAM_MEDIA_TYPE): FRAME, **problems(400, 401, 404, 409, 429, 503)},
            request=s.SendSerializer, parameters=(RETRY_AFTER,),
        )
    }

    def post(self, request, thread_id):
        self.service.ensure_available()  # 503 before anything is read or stored
        thread = self.thread_of(request, thread_id)
        body = s.SendSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data
        opened = self.service.begin(
            request.user, thread, data["text"], data.get("client_id"), data.get("context"),
            attachments=[a["id"] for a in data.get("attachments") or []],
        )
        return StreamingHttpResponse(self.service.frames(opened), content_type=STREAM_MEDIA_TYPE, headers=SSE_HEADERS)  # a resend of a running answer streams it from storage


class MessageStreamView(ChatView):
    """Follow an answer from storage: a second tab, or a reconnect after the connection dropped."""

    docs = {
        "GET": Doc(
            "messages_stream", "Follow an answer being written",
            {(200, STREAM_MEDIA_TYPE): FRAME, **problems(400, 401, 404)},
            parameters=(
                OpenApiParameter("after", int, OpenApiParameter.QUERY, required=False, description="The last frame `id:` the client holds; only later steps and parts are sent. The `Last-Event-ID` header is read when this is left out. Default 0."),
                OpenApiParameter("text_offset", int, OpenApiParameter.QUERY, required=False, description="How much of the answer's text the client holds, in UTF-16 code units (a JavaScript `string.length`). Default 0."),
            ),
        )
    }

    def get(self, request, thread_id, message_id):
        thread = self.thread_of(request, thread_id)
        raw_after = request.query_params.get("after")
        if raw_after is None:
            raw_after = request.headers.get("Last-Event-ID")
        try:
            after = int(raw_after) if raw_after not in (None, "") else 0
            offset = int(request.query_params.get("text_offset") or 0)
        except ValueError:
            return Problem(400, "invalid", "after and text_offset must be whole numbers.").response()
        if after < 0 or offset < 0:
            return Problem(400, "invalid", "after and text_offset must not be negative.").response()
        frames = self.service.attach(thread, message_id, Cursor(after=after, text_offset=offset))
        return StreamingHttpResponse(frames, content_type=STREAM_MEDIA_TYPE, headers=SSE_HEADERS)


class MessageCancelView(ChatView):
    """Ask a running answer to stop. What it had said is kept and the message reads `cancelled`."""

    docs = {"POST": Doc("messages_cancel", "Stop an answer being written", {200: s.CancelSerializer, 202: s.CancelSerializer, **problems(401, 404)})}

    def post(self, request, thread_id, message_id):
        thread = self.thread_of(request, thread_id)
        state = self.service.cancel(thread, message_id)
        return Response(s.CancelSerializer({"status": state}).data, status=status.HTTP_202_ACCEPTED if state == "cancelling" else status.HTTP_200_OK)


class PartAckView(ChatView):
    """The browser's verdict on a `ui_payload` part of an answer: applied, or refused and why."""

    docs = {
        "POST": Doc(
            "parts_ack", "Report what became of a ui payload",
            {200: s.PartSerializer, **problems(400, 401, 404)},
            request=s.AckSerializer,
        )
    }

    def post(self, request, thread_id, message_id, index):
        thread = self.thread_of(request, thread_id)
        body = s.AckSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        part = self.service.ack_part(thread, message_id, index, applied=body.validated_data["applied"], reason=body.validated_data.get("reason", ""))
        return Response(s.PartSerializer(part).data)


class SearchView(ChatView):
    """Search across your chats by meaning (optional: mounted when the host passes `search=` to `urls()`)."""

    search: Callable[..., list] | None = None  # (user, query, *, kind, limit) -> list[Hit]
    docs = {
        "GET": Doc(
            "search", "Search your chats",
            {200: s.SearchHitSerializer(many=True), **problems(400, 401, 503)},
            parameters=(
                OpenApiParameter("q", str, OpenApiParameter.QUERY, required=True, description="What to look for, in any language."),
                OpenApiParameter("kind", str, OpenApiParameter.QUERY, required=False, description="Only chats of this kind."),
                OpenApiParameter("limit", int, OpenApiParameter.QUERY, required=False, description="At most this many hits (1-20, default 8)."),
            ),
        )
    }

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Problem(400, "invalid", "q is required.").response()
        try:
            limit = max(1, min(20, int(request.query_params.get("limit", 8))))
        except ValueError:
            return Problem(400, "invalid", "limit must be a number.").response()
        hits = self.search(request.user, query[:500], kind=request.query_params.get("kind"), limit=limit)
        return Response(s.SearchHitSerializer([vars(h) if not isinstance(h, dict) else h for h in hits], many=True).data)


class AttachmentsView(ChatView):
    """Upload a file for a later message. It stays private to you and is deleted after a day unless a message carries it."""

    parser_classes = [MultiPartParser]
    docs = {
        "POST": Doc(
            "attachments_create", "Upload a file to attach to a message",
            {201: s.AttachmentSerializer, **problems(400, 401, 404, 413, 415, 429, 503)},
            request=s.AttachmentUploadSerializer, parameters=(RETRY_AFTER,),
        )
    }

    def post(self, request):
        self.service.ensure_available()
        body = s.AttachmentUploadSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        kind = body.validated_data.get("kind") or self.default_kind
        if not kind:
            raise InvalidKind("")
        row = self.attachment_store().stage(request.user, kind, body.validated_data["file"])
        return Response(s.AttachmentSerializer(row, context=self.message_context(request, kind)).data, status=status.HTTP_201_CREATED)


class AttachmentView(ChatView):
    """Take a file you have not sent yet off the tray."""

    docs = {"DELETE": Doc("attachments_destroy", "Remove an unsent file", {204: None, **problems(401, 404)})}

    def delete(self, request, attachment_id):
        self.attachment_store().destroy(request.user, attachment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttachmentLimitsView(ChatView):
    """What a chat kind accepts as files."""

    docs = {
        "GET": Doc(
            "attachments_limits", "What files a chat accepts",
            {200: s.AttachmentLimitsSerializer, **problems(401)},
            parameters=(OpenApiParameter("kind", str, OpenApiParameter.QUERY, required=False, description="The chat kind; the host's default when left out."),),
        )
    }

    def get(self, request):
        kind = request.query_params.get("kind") or self.default_kind or ""
        try:
            policy = policy_of(kind) if self.service.attachment_store is not None else None
        except NotFound:
            policy = None
        if policy is None:
            return Response({"enabled": False, "kinds": [], "accept": [], "max_files": 0, "max_bytes": 0, "max_total_bytes": 0})
        return Response({
            "enabled": True, "kinds": sorted(policy.kinds), "accept": policy.accept_list(),
            "max_files": policy.max_files, "max_bytes": policy.max_bytes, "max_total_bytes": policy.max_total_bytes,
        })


class AttachmentContentView(ChatView):
    """The bytes of a file: its owner signed in, or anyone holding the short-lived link a thread read minted (an `<img>` cannot send a header)."""

    permission_classes = [AllowAny]
    docs = {
        "GET": Doc(
            "attachments_content", "Download an attached file",
            {(200, "application/octet-stream"): OpenApiTypes.BINARY, **problems(404)},
            parameters=(OpenApiParameter("t", str, OpenApiParameter.QUERY, required=False, description="The link token from the attachment's `url`."),),
        )
    }

    def get(self, request, attachment_id):
        store = self.attachment_store()
        token = request.query_params.get("t")
        row = None
        if token:
            found = store.model.objects.filter(pk=attachment_id).first()
            if found is not None:
                try:
                    ttl = policy_of(found.chat_kind).url_ttl_s
                except NotFound:
                    ttl = 0
                if ttl and store.check_token(token, found.pk, ttl) == str(found.owner_id):
                    row = found
        if row is None and request.user.is_authenticated:
            row = store.model.objects.for_owner(request.user).filter(pk=attachment_id).first()
        if row is None or row.status == "expired" or not row.file:
            raise NotFound(str(attachment_id))  # a stranger's file, a bad or expired token, a missing file and one whose bytes were deleted: one answer
        inline = is_inline(row.mime, row.media_kind)
        response = FileResponse(store.open(row), content_type=row.mime, as_attachment=not inline, filename=row.name)
        response["X-Content-Type-Options"] = "nosniff"
        response["Content-Security-Policy"] = "sandbox; default-src 'none'"
        response["Cache-Control"] = "private, max-age=300"
        return response
