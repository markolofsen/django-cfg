"""
RPC Configuration for Unrealon Cloud IDE WebSocket Server.

Defines RPC endpoints for different environments and server configuration.
"""

from django_ipc.config import RPCServerConfig, RPCEndpointConfig
from django_ipc.server.config import ServerConfig, WSServerConfig, HandlerConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# Environment-Aware RPC Configuration
# =============================================================================

rpc_config = RPCServerConfig(
    development=RPCEndpointConfig(
        websocket_url="ws://localhost:8765/ws",
        redis_url="redis://localhost:6379/2",
    ),
    staging=RPCEndpointConfig(
        websocket_url="wss://ws-staging.unrealon.com/ws",
        redis_url="redis://redis-staging:6379/2",
    ),
    production=RPCEndpointConfig(
        websocket_url="wss://ws.unrealon.com/ws",
        redis_url="redis://redis:6379/2",
    ),
)


# =============================================================================
# WebSocket Server Configuration
# =============================================================================

server_config = ServerConfig(
    server=WSServerConfig(
        host=os.getenv("WS_HOST", "0.0.0.0"),
        port=int(os.getenv("WS_PORT", "8765")),
        health_port=int(os.getenv("HEALTH_PORT", "8766")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/2"),
        jwt_secret=os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    ),
    handlers=HandlerConfig(
        enable_notifications=True,
        enable_broadcasts=True,
        custom_handlers=True,
    ),
)
