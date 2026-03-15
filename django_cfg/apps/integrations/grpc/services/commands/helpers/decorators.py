"""
Command Decorators - Eliminate Boilerplate

The @command decorator handles all repetitive patterns in command implementations:
- Error handling with try/except
- Unified logging (entry/exit/error)
- Automatic model status updates
- Consistent return values

This reduces command functions from ~50 lines to ~10 lines.

Example:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import command, CommandBuilder

    @command(success_status="RUNNING")
    async def start_bot(client, bot) -> bool:
        cmd = CommandBuilder.create(pb2.Command, Converter)
        cmd.start.CopyFrom(pb2.StartCommand())
        return await client._send_command(cmd)
"""

import functools
import logging
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, List, Union

logger = logging.getLogger(__name__)

TFunc = TypeVar('TFunc', bound=Callable[..., Any])


def _normalize_status(status: Optional[Union[str, Enum]]) -> Optional[str]:
    """Convert enum to string value if needed."""
    if status is None:
        return None
    if isinstance(status, Enum):
        return status.value
    return status


def command(
    success_status: Optional[Union[str, Enum]] = None,
    error_status: Optional[Union[str, Enum]] = None,
    update_fields: Optional[List[str]] = None,
    log_reason: bool = True,
    log_level: str = "info",
) -> Callable[[TFunc], TFunc]:
    """
    Universal command decorator that handles common patterns.

    Automatically handles:
    1. Entry logging with emoji
    2. Error handling with try/except
    3. Model status updates on success/error
    4. Exit logging (success/warning)
    5. Reason parameter logging (if present)

    Args:
        success_status: Status to set on model if command succeeds (str or Enum)
        error_status: Status to set on model if exception occurs (str or Enum, default: no change)
        update_fields: Fields to update on model (default: ['status', 'updated_at'])
        log_reason: Whether to log 'reason' parameter if present (default: True)
        log_level: Logging level for entry/exit logs (default: "info")

    Returns:
        Decorated async function

    Example usage:

        # Simple start command (using enum)
        @command(success_status=Bot.Status.RUNNING)
        async def start_bot(client, bot) -> bool:
            cmd = CommandBuilder.create(pb2.Command, Converter)
            cmd.start.CopyFrom(pb2.StartCommand())
            return await client._send_command(cmd)

        # Stop with reason
        @command(
            success_status=Bot.Status.STOPPED,
            update_fields=['status', 'stopped_at', 'updated_at']
        )
        async def stop_bot(client, bot, reason: str = None) -> bool:
            cmd = CommandBuilder.create(pb2.Command, Converter)
            cmd.stop.CopyFrom(pb2.StopCommand(reason=reason or ""))
            return await client._send_command(cmd)

        # No status update, just logging
        @command()
        async def ping(client) -> bool:
            cmd = CommandBuilder.create(pb2.Command, Converter)
            cmd.ping.CopyFrom(pb2.PingCommand())
            return await client._send_command(cmd)

    Result:
        - 70% less code per command
        - Consistent logging format
        - Unified error handling
        - Type-safe with protocols
    """

    def decorator(func: TFunc) -> TFunc:
        @functools.wraps(func)
        async def wrapper(client, model_or_none=None, *args, **kwargs) -> bool:
            # Normalize status values (convert enum to string if needed)
            status_value = _normalize_status(success_status)
            error_status_value = _normalize_status(error_status)

            # Determine command name from function
            cmd_name = func.__name__.replace('_', ' ').upper()

            # Get client ID (support both client.client_id and client.bot_id)
            client_id = getattr(client, 'client_id', getattr(client, 'bot_id', 'unknown'))

            # Extract reason if present for logging
            reason = kwargs.get('reason') or (args[0] if args and isinstance(args[0], str) else None)

            # Entry log
            log_func = getattr(logger, log_level, logger.info)
            log_func(f"Sending {cmd_name} to {client_id} (streaming)")

            # Log reason if present and enabled
            if log_reason and reason:
                log_func(f"   Reason: {reason}")

            try:
                # Execute the actual command function
                result = await func(client, model_or_none, *args, **kwargs)

                # Handle successful execution
                if result:
                    logger.info(f"✅ {cmd_name} sent to {client_id}")

                    # Update model status if requested
                    if status_value and model_or_none is not None:
                        model_or_none.status = status_value

                        # Determine which fields to update
                        fields = update_fields or ['status', 'updated_at']

                        # Save model
                        await model_or_none.asave(update_fields=fields)

                else:
                    # Command returned False (client not connected)
                    logger.warning(f"⚠️  {client_id} not connected to streaming service")

                return result

            except Exception as e:
                # Error handling
                logger.error(f"❌ Error sending {cmd_name} to {client_id}: {e}", exc_info=True)

                # Update model to error status if requested
                if error_status_value and model_or_none is not None:
                    try:
                        model_or_none.status = error_status_value
                        await model_or_none.asave(update_fields=['status', 'updated_at'])
                    except Exception as save_error:
                        logger.error(f"Failed to update error status: {save_error}")

                return False

        return wrapper  # type: ignore

    return decorator


def command_with_timestamps(
    success_status: Optional[Union[str, Enum]] = None,
    timestamp_field: str = 'started_at',
) -> Callable[[TFunc], TFunc]:
    """
    Command decorator that also updates timestamp field.

    Useful for commands like start/stop that need to track when they occurred.

    Args:
        success_status: Status to set on success (str or Enum)
        timestamp_field: Field to update with current time (e.g., 'started_at', 'stopped_at')

    Example:
        @command_with_timestamps(
            success_status=Bot.Status.RUNNING,
            timestamp_field='started_at'
        )
        async def start_bot(client, bot) -> bool:
            cmd = CommandBuilder.create(pb2.Command, Converter)
            cmd.start.CopyFrom(pb2.StartCommand())
            return await client._send_command(cmd)
    """

    def decorator(func: TFunc) -> TFunc:
        @functools.wraps(func)
        async def wrapper(client, model, *args, **kwargs) -> bool:
            from django.utils import timezone

            # Set timestamp before executing command
            setattr(model, timestamp_field, timezone.now())

            # Use regular command decorator with timestamp field included
            update_fields = ['status', timestamp_field, 'updated_at']

            inner_decorator = command(
                success_status=success_status,
                update_fields=update_fields
            )

            decorated_func = inner_decorator(func)
            return await decorated_func(client, model, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


__all__ = [
    'command',
    'command_with_timestamps',
]
