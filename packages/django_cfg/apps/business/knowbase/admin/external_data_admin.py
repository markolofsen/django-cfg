"""
External Data Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced external data management with Material Icons and clean declarative config.
"""

from django.contrib import admin, messages
from django.db import models
from django.db.models import Count, Q, Sum
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

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

from ..models.external_data import (
    ExternalData,
    ExternalDataChunk,
)
from .external_data_actions import (
    activate_data,
    clear_embeddings,
    deactivate_data,
    mark_as_private,
    mark_as_public,
    regenerate_embeddings,
    reprocess_data,
)


class ExternalDataChunkInline(TabularInline):
    """Inline for external data chunks with Unfold styling."""

    model = ExternalDataChunk
    verbose_name = "External Data Chunk"
    verbose_name_plural = "🔗 External Data Chunks (Read-only)"
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
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count',
        'has_embedding_inline', 'embedding_cost'
    ]
    readonly_fields = [
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count', 'character_count',
        'has_embedding_inline', 'embedding_cost', 'created_at'
    ]

    hide_title = False
    classes = ['collapse']

    @computed_field("Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "—"
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    @computed_field("Has Embedding")
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('external_data', 'user')


# ===== External Data Admin Config =====

external_data_config = AdminConfig(
    model=ExternalData,

    # Performance optimization
    select_related=['user', 'category'],

    # List display
    list_display=[
        "title_display",
        "source_type_display",
        "source_identifier_display",
        "user_display",
        "status_display",
        "chunks_count_display",
        "tokens_display",
        "cost_display",
        "visibility_display",
        "processed_at_display",
        "created_at_display"
    ],
    list_display_links=["title_display"],

    # Autocomplete fields
    autocomplete_fields=["user", "category"],

    # Search and filters
    search_fields=["title", "description", "source_identifier", "user__username", "user__email"],
    list_filter=[
        "source_type",
        "status",
        "is_active",
        "is_public",
        "embedding_model",
        "processed_at",
        "created_at",
        ("user", AutocompleteSelectFilter),
        ("category", AutocompleteSelectFilter)
    ],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    },

    # Ordering
    ordering=["-created_at"],

    # Actions
    actions=[
        ActionConfig(
            name="reprocess_data",
            description="Reprocess data",
            variant="primary",
            icon=Icons.REFRESH,
            handler=reprocess_data
        ),
        ActionConfig(
            name="activate_data",
            description="Activate data",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_data
        ),
        ActionConfig(
            name="deactivate_data",
            description="Deactivate data",
            variant="warning",
            icon=Icons.PAUSE_CIRCLE,
            handler=deactivate_data
        ),
        ActionConfig(
            name="mark_as_public",
            description="Mark as public",
            variant="success",
            icon=Icons.PUBLIC,
            handler=mark_as_public
        ),
        ActionConfig(
            name="mark_as_private",
            description="Mark as private",
            variant="danger",
            icon=Icons.LOCK,
            handler=mark_as_private
        ),
    ],
)


