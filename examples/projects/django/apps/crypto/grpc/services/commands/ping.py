"""PING command implementation - ping crypto client."""
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder, command
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


@command()
async def ping_client(client, client_model, sequence: int = 1) -> bool:
    """Send Ping command to crypto client."""
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.ping.CopyFrom(pb2.PingCommand(sequence=sequence))
    return await client._send_command(command)
