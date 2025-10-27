"""
Generated API Client.

Auto-generated thin wrapper over CentrifugoRPCClient - DO NOT EDIT
"""

from typing import Optional
from .models import (
    HealthCheckParams,
    HealthCheckResult,
    UserPresenceParams,
    UserPresenceResult,
)
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

    async def system_health(self, params: HealthCheckParams) -> HealthCheckResult:
        """
        Check system health status.
        
        Returns current status of all system components including
        database, cache, and overall health.

        Args:
            params: HealthCheckParams parameters

        Returns:
            HealthCheckResult

        Raises:
            asyncio.TimeoutError: If RPC call times out
            Exception: If RPC call fails
        """
        result = await self._rpc.call('system.health', params.model_dump())
        return HealthCheckResult(**result)

    async def users_update_presence(self, params: UserPresenceParams) -> UserPresenceResult:
        """
        Update user presence status.
        
        Updates the user's online status and broadcasts to subscribers.

        Args:
            params: UserPresenceParams parameters

        Returns:
            UserPresenceResult

        Raises:
            asyncio.TimeoutError: If RPC call times out
            Exception: If RPC call fails
        """
        result = await self._rpc.call('users.update_presence', params.model_dump())
        return UserPresenceResult(**result)


__all__ = ["APIClient"]