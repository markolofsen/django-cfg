"""MCP Agent Chat View."""

import logging
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from django_cfg.modules.django_mcp.agents.services.agent_service import agent_service
from django_cfg.modules.django_mcp.agents.serializers import (
    AgentChatRequestSerializer,
    AgentChatResponseSerializer,
)

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
        # Authenticate
        user = self.authenticate(request)
        if not user:
            return Response(
                {"error": "Invalid or missing X-MCP-Access-Key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Validate request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get MCP config
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        mcp_config = config.mcp if config and config.mcp else None

        # Execute agent
        result = agent_service.run_agent(
            message=serializer.validated_data["message"],
            session_id=serializer.validated_data.get("session_id", "agent-session"),
            model=serializer.validated_data.get("model") or None,
            mcp_config=mcp_config,
        )

        return Response(result)
