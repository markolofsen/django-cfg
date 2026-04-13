"""Custom exceptions for MCP module."""


class MCPError(Exception):
    """Base exception for MCP errors."""
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.code = code


class MCPPermissionDenied(MCPError):
    """Raised when user lacks permission for MCP operation."""
    code = "PERMISSION_DENIED"


class MCPValidationError(MCPError):
    """Raised when MCP request validation fails."""
    code = "VALIDATION_ERROR"


class MCPResourceNotFound(MCPError):
    """Raised when requested resource doesn't exist."""
    code = "RESOURCE_NOT_FOUND"


class MCPMethodNotSupported(MCPError):
    """Raised when MCP method is not supported."""
    code = "METHOD_NOT_SUPPORTED"
