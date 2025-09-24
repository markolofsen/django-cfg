"""
Import/Export resources for Support app.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget, BooleanWidget
from django.contrib.auth import get_user_model

from ..models import Ticket, Message

User = get_user_model()


class TicketResource(resources.ModelResource):
    """Resource for exporting tickets (export only)."""
    
    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        readonly=True
    )
    
    user_full_name = fields.Field(
        column_name='user_full_name',
        attribute='user__get_full_name',
        readonly=True
    )
    
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display',
        readonly=True
    )
    
    messages_count = fields.Field(
        column_name='messages_count',
        readonly=True
    )
    
    last_message_text = fields.Field(
        column_name='last_message_text',
        readonly=True
    )
    
    last_message_at = fields.Field(
        column_name='last_message_at',
        readonly=True,
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    unanswered_messages_count = fields.Field(
        column_name='unanswered_messages_count',
        attribute='unanswered_messages_count',
        readonly=True
    )
    
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = Ticket
        fields = (
            'uuid',
            'user_email',
            'user_full_name',
            'subject',
            'status',
            'status_display',
            'messages_count',
            'last_message_text',
            'last_message_at',
            'unanswered_messages_count',
            'created_at',
        )
        export_order = fields
        # No import - this is export only
        
    def dehydrate_messages_count(self, ticket):
        """Calculate messages count for export."""
        return ticket.messages.count()
        
    def dehydrate_last_message_text(self, ticket):
        """Get last message text for export."""
        last_message = ticket.last_message
        if last_message:
            # Truncate long messages
            text = last_message.text
            return text[:100] + '...' if len(text) > 100 else text
        return ''
        
    def dehydrate_last_message_at(self, ticket):
        """Get last message timestamp for export."""
        last_message = ticket.last_message
        return last_message.created_at if last_message else None
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('user').prefetch_related('messages')


class MessageResource(resources.ModelResource):
    """Resource for exporting messages (export only)."""
    
    ticket_uuid = fields.Field(
        column_name='ticket_uuid',
        attribute='ticket__uuid',
        readonly=True
    )
    
    ticket_subject = fields.Field(
        column_name='ticket_subject',
        attribute='ticket__subject',
        readonly=True
    )
    
    sender_email = fields.Field(
        column_name='sender_email',
        attribute='sender__email',
        readonly=True
    )
    
    sender_full_name = fields.Field(
        column_name='sender_full_name',
        attribute='sender__get_full_name',
        readonly=True
    )
    
    is_from_author = fields.Field(
        column_name='is_from_author',
        attribute='is_from_author',
        widget=BooleanWidget(),
        readonly=True
    )
    
    is_from_staff = fields.Field(
        column_name='is_from_staff',
        readonly=True,
        widget=BooleanWidget()
    )
    
    text_preview = fields.Field(
        column_name='text_preview',
        readonly=True
    )
    
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = Message
        fields = (
            'uuid',
            'ticket_uuid',
            'ticket_subject',
            'sender_email',
            'sender_full_name',
            'is_from_author',
            'is_from_staff',
            'text',
            'text_preview',
            'created_at',
        )
        export_order = fields
        # No import - this is export only
        
    def dehydrate_is_from_staff(self, message):
        """Check if message is from staff member."""
        return message.sender.is_staff
        
    def dehydrate_text_preview(self, message):
        """Get truncated text preview for export."""
        text = message.text
        return text[:200] + '...' if len(text) > 200 else text
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('ticket', 'sender')
