"""
WebSocket Server Components.

Complete WebSocket server implementation with all components.

Example:
    >>> from django_ipc.server import (
    ...     WebSocketServer,
    ...     ServerConfig,
    ...     WSServerConfig,
    ...     HandlerConfig,
    ...     ConnectionManager,
    ...     MessageRouter,
    ... )
"""

from .config import (
    LogLevel,
    AuthMode,
    WSServerConfig,
    HandlerConfig,
    ServerConfig,
)

from .connection_manager import (
    ActiveConnection,
    ConnectionStats,
    ConnectionManager,
)

from .message_router import (
    IncomingMessage,
    OutgoingMessage,
    HandlerFunc,
    MessageRouter,
)

from .websocket_server import (
    WebSocketServer,
    run_server,
)

__all__ = [
    # Config
    "LogLevel",
    "AuthMode",
    "WSServerConfig",
    "HandlerConfig",
    "ServerConfig",
    # Connection management
    "ActiveConnection",
    "ConnectionStats",
    "ConnectionManager",
    # Message routing
    "IncomingMessage",
    "OutgoingMessage",
    "HandlerFunc",
    "MessageRouter",
    # Server
    "WebSocketServer",
    "run_server",
]
