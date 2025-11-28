"""RESUME command implementation - resume crypto client."""
from typing import Optional
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder, command
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


@command()
async def resume_client(client, client_model, message: Optional[str] = None) -> bool:
    """Send Resume command to crypto client."""
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.resume.CopyFrom(pb2.ResumeClientCommand(message=message or "Resumed by admin"))
    return await client._send_command(command)
