"""
Chat admin interfaces using Django Admin Utilities.

Enhanced chat management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from django_cfg import ExportMixin

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import ChatSession, ChatMessage


class ChatMessageInline(TabularInline):
    """Inline for chat messages with Unfold styling."""
    
    model = ChatMessage
    verbose_name = "Chat Message"
    verbose_name_plural = "💬 Chat Messages (Read-only)"
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fields = [
        'short_uuid', 'role_badge_inline', 'content_preview_inline', 'tokens_used', 
        'cost_display_inline', 'processing_time_inline', 'created_at'
    ]
    readonly_fields = [
        'short_uuid', 'role_badge_inline', 'content_preview_inline', 'tokens_used', 
        'cost_display_inline', 'processing_time_inline', 'created_at'
    ]
    
    hide_title = False
    classes = ['collapse']
    
    @display(description="Role")
    def role_badge_inline(self, obj):
        """Display message role with color coding for inline."""
        role_variants = {
            'user': 'primary',
            'assistant': 'success', 
            'system': 'info'
        }
        variant = role_variants.get(obj.role, 'secondary')
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PERSON)
        return StatusBadge.create(
            text=obj.role.upper(),
            variant=variant,
            config=config
        )
    
    @display(description="Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "—"
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    
    @display(description="Cost (USD)")
    def cost_display_inline(self, obj):
        """Display cost with currency formatting for inline."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
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
class ChatSessionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ChatSession model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    list_display = [
        'title_display', 'user_display', 'status_display', 'messages_count_display',
        'total_tokens_display', 'total_cost_display', 'last_activity_display', 'created_at_display'
    ]
    list_display_links = ['title_display']
    ordering = ['-updated_at']
    inlines = [ChatMessageInline]
    list_filter = [
        'is_active', 'created_at',
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = ['title', 'user__username', 'user__email']
    autocomplete_fields = ['user']
    readonly_fields = [
        'id', 'user', 'messages_count', 'total_tokens_used', 'total_cost_usd',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('💬 Session Info', {
            'fields': ('id', 'title', 'user', 'is_active'),
            'classes': ('tab',)
        }),
        ('📊 Statistics', {
            'fields': ('message_count', 'total_tokens', 'total_cost_usd'),
            'classes': ('tab',)
        }),
        ('⏰ Activity', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',)
        }),
    )
    
    actions = ['activate_sessions', 'deactivate_sessions', 'clear_old_sessions']
    
    @display(description="Session Title", ordering="title")
    def title_display(self, obj):
        """Display session title."""
        title = obj.title or "Untitled Session"
        if len(title) > 50:
            title = title[:47] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CHAT)
        return StatusBadge.create(
            text=title,
            variant="primary",
            config=config
        )
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Status")
    def status_display(self, obj):
        """Display session status."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PAUSE_CIRCLE)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Messages", ordering="message_count")
    def messages_count_display(self, obj):
        """Display messages count."""
        count = obj.message_count
        return f"{count} messages"
    
    @display(description="Tokens", ordering="total_tokens")
    def total_tokens_display(self, obj):
        """Display total tokens with formatting."""
        tokens = obj.total_tokens
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Cost (USD)", ordering="total_cost_usd")
    def total_cost_display(self, obj):
        """Display total cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return self.display_money_amount(obj, 'total_cost_usd', config)
    
    @display(description="Last Activity", ordering="last_activity_at")
    def last_activity_display(self, obj):
        """Last activity time with relative display."""
        if not obj.last_activity_at:
            return "—"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'last_activity_at', config)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Activate sessions", variant=ActionVariant.SUCCESS)
    def activate_sessions(self, request, queryset):
        """Activate selected sessions."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} sessions.")
    
    @action(description="Deactivate sessions", variant=ActionVariant.WARNING)
    def deactivate_sessions(self, request, queryset):
        """Deactivate selected sessions."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} sessions.")
    
    @action(description="Clear old sessions", variant=ActionVariant.DANGER)
    def clear_old_sessions(self, request, queryset):
        """Clear old inactive sessions."""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=30)
        old_sessions = queryset.filter(is_active=False, last_activity_at__lt=cutoff_date)
        count = old_sessions.count()
        
        if count > 0:
            messages.warning(request, f"Clear old sessions functionality not implemented yet. {count} old sessions found.")
        else:
            messages.info(request, "No old sessions found to clear.")
    
    def changelist_view(self, request, extra_context=None):
        """Add session statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(is_active=True)),
            total_messages=Sum('message_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd')
        )
        
        extra_context['session_stats'] = {
            'total_sessions': stats['total_sessions'] or 0,
            'active_sessions': stats['active_sessions'] or 0,
            'total_messages': stats['total_messages'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}"
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(ChatMessage)
class ChatMessageAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ChatMessage model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['session', 'user']
    
    list_display = [
        'message_display', 'session_display', 'user_display', 'role_display',
        'tokens_display', 'cost_display', 'processing_time_display', 'created_at_display'
    ]
    list_display_links = ['message_display']
    ordering = ['-created_at']
    list_filter = [
        'role', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('session', AutocompleteSelectFilter)
    ]
    search_fields = ['content', 'user__username', 'session__title']
    autocomplete_fields = ['user', 'session']
    readonly_fields = [
        'id', 'user', 'tokens_used', 'cost_usd', 'processing_time_ms',
        'created_at', 'updated_at', 'content_preview'
    ]
    
    fieldsets = (
        ('💬 Message Info', {
            'fields': ('id', 'session', 'user', 'role'),
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ('content_preview', 'content'),
            'classes': ('tab',)
        }),
        ('📊 Metrics', {
            'fields': ('tokens_used', 'cost_usd', 'processing_time_ms'),
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )
    
    actions = ['delete_user_messages', 'delete_assistant_messages']
    
    @display(description="Message", ordering="id")
    def message_display(self, obj):
        """Display message identifier."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.MESSAGE)
        return StatusBadge.create(
            text=f"#{str(obj.id)[:8]}",
            variant="secondary",
            config=config
        )
    
    @display(description="Session", ordering="session__title")
    def session_display(self, obj):
        """Display session title."""
        return obj.session.title or "Untitled Session"
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Role")
    def role_display(self, obj):
        """Display message role with color coding."""
        role_variants = {
            'user': 'primary',
            'assistant': 'success', 
            'system': 'info'
        }
        variant = role_variants.get(obj.role, 'secondary')
        
        role_icons = {
            'user': Icons.PERSON,
            'assistant': Icons.SMART_TOY,
            'system': Icons.SETTINGS
        }
        icon = role_icons.get(obj.role, Icons.MESSAGE)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.role.title(),
            variant=variant,
            config=config
        )
    
    @display(description="Tokens", ordering="tokens_used")
    def tokens_display(self, obj):
        """Display tokens used with formatting."""
        tokens = obj.tokens_used
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Cost (USD)", ordering="cost_usd")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return self.display_money_amount(obj, 'cost_usd', config)
    
    @display(description="Processing Time", ordering="processing_time_ms")
    def processing_time_display(self, obj):
        """Display processing time."""
        ms = obj.processing_time_ms
        if ms < 1000:
            return f"{ms}ms"
        else:
            seconds = ms / 1000
            return f"{seconds:.1f}s"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Content Preview")
    def content_preview(self, obj):
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
    
    @action(description="Delete user messages", variant=ActionVariant.DANGER)
    def delete_user_messages(self, request, queryset):
        """Delete user messages from selection."""
        user_messages = queryset.filter(role='user')
        count = user_messages.count()
        
        if count > 0:
            messages.warning(request, f"Delete user messages functionality not implemented yet. {count} user messages selected.")
        else:
            messages.info(request, "No user messages in selection.")
    
    @action(description="Delete assistant messages", variant=ActionVariant.DANGER)
    def delete_assistant_messages(self, request, queryset):
        """Delete assistant messages from selection."""
        assistant_messages = queryset.filter(role='assistant')
        count = assistant_messages.count()
        
        if count > 0:
            messages.warning(request, f"Delete assistant messages functionality not implemented yet. {count} assistant messages selected.")
        else:
            messages.info(request, "No assistant messages in selection.")
    
    def changelist_view(self, request, extra_context=None):
        """Add message statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_messages=Count('id'),
            user_messages=Count('id', filter=Q(role='user')),
            assistant_messages=Count('id', filter=Q(role='assistant')),
            system_messages=Count('id', filter=Q(role='system')),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost_usd'),
            avg_processing_time=Avg('processing_time_ms')
        )
        
        extra_context['message_stats'] = {
            'total_messages': stats['total_messages'] or 0,
            'user_messages': stats['user_messages'] or 0,
            'assistant_messages': stats['assistant_messages'] or 0,
            'system_messages': stats['system_messages'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'avg_processing_time': f"{(stats['avg_processing_time'] or 0):.0f}ms"
        }
        
        return super().changelist_view(request, extra_context)
