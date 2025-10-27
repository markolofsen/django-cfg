"""
Commands ViewSet

Endpoints for Django management commands:
- GET /commands/ - All available commands
- GET /commands/summary/ - Commands summary with statistics
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..services import CommandsService
from ..serializers import CommandSerializer, CommandsSummarySerializer

logger = logging.getLogger(__name__)


class CommandsViewSet(viewsets.GenericViewSet):
    """
    Commands ViewSet

    Provides endpoints for Django management commands discovery.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]
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
