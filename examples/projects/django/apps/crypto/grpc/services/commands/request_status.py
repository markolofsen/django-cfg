"""REQUEST_STATUS command implementation - request status from crypto client."""
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder, command
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


@command()
async def request_status(client, client_model, include_stats: bool = False) -> bool:
    """
    Send RequestStatus command to crypto client.

    Args:
        client: Command client instance
        client_model: Client model (not used for crypto)
        include_stats: Include detailed statistics in response

    Returns:
        bool: True if command sent successfully
    """
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.request_status.CopyFrom(pb2.RequestStatusCommand(include_stats=include_stats))
    return await client._send_command(command)
