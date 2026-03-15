"""
Centrifugo RPC Proxy View.

Handles RPC calls proxied from Centrifugo server to Django.
When a client calls centrifuge.rpc('method', data), Centrifugo
forwards the request to this endpoint.

Flow:
1. Client calls: centrifuge.rpc('terminal.input', {session_id: '...', data: '...'})
2. Centrifugo proxies to: POST /centrifugo/rpc/
3. This view routes to registered @websocket_rpc handler
4. Response returned to client via Centrifugo
"""

import json
import logging
import traceback
from typing import Any

from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import BaseModel, Field, ValidationError

from ..router import get_global_router

logger = logging.getLogger(__name__)


class RPCProxyRequest(BaseModel):
    """Request from Centrifugo RPC proxy."""

    client: str = Field("", description="Client connection ID")
    transport: str = Field("websocket", description="Transport type")
    protocol: str = Field("json", description="Protocol format")
    encoding: str = Field("json", description="Encoding type")
    user: str = Field("", description="User ID from auth")
    method: str = Field("", description="RPC method name")
    data: dict[str, Any] = Field(default_factory=dict, description="RPC params")
    meta: dict[str, Any] | None = Field(None, description="Connection metadata")


class RPCConnection:
    """
    Connection context passed to RPC handlers.

    Provides user_id and metadata from Centrifugo connection.
    """

    def __init__(self, request: RPCProxyRequest):
        self.client_id = request.client
        self.user_id = request.user or None
        self.transport = request.transport
        self.protocol = request.protocol
        self.meta = request.meta or {}

    def __repr__(self):
        return f"<RPCConnection user={self.user_id} client={self.client_id[:8]}...>"


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(transaction.non_atomic_requests, name='dispatch')
class RPCProxyView(View):
    """
    Centrifugo RPC Proxy endpoint.

    Receives RPC calls from Centrifugo and routes them to
    registered @websocket_rpc handlers.

    Request format (from Centrifugo):
    {
        "client": "uuid",
        "user": "user_id",
        "method": "terminal.input",
        "data": {"session_id": "...", "data": "..."}
    }

    Response format (to Centrifugo):
    Success: {"result": {"data": {...}}}
    Error: {"error": {"code": 100, "message": "error"}}
    """

    async def post(self, request):
        """Handle RPC proxy request from Centrifugo."""
        try:
            # Parse request body
            body = json.loads(request.body)
            rpc_request = RPCProxyRequest(**body)

            logger.info(
                f"RPC proxy: method={rpc_request.method} "
                f"user={rpc_request.user} client={rpc_request.client[:8]}..."
            )

            # Get router and check if handler exists
            router = get_global_router()

            if not rpc_request.method:
                return self._error_response(101, "Method name required")

            if not router.has_handler(rpc_request.method):
                logger.warning(f"RPC method not found: {rpc_request.method}")
                return self._error_response(102, f"Method '{rpc_request.method}' not found")

            # Create connection context
            conn = RPCConnection(rpc_request)

            # Get handler and extract param type
            handler = router.get_handler(rpc_request.method)

            # Try to validate params using handler's type hints
            params = rpc_request.data
            try:
                # Get param type from handler signature
                import inspect
                from typing import get_type_hints

                hints = get_type_hints(handler)
                sig = inspect.signature(handler)
                params_list = list(sig.parameters.values())

                if len(params_list) >= 2:
                    param_name = params_list[1].name
                    param_type = hints.get(param_name)

                    if param_type and hasattr(param_type, 'model_validate'):
                        # Pydantic model - validate
                        params = param_type.model_validate(params)

            except ValidationError as e:
                logger.warning(f"RPC param validation error: {e}")
                return self._error_response(103, f"Invalid params: {e.errors()}")
            except Exception as e:
                # Continue without validation
                logger.debug(f"Could not validate params: {e}")

            # Call handler
            try:
                result = await handler(conn, params)

                # Serialize result
                # Note: exclude_none=True ensures fields with value 0 (valid enum values)
                # are included, while only None values are excluded
                if hasattr(result, 'model_dump'):
                    result_data = result.model_dump(exclude_none=True)
                elif isinstance(result, dict):
                    result_data = result
                else:
                    result_data = {"result": result}

                # DEBUG: Log first entry's load_method for file.list_directory
                if rpc_request.method == "file.list_directory" and "entries" in result_data:
                    for e in result_data.get("entries", [])[:3]:
                        if e.get("size", 0) > 10_000_000:
                            logger.warning(f"[RPC DEBUG] {e.get('name')}: viewer_type={e.get('viewer_type')}, load_method={e.get('load_method')}")

                logger.info(f"RPC success: {rpc_request.method}")
                return self._success_response(result_data)

            except Exception as e:
                logger.error(
                    f"RPC handler error: {rpc_request.method}: {e}",
                    exc_info=True
                )
                return self._error_response(500, str(e))

        except json.JSONDecodeError as e:
            logger.error(f"RPC proxy: invalid JSON: {e}")
            return self._error_response(100, "Invalid JSON")

        except ValidationError as e:
            logger.error(f"RPC proxy: validation error: {e}")
            return self._error_response(100, f"Invalid request: {e.errors()}")

        except Exception as e:
            logger.error(f"RPC proxy error: {e}", exc_info=True)
            return self._error_response(500, "Internal server error")

    def _success_response(self, data: dict) -> JsonResponse:
        """Return success response in Centrifugo format."""
        return JsonResponse({
            "result": {
                "data": data
            }
        })

    def _error_response(self, code: int, message: str) -> JsonResponse:
        """Return error response in Centrifugo format."""
        return JsonResponse({
            "error": {
                "code": code,
                "message": message
            }
        })


__all__ = ["RPCProxyView", "RPCConnection"]
