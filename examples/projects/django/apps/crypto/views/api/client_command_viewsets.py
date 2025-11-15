"""DRF ViewSets for Crypto Client management via gRPC commands."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.crypto.views.serializers import (
    ClientCommandSerializer,
    ClientCommandListSerializer,
)
from apps.crypto.grpc.services.commands import StreamingCommandClient
from django_cfg.modules.django_logging import get_logger
from django_cfg.apps.integrations.grpc.services.commands import StreamingCommandViewSetMixin

logger = get_logger("crypto.views.command")


@extend_schema(tags=['Crypto Client Commands'])
@extend_schema_view(
    list=extend_schema(summary='List active crypto clients'),
    retrieve=extend_schema(summary='Get crypto client details'),
)
class ClientCommandViewSet(StreamingCommandViewSetMixin, viewsets.ViewSet):
    """
    ViewSet for Crypto Client management via gRPC commands.

    Clients are not stored in database - they exist as gRPC connections.
    This ViewSet provides management actions via streaming commands.

    Authentication: Requires Django session or JWT authentication.
    """

    permission_classes = [IsAuthenticated]

    # StreamingCommandViewSetMixin configuration
    command_client_class = StreamingCommandClient
    client_id_field = "client_id"  # Client UUID
    streaming_service_name = "crypto"  # Registry name for streaming service

    def _get_streaming_service(self):
        """Get the CryptoStreamingService instance."""
        from apps.crypto.grpc.services.server import CryptoStreamingService
        from django_cfg.apps.integrations.grpc.services.commands.registry import get_streaming_service

        # Try to get from registry first
        service = get_streaming_service("crypto")
        if service:
            return service

        # Fallback: service might not be registered yet
        # In production, service should be registered in rungrpc command
        logger.warning("CryptoStreamingService not found in registry")
        return None

    def list(self, request):
        """List all active crypto clients."""
        service = self._get_streaming_service()
        if not service:
            return Response({
                'error': 'gRPC service not available',
                'clients': []
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Get active connections
        connections = service._streaming_service.get_active_connections()

        clients = []
        for client_id, metadata in connections.items():
            client_data = {
                'client_id': client_id,
                'client_name': metadata.get('client_name', 'Unknown'),
                'connected': True,
                'last_heartbeat': metadata.get('last_heartbeat'),
                'metadata': metadata,
                'wallets_synced': metadata.get('wallets_synced', 0),
                'sync_requests': metadata.get('sync_requests', 0),
                'last_sync': metadata.get('last_sync'),
            }
            clients.append(client_data)

        serializer = ClientCommandListSerializer(clients, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get specific crypto client details."""
        client_id = pk
        service = self._get_streaming_service()

        if not service:
            return Response({
                'error': 'gRPC service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Check if client is connected
        if not service.is_client_connected(client_id):
            return Response({
                'error': 'client_not_connected',
                'message': f'Client {client_id} is not connected'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get client metadata
        connections = service._streaming_service.get_active_connections()
        metadata = connections.get(client_id, {})

        client_data = {
            'client_id': client_id,
            'client_name': metadata.get('client_name', 'Unknown'),
            'connected': True,
            'last_heartbeat': metadata.get('last_heartbeat'),
            'metadata': metadata,
            'wallets_synced': metadata.get('wallets_synced', 0),
            'sync_requests': metadata.get('sync_requests', 0),
            'last_sync': metadata.get('last_sync'),
        }

        serializer = ClientCommandSerializer(client_data)
        return Response(serializer.data)

    def handle_exception(self, exc):
        """
        Universal exception handler with traceback for debugging.

        Returns proper API error response with traceback in debug mode.
        """
        import traceback
        from django.conf import settings
        from django_cfg.apps.integrations.grpc.services.commands.base import (
            CommandError,
            CommandTimeoutError,
            ClientNotConnectedError,
        )

        # Handle gRPC command errors
        if isinstance(exc, ClientNotConnectedError):
            return Response({
                'error': 'client_not_connected',
                'message': str(exc),
                'detail': 'Client is not connected to gRPC server',
            }, status=503)

        if isinstance(exc, CommandTimeoutError):
            return Response({
                'error': 'command_timeout',
                'message': str(exc),
                'detail': 'Client did not respond within timeout period',
            }, status=504)

        if isinstance(exc, CommandError):
            response_data = {
                'error': 'command_error',
                'message': str(exc),
                'detail': 'Failed to execute command on client',
            }
            if settings.DEBUG:
                response_data['traceback'] = traceback.format_exc()
            return Response(response_data, status=500)

        # Default DRF exception handling
        return super().handle_exception(exc)

    # ========================================================================
    # Client Control Actions
    # ========================================================================

    @extend_schema(
        summary='Pause crypto client',
        request=None,
        responses={200: ClientCommandSerializer, 503: dict, 504: dict}
    )
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause crypto client and send PAUSE command via gRPC streaming (synchronous)."""
        client_id = pk

        # Create simple client object
        client = type('Client', (), {'client_id': client_id})()

        success, result = self.exec_sync_command(
            client, 'pause_client_sync',
            timeout=15.0,
            reason='Manual pause via API'
        )

        if not success:
            return result  # Error response

        # Get updated client metadata
        service = self._get_streaming_service()
        if service:
            connections = service._streaming_service.get_active_connections()
            metadata = connections.get(client_id, {})

            client_data = {
                'client_id': client_id,
                'client_name': metadata.get('client_name', 'Unknown'),
                'connected': True,
                'last_heartbeat': metadata.get('last_heartbeat'),
                'metadata': metadata,
                'wallets_synced': metadata.get('wallets_synced', 0),
                'sync_requests': metadata.get('sync_requests', 0),
                'last_sync': metadata.get('last_sync'),
            }

            serializer = ClientCommandSerializer(client_data)
            return Response({
                **serializer.data,
                'command_result': self.format_command_response(result)
            })

        return Response({
            'client_id': client_id,
            'command_result': self.format_command_response(result)
        })

    @extend_schema(
        summary='Resume crypto client',
        request=None,
        responses={200: ClientCommandSerializer, 503: dict, 504: dict}
    )
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume paused crypto client and send RESUME command via gRPC streaming (synchronous)."""
        client_id = pk

        # Create simple client object
        client = type('Client', (), {'client_id': client_id})()

        success, result = self.exec_sync_command(client, 'resume_client_sync')

        if not success:
            return result  # Error response

        # Get updated client metadata
        service = self._get_streaming_service()
        if service:
            connections = service._streaming_service.get_active_connections()
            metadata = connections.get(client_id, {})

            client_data = {
                'client_id': client_id,
                'client_name': metadata.get('client_name', 'Unknown'),
                'connected': True,
                'last_heartbeat': metadata.get('last_heartbeat'),
                'metadata': metadata,
                'wallets_synced': metadata.get('wallets_synced', 0),
                'sync_requests': metadata.get('sync_requests', 0),
                'last_sync': metadata.get('last_sync'),
            }

            serializer = ClientCommandSerializer(client_data)
            return Response({
                **serializer.data,
                'command_result': self.format_command_response(result)
            })

        return Response({
            'client_id': client_id,
            'command_result': self.format_command_response(result)
        })

    @extend_schema(
        summary='Ping crypto client',
        request=None,
        responses={200: dict, 503: dict, 504: dict}
    )
    @action(detail=True, methods=['post'])
    def ping(self, request, pk=None):
        """Send PING command to crypto client via gRPC streaming (synchronous)."""
        client_id = pk

        # Create simple client object
        client = type('Client', (), {'client_id': client_id})()

        success, result = self.exec_sync_command(client, 'ping_client_sync', sequence=1)

        if not success:
            return result  # Error response

        return Response({
            'client_id': client_id,
            'ping': 'pong',
            'command_result': self.format_command_response(result)
        })

    @extend_schema(
        summary='Sync wallets on crypto client',
        request=None,
        responses={200: dict, 503: dict, 504: dict},
        parameters=[
            OpenApiParameter(
                name='symbols',
                description='Comma-separated list of coin symbols to sync (e.g., BTC,ETH,USDT). Empty = sync all.',
                required=False,
                type=str,
            ),
        ],
    )
    @action(detail=True, methods=['post'])
    def sync_wallets(self, request, pk=None):
        """Request wallet sync from crypto client via gRPC streaming (synchronous)."""
        client_id = pk

        # Parse symbols from query params
        symbols_str = request.query_params.get('symbols', '')
        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()] if symbols_str else None

        # Create simple client object
        client = type('Client', (), {'client_id': client_id})()

        success, result = self.exec_sync_command(
            client, 'sync_wallets_sync',
            timeout=30.0,  # Longer timeout for wallet sync
            symbols=symbols
        )

        if not success:
            return result  # Error response

        return Response({
            'client_id': client_id,
            'symbols': symbols or 'all',
            'command_result': self.format_command_response(result)
        })

    @extend_schema(
        summary='Request status from crypto client',
        request=None,
        responses={200: ClientCommandSerializer, 503: dict, 504: dict},
        parameters=[
            OpenApiParameter(
                name='include_stats',
                description='Include detailed statistics in response',
                required=False,
                type=bool,
            ),
        ],
    )
    @action(detail=True, methods=['post'])
    def request_status(self, request, pk=None):
        """Request status from crypto client via gRPC streaming (synchronous)."""
        client_id = pk

        # Parse include_stats from query params
        include_stats = request.query_params.get('include_stats', 'false').lower() == 'true'

        # Create simple client object
        client = type('Client', (), {'client_id': client_id})()

        success, result = self.exec_sync_command(
            client, 'request_status_sync',
            include_stats=include_stats
        )

        if not success:
            return result  # Error response

        # Get updated client metadata
        service = self._get_streaming_service()
        if service:
            connections = service._streaming_service.get_active_connections()
            metadata = connections.get(client_id, {})

            client_data = {
                'client_id': client_id,
                'client_name': metadata.get('client_name', 'Unknown'),
                'connected': True,
                'last_heartbeat': metadata.get('last_heartbeat'),
                'metadata': metadata,
                'wallets_synced': metadata.get('wallets_synced', 0),
                'sync_requests': metadata.get('sync_requests', 0),
                'last_sync': metadata.get('last_sync'),
            }

            serializer = ClientCommandSerializer(client_data)
            return Response({
                **serializer.data,
                'command_result': self.format_command_response(result)
            })

        return Response({
            'client_id': client_id,
            'command_result': self.format_command_response(result)
        })

    # ========================================================================
    # Bulk Actions
    # ========================================================================

    @extend_schema(
        summary='Pause all crypto clients',
        request=None,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def pause_all(self, request):
        """Pause all active crypto clients."""
        service = self._get_streaming_service()
        if not service:
            return Response({
                'error': 'gRPC service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        client_ids = service.get_active_clients()
        results = []

        for client_id in client_ids:
            client = type('Client', (), {'client_id': client_id})()
            success, result = self.exec_sync_command(
                client, 'pause_client_sync',
                timeout=5.0,
                reason='Bulk pause via API'
            )
            results.append({
                'client_id': client_id,
                'success': success,
                'result': self.format_command_response(result) if success else str(result)
            })

        return Response({
            'total': len(client_ids),
            'results': results
        })

    @extend_schema(
        summary='Resume all crypto clients',
        request=None,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def resume_all(self, request):
        """Resume all active crypto clients."""
        service = self._get_streaming_service()
        if not service:
            return Response({
                'error': 'gRPC service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        client_ids = service.get_active_clients()
        results = []

        for client_id in client_ids:
            client = type('Client', (), {'client_id': client_id})()
            success, result = self.exec_sync_command(
                client, 'resume_client_sync',
                timeout=5.0
            )
            results.append({
                'client_id': client_id,
                'success': success,
                'result': self.format_command_response(result) if success else str(result)
            })

        return Response({
            'total': len(client_ids),
            'results': results
        })

    @extend_schema(
        summary='Sync wallets on all crypto clients',
        request=None,
        responses={200: dict},
        parameters=[
            OpenApiParameter(
                name='symbols',
                description='Comma-separated list of coin symbols to sync on all clients',
                required=False,
                type=str,
            ),
        ],
    )
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Trigger wallet sync on all active crypto clients."""
        service = self._get_streaming_service()
        if not service:
            return Response({
                'error': 'gRPC service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Parse symbols from query params
        symbols_str = request.query_params.get('symbols', '')
        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()] if symbols_str else None

        client_ids = service.get_active_clients()
        results = []

        for client_id in client_ids:
            client = type('Client', (), {'client_id': client_id})()
            success, result = self.exec_sync_command(
                client, 'sync_wallets_sync',
                timeout=30.0,
                symbols=symbols
            )
            results.append({
                'client_id': client_id,
                'success': success,
                'result': self.format_command_response(result) if success else str(result)
            })

        return Response({
            'total': len(client_ids),
            'symbols': symbols or 'all',
            'results': results
        })
