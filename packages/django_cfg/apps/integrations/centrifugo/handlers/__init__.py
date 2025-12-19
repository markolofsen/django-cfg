"""
Built-in Centrifugo RPC handlers.

These handlers are automatically registered when the app is loaded.
"""

from .system import *  # noqa: F401, F403

__all__ = [
    "system",
]
