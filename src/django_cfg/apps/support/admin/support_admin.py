from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from django.utils.timesince import timesince
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_cfg import ExportMixin, ExportForm

from ..models import Ticket, Message
from .filters import TicketUserEmailFilter, TicketUserNameFilter, MessageSenderEmailFilter
from .resources import TicketResource, MessageResource
from django import forms

class MessageInline(TabularInline):
    """Read-only inline for viewing messages. Use Chat interface for replies."""
    
    model = Message
    extra = 0
    fields = ("sender_avatar", "created_at", "text")
    readonly_fields = ("sender_avatar", "created_at", "text")
    show_change_link = False
    classes = ('collapse',)
    
    def has_add_permission(self, request, obj=None):
        """Disable adding messages through admin - use chat interface instead."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting messages through admin."""
        return False

    def sender_avatar(self, obj):
        """Display sender avatar with fallback to initials."""
        if obj.sender.avatar:
            return format_html(
                '<img src="{}" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" />',
                obj.sender.avatar.url
            )
        else:
            initials = obj.sender.__class__.objects.get_initials(obj.sender)
            bg_color = '#0d6efd' if obj.sender.is_staff else '#6f42c1' if obj.sender.is_superuser else '#198754'
            
            return format_html(
                '<div style="width: 24px; height: 24px; border-radius: 50%; background: {}; '
                'color: white; display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; font-size: 10px;">{}</div>',
                bg_color, initials
            )
    sender_avatar.short_description = "Sender"


@admin.register(Ticket)
class TicketAdmin(ModelAdmin, ExportMixin):
    # Export-only configuration
    resource_class = TicketResource
    export_form_class = ExportForm
    list_display = ("user_avatar", "uuid_link", "subject", "status", "last_message_short", "last_message_ago", "chat_link", "created_at")
    list_display_links = ("subject",)
    list_editable = ("status",)
    search_fields = ("uuid", "user__username", "user__email", "subject")
    list_filter = ("status", "created_at", TicketUserEmailFilter, TicketUserNameFilter)
    ordering = ("-created_at",)
    inlines = [MessageInline]
    def get_readonly_fields(self, request, obj=None):
        """Different readonly fields for add/change forms."""
        if obj is None:  # Adding new ticket
            return ("uuid", "created_at")
        else:  # Editing existing ticket
            return ("uuid", "user", "created_at")
    actions_detail = ["open_chat"]
    autocomplete_fields = ["user"]
    def get_fieldsets(self, request, obj=None):
        """Different fieldsets for add/change forms."""
        if obj is None:  # Adding new ticket
            return (
                (None, {
                    "fields": ("user", "subject", "status")
                }),
            )
        else:  # Editing existing ticket
            return (
                (None, {
                    "fields": (("uuid", "user"), "subject", "status", "created_at")
                }),
                ("💬 Chat Interface", {
                    "description": "Use the beautiful Chat interface to reply to this ticket. Click the '💬 Chat' button above.",
                    "fields": (),
                    "classes": ("collapse",)
                }),
            )


    def user_avatar(self, obj):
        """Display user avatar with fallback to initials."""
        if obj.user.avatar:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />',
                obj.user.avatar.url
            )
        else:
            initials = obj.user.__class__.objects.get_initials(obj.user)
            bg_color = '#0d6efd' if obj.user.is_staff else '#6f42c1' if obj.user.is_superuser else '#198754'
            
            return format_html(
                '<div style="width: 32px; height: 32px; border-radius: 50%; background: {}; '
                'color: white; display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; font-size: 12px;">{}</div>',
                bg_color, initials
            )
    user_avatar.short_description = "User"

    def uuid_link(self, obj):
        """Make UUID clickable link to ticket detail."""
        url = reverse('admin:django_cfg_support_ticket_change', args=[obj.uuid])
        return format_html(
            '<a href="{}" style="font-family: monospace; font-size: 11px; background: #f8f9fa; '
            'padding: 2px 4px; border-radius: 3px; text-decoration: none; color: #0d6efd;">{}</a>',
            url, str(obj.uuid)[:8] + '...'
        )
    uuid_link.short_description = "ID"


    def last_message_short(self, obj):
        msg = obj.last_message
        if msg:
            return (msg.text[:40] + '...') if len(msg.text) > 40 else msg.text
        return "-"
    last_message_short.short_description = "Last Message"

    def last_message_ago(self, obj):
        msg = obj.last_message
        if msg:
            return timesince(msg.created_at) + ' ago'
        return "-"
    last_message_ago.short_description = "Last Reply"

    def chat_link(self, obj):
        """Display chat link button in list view."""
        chat_url = reverse('cfg_support:ticket-chat', kwargs={'ticket_uuid': obj.uuid})
        return format_html(
            '<a href="{}" target="_blank" class="btn btn-sm btn-primary" '
            'style="background: #0d6efd; color: white; padding: 4px 8px; '
            'border-radius: 4px; text-decoration: none; font-size: 11px; '
            'display: inline-flex; align-items: center; gap: 4px;">'
            '<svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16">'
            '<path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>'
            '</svg>Chat</a>',
            chat_url
        )
    chat_link.short_description = "💬"

    @action(
        description=_("💬 Open Chat Interface"),
        url_path="chat",
        attrs={"target": "_blank", "class": "btn btn-primary"},
    )
    def open_chat(self, request: HttpRequest, object_id: int):
        """Open the beautiful chat interface for this ticket."""
        ticket = Ticket.objects.get(pk=object_id)
        chat_url = reverse('cfg_support:ticket-chat', kwargs={'ticket_uuid': ticket.uuid})
        return redirect(chat_url)

@admin.register(Message)
class MessageAdmin(ModelAdmin, ExportMixin):
    # Export-only configuration
    resource_class = MessageResource
    export_form_class = ExportForm
    list_display = ("sender_avatar", "uuid", "ticket", "text_short", "created_at")
    list_display_links = ("uuid", "ticket")
    search_fields = ("uuid", "ticket__subject", "sender__username", "sender__email", "text")
    list_filter = ("created_at", MessageSenderEmailFilter)
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "ticket", "sender", "created_at")
    fieldsets = (
        (None, {
            "fields": (("uuid", "ticket"), "sender", "text", "created_at")
        }),
    )

    def sender_avatar(self, obj):
        """Display sender avatar with fallback to initials."""
        if obj.sender.avatar:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />',
                obj.sender.avatar.url
            )
        else:
            initials = obj.sender.__class__.objects.get_initials(obj.sender)
            bg_color = '#0d6efd' if obj.sender.is_staff else '#6f42c1' if obj.sender.is_superuser else '#198754'
            
            return format_html(
                '<div style="width: 32px; height: 32px; border-radius: 50%; background: {}; '
                'color: white; display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; font-size: 12px;">{}</div>',
                bg_color, initials
            )
    sender_avatar.short_description = "Sender"

    def text_short(self, obj):
        """Show shortened message text."""
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text
    text_short.short_description = "Message"
