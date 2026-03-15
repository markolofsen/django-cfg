"""
Command Builders - Auto-generate command metadata

Eliminates repetitive UUID and timestamp generation in every command.

Example:
    # Before:
    command = pb2.Command(
        command_id=str(uuid.uuid4()),
        timestamp=Converter.datetime_to_timestamp(timezone.now())
    )

    # After:
    command = CommandBuilder.create(pb2.Command, Converter)
"""

import uuid
from typing import Any, Type, TypeVar
from django.utils import timezone

TCommand = TypeVar('TCommand')


class CommandBuilder:
    """
    Universal command builder with auto-generated metadata.

    Automatically adds:
    - command_id: Unique UUID for tracking
    - timestamp: Current time in protobuf format

    Usage:
        from your_app.proto import converters, messages_pb2 as pb2

        # Create command with metadata
        command = CommandBuilder.create(pb2.DjangoCommand, converters.ProtobufConverter)

        # Now add your command-specific data
        command.start.CopyFrom(pb2.StartCommand())
    """

    @staticmethod
    def create(
        command_class: Type[TCommand],
        converter_class: Any,
        **extra_fields
    ) -> TCommand:
        """
        Create command with auto-generated ID and timestamp.

        Args:
            command_class: Protobuf command message class
            converter_class: Converter with datetime_to_timestamp method
            **extra_fields: Additional fields to set on command

        Returns:
            Command instance with command_id and timestamp populated

        Example:
            >>> command = CommandBuilder.create(
            ...     pb2.DjangoCommand,
            ...     ProtobufConverter,
            ...     priority=5  # Optional extra field
            ... )
            >>> print(command.command_id)
            'a1b2c3d4-...'
            >>> print(command.timestamp)
            Timestamp(seconds=1699999999)
        """
        # Generate UUID and timestamp
        command = command_class(
            command_id=str(uuid.uuid4()),
            timestamp=converter_class.datetime_to_timestamp(timezone.now()),
            **extra_fields
        )

        return command

    @staticmethod
    def create_with_id(
        command_class: Type[TCommand],
        converter_class: Any,
        command_id: str,
        **extra_fields
    ) -> TCommand:
        """
        Create command with specific ID (for testing or correlation).

        Args:
            command_class: Protobuf command message class
            converter_class: Converter with datetime_to_timestamp method
            command_id: Specific command ID to use
            **extra_fields: Additional fields

        Returns:
            Command instance with provided command_id and auto-generated timestamp

        Example:
            >>> command = CommandBuilder.create_with_id(
            ...     pb2.DjangoCommand,
            ...     ProtobufConverter,
            ...     command_id="correlation-123"
            ... )
        """
        command = command_class(
            command_id=command_id,
            timestamp=converter_class.datetime_to_timestamp(timezone.now()),
            **extra_fields
        )

        return command


__all__ = ['CommandBuilder']
