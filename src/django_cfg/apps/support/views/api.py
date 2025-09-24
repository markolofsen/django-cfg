"""
Support API Views

REST API ViewSets for tickets and messages.
"""

from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..models import Ticket, Message
from ..serializers import TicketSerializer, MessageSerializer, MessageCreateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for managing support tickets."""
    
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        # Handle swagger fake view
        if getattr(self, 'swagger_fake_view', False):
            return Ticket.objects.none()
        
        if self.request.user.is_staff:
            return Ticket.objects.all().order_by('-created_at')
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing support messages."""
    
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
            OpenApiParameter(
                name='uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the message'
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
            OpenApiParameter(
                name='uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the message'
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
            OpenApiParameter(
                name='uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the message'
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ticket_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the ticket'
            ),
            OpenApiParameter(
                name='uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the message'
            ),
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Handle swagger fake view
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
        
        ticket_uuid = self.kwargs.get('ticket_uuid')
        
        # Base queryset filtered by ticket
        queryset = Message.objects.filter(ticket__uuid=ticket_uuid)
        
        # Additional permission filtering
        if not self.request.user.is_staff:
            queryset = queryset.filter(ticket__user=self.request.user)
        
        return queryset.order_by('created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        ticket_uuid = self.kwargs.get('ticket_uuid')
        ticket = Ticket.objects.get(uuid=ticket_uuid)
        serializer.save(sender=self.request.user, ticket=ticket)
