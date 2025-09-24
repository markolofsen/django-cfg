"""
Exception classes for Django Agents.
"""

from typing import Optional, Any


class AgentError(Exception):
    """Base exception for Django Agents."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentNotFoundError(AgentError):
    """Raised when requested agent is not found in registry."""
    
    def __init__(self, agent_name: str):
        message = f"Agent '{agent_name}' not found in registry"
        super().__init__(message)
        self.agent_name = agent_name


class ExecutionError(AgentError):
    """Raised when agent execution fails."""
    
    def __init__(
        self, 
        message: str, 
        agent_name: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.agent_name = agent_name
        self.original_error = original_error


class ValidationError(AgentError):
    """Raised when input/output validation fails."""
    
    def __init__(self, message: str, validation_errors: Optional[list] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []


class ConfigurationError(AgentError):
    """Raised when agent configuration is invalid."""
    pass


class PermissionError(AgentError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str, required_permission: Optional[str] = None):
        super().__init__(message)
        self.required_permission = required_permission


class TimeoutError(AgentError):
    """Raised when agent execution times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
