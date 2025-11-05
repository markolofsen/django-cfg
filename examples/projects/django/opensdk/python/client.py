"""
Generated API Client.

Auto-generated thin wrapper over CentrifugoRPCClient - DO NOT EDIT
"""

from typing import Optional
from .rpc_client import CentrifugoRPCClient


class APIClient:
    """
    Generated API client.

    Thin wrapper over CentrifugoRPCClient providing type-safe RPC methods.
    """

    def __init__(self, rpc_client: CentrifugoRPCClient):
        """
        Initialize API client.

        Args:
            rpc_client: Connected CentrifugoRPCClient instance

        Example:
            >>> rpc = CentrifugoRPCClient(
            ...     url='ws://localhost:8000/connection/websocket',
            ...     token='jwt-token',
            ...     user_id='user-123'
            ... )
            >>> await rpc.connect()
            >>>
            >>> api = APIClient(rpc)
            >>> result = await api.some_method(params)
        """
        self._rpc = rpc_client

    # ========== Generated RPC Methods ==========


__all__ = ["APIClient"]