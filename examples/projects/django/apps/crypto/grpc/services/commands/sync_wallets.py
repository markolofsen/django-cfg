"""SYNC_WALLETS command implementation - request wallet sync from client."""
from typing import Optional, List
from django_cfg.apps.integrations.grpc.services.commands.helpers import CommandBuilder, command
from ..generated import crypto_streaming_pb2 as pb2
from ..proto.converters import ProtobufConverter


@command()
async def sync_wallets(client, client_model, symbols: Optional[List[str]] = None) -> bool:
    """
    Send SyncWallets command to crypto client.

    Args:
        client: Command client instance
        client_model: Client model (not used for crypto)
        symbols: List of coin symbols to sync (empty = sync all)

    Returns:
        bool: True if command sent successfully
    """
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.sync_wallets.CopyFrom(pb2.SyncWalletsCommand(symbols=symbols or []))
    return await client._send_command(command)
