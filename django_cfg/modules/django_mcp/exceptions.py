"""Custom exceptions for MCP module."""


class MCPError(Exception):
    """Base exception for MCP errors."""
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        # `code=None` means "use the subclass's own", rather than overwriting it
        # with the base default. It was overwritten unconditionally, so every
        # subclass's `code` attribute was dead: MCPPermissionDenied declared
        # PERMISSION_DENIED and raised INTERNAL_ERROR, and a caller switching on
        # the code could not tell "you may not" from "we broke".
        if code is not None:
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
