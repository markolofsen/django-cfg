"""
Support admin interfaces using Django Admin Utilities.

Enhanced support ticket management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.timesince import timesince
from django.utils.html import format_html
from django.db import models
from django.db.models import Count, Q
from unfold.admin import ModelAdmin, TabularInline
from django_cfg import ExportMixin, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import Ticket, Message
from .filters import TicketUserEmailFilter, TicketUserNameFilter, MessageSenderEmailFilter
from .resources import TicketResource, MessageResource


class MessageInline(TabularInline):
    """Read-only inline for viewing messages. Use Chat interface for replies."""
    
    model = Message
    extra = 0
    fields = ["sender_display", "created_at", "text_preview"]
    readonly_fields = ["sender_display", "created_at", "text_preview"]
    show_change_link = False
    classes = ('collapse',)
    
    def has_add_permission(self, request, obj=None):
        """Disable adding messages through admin - use chat interface instead."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting messages through admin."""
        return False

    @display(description="Sender")
    def sender_display(self, obj):
        """Display sender with badge."""
        if not obj.sender:
            return "—"
        
        # Determine sender type and variant
        if obj.sender.is_superuser:
            variant = "danger"
            icon = Icons.ADMIN_PANEL_SETTINGS
        elif obj.sender.is_staff:
            variant = "primary"
            icon = Icons.SUPPORT_AGENT
        else:
            variant = "info"
            icon = Icons.PERSON
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.sender.get_full_name() or obj.sender.username,
            variant=variant,
            config=config
        )
    
    @display(description="Message")
    def text_preview(self, obj):
        """Display message preview."""
        if not obj.text:
            return "—"
        
        preview = obj.text[:100]
        if len(obj.text) > 100:
            preview += "..."
        
        return preview


