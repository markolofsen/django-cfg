"""PAUSE command implementation - pause crypto client."""
from typing import Optional
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder, command
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


@command()
async def pause_client(client, client_model, reason: Optional[str] = None) -> bool:
    """Send Pause command to crypto client."""
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.pause.CopyFrom(pb2.PauseClientCommand(reason=reason or "Paused by admin"))
    return await client._send_command(command)
