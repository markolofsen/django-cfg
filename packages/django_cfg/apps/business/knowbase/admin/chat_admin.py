"""
Chat Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced chat management with Material Icons and clean declarative config.
"""

from django.contrib import admin, messages
from django.db.models import Avg, Count, Q, Sum
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from django_cfg import ExportMixin
from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
    computed_field
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import ChatMessage, ChatSession
from .chat_actions import (
    activate_sessions,
    clear_old_sessions,
    deactivate_sessions,
    delete_assistant_messages,
    delete_user_messages,
)


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

    def role_badge_inline(self, obj):
        """Display message role with color coding for inline."""
        role_variants = {
            'user': 'primary',
            'assistant': 'success',
            'system': 'info'
        }
        variant = role_variants.get(obj.role, 'secondary')

        # Note: self.html is not available in inline context
        # We'll use a simple HTML string for now
        from django.utils.html import format_html
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            variant,
            obj.role.upper()
        )
    role_badge_inline.short_description = "Role"

    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "—"
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    content_preview_inline.short_description = "Content Preview"

    def cost_display_inline(self, obj):
        """Display cost with currency formatting for inline."""
        return f"${obj.cost_usd:.6f}"
    cost_display_inline.short_description = "Cost (USD)"

    def processing_time_inline(self, obj):
        """Display processing time in compact format for inline."""
        ms = obj.processing_time_ms
        if ms < 1000:
            return f"{ms}ms"
        else:
            seconds = ms / 1000
            return f"{seconds:.1f}s"
    processing_time_inline.short_description = "Time"

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('session', 'user').order_by('created_at')


# ===== ChatSession Admin Config =====

