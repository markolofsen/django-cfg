"""The views of the chat API. Thin over `ChatService`; mounted by `urls()` with the service and the host's names as initkwargs.

Someone else's thread is the same 404 as a missing one. The answer is `text/event-stream` (the widget wire); it is declared in
the schema as a `oneOf` of frame schemas, and every refusal before it is problem+json (`problems.py`).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiParameter
from rest_framework import status
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cfg.modules.django_llm.agent.bus.events import SSE_HEADERS
from django_cfg.modules.django_llm.agent.chat import turn as rules
from django_cfg.modules.django_llm.agent.chat.api import serializers as s
from django_cfg.modules.django_llm.agent.chat.api.frames import FRAME
from django_cfg.modules.django_llm.agent.chat.api.problems import Problem, ProblemMixin
from django_cfg.modules.django_llm.agent.chat.api.schema import RETRY_AFTER, ChatSchema, Doc, problems
from django_cfg.modules.django_llm.agent.chat.errors import InvalidKind
from django_cfg.modules.django_llm.agent.chat.service import ChatService

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
        messages = s.MessageSerializer(self.service.page(thread), many=True, context={"kind": thread.kind})
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
        opened = self.service.begin(request.user, thread, data["text"], data.get("client_id"), data.get("context"))
        if opened.turn.kind is rules.TurnKind.BUSY:
            return Problem(409, "busy", "An answer is still being written.").response()
        return StreamingHttpResponse(self.service.frames(opened), content_type=STREAM_MEDIA_TYPE, headers=SSE_HEADERS)


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
