"""JSON-RPC 2.0 Protocol Implementation for MCP."""

from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
import json


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 Request object."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 Response object."""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            result["result"] = self.result
        if self.error is not None:
            result["error"] = self.error
        if self.id is not None:
            result["id"] = self.id
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class JSONRPCError:
    """JSON-RPC 2.0 Error object."""
    code: int
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


# Standard JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class JSONRPCParser:
    """Parse and validate JSON-RPC 2.0 requests."""

    @staticmethod
    def parse(raw_body: bytes) -> JSONRPCRequest:
        """Parse raw request body into JSONRPCRequest object."""
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as e:
            raise JSONRPCParseError(f"Invalid JSON: {e}")

        if not isinstance(data, dict):
            raise JSONRPCInvalidRequest("Request must be a JSON object")

        # Validate jsonrpc version
        if data.get("jsonrpc") != "2.0":
            raise JSONRPCInvalidRequest("Missing or invalid 'jsonrpc' field. Must be '2.0'")

        # Validate method
        if "method" not in data:
            raise JSONRPCInvalidRequest("Missing 'method' field")

        if not isinstance(data["method"], str):
            raise JSONRPCInvalidRequest("'method' must be a string")

        # Validate params (if present)
        params = data.get("params")
        if params is not None and not isinstance(params, dict):
            raise JSONRPCInvalidParams("'params' must be an object if present")

        # Extract id
        request_id = data.get("id")
        if request_id is not None and not isinstance(request_id, (str, int)):
            raise JSONRPCInvalidRequest("'id' must be a string, integer, or null")

        return JSONRPCRequest(
            jsonrpc="2.0",
            method=data["method"],
            params=params or {},
            id=request_id,
        )

    @staticmethod
    def create_success_response(
        result: Any,
        request_id: Optional[Union[str, int]] = None,
    ) -> JSONRPCResponse:
        """Create a successful JSON-RPC response."""
        return JSONRPCResponse(
            result=result,
            id=request_id,
        )

    @staticmethod
    def create_error_response(
        error_code: int,
        error_message: str,
        error_data: Optional[Any] = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> JSONRPCResponse:
        """Create an error JSON-RPC response."""
        return JSONRPCResponse(
            error=JSONRPCError(
                code=error_code,
                message=error_message,
                data=error_data,
            ).to_dict(),
            id=request_id,
        )


class JSONRPCParseError(Exception):
    """Raised when JSON-RPC parsing fails."""
    error_code = PARSE_ERROR


class JSONRPCInvalidRequest(Exception):
    """Raised when JSON-RPC request is invalid."""
    error_code = INVALID_REQUEST


class JSONRPCInvalidParams(Exception):
    """Raised when JSON-RPC params are invalid."""
    error_code = INVALID_PARAMS
