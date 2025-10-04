"""
WebSocket RPC Server.

Complete WebSocket server with built-in RPC bridge and handlers.

File size: ~650 lines
"""

import asyncio
import signal
from typing import Optional, List, Dict, Any
from uuid import uuid4
import websockets
from websockets.server import WebSocketServerProtocol, serve
from loguru import logger
from aiohttp import web

from .config import ServerConfig, WSServerConfig, HandlerConfig
from .connection_manager import ConnectionManager, ActiveConnection
from .message_router import MessageRouter
from ..bridge import RPCBridge
from ..handlers import NotificationHandler, BroadcastHandler, BaseHandler
from ..utils.auth import AuthManager, AuthenticationError
from ..utils.version_checker import display_startup_banner, check_version, get_server_version


class WebSocketServer:
    """
    Complete WebSocket RPC Server.

    Features:
        - WebSocket connections with authentication
        - Built-in RPC bridge for Django integration
        - Connection management with presence tracking
        - Message routing to handlers
        - Built-in handlers (notifications, broadcasts)
        - Extensible with custom handlers
        - Health check HTTP endpoint
        - Graceful shutdown

    Example:
        >>> from django_ipc.server import WebSocketServer, ServerConfig
        >>> from django_ipc.server.config import WSServerConfig, HandlerConfig
        >>>
        >>> # Configure server
        >>> config = ServerConfig(
        ...     server=WSServerConfig(
        ...         host="0.0.0.0",
        ...         port=8765,
        ...         redis_url="redis://localhost:6379/2",
        ...         jwt_secret="your-secret-key",
        ...     ),
        ...     handlers=HandlerConfig(
        ...         enable_notifications=True,
        ...         enable_broadcasts=True,
        ...     ),
        ... )
        >>>
        >>> # Create and run server
        >>> server = WebSocketServer(config)
        >>> await server.start()
    """

    def __init__(
        self,
        config: ServerConfig,
        custom_handlers: Optional[List[BaseHandler]] = None,
    ):
        """
        Initialize WebSocket server.

        Args:
            config: Server configuration
            custom_handlers: Optional list of custom handlers
        """
        self.config = config
        self.server_id = str(uuid4())

        # Core components
        self.connection_manager: Optional[ConnectionManager] = None
        self.message_router: Optional[MessageRouter] = None
        self.rpc_bridge: Optional[RPCBridge] = None
        self.auth_manager: Optional[AuthManager] = None

        # Handlers
        self.handlers: List[BaseHandler] = []
        self.custom_handlers = custom_handlers or []

        # Server state
        self._ws_server: Optional[websockets.server.WebSocketServer] = None
        self._health_server: Optional[web.AppRunner] = None
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """
        Start WebSocket server.

        Initializes all components and starts listening.
        """
        # Display startup banner with version info
        display_startup_banner()

        # Check for updates
        check_version(silent=False)

        logger.info(f"Starting WebSocket server (ID: {self.server_id})")

        # Initialize components
        await self._initialize_components()

        # Start WebSocket server
        self._ws_server = await serve(
            self._handle_connection,
            self.config.server.host,
            self.config.server.port,
            ping_interval=self.config.server.ping_interval,
            ping_timeout=self.config.server.ping_timeout,
            max_size=self.config.server.max_message_size,
            compression="deflate" if self.config.server.enable_compression else None,
        )

        logger.info(
            f"WebSocket server listening on "
            f"{self.config.server.host}:{self.config.server.port}"
        )

        # Start health check endpoint
        if self.config.server.enable_health_endpoint:
            await self._start_health_server()

        # Start RPC bridge
        await self.rpc_bridge.start()

        self._running = True

        # Setup signal handlers
        self._setup_signal_handlers()

        logger.info("WebSocket server started successfully")

        # Wait for shutdown
        await self._shutdown_event.wait()

        # Cleanup
        await self.shutdown()

    async def shutdown(self) -> None:
        """Shutdown WebSocket server gracefully."""
        if not self._running:
            return

        logger.info("Shutting down WebSocket server...")
        self._running = False

        # Stop RPC bridge
        if self.rpc_bridge:
            await self.rpc_bridge.stop()

        # Close WebSocket server
        if self._ws_server:
            self._ws_server.close()
            await self._ws_server.wait_closed()

        # Stop health server
        if self._health_server:
            await self._health_server.cleanup()

        # Shutdown handlers
        for handler in self.handlers:
            await handler.shutdown()

        # Shutdown connection manager
        if self.connection_manager:
            await self.connection_manager.shutdown()

        logger.info("WebSocket server shutdown complete")

    async def _initialize_components(self) -> None:
        """Initialize all server components."""
        # Connection manager
        self.connection_manager = ConnectionManager(
            redis_url=self.config.server.redis_url,
            presence_ttl=self.config.handlers.presence_timeout,
        )
        await self.connection_manager.initialize()

        # Message router
        self.message_router = MessageRouter(self.connection_manager)

        # Auth manager
        self.auth_manager = AuthManager.from_config(self.config.server)

        # Initialize handlers
        await self._initialize_handlers()

        # RPC Bridge
        self.rpc_bridge = RPCBridge(
            redis_url=self.config.server.redis_url,
            request_stream=self.config.server.request_stream,
            consumer_group=self.config.server.consumer_group,
            consumer_name=self.config.server.get_consumer_name(self.server_id),
        )

        # Register RPC bridge handlers
        self._register_bridge_handlers()

        logger.info("All components initialized")

    async def _initialize_handlers(self) -> None:
        """Initialize and register handlers."""
        # Built-in handlers
        if self.config.handlers.enable_notifications:
            handler = NotificationHandler(
                self.connection_manager,
                enabled=True,
            )
            self.handlers.append(handler)

        if self.config.handlers.enable_broadcasts:
            handler = BroadcastHandler(
                self.connection_manager,
                enabled=True,
            )
            self.handlers.append(handler)

        # Custom handlers
        self.handlers.extend(self.custom_handlers)

        # Initialize all handlers
        for handler in self.handlers:
            await handler.initialize()
            handler.register(self.message_router)

        logger.info(f"Initialized {len(self.handlers)} handlers")

    def _register_bridge_handlers(self) -> None:
        """Register handlers with RPC bridge."""
        # Get all registered methods from router
        registered = self.message_router.list_handlers()

        # Register each method with bridge
        for method in registered["methods"]:
            # Create wrapper that calls through message router
            async def handler_wrapper(params: dict, method_name=method):
                # Create fake connection for RPC calls
                fake_conn = ActiveConnection(
                    websocket=None,  # type: ignore
                    authenticated=True,
                    user_id="rpc_bridge",
                )

                # Get handler
                from ..server.message_router import IncomingMessage
                message = IncomingMessage(
                    type="rpc",
                    method=method_name,
                    params=params,
                )

                # Process through router
                response_json = await self.message_router._handle_rpc(fake_conn, message)

                # Parse response
                import json
                response = json.loads(response_json)

                if response.get("error"):
                    raise Exception(response["error"])

                return response.get("result", {})

            self.rpc_bridge.register_method(method, handler_wrapper)

        logger.info(f"Registered {len(registered['methods'])} methods with RPC bridge")

    async def _handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle new WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        conn_info: Optional[ActiveConnection] = None

        try:
            # Wait for authentication message
            auth_message = await asyncio.wait_for(
                websocket.recv(),
                timeout=10.0,  # 10 second auth timeout
            )

            # Authenticate
            try:
                user_id = self.auth_manager.authenticate(auth_message)
                authenticated = True
            except AuthenticationError as e:
                logger.warning(f"Authentication failed: {e}")
                await websocket.close(1008, "Authentication failed")
                return

            # Add connection
            conn_info = await self.connection_manager.add_connection(
                websocket=websocket,
                user_id=user_id,
                authenticated=authenticated,
                metadata={
                    "remote_address": str(websocket.remote_address),
                },
            )

            # Send auth success with server version
            import json
            auth_response = {
                "type": "auth",
                "status": "ok",
                "server_version": get_server_version(),
            }
            await websocket.send(json.dumps(auth_response))

            # Message loop
            async for message in websocket:
                response = await self.message_router.process_message(
                    conn_info,
                    message,
                )

                if response:
                    await websocket.send(response)

        except asyncio.TimeoutError:
            logger.warning("Authentication timeout")
            await websocket.close(1008, "Authentication timeout")

        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"Connection closed: {conn_info.connection_id if conn_info else 'unknown'}")

        except Exception as e:
            logger.exception(f"Error handling connection: {e}")

        finally:
            # Remove connection
            if conn_info:
                await self.connection_manager.remove_connection(conn_info.connection_id)

    async def _start_health_server(self) -> None:
        """Start health check HTTP server."""
        app = web.Application()
        app.router.add_get("/health", self._handle_health_check)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(
            runner,
            self.config.server.host,
            self.config.server.health_port,
        )
        await site.start()

        self._health_server = runner

        logger.info(
            f"Health check endpoint: "
            f"http://{self.config.server.host}:{self.config.server.health_port}/health"
        )

    async def _handle_health_check(self, request: web.Request) -> web.Response:
        """
        Handle health check request.

        Args:
            request: HTTP request

        Returns:
            Health check response
        """
        stats = await self.connection_manager.get_stats()

        health_data = {
            "status": "ok",
            "server_id": self.server_id,
            "connections": stats.total_connections,
            "authenticated": stats.authenticated_connections,
            "users": stats.unique_users,
            "rooms": len(stats.rooms),
        }

        return web.json_response(health_data)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown...")
            self._shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics.

        Returns:
            Stats dict
        """
        conn_stats = await self.connection_manager.get_stats()

        return {
            "server_id": self.server_id,
            "running": self._running,
            "connections": conn_stats.model_dump(),
            "handlers": [h.__class__.__name__ for h in self.handlers],
        }


async def run_server(
    config: ServerConfig,
    custom_handlers: Optional[List[BaseHandler]] = None,
) -> None:
    """
    Run WebSocket server.

    Convenience function to create and run server.

    Args:
        config: Server configuration
        custom_handlers: Optional custom handlers

    Example:
        >>> from django_ipc.server import run_server, ServerConfig
        >>>
        >>> config = ServerConfig(...)
        >>> await run_server(config)
    """
    server = WebSocketServer(config, custom_handlers)
    await server.start()


__all__ = [
    "WebSocketServer",
    "run_server",
]
