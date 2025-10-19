#!/usr/bin/env python3
"""
Unrealon Cloud IDE - WebSocket RPC Server.

Main entry point for the WebSocket server with RPC handlers.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from django_ipc.server import WebSocketServer
from django_ipc.server.connection_manager import ConnectionManager
from config import server_config
from src.handlers import WorkspaceHandler, SessionHandler, NotificationHandler
from src.handlers.django_rpc_handler import DjangoRPCHandler
from src.consumers import FileWatcherConsumer, AICommandConsumer
from loguru import logger
from redis.asyncio import Redis


def configure_logging():
    """Configure logging for the server."""
    logger.remove()  # Remove default handler

    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level="INFO",
    )

    # File logging
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "websocket.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
        level="DEBUG",
    )


async def main():
    """Main entry point."""
    configure_logging()

    logger.info("=" * 80)
    logger.info("🚀 Starting Unrealon WebSocket Server")
    logger.info("=" * 80)

    # Log configuration
    logger.info(f"📡 WebSocket: {server_config.server.host}:{server_config.server.port}")
    logger.info(f"🏥 Health Check: {server_config.server.host}:{server_config.server.health_port}")
    logger.info(f"📦 Redis: {server_config.server.redis_url}")
    logger.info(f"🔐 JWT Auth: {server_config.server.auth_mode.value}")
    logger.info("=" * 80)

    # Create connection manager for custom handlers
    connection_manager = ConnectionManager(
        redis_url=server_config.server.redis_url,
    )
    await connection_manager.initialize()

    # Create custom handlers
    custom_handlers = [
        # Workspace events (file changes, snapshots)
        WorkspaceHandler(connection_manager),

        # AI Session events (messages, tasks)
        SessionHandler(connection_manager),

        # Unrealon notifications
        NotificationHandler(connection_manager),
    ]

    # Initialize File Watcher Consumer
    redis_client = Redis.from_url(
        server_config.server.redis_url,
        decode_responses=False,  # Binary mode for XREADGROUP
    )

    file_watcher_consumer = FileWatcherConsumer(
        redis=redis_client,
        connection_manager=connection_manager,
        stream_name="stream:file-events",
        consumer_group="websocket-consumers",
        consumer_name="websocket-1",
    )

    await file_watcher_consumer.initialize()
    logger.info("✅ File Watcher Consumer initialized")

    # Initialize AI Command Consumer (Router replacement)
    ai_command_consumer = AICommandConsumer(
        redis=redis_client,
        stream_name="stream:ai-commands",
        consumer_group="websocket-router",
        consumer_name="websocket-1",
    )

    await ai_command_consumer.initialize()
    logger.info("✅ AI Command Consumer initialized (Router replacement)")

    # Initialize Django RPC Handler (listens for RPC from Django)
    django_rpc_handler = DjangoRPCHandler(
        redis_url=server_config.server.redis_url,
        connection_manager=connection_manager,
    )
    logger.info("✅ Django RPC Handler initialized")

    # Initialize server with custom handlers
    server = WebSocketServer(
        config=server_config,
        custom_handlers=custom_handlers,
    )

    try:
        # Start consumers (background tasks)
        await file_watcher_consumer.start()
        await ai_command_consumer.start()
        await django_rpc_handler.start()  # Start Django RPC listener

        # Start server
        await server.start()

    except KeyboardInterrupt:
        logger.info("⚠️  Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        raise
    finally:
        logger.info("🛑 Shutting down WebSocket server...")
        await file_watcher_consumer.stop()
        await ai_command_consumer.stop()
        await django_rpc_handler.stop()  # Stop Django RPC handler
        await redis_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
        sys.exit(0)
