"""
Command History ViewSet.
"""
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.terminal.models import CommandHistory
from ..serializers import (
    CommandHistoryListSerializer,
    CommandHistoryDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List command history",
        tags=["terminal"],
        parameters=[
            OpenApiParameter(
                name='session',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by session UUID',
                required=False,
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status (SUCCESS, FAILED, etc.)',
                required=False,
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in command text',
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(summary="Get command details", tags=["terminal"]),
)
class TerminalCommandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Terminal Command History (read-only).

    Query parameters:
    - session: Filter by session ID
    - status: Filter by status (SUCCESS, FAILED, etc.)
    - search: Search in command text
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CommandHistory.objects.filter(
            session__user=self.request.user
        ).select_related('session').order_by('-created_at')

        # Session filter
        session_id = self.request.query_params.get('session')
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # Status filter
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(command__icontains=search)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CommandHistoryListSerializer
        return CommandHistoryDetailSerializer
