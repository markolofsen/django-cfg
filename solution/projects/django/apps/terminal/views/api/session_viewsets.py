"""
Terminal Session ViewSet.
"""
import base64
import logging

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.terminal.models import TerminalSession
from ..serializers import (
    TerminalSessionListSerializer,
    TerminalSessionDetailSerializer,
    TerminalSessionCreateSerializer,
    TerminalInputSerializer,
    TerminalResizeSerializer,
    TerminalSignalSerializer,
    CommandHistoryListSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List user's terminal sessions", tags=["terminal"]),
    retrieve=extend_schema(summary="Get session details", tags=["terminal"]),
    create=extend_schema(summary="Create new terminal session", tags=["terminal"]),
    destroy=extend_schema(summary="Close terminal session", tags=["terminal"]),
)
class TerminalSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Terminal Session management.

    Provides REST API for:
    - Creating/listing/closing terminal sessions
    - Sending input to terminal
    - Resizing terminal
    - Sending signals (SIGINT, SIGTERM, SIGKILL)

    Real-time output is delivered via Centrifugo WebSocket:
    - Channel: terminal#session#{session_id}
    - Events: output, status, error, command_complete
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """Get all terminal sessions."""
        return TerminalSession.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return TerminalSessionListSerializer
        elif self.action == 'create':
            return TerminalSessionCreateSerializer
        elif self.action == 'input':
            return TerminalInputSerializer
        elif self.action == 'resize':
            return TerminalResizeSerializer
        elif self.action == 'signal':
            return TerminalSignalSerializer
        return TerminalSessionDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new terminal session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = TerminalSession.objects.create(
            user=request.user,
            name=serializer.validated_data.get('name', ''),
            shell=serializer.validated_data.get('shell', '/bin/zsh'),
            working_directory=serializer.validated_data.get('working_directory', '~'),
            environment=serializer.validated_data.get('environment', {}),
            status=TerminalSession.Status.PENDING,
        )

        return Response(
            TerminalSessionDetailSerializer(session).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """Close terminal session."""
        session = self.get_object()

        # Send close command via gRPC if session is active
        if session.is_active:
            try:
                from apps.terminal.grpc.services.handlers import get_terminal_service
                import asyncio

                service = get_terminal_service()
                if service:
                    asyncio.run(service.close_session(str(session.id), "Closed via API"))
            except Exception as e:
                logger.warning(f"Failed to send close command: {e}")

        session.status = TerminalSession.Status.DISCONNECTED
        session.save(update_fields=['status'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    # ==================== Custom Actions ====================

    @extend_schema(
        summary="Send input to terminal",
        request=TerminalInputSerializer,
        responses={200: dict, 400: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def input(self, request, pk=None):
        """Send input data to terminal session."""
        session = self.get_object()

        if not session.is_active:
            return Response(
                {'error': 'session_not_active', 'message': 'Session is not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TerminalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Decode data
        data_str = serializer.validated_data.get('data', '')
        if serializer.validated_data.get('data_base64'):
            data = base64.b64decode(serializer.validated_data['data_base64'])
        else:
            data = data_str.encode('utf-8')

        # Send via gRPC
        success = self._send_input(session, data)

        if success:
            return Response({'status': 'sent', 'bytes': len(data)})
        else:
            return Response(
                {'error': 'send_failed', 'message': 'Failed to send input'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Resize terminal",
        request=TerminalResizeSerializer,
        responses={200: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def resize(self, request, pk=None):
        """Resize terminal dimensions."""
        session = self.get_object()

        serializer = TerminalResizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = self._send_resize(
            session,
            cols=serializer.validated_data['cols'],
            rows=serializer.validated_data['rows']
        )

        if success:
            return Response({
                'status': 'resized',
                'cols': serializer.validated_data['cols'],
                'rows': serializer.validated_data['rows']
            })
        else:
            return Response(
                {'error': 'resize_failed', 'message': 'Failed to resize terminal'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Send signal to terminal",
        request=TerminalSignalSerializer,
        responses={200: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def signal(self, request, pk=None):
        """Send signal to terminal process (SIGINT, SIGTERM, SIGKILL)."""
        session = self.get_object()

        serializer = TerminalSignalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signal_num = serializer.validated_data['signal']
        success = self._send_signal(session, signal_num)

        signal_names = {2: 'SIGINT', 9: 'SIGKILL', 15: 'SIGTERM'}

        if success:
            return Response({
                'status': 'sent',
                'signal': signal_num,
                'signal_name': signal_names.get(signal_num, 'UNKNOWN')
            })
        else:
            return Response(
                {'error': 'signal_failed', 'message': 'Failed to send signal'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Get command history for session",
        tags=["terminal"],
        responses={200: CommandHistoryListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get command history for this session with pagination."""
        session = self.get_object()
        queryset = session.commands.order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommandHistoryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommandHistoryListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active sessions only",
        tags=["terminal"],
        responses={200: TerminalSessionListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """List only active (connected) sessions with pagination."""
        queryset = self.get_queryset().filter(
            status=TerminalSession.Status.CONNECTED
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TerminalSessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TerminalSessionListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ==================== Internal Methods ====================

    def _send_input(self, session, data: bytes) -> bool:
        """Send input via gRPC."""
        try:
            from apps.terminal.grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_input(str(session.id), data))
        except Exception as e:
            logger.error(f"Failed to send input: {e}")
        return False

    def _send_resize(self, session, cols: int, rows: int) -> bool:
        """Send resize via gRPC."""
        try:
            from apps.terminal.grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_resize(str(session.id), cols, rows))
        except Exception as e:
            logger.error(f"Failed to send resize: {e}")
        return False

    def _send_signal(self, session, signal: int) -> bool:
        """Send signal via gRPC."""
        try:
            from apps.terminal.grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_signal(str(session.id), signal))
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
        return False
