"""
Support Views Package

Decomposed views for better organization:
- api.py: REST API ViewSets
- chat.py: Chat interface views
- admin.py: Admin-specific views
"""

from .admin import ticket_admin_chat_view
from .api import MessageViewSet, TicketViewSet
from .chat import send_message_ajax, ticket_chat_view

__all__ = [
    'TicketViewSet',
    'MessageViewSet',
    'ticket_chat_view',
    'send_message_ajax',
    'ticket_admin_chat_view',
]
