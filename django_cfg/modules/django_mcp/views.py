"""MCP View - Main endpoint for Model Context Protocol."""

import hashlib
import json
import logging
from typing import Any, Dict

from django.http import JsonResponse
from rest_framework.views import APIView

from django_cfg.modules.django_mcp.exceptions import (
    MCPError,
    MCPPermissionDenied,
)
from django_cfg.modules.django_mcp.protocols.jsonrpc import (
    JSONRPCParser,
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INTERNAL_ERROR,
)
from django_cfg.modules.django_mcp.handlers.initialize import InitializeHandler
from django_cfg.modules.django_mcp.handlers.tools import ToolsHandler
from django_cfg.modules.django_mcp.handlers.resources import ResourcesHandler
from django_cfg.modules.django_mcp.services.context import MCPContext

logger = logging.getLogger(__name__)


class MCPView(APIView):
    """
    Main MCP endpoint that handles JSON-RPC 2.0 requests.

    This view transforms Django into an MCP server by translating
    JSON-RPC calls into Django model queries, tool executions, and
    introspection operations.
    """
    authentication_classes = []  # Custom auth handled in dispatch
    permission_classes = []  # Permissions checked per-method

    # Track initialization state per-session (or per-user if authenticated)
    _initialized_sessions: Dict[str, bool] = {}

    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to handle JSON-RPC error formatting."""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as exc:
            logger.exception("Unhandled exception in MCP view")
            return self._create_error_response(
                error_code=INTERNAL_ERROR,
                error_message=f"Internal server error: {str(exc)}",
                request_id=None,
            )

    def post(self, request):
        """Handle POST requests containing JSON-RPC method calls."""
        # Step 1: Parse JSON-RPC request
        try:
            rpc_request = JSONRPCParser.parse(request.body)
        except Exception as e:
            return self._create_error_response(
                error_code=getattr(e, "error_code", PARSE_ERROR),
                error_message=str(e),
                request_id=None,
            )

        # Step 2: Authenticate user
        user = self._authenticate(request)

        # Step 3: Check if session is initialized (except for initialize method)
        session_key = self._get_session_key(request, user)
        if rpc_request.method != "initialize" and not self._is_initialized(session_key):
            return self._create_error_response(
                error_code=INVALID_REQUEST,
                error_message="Session not initialized. Call 'initialize' first.",
                request_id=rpc_request.id,
            )

        # Step 4: Build MCP context
        try:
            mcp_config = self._get_mcp_config()
        except MCPError as e:
            return self._create_error_response(
                error_code=INTERNAL_ERROR,
                error_message=str(e),
                request_id=rpc_request.id,
            )

        context = MCPContext(
            user=user,
            request=request,
            session_key=session_key,
            config=mcp_config,
        )

        # Step 5: Route to appropriate handler
        try:
            result = self._route_method(rpc_request.method, rpc_request.params, context)
            return self._create_success_response(result, rpc_request.id)
        except MCPPermissionDenied as e:
            return self._create_error_response(
                error_code=METHOD_NOT_FOUND,  # Don't reveal existence of restricted methods
                error_message="Permission denied",
                request_id=rpc_request.id,
            )
        except MCPError as e:
            return self._create_error_response(
                error_code=INVALID_REQUEST,
                error_message=str(e),
                request_id=rpc_request.id,
            )
        except Exception as e:
            logger.exception(f"Error handling MCP method {rpc_request.method}")
            return self._create_error_response(
                error_code=INTERNAL_ERROR,
                error_message=f"Error executing {rpc_request.method}: {str(e)}",
                request_id=rpc_request.id,
            )

    def _authenticate(self, request) -> Any:
        """Authenticate user using MCP access key."""
        # Check MCP Access Key (required)
        try:
            mcp_config = self._get_mcp_config()
            access_key_header = request.headers.get("X-MCP-Access-Key")
            if (
                mcp_config.access_key
                and access_key_header
                and access_key_header == mcp_config.access_key
            ):
                # Authenticated via access key -> return a generic MCP agent user
                from django.contrib.auth import get_user_model
                return get_user_model().get_anonymous()
        except Exception:
            pass

        return None

    def _get_session_key(self, request, user) -> str:
        """Generate session key for initialization tracking."""
        if user and getattr(user, "is_authenticated", False):
            return f"user:{user.pk}"
        # For anonymous users, use IP + User-Agent hash
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        return f"anon:{hashlib.sha256(f'{ip}:{ua}'.encode()).hexdigest()[:16]}"

    def _is_initialized(self, session_key: str) -> bool:
        """Check if session has completed MCP initialization handshake."""
        return self._initialized_sessions.get(session_key, False)

    def _mark_initialized(self, session_key: str):
        """Mark session as initialized."""
        self._initialized_sessions[session_key] = True

    def _get_mcp_config(self):
        """Get MCP configuration."""
        from django_cfg.core.state import get_current_config
        from django_cfg.modules.django_mcp import DjangoMCPModuleConfig

        config = get_current_config()
        if config.mcp is None:
            raise MCPError("MCP module is not enabled")

        # Convert dict to model if needed
        if isinstance(config.mcp, dict):
            return DjangoMCPModuleConfig(**config.mcp)

        return config.mcp

    def _route_method(self, method: str, params: Dict[str, Any], context: MCPContext) -> Any:
        """Route JSON-RPC method to appropriate handler."""
        # MCP protocol methods
        if method == "initialize":
            result = InitializeHandler.handle_initialize(params, context)
            self._mark_initialized(context.session_key)
            return result

        elif method == "notifications/initialized":
            # Client acknowledges initialization
            return None

        # Tools methods
        elif method == "tools/list":
            return ToolsHandler.handle_tools_list(params, context)

        elif method == "tools/call":
            return ToolsHandler.handle_tools_call(params, context)

        # Resources methods
        elif method == "resources/list":
            return ResourcesHandler.handle_resources_list(params, context)

        elif method == "resources/read":
            return ResourcesHandler.handle_resources_read(params, context)

        else:
            raise MCPError(f"Method '{method}' is not supported")

    def _create_success_response(self, result: Any, request_id) -> JsonResponse:
        """Create JSON-RPC success response."""
        response = JSONRPCParser.create_success_response(result, request_id)
        return JsonResponse(response.to_dict())

    def _create_error_response(self, error_code: int, error_message: str, request_id) -> JsonResponse:
        """Create JSON-RPC error response."""
        response = JSONRPCParser.create_error_response(
            error_code, error_message, request_id=request_id
        )
        return JsonResponse(response.to_dict(), status=400)