@admin.register(Ticket)
class TicketAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for Ticket using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    # Export-only configuration
    resource_class = TicketResource
    export_form_class = ExportForm
    
    list_display = [
        "user_display", "uuid_display", "subject_display", "status_display", 
        "last_message_display", "last_message_ago_display", "chat_link_display", "created_at_display"
    ]
    list_display_links = ["subject_display"]
    ordering = ["-created_at"]
    search_fields = ["uuid", "user__username", "user__email", "subject"]
    list_filter = ["status", "created_at", TicketUserEmailFilter, TicketUserNameFilter]
    inlines = [MessageInline]
    autocomplete_fields = ["user"]
    
    actions = ["mark_as_open", "mark_as_waiting_for_user", "mark_as_waiting_for_admin", "mark_as_resolved", "mark_as_closed"]
    
    def get_readonly_fields(self, request, obj=None):
        """Different readonly fields for add/change forms."""
        if obj is None:  # Adding new ticket
            return ("uuid", "created_at")
        else:  # Editing existing ticket
            return ("uuid", "user", "created_at")
    
    def get_fieldsets(self, request, obj=None):
        """Different fieldsets for add/change forms."""
        if obj is None:  # Adding new ticket
            return (
                ('🎫 New Ticket', {
                    "fields": ("user", "subject", "status"),
                    "classes": ("tab",)
                }),
            )
        else:  # Editing existing ticket
            return (
                ('🎫 Ticket Information', {
                    "fields": (("uuid", "user"), "subject", "status", "created_at"),
                    "classes": ("tab",)
                }),
                ('💬 Chat Interface', {
                    "description": "Use the Chat interface to reply to this ticket. Click the Chat button.",
                    "fields": (),
                    "classes": ("tab", "collapse")
                }),
            )

    @display(description="User")
    def user_display(self, obj: Ticket) -> str:
        """Display user with avatar representation."""
        if not obj.user:
            return "—"

        # Use simple user display from DisplayMixin
        from django_cfg.modules.django_admin.models.display_models import UserDisplayConfig
        config = UserDisplayConfig(show_email=True)
        return self.display_user_simple(obj, 'user', config)

    @display(description="UUID", ordering="uuid")
    def uuid_display(self, obj: Ticket) -> str:
        """Display ticket UUID."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CONFIRMATION_NUMBER)
        return StatusBadge.create(
            text=str(obj.uuid)[:8] + "...",
            variant="secondary",
            config=config
        )

    @display(description="Subject", ordering="subject")
    def subject_display(self, obj: Ticket) -> str:
        """Display ticket subject."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SUBJECT)
        return StatusBadge.create(
            text=obj.subject,
            variant="primary",
            config=config
        )

    @display(description="Status")
    def status_display(self, obj: Ticket) -> str:
        """Display ticket status with color coding."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'open': 'info',
                'waiting_for_user': 'warning',
                'waiting_for_admin': 'primary',
                'resolved': 'success',
                'closed': 'secondary'
            },
            show_icons=True,
            icon=Icons.NEW_RELEASES if obj.status == 'open' else Icons.PENDING if obj.status == 'waiting_for_user' else Icons.SUPPORT_AGENT if obj.status == 'waiting_for_admin' else Icons.CHECK_CIRCLE if obj.status == 'resolved' else Icons.ARCHIVE
        )
        return self.display_status_auto(obj, 'status', status_config)

    @display(description="Last Message")
    def last_message_display(self, obj: Ticket) -> str:
        """Display last message preview."""
        last_message = obj.messages.order_by('-created_at').first()
        if not last_message:
            return "No messages"

        preview = last_message.text[:50]
        if len(last_message.text) > 50:
            preview += "..."

        return preview

    @display(description="Last Activity")
    def last_message_ago_display(self, obj: Ticket) -> str:
        """Display time since last message."""
        last_message = obj.messages.order_by('-created_at').first()
        if not last_message:
            return "—"

        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(last_message, 'created_at', config)

    @display(description="Chat")
    def chat_link_display(self, obj: Ticket) -> str:
        """Display clickable chat link button."""
        chat_url = reverse('cfg_support:ticket-chat', kwargs={'ticket_uuid': obj.uuid})
        return format_html(
            '<a href="{}" target="_blank" '
            'style="background: #0d6efd; color: white; padding: 6px 12px; '
            'border-radius: 6px; text-decoration: none; font-size: 12px; '
            'display: inline-flex; align-items: center; gap: 6px; font-weight: 500;">'
            '<svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">'
            '<path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>'
            '</svg>Open Chat</a>',
            chat_url
        )

    @display(description="Created")
    def created_at_display(self, obj: Ticket) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)

    @action(description="Mark as open", variant=ActionVariant.INFO)
    def mark_as_open(self, request: HttpRequest, queryset) -> None:
        """Mark selected tickets as open."""
        count = queryset.update(status='open')
        messages.info(request, f"Marked {count} tickets as open.")

    @action(description="Mark as waiting for user", variant=ActionVariant.WARNING)
    def mark_as_waiting_for_user(self, request: HttpRequest, queryset) -> None:
        """Mark selected tickets as waiting for user."""
        count = queryset.update(status='waiting_for_user')
        messages.warning(request, f"Marked {count} tickets as waiting for user.")

    @action(description="Mark as waiting for admin", variant=ActionVariant.PRIMARY)
    def mark_as_waiting_for_admin(self, request: HttpRequest, queryset) -> None:
        """Mark selected tickets as waiting for admin."""
        count = queryset.update(status='waiting_for_admin')
        messages.info(request, f"Marked {count} tickets as waiting for admin.")

    @action(description="Mark as resolved", variant=ActionVariant.SUCCESS)
    def mark_as_resolved(self, request: HttpRequest, queryset) -> None:
        """Mark selected tickets as resolved."""
        count = queryset.update(status='resolved')
        messages.success(request, f"Marked {count} tickets as resolved.")

    @action(description="Mark as closed", variant=ActionVariant.DANGER)
    def mark_as_closed(self, request: HttpRequest, queryset) -> None:
        """Mark selected tickets as closed."""
        count = queryset.update(status='closed')
        messages.error(request, f"Marked {count} tickets as closed.")

    def changelist_view(self, request, extra_context=None):
        """Add ticket statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_tickets=Count('uuid'),
            open_tickets=Count('uuid', filter=Q(status='open')),
            waiting_for_user_tickets=Count('uuid', filter=Q(status='waiting_for_user')),
            waiting_for_admin_tickets=Count('uuid', filter=Q(status='waiting_for_admin')),
            resolved_tickets=Count('uuid', filter=Q(status='resolved')),
            closed_tickets=Count('uuid', filter=Q(status='closed'))
        )
        
        extra_context['ticket_stats'] = {
            'total_tickets': stats['total_tickets'] or 0,
            'open_tickets': stats['open_tickets'] or 0,
            'waiting_for_user_tickets': stats['waiting_for_user_tickets'] or 0,
            'waiting_for_admin_tickets': stats['waiting_for_admin_tickets'] or 0,
            'resolved_tickets': stats['resolved_tickets'] or 0,
            'closed_tickets': stats['closed_tickets'] or 0
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(Message)
class MessageAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for Message using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['ticket', 'sender']
    
    # Export-only configuration
    resource_class = MessageResource
    export_form_class = ExportForm
    
    list_display = [
        "ticket_display", "sender_display", "text_preview", "created_at_display"
    ]
    list_display_links = ["text_preview"]
    ordering = ["-created_at"]
    search_fields = ["ticket__uuid", "ticket__subject", "sender__username", "sender__email", "text"]
    list_filter = ["created_at", "ticket__status", MessageSenderEmailFilter]
    readonly_fields = ["ticket", "sender", "created_at"]
    
    fieldsets = [
        ('💬 Message Information', {
            'fields': ['ticket', 'sender', 'text'],
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ['created_at'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    def has_add_permission(self, request):
        """Disable adding messages through admin - use chat interface instead."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing messages through admin."""
        return False

    @display(description="Ticket")
    def ticket_display(self, obj: Message) -> str:
        """Display ticket information."""
        if not obj.ticket:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CONFIRMATION_NUMBER)
        return StatusBadge.create(
            text=f"{obj.ticket.subject} ({str(obj.ticket.uuid)[:8]}...)",
            variant="primary",
            config=config
        )

    @display(description="Sender")
    def sender_display(self, obj: Message) -> str:
        """Display sender with role indication."""
        if not obj.sender:
            return "—"
        
        # Determine sender type and variant
        if obj.sender.is_superuser:
            variant = "danger"
            icon = Icons.ADMIN_PANEL_SETTINGS
        elif obj.sender.is_staff:
            variant = "primary"
            icon = Icons.SUPPORT_AGENT
        else:
            variant = "info"
            icon = Icons.PERSON
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.sender.get_full_name() or obj.sender.username,
            variant=variant,
            config=config
        )

    @display(description="Message", ordering="text")
    def text_preview(self, obj: Message) -> str:
        """Display message text preview."""
        if not obj.text:
            return "—"
        
        preview = obj.text[:100]
        if len(obj.text) > 100:
            preview += "..."
        
        return preview

    @display(description="Created")
    def created_at_display(self, obj: Message) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)

    def changelist_view(self, request, extra_context=None):
        """Add message statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_messages=Count('uuid'),
            staff_messages=Count('uuid', filter=Q(sender__is_staff=True)),
            user_messages=Count('uuid', filter=Q(sender__is_staff=False))
        )
        
        # Messages by ticket status
        ticket_status_counts = dict(
            queryset.values_list('ticket__status').annotate(
                count=Count('uuid')
            )
        )
        
        extra_context['message_stats'] = {
            'total_messages': stats['total_messages'] or 0,
            'staff_messages': stats['staff_messages'] or 0,
            'user_messages': stats['user_messages'] or 0,
            'ticket_status_counts': ticket_status_counts
        }
        
        return super().changelist_view(request, extra_context)
