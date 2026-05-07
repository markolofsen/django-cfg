"""MCP Agent Chat Views."""

import json
import logging
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser
from django.http import StreamingHttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django_cfg.modules.django_mcp.agents.services.agent_service import agent_service
from django_cfg.modules.django_mcp.agents.runner import AgentContext, agent_runner
from django_cfg.modules.django_mcp.handlers.tools import tool_registry
from django_cfg.modules.django_mcp.agents.api.serializers import (
    AgentChatRequestSerializer,
    AgentChatResponseSerializer,
)
from django_cfg.modules.django_mcp.chat.store import RedisMCPChatStore

logger = logging.getLogger(__name__)


class MCPAgentChatView(generics.GenericAPIView):
    """
    Chat endpoint for MCP agents.

    POST /cfg/mcp/agent/
    {
        "message": "How many users are there?",
        "model": "openai/gpt-4.1-nano",  # optional, overrides default
        "session_id": "abc123"           # optional
    }
    """
    serializer_class = AgentChatRequestSerializer
    permission_classes = [AllowAny]

    def get_authenticate_key(self, request):
        """Extract MCP access key from request."""
        return request.headers.get("X-MCP-Access-Key", "") or request.META.get("HTTP_X_MCP_ACCESS_KEY", "")

    def authenticate(self, request):
        """Check X-MCP-Access-Key header."""
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            mcp_config = config.mcp if config and config.mcp else None
            if not mcp_config:
                return None

            access_key = self.get_authenticate_key(request)
            expected_key = getattr(mcp_config, 'access_key', None)
            if expected_key and access_key == expected_key:
                return AnonymousUser()
        except Exception as e:
            logger.warning(f"MCP agent auth error: {e}")
        return None

    def post(self, request, *args, **kwargs):
        user = self.authenticate(request)
        if not user:
            return Response(
                {"error": "Invalid or missing X-MCP-Access-Key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django_cfg.core.state import get_current_config
        config = get_current_config()
        mcp_config = config.mcp if config and config.mcp else None

        result = agent_service.run_agent(
            message=serializer.validated_data["message"],
            session_id=serializer.validated_data.get("session_id", "agent-session"),
            model=serializer.validated_data.get("model") or None,
            mcp_config=mcp_config,
        )

        return Response(result)


@method_decorator(csrf_protect, name="dispatch")
class MCPAgentHistoryView(View):
    """GET /cfg/mcp/agent/history/?session_id=... — returns chat history for the current user."""

    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        session_id = request.GET.get("session_id") or "agent-session"
        store = RedisMCPChatStore(user_id=request.user.pk, session_id=session_id)
        return JsonResponse({"messages": store.get_history()})


def _sse_line(event_dict: dict) -> str:
    event_type = event_dict.get("event", "message")
    data = json.dumps({k: v for k, v in event_dict.items() if k != "event"})
    return f"event: {event_type}\ndata: {data}\n\n"


@method_decorator(csrf_protect, name="dispatch")
class MCPAgentStreamView(View):
    """
    SSE streaming endpoint for MCP agent chat.

    POST /cfg/mcp/agent/stream/
    Body: {"message": "...", "session_id": "...", "model": "..."}

    Requires active Django session (user must be authenticated in admin).
    Streams SSE events: tool_start, tool_result, text, error, done.
    """

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return StreamingHttpResponse(
                (_sse_line({"event": "error", "message": "Authentication required"}) +
                 _sse_line({"event": "done"})),
                content_type="text/event-stream",
                status=401,
            )

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return StreamingHttpResponse(
                (_sse_line({"event": "error", "message": "Invalid JSON body"}) +
                 _sse_line({"event": "done"})),
                content_type="text/event-stream",
                status=400,
            )

        message = (body.get("message") or "").strip()
        if not message:
            return StreamingHttpResponse(
                (_sse_line({"event": "error", "message": "message is required"}) +
                 _sse_line({"event": "done"})),
                content_type="text/event-stream",
                status=400,
            )

        session_id = body.get("session_id") or "agent-session"
        model_override = body.get("model") or None

        from django_cfg.core.state import get_current_config
        config = get_current_config()
        mcp_config = config.mcp if config and config.mcp else None

        model = model_override or (
            getattr(mcp_config, "llm_model", None) if mcp_config else None
        ) or "openai/gpt-4o-mini"

        store = RedisMCPChatStore(user_id=request.user.pk, session_id=session_id)
        history = store.get_history()

        tools = {tool.name: tool for tool in tool_registry.get_all_tools(None)}
        context = AgentContext(tools=tools, session_key=session_id, config=mcp_config)

        for entry in history:
            context.add_message(entry["role"], entry["content"])

        def event_stream():
            assistant_chunks: list[str] = []
            for event in agent_runner.stream(message, context, model=model):
                yield _sse_line(event)
                if event.get("event") == "text":
                    assistant_chunks.append(event.get("content", ""))
            assistant_reply = "".join(assistant_chunks)
            store.append_message("user", message)
            if assistant_reply:
                store.append_message("assistant", assistant_reply)

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
