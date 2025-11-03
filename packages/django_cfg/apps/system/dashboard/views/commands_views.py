"""
Commands ViewSet

Endpoints for Django management commands:
- GET /commands/ - All available commands
- GET /commands/summary/ - Commands summary with statistics
- POST /commands/execute/ - Execute a command with streaming output
- GET /commands/{name}/help/ - Get help for a specific command
"""

import json
import logging

from django.http import StreamingHttpResponse
from django_cfg.mixins import SuperAdminAPIMixin
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import CommandsService
from ..serializers import (
    CommandSerializer,
    CommandsSummarySerializer,
    CommandExecuteRequestSerializer,
    CommandHelpResponseSerializer,
)

logger = logging.getLogger(__name__)


class CommandsViewSet(SuperAdminAPIMixin, viewsets.GenericViewSet):
    """
    Commands ViewSet

    Provides endpoints for Django management commands discovery.
    Requires superuser privileges for all operations.
    """

    serializer_class = CommandSerializer
    pagination_class = None  # Disable pagination for commands list

    @extend_schema(
        summary="Get all commands",
        description="Retrieve all available Django management commands",
        responses=CommandSerializer(many=True),
        tags=["Dashboard - Commands"]
    )
    def list(self, request):
        """Get all Django management commands."""
        try:
            commands_service = CommandsService()
            commands = commands_service.get_all_commands()
            return Response(commands)

        except Exception as e:
            logger.error(f"Commands list API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get commands summary",
        description="Retrieve commands summary with statistics and categorization",
        responses={200: CommandsSummarySerializer},
        tags=["Dashboard - Commands"]
    )
    @action(detail=False, methods=['get'], url_path='summary', serializer_class=CommandsSummarySerializer)
    def summary(self, request):
        """Get commands summary with statistics."""
        try:
            commands_service = CommandsService()
            summary = commands_service.get_commands_summary()
            return Response(summary)

        except Exception as e:
            logger.error(f"Commands summary API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Execute command",
        description="Execute a Django management command and stream output in Server-Sent Events format",
        request=CommandExecuteRequestSerializer,
        responses={
            200: {"description": "Command execution started (SSE stream)"},
            400: {"description": "Invalid request"},
            403: {"description": "Command not allowed"},
        },
        tags=["Dashboard - Commands"]
    )
    @action(detail=False, methods=['post'], url_path='execute', serializer_class=CommandExecuteRequestSerializer)
    def execute(self, request):
        """Execute a Django management command with streaming output."""
        try:
            # Validate request data
            serializer = CommandExecuteRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            command_name = serializer.validated_data['command']
            args = serializer.validated_data.get('args', [])
            options = serializer.validated_data.get('options', {})

            # Create streaming response
            def stream_execution():
                """Generator that streams command output as Server-Sent Events."""
                commands_service = CommandsService()

                for event in commands_service.execute_command(
                    command_name=command_name,
                    args=args,
                    options=options,
                    user=request.user
                ):
                    # Format as Server-Sent Event
                    yield f"data: {json.dumps(event)}\n\n"

            response = StreamingHttpResponse(
                stream_execution(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering

            return response

        except Exception as e:
            logger.error(f"Command execution API error: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get command help",
        description="Get detailed help text for a specific Django management command",
        responses={200: CommandHelpResponseSerializer},
        tags=["Dashboard - Commands"]
    )
    @action(detail=True, methods=['get'], url_path='help', serializer_class=CommandHelpResponseSerializer)
    def help(self, request, pk=None):
        """Get help text for a specific command."""
        try:
            commands_service = CommandsService()
            help_data = commands_service.get_command_help(pk)

            if help_data.get('status') == 'error':
                return Response(help_data, status=status.HTTP_404_NOT_FOUND)

            return Response(help_data)

        except Exception as e:
            logger.error(f"Command help API error: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
