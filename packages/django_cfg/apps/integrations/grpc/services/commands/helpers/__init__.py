"""
Command Helpers - Reduce Boilerplate in gRPC Command Implementations

This package provides utilities to eliminate repetitive code in command implementations:

1. CommandBuilder - Auto-generate command_id and timestamp
2. @command decorator - Handle errors, logging, and model updates
3. Protocols - Type-safe model interfaces

Usage:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import (
        CommandBuilder,
        command,
        HasStatus,
        HasConfig,
    )

    @command(success_status=Bot.Status.RUNNING, log_emoji="▶️")
    async def start_bot(client, bot) -> bool:
        cmd = CommandBuilder.create(pb2.Command, Converter)
        cmd.start.CopyFrom(pb2.StartCommand())
        return await client._send_command(cmd)

Benefits:
- 70% less code in command implementations
- Unified error handling and logging
- Type-safe model operations
- Consistent patterns across projects
"""

from .builders import CommandBuilder
from .decorators import command, command_with_timestamps
from .protocols import HasStatus, HasConfig, HasTimestamps, HasStatusAndTimestamps

__all__ = [
    'CommandBuilder',
    'command',
    'command_with_timestamps',
    'HasStatus',
    'HasConfig',
    'HasTimestamps',
    'HasStatusAndTimestamps',
]
