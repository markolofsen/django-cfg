"""
Chat admin interfaces with Unfold optimization.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from django_cfg import ExportMixin

from ..models import ChatSession, ChatMessage


class ChatMessageInline(TabularInline):
    """Inline for chat messages with Unfold styling."""
    
    model = ChatMessage
    verbose_name = "Chat Message"
    verbose_name_plural = "💬 Chat Messages (Read-only)"
    extra = 0
    max_num = 0  # No new messages allowed
    can_delete = False  # Prevent deletion through inline
    show_change_link = True  # Allow viewing individual messages
    
    def has_add_permission(self, request, obj=None):
        """Disable adding new messages through inline."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing messages through inline."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting messages through inline."""
        return False
    
    fields = [
        'short_uuid', 'role_badge_inline', 'content_preview_inline', 'tokens_used', 
        'cost_display_inline', 'processing_time_inline', 'created_at'
    ]
    readonly_fields = [
        'short_uuid', 'role_badge_inline', 'content_preview_inline', 'tokens_used', 
        'cost_display_inline', 'processing_time_inline', 'created_at'
    ]
    
    # Unfold specific options
    hide_title = False  # Show titles for better UX
    classes = ['collapse']  # Collapsed by default
    
    @display(description="Role")
    def role_badge_inline(self, obj):
        """Display message role with color coding for inline."""
        role_colors = {
            'user': '#2563eb',
            'assistant': '#059669', 
            'system': '#7c3aed'
        }
        color = role_colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 1px 6px; '
            'border-radius: 8px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.role.upper()
        )
    
    @display(description="Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "-"
        preview = obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
        return format_html(
            '<div style="max-width: 250px; font-size: 12px; color: #666; '
            'font-family: monospace;">{}</div>',
            preview
        )
    
    @display(description="Cost (USD)")
    def cost_display_inline(self, obj):
        """Display cost with currency formatting for inline."""
        return f"${obj.cost_usd:.6f}"
    
    @display(description="Time")
    def processing_time_inline(self, obj):
        """Display processing time in compact format for inline."""
        ms = obj.processing_time_ms
        if ms < 1000:
            return f"{ms}ms"
        else:
            seconds = ms / 1000
            return f"{seconds:.1f}s"
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('session', 'user').order_by('created_at')


@admin.register(ChatSession)
class ChatSessionAdmin(ModelAdmin, ExportMixin):
    """Admin interface for ChatSession model with Unfold styling."""
    
    list_display = [
        'short_uuid', 'title_display', 'user', 'status_badge', 'messages_count',
        'tokens_display', 'cost_display', 'model_name', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    inlines = [ChatMessageInline]
    list_filter = [
        'is_active', 'model_name', 'created_at',
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = ['title', 'user__username', 'user__email']
    autocomplete_fields = ['user']
    readonly_fields = [
        'id', 'messages_count', 'total_tokens_used', 'total_cost_usd',
        'created_at', 'updated_at', 'avg_tokens_per_message'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'user', 'is_active')
        }),
        ('Configuration', {
            'fields': ('model_name', 'temperature', 'max_context_chunks')
        }),
        ('Statistics', {
            'fields': (
                'messages_count', 'total_tokens_used', 'total_cost_usd',
                'avg_tokens_per_message'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')
    
    @display(description="Session Title", ordering="title")
    def title_display(self, obj):
        """Display session title with truncation."""
        title = obj.title or "Untitled Session"
        if len(title) > 50:
            title = title[:47] + "..."
        return format_html(
            '<div style="font-weight: 500;">{}</div>',
            title
        )
    
    @display(description="Status", ordering="is_active")
    def status_badge(self, obj):
        """Display session status with color coding."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: gray; font-weight: bold;">● Inactive</span>'
        )
    
    @display(description="Tokens", ordering="total_tokens_used")
    def tokens_display(self, obj):
        """Display token usage with formatting."""
        tokens = obj.total_tokens_used
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Cost (USD)", ordering="total_cost_usd")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        return f"${obj.total_cost_usd:.6f}"
    
    @display(description="Avg Tokens/Message")
    def avg_tokens_per_message(self, obj):
        """Calculate average tokens per message."""
        if obj.messages_count > 0:
            avg = obj.total_tokens_used / obj.messages_count
            return f"{avg:.0f}"
        return "0"
    
    def changelist_view(self, request, extra_context=None):
        """Add session statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(is_active=True)),
            total_messages=Sum('messages_count'),
            total_tokens=Sum('total_tokens_used'),
            total_cost=Sum('total_cost_usd'),
            avg_messages_per_session=Avg('messages_count')
        )
        
        # Model breakdown
        model_counts = dict(
            queryset.values_list('model_name').annotate(
                count=Count('id')
            )
        )
        
        extra_context['session_stats'] = {
            'total_sessions': stats['total_sessions'] or 0,
            'active_sessions': stats['active_sessions'] or 0,
            'total_messages': stats['total_messages'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'avg_messages_per_session': f"{(stats['avg_messages_per_session'] or 0):.1f}",
            'model_counts': model_counts
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin, ExportMixin):
    """Admin interface for ChatMessage model with Unfold styling."""
    
    list_display = [
        'short_uuid', 'session_link', 'role_badge', 'content_preview', 'user',
        'tokens_display', 'cost_display', 'processing_time_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    list_filter = [
        'role', 'model_name', 'finish_reason', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('session', AutocompleteSelectFilter)
    ]
    search_fields = ['session__title', 'user__username', 'content']
    readonly_fields = [
        'id', 'tokens_used', 'cost_usd', 'processing_time_ms',
        'created_at', 'updated_at', 'content_stats'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'session', 'user', 'role')
        }),
        ('Content', {
            'fields': ('content', 'content_stats')
        }),
        ('Context', {
            'fields': ('context_chunks',),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('tokens_used', 'cost_usd', 'processing_time_ms')
        }),
        ('Response Metadata', {
            'fields': ('model_name', 'finish_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('session', 'user')
    
    @display(description="Session", ordering="session__title")
    def session_link(self, obj):
        """Display session title with admin link."""
        url = reverse('admin:django_cfg_knowbase_chatsession_change', args=[obj.session.id])
        title = obj.session.title or "Untitled Session"
        if len(title) > 30:
            title = title[:27] + "..."
        return format_html(
            '<a href="{}" style="text-decoration: none;">{}</a>',
            url,
            title
        )
    
    @display(description="Role", ordering="role")
    def role_badge(self, obj):
        """Display message role with color coding."""
        role_colors = {
            'user': '#2563eb',
            'assistant': '#059669',
            'system': '#7c3aed'
        }
        color = role_colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: 500;">{}</span>',
            color,
            obj.role.upper()
        )
    
    @display(description="Content Preview")
    def content_preview(self, obj):
        """Display content preview with truncation."""
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return format_html(
            '<div style="max-width: 300px; word-wrap: break-word; '
            'font-family: monospace; font-size: 13px;">{}</div>',
            preview
        )
    
    @display(description="Tokens", ordering="tokens_used")
    def tokens_display(self, obj):
        """Display token usage with formatting."""
        tokens = obj.tokens_used
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Cost (USD)", ordering="cost_usd")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        return f"${obj.cost_usd:.6f}"
    
    @display(description="Processing Time", ordering="processing_time_ms")
    def processing_time_display(self, obj):
        """Display processing time in readable format."""
        ms = obj.processing_time_ms
        if ms < 1000:
            return f"{ms}ms"
        else:
            seconds = ms / 1000
            return f"{seconds:.1f}s"
    
    @display(description="Content Statistics")
    def content_stats(self, obj):
        """Display content statistics."""
        char_count = len(obj.content)
        word_count = len(obj.content.split())
        return format_html(
            '<div style="font-size: 12px; color: #6b7280;">'
            'Characters: {} | Words: {} | Context Chunks: {}</div>',
            char_count,
            word_count,
            len(obj.context_chunks)
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add message statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_messages=Count('id'),
            user_messages=Count('id', filter=Q(role='user')),
            assistant_messages=Count('id', filter=Q(role='assistant')),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost_usd'),
            avg_processing_time=Avg('processing_time_ms'),
            avg_tokens_per_message=Avg('tokens_used')
        )
        
        # Role breakdown
        role_counts = dict(
            queryset.values_list('role').annotate(
                count=Count('id')
            )
        )
        
        extra_context['message_stats'] = {
            'total_messages': stats['total_messages'] or 0,
            'user_messages': stats['user_messages'] or 0,
            'assistant_messages': stats['assistant_messages'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'avg_processing_time': f"{(stats['avg_processing_time'] or 0):.0f}ms",
            'avg_tokens_per_message': f"{(stats['avg_tokens_per_message'] or 0):.0f}",
            'role_counts': role_counts
        }
        
        return super().changelist_view(request, extra_context)
