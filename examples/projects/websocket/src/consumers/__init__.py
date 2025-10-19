"""
Background consumers for WebSocket server.

Consumers process events from Redis Streams and broadcast to WebSocket clients.
"""

from .file_watcher_consumer import FileWatcherConsumer
from .ai_command_consumer import AICommandConsumer

__all__ = [
    "FileWatcherConsumer",
    "AICommandConsumer",
]