chat_session_config = AdminConfig(
    model=ChatSession,

    # Performance optimization
    select_related=['user'],

    # List display
    list_display=[
        'title_display',
        'user_display',
        'status_display',
        'messages_count_display',
        'total_tokens_display',
        'total_cost_display',
        'last_activity_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="title",
            title="Session Title",
            variant="primary",
            icon=Icons.CHAT,
            header=True
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        TextField(
            name="messages_count",
            title="Messages",
            ordering="messages_count"
        ),
        TextField(
            name="total_tokens",
            title="Tokens",
            ordering="total_tokens"
        ),
        TextField(
            name="total_cost_usd",
            title="Cost (USD)",
            ordering="total_cost_usd"
        ),
        DateTimeField(
            name="last_activity_at",
            title="Last Activity",
            ordering="last_activity_at"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['title', 'user__username', 'user__email'],
    list_filter=[
        'is_active',
        'created_at',
        ('user', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['title_display'],

    # Autocomplete fields
    autocomplete_fields=['user'],

    # Ordering
    ordering=['-updated_at'],

    # Actions
    actions=[
        ActionConfig(
            name="activate_sessions",
            description="Activate sessions",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_sessions
        ),
        ActionConfig(
            name="deactivate_sessions",
            description="Deactivate sessions",
            variant="warning",
            icon=Icons.PAUSE_CIRCLE,
            handler=deactivate_sessions
        ),
        ActionConfig(
            name="clear_old_sessions",
            description="Clear old sessions",
            variant="danger",
            icon=Icons.DELETE,
            confirmation=True,
            handler=clear_old_sessions
        ),
    ],
)


@admin.register(ChatSession)
class ChatSessionAdmin(PydanticAdmin):
    """
    ChatSession admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality
    - Custom actions for session management (using ActionConfig)
    - Statistics in changelist_view
    """
    config = chat_session_config

    # Readonly fields
    readonly_fields = [
        'id', 'user', 'messages_count', 'total_tokens_used', 'total_cost_usd',
        'created_at', 'updated_at'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Session Info",
            fields=['title', 'is_active']
        ),
        FieldsetConfig(
            title="Statistics",
            fields=['messages_count', 'total_tokens_used', 'total_cost_usd']
        ),
        FieldsetConfig(
            title="Activity",
            fields=['created_at', 'updated_at']
        ),
    ]

    # Inlines
    inlines = [ChatMessageInline]

    # Custom display methods using @computed_field decorator
    @computed_field("Session Title")
    def title_display(self, obj: ChatSession) -> str:
        """Display session title."""
        title = obj.title or "Untitled Session"
        if len(title) > 50:
            title = title[:47] + "..."

        return self.html.badge(title, variant="primary", icon=Icons.CHAT)

    @computed_field("User")
    def user_display(self, obj: ChatSession) -> str:
        """User display."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Status")
    def status_display(self, obj: ChatSession) -> str:
        """Display session status."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.PAUSE_CIRCLE)

    @computed_field("Messages")
    def messages_count_display(self, obj: ChatSession) -> str:
        """Display messages count."""
        count = obj.messages_count
        return f"{count} messages"

    @computed_field("Tokens")
    def total_tokens_display(self, obj: ChatSession) -> str:
        """Display total tokens with formatting."""
        tokens = obj.total_tokens
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Cost (USD)")
    def total_cost_display(self, obj: ChatSession) -> str:
        """Display total cost with currency formatting."""
        return f"${obj.total_cost_usd:.6f}"

    @computed_field("Last Activity")
    def last_activity_display(self, obj: ChatSession) -> str:
        """Last activity time with relative display."""
        if not obj.last_activity_at:
            return "—"
        # DateTimeField in display_fields handles formatting automatically
        return obj.last_activity_at

    @computed_field("Created")
    def created_at_display(self, obj: ChatSession) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    def changelist_view(self, request, extra_context=None):
        """Add session statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(is_active=True)),
            total_messages=Sum('messages_count'),
            total_tokens=Sum('total_tokens_used'),
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


# ===== ChatMessage Admin Config =====

chat_message_config = AdminConfig(
    model=ChatMessage,

    # Performance optimization
    select_related=['session', 'user'],

    # List display
    list_display=[
        'message_display',
        'session_display',
        'user_display',
        'role_display',
        'tokens_display',
        'cost_display',
        'processing_time_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="id",
            title="Message",
            variant="secondary",
            icon=Icons.MESSAGE,
            header=True
        ),
        TextField(
            name="session",
            title="Session",
            ordering="session__title"
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="role",
            title="Role"
        ),
        TextField(
            name="tokens_used",
            title="Tokens",
            ordering="tokens_used"
        ),
        TextField(
            name="cost_usd",
            title="Cost (USD)",
            ordering="cost_usd"
        ),
        TextField(
            name="processing_time_ms",
            title="Processing Time",
            ordering="processing_time_ms"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['content', 'user__username', 'session__title'],
    list_filter=[
        'role',
        'created_at',
        ('user', AutocompleteSelectFilter),
        ('session', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['message_display'],

    # Autocomplete fields
    autocomplete_fields=['user', 'session'],

    # Ordering
    ordering=['-created_at'],

    # Actions
    actions=[
        ActionConfig(
            name="delete_user_messages",
            description="Delete user messages",
            variant="danger",
            icon=Icons.DELETE,
            confirmation=True,
            handler=delete_user_messages
        ),
        ActionConfig(
            name="delete_assistant_messages",
            description="Delete assistant messages",
            variant="danger",
            icon=Icons.DELETE,
            confirmation=True,
            handler=delete_assistant_messages
        ),
    ],
)


@admin.register(ChatMessage)
class ChatMessageAdmin(PydanticAdmin):
    """
    ChatMessage admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Export functionality
    - Custom actions for message management (using ActionConfig)
    - Statistics in changelist_view
    """
    config = chat_message_config

    # Readonly fields
    readonly_fields = [
        'id', 'user', 'tokens_used', 'cost_usd', 'processing_time_ms',
        'created_at', 'updated_at', 'content_preview'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Message Info",
            fields=['session', 'role']
        ),
        FieldsetConfig(
            title="Content",
            fields=['content_preview', 'content']
        ),
        FieldsetConfig(
            title="Metrics",
            fields=['tokens_used', 'cost_usd', 'processing_time_ms']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'updated_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Message")
    def message_display(self, obj: ChatMessage) -> str:
        """Display message identifier."""
        return self.html.badge(
            f"#{str(obj.id)[:8]}",
            variant="secondary",
            icon=Icons.MESSAGE
        )

    @computed_field("Session")
    def session_display(self, obj: ChatMessage) -> str:
        """Display session title."""
        return obj.session.title or "Untitled Session"

    @computed_field("User")
    def user_display(self, obj: ChatMessage) -> str:
        """User display."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Role")
    def role_display(self, obj: ChatMessage) -> str:
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

        return self.html.badge(obj.role.title(), variant=variant, icon=icon)

    @computed_field("Tokens")
    def tokens_display(self, obj: ChatMessage) -> str:
        """Display tokens used with formatting."""
        tokens = obj.tokens_used
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Cost (USD)")
    def cost_display(self, obj: ChatMessage) -> str:
        """Display cost with currency formatting."""
        return f"${obj.cost_usd:.6f}"

    @computed_field("Processing Time")
    def processing_time_display(self, obj: ChatMessage) -> str:
        """Display processing time."""
        ms = obj.processing_time_ms
        if ms < 1000:
            return f"{ms}ms"
        else:
            seconds = ms / 1000
            return f"{seconds:.1f}s"

    @computed_field("Created")
    def created_at_display(self, obj: ChatMessage) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    def content_preview(self, obj):
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
    content_preview.short_description = "Content Preview"

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