@admin.register(ExternalData)
class ExternalDataAdmin(PydanticAdmin):
    """
    External Data admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Custom actions for data processing (using ActionConfig)
    - Statistics in changelist_view
    - Chunk management via inline
    """
    config = external_data_config

    # Inlines
    inlines = [ExternalDataChunkInline]

    # Readonly fields
    readonly_fields = [
        "id", "user", "source_type", "source_identifier", "status",
        "processed_at", "processing_error",
        "total_chunks", "total_tokens", "processing_cost",
        "created_at", "updated_at"
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="External Data Info",
            fields=["title", "description", "category"]
        ),
        FieldsetConfig(
            title="Source Details",
            fields=["source_type", "source_identifier", "source_metadata"]
        ),
        FieldsetConfig(
            title="Processing Status",
            fields=["status", "processing_error"]
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["total_chunks", "total_tokens", "processing_cost"]
        ),
        FieldsetConfig(
            title="Settings",
            fields=["is_active", "is_public", "embedding_model"]
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        )
    ]

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Custom display methods using @computed_field decorator
    @computed_field("Title")
    def title_display(self, obj: ExternalData) -> str:
        """Display external data title."""
        title = obj.title or "Untitled External Data"
        if len(title) > 50:
            title = title[:47] + "..."

        return self.html.badge(title, variant="primary", icon=Icons.CLOUD)

    @computed_field("Source Type")
    def source_type_display(self, obj: ExternalData) -> str:
        """Display source type with badge."""
        if not obj.source_type:
            return "—"

        type_variants = {
            'api': 'info',
            'webhook': 'success',
            'database': 'warning',
            'file': 'secondary'
        }
        variant = type_variants.get(obj.source_type.lower(), 'secondary')

        type_icons = {
            'api': Icons.API,
            'webhook': Icons.WEBHOOK,
            'database': Icons.STORAGE,
            'file': Icons.INSERT_DRIVE_FILE
        }
        icon = type_icons.get(obj.source_type.lower(), Icons.CLOUD)

        return self.html.badge(obj.source_type.upper(), variant=variant, icon=icon)

    @computed_field("Source ID")
    def source_identifier_display(self, obj: ExternalData) -> str:
        """Display source identifier with truncation."""
        if not obj.source_identifier:
            return "—"

        identifier = obj.source_identifier
        if len(identifier) > 30:
            identifier = identifier[:27] + "..."

        return identifier

    @computed_field("User")
    def user_display(self, obj: ExternalData) -> str:
        """User display."""
        if not obj.user:
            return "—"
                # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Status")
    def status_display(self, obj: ExternalData) -> str:
        """Display processing status."""
        icon_map = {
            'pending': Icons.SCHEDULE,
            'processing': Icons.SCHEDULE,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'cancelled': Icons.CANCEL
        }

        variant_map = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')
        text = obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status.title()
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Chunks")
    def chunks_count_display(self, obj: ExternalData) -> str:
        """Display chunks count."""
        count = obj.total_chunks or 0
        return f"{count} chunks"

    @computed_field("Tokens")
    def tokens_display(self, obj: ExternalData) -> str:
        """Display token count with formatting."""
        tokens = obj.total_tokens or 0
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Cost (USD)")
    def cost_display(self, obj: ExternalData) -> str:
        """Display cost with currency formatting."""
        cost = obj.processing_cost or 0
        return f"${cost:.6f}"

    @computed_field("Visibility")
    def visibility_display(self, obj: ExternalData) -> str:
        """Display visibility status."""
        if obj.is_public:
            return self.html.badge("Public", variant="success", icon=Icons.PUBLIC)
        else:
            return self.html.badge("Private", variant="danger", icon=Icons.LOCK)

    @computed_field("Processed")
    def processed_at_display(self, obj: ExternalData) -> str:
        """Processed time with relative display."""
        if not obj.processed_at:
            return "—"
        # DateTimeField in display_fields handles formatting automatically
        return obj.processed_at

    @computed_field("Created")
    def created_at_display(self, obj: ExternalData) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    def changelist_view(self, request, extra_context=None):
        """Add external data statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_items=Count('id'),
            active_items=Count('id', filter=Q(is_active=True)),
            completed_items=Count('id', filter=Q(status='completed')),
            total_chunks=Sum('total_chunks'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('processing_cost')
        )

        # Source type breakdown
        source_type_counts = dict(
            queryset.values_list('source_type').annotate(
                count=Count('id')
            )
        )

        extra_context['external_data_stats'] = {
            'total_items': stats['total_items'] or 0,
            'active_items': stats['active_items'] or 0,
            'completed_items': stats['completed_items'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'source_type_counts': source_type_counts
        }

        return super().changelist_view(request, extra_context)


# ===== External Data Chunk Admin Config =====

external_data_chunk_config = AdminConfig(
    model=ExternalDataChunk,

    # Performance optimization
    select_related=['external_data', 'user'],

    # List display
    list_display=[
        "chunk_display",
        "external_data_display",
        "user_display",
        "token_count_display",
        "embedding_status",
        "embedding_cost_display",
        "created_at_display"
    ],
    list_display_links=["chunk_display"],

    # Autocomplete fields
    autocomplete_fields=["external_data", "user"],

    # Search and filters
    search_fields=["external_data__title", "user__username", "content"],
    list_filter=[
        "embedding_model",
        "created_at",
        ("user", AutocompleteSelectFilter),
        ("external_data", AutocompleteSelectFilter)
    ],

    # Ordering
    ordering=["-created_at"],

    # Actions
    actions=[
        ActionConfig(
            name="regenerate_embeddings",
            description="Regenerate embeddings",
            variant="primary",
            icon=Icons.REFRESH,
            handler=regenerate_embeddings
        ),
        ActionConfig(
            name="clear_embeddings",
            description="Clear embeddings",
            variant="danger",
            icon=Icons.DELETE,
            confirmation=True,
            handler=clear_embeddings
        ),
    ],
)


@admin.register(ExternalDataChunk)
class ExternalDataChunkAdmin(PydanticAdmin):
    """
    External Data Chunk admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Custom actions for embedding management (using ActionConfig)
    - Embedding status visualization
    """
    config = external_data_chunk_config

    # Readonly fields
    readonly_fields = [
        "id", "token_count", "character_count", "embedding_cost",
        "created_at", "updated_at", "content_preview"
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Chunk Info",
            fields=["external_data", "chunk_index"]
        ),
        FieldsetConfig(
            title="Content",
            fields=["content_preview", "content"]
        ),
        FieldsetConfig(
            title="Embedding",
            fields=["embedding_model", "token_count", "character_count", "embedding_cost"]
        ),
        FieldsetConfig(
            title="Vector",
            fields=["embedding"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Chunk")
    def chunk_display(self, obj: ExternalDataChunk) -> str:
        """Display chunk identifier."""
        return self.html.badge(f"Chunk {obj.chunk_index + 1}", variant="info", icon=Icons.ARTICLE)

    @computed_field("External Data")
    def external_data_display(self, obj: ExternalDataChunk) -> str:
        """Display external data title."""
        return obj.external_data.title or "Untitled External Data"

    @computed_field("User")
    def user_display(self, obj: ExternalDataChunk) -> str:
        """User display."""
        if not obj.user:
            return "—"
                # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Tokens")
    def token_count_display(self, obj: ExternalDataChunk) -> str:
        """Display token count with formatting."""
        tokens = obj.token_count
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Embedding")
    def embedding_status(self, obj: ExternalDataChunk) -> str:
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            return self.html.badge("✓ Vectorized", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("✗ Not vectorized", variant="danger", icon=Icons.ERROR)

    @computed_field("Cost (USD)")
    def embedding_cost_display(self, obj: ExternalDataChunk) -> str:
        """Display embedding cost with currency formatting."""
        cost = obj.embedding_cost or 0
        return f"${cost:.6f}"

    @computed_field("Created")
    def created_at_display(self, obj: ExternalDataChunk) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    @computed_field("Content Preview")
    def content_preview(self, obj: ExternalDataChunk) -> str:
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
