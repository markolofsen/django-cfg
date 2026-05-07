"""MCP URL Configuration."""

from django.urls import path
from .views import MCPView
from .agents.api.views import MCPAgentChatView, MCPAgentStreamView, MCPAgentHistoryView
from .info_view import MCPInfoView

urlpatterns = [
    path("", MCPView.as_view(), name="mcp-endpoint"),
    path("info/", MCPInfoView.as_view(), name="mcp-info"),
    path("agent/", MCPAgentChatView.as_view(), name="mcp-agent"),
    path("agent/stream/", MCPAgentStreamView.as_view(), name="mcp-agent-stream"),
    path("agent/history/", MCPAgentHistoryView.as_view(), name="mcp-agent-history"),
]
