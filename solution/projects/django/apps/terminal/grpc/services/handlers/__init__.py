"""
Terminal gRPC handlers.

Exports grpc_handlers for auto-registration with django-cfg.
"""

from .registration import handle_registration
from .output import handle_terminal_output
from .status import handle_status_update
from .error import handle_error_report
from .server import (
    TerminalStreamingServiceServicer,
    grpc_handlers,
    get_terminal_service,
)

__all__ = [
    'handle_registration',
    'handle_terminal_output',
    'handle_status_update',
    'handle_error_report',
    'TerminalStreamingServiceServicer',
    'grpc_handlers',
    'get_terminal_service',
]
