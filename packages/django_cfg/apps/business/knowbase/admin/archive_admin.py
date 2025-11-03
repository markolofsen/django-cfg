"""
Archive Admin v2.0 - NEW Declarative Pydantic Approach

Enhanced archive management with Material Icons and clean declarative config.
"""

import logging

from django.contrib import admin, messages
from django.db import models
from django.db.models import Count, Q, Sum
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg import ExportForm, ImportExportModelAdmin, ImportForm
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

from ..models.archive import ArchiveItem, ArchiveItemChunk, DocumentArchive
from .archive_actions import (
    clear_embeddings,
    mark_as_not_processable,
    mark_as_private,
    mark_as_processable,
    mark_as_public,
    regenerate_embeddings,
    reprocess_archives,
)

logger = logging.getLogger(__name__)


class ArchiveItemInline(TabularInline):
    """Inline for archive items with Unfold styling."""

    model = ArchiveItem
    verbose_name = "Archive Item"
    verbose_name_plural = "Archive Items (Read-only)"
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
        'item_name', 'content_type', 'file_size_display_inline',
        'is_processable', 'chunks_count', 'created_at'
    ]
    readonly_fields = [
        'item_name', 'content_type', 'file_size_display_inline',
        'is_processable', 'chunks_count', 'created_at'
    ]

    hide_title = False
    classes = ['collapse']

    @computed_field("File Size")
    def file_size_display_inline(self, obj):
        """Display file size in human readable format for inline."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('archive', 'user')


# ===== DocumentArchive Admin Config =====

document_archive_config = AdminConfig(
    model=DocumentArchive,

    # Performance optimization
    select_related=['user'],

    # List display
    list_display=[
        'title_display',
        'user_display',
        'archive_type_display',
        'status_display',
        'items_count',
        'chunks_count',
        'vectorization_progress',
        'file_size_display',
        'progress_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="title",
            title="Archive Title",
            variant="primary",
            icon=Icons.ARCHIVE,
            ordering="title",
            header=True
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="archive_type",
            title="Archive Type",
            icon=Icons.FOLDER_ZIP
        ),
        BadgeField(
            name="processing_status",
            title="Status"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['title', 'description', 'original_filename', 'user__username'],
    list_filter=[
        'processing_status',
        'archive_type',
        'is_public',
        'created_at',
        'processed_at',
        ('user', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['title_display'],

    # Autocomplete fields
    autocomplete_fields=['user', 'categories'],

    # Form field overrides
    formfield_overrides={
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    },

    # Ordering
    ordering=['-created_at'],

    # Actions
    actions=[
        ActionConfig(
            name="reprocess_archives",
            description="Reprocess archives",
            variant="primary",
            icon=Icons.REFRESH,
            handler=reprocess_archives
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


@admin.register(DocumentArchive)
class DocumentArchiveAdmin(PydanticAdmin):
    """
    DocumentArchive admin using NEW Pydantic declarative approach.

    Features:
    - Declarative configuration with type safety
    - Automatic display method generation
    - Material Icons integration
    - Archive statistics tracking
    - Custom actions for visibility and reprocessing (using ActionConfig)
    """
    config = document_archive_config

    # Import/Export configuration (if needed)
    import_form_class = ImportForm
    export_form_class = ExportForm

    # Readonly fields
    readonly_fields = [
        'id', 'user', 'content_hash', 'original_filename', 'file_size', 'archive_type',
        'processing_status', 'processed_at', 'processing_duration_ms',
        'processing_error', 'total_items', 'processed_items', 'total_chunks',
        'vectorized_chunks', 'total_cost_usd', 'created_at', 'updated_at'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Archive Info",
            fields=['title', 'description', 'categories', 'is_public']
        ),
        FieldsetConfig(
            title="File Details",
            fields=['original_filename', 'file_size', 'archive_type', 'content_hash']
        ),
        FieldsetConfig(
            title="Processing Status",
            fields=['processing_status', 'processing_error']
        ),
        FieldsetConfig(
            title="Statistics",
            fields=['total_items', 'processed_items', 'total_chunks', 'vectorized_chunks', 'total_cost_usd']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'updated_at'],
            collapsed=True
        )
    ]

    # Inlines
    inlines = [ArchiveItemInline]

    # Filter horizontal
    filter_horizontal = ['categories']

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Custom display methods using @computed_field decorator
    @computed_field("Archive Title")
    def title_display(self, obj: DocumentArchive) -> str:
        """Display archive title."""
        title = obj.title or "Untitled Archive"
        if len(title) > 50:
            title = title[:47] + "..."

        return self.html.badge(title, variant="primary", icon=Icons.ARCHIVE)

    @computed_field("User")
    def user_display(self, obj: DocumentArchive) -> str:
        """User display."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Archive Type")
    def archive_type_display(self, obj: DocumentArchive) -> str:
        """Display archive type with badge."""
        if not obj.archive_type:
            return "—"

        type_variants = {
            'zip': 'info',
            'tar': 'warning',
            'rar': 'secondary',
            '7z': 'primary'
        }
        variant = type_variants.get(obj.archive_type.lower(), 'secondary')

        return self.html.badge(obj.archive_type.upper(), variant=variant, icon=Icons.FOLDER_ZIP)

    @computed_field("Status")
    def status_display(self, obj: DocumentArchive) -> str:
        """Display processing status."""
        status_variants = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        status_icons = {
            'pending': Icons.SCHEDULE,
            'processing': Icons.SCHEDULE,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'cancelled': Icons.CANCEL
        }

        variant = status_variants.get(obj.processing_status, 'secondary')
        icon = status_icons.get(obj.processing_status, Icons.SCHEDULE)
        text = obj.get_processing_status_display() if hasattr(obj, 'get_processing_status_display') else obj.processing_status
        return self.html.badge(text, variant=variant, icon=icon)

    @computed_field("Items")
    def items_count(self, obj: DocumentArchive) -> str:
        """Display items count."""
        total = obj.total_items or 0
        processed = obj.processed_items or 0
        return f"{processed}/{total} items"

    @computed_field("Chunks")
    def chunks_count(self, obj: DocumentArchive) -> str:
        """Display chunks count."""
        total = obj.total_chunks or 0
        vectorized = obj.vectorized_chunks or 0
        return f"{vectorized}/{total} chunks"

    @computed_field("Vectorization")
    def vectorization_progress(self, obj: DocumentArchive) -> str:
        """Display vectorization progress."""
        total = obj.total_chunks or 0
        vectorized = obj.vectorized_chunks or 0

        if total == 0:
            return "No chunks"

        percentage = (vectorized / total) * 100

        if percentage == 100:
            return self.html.badge("100%", variant="success", icon=Icons.CHECK_CIRCLE)
        elif percentage > 0:
            return self.html.badge(f"{percentage:.1f}%", variant="warning", icon=Icons.SCHEDULE)
        else:
            return self.html.badge("0%", variant="danger", icon=Icons.ERROR)

    @computed_field("File Size")
    def file_size_display(self, obj: DocumentArchive) -> str:
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    @computed_field("Progress")
    def progress_display(self, obj: DocumentArchive) -> str:
        """Display overall progress."""
        total_items = obj.total_items or 0
        processed_items = obj.processed_items or 0

        if total_items == 0:
            return "No items"

        percentage = (processed_items / total_items) * 100
        return f"{percentage:.1f}%"

    @computed_field("Created")
    def created_at_display(self, obj: DocumentArchive) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    def changelist_view(self, request, extra_context=None):
        """Add archive statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_archives=Count('id'),
            completed_archives=Count('id', filter=Q(processing_status='completed')),
            total_items=Sum('total_items'),
            total_chunks=Sum('total_chunks'),
            total_cost=Sum('total_cost_usd')
        )

        extra_context['archive_stats'] = {
            'total_archives': stats['total_archives'] or 0,
            'completed_archives': stats['completed_archives'] or 0,
            'total_items': stats['total_items'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}"
        }

        return super().changelist_view(request, extra_context)


# ===== ArchiveItem Admin Config =====

archive_item_config = AdminConfig(
    model=ArchiveItem,

    # Performance optimization
    select_related=['archive', 'user'],

    # List display
    list_display=[
        'item_name_display',
        'archive_display',
        'user_display',
        'content_type_display',
        'file_size_display',
        'processable_display',
        'chunks_count_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="item_name",
            title="Item Name",
            variant="primary",
            icon=Icons.INSERT_DRIVE_FILE,
            ordering="item_name",
            header=True
        ),
        TextField(
            name="archive",
            title="Archive",
            ordering="archive__title"
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="content_type",
            title="Content Type",
            variant="info",
            icon=Icons.DESCRIPTION
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['item_name', 'content_type', 'archive__title', 'user__username'],
    list_filter=[
        'content_type',
        'is_processable',
        'created_at',
        ('archive', AutocompleteSelectFilter),
        ('user', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['item_name_display'],

    # Autocomplete fields
    autocomplete_fields=['archive', 'user'],

    # Ordering
    ordering=['-created_at'],

    # Actions
    actions=[
        ActionConfig(
            name="mark_as_processable",
            description="Mark as processable",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=mark_as_processable
        ),
        ActionConfig(
            name="mark_as_not_processable",
            description="Mark as not processable",
            variant="warning",
            icon=Icons.CANCEL,
            handler=mark_as_not_processable
        ),
    ],
)


@admin.register(ArchiveItem)
class ArchiveItemAdmin(PydanticAdmin):
    """
    ArchiveItem admin using NEW Pydantic declarative approach.
    """
    config = archive_item_config

    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm

    # Readonly fields
    readonly_fields = [
        'id', 'user', 'file_size', 'content_type', 'is_processable',
        'chunks_count', 'created_at', 'updated_at'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Item Info",
            fields=['item_name', 'archive']
        ),
        FieldsetConfig(
            title="File Details",
            fields=['content_type', 'file_size', 'is_processable']
        ),
        FieldsetConfig(
            title="Processing",
            fields=['chunks_count']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'updated_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Item Name")
    def item_name_display(self, obj: ArchiveItem) -> str:
        """Display item name."""
        name = obj.item_name
        if len(name) > 50:
            name = name[:47] + "..."

        return self.html.badge(name, variant="primary", icon=Icons.INSERT_DRIVE_FILE)

    @computed_field("Archive")
    def archive_display(self, obj: ArchiveItem) -> str:
        """Display archive title."""
        return obj.archive.title or "Untitled Archive"

    @computed_field("User")
    def user_display(self, obj: ArchiveItem) -> str:
        """User display."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Content Type")
    def content_type_display(self, obj: ArchiveItem) -> str:
        """Display content type with badge."""
        if not obj.content_type:
            return "—"

        return self.html.badge(obj.content_type, variant="info", icon=Icons.DESCRIPTION)

    @computed_field("File Size")
    def file_size_display(self, obj: ArchiveItem) -> str:
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    @computed_field("Processable")
    def processable_display(self, obj: ArchiveItem) -> str:
        """Display processable status."""
        if obj.is_processable:
            return self.html.badge("Yes", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("No", variant="danger", icon=Icons.CANCEL)

    @computed_field("Chunks")
    def chunks_count_display(self, obj: ArchiveItem) -> str:
        """Display chunks count."""
        count = obj.chunks_count or 0
        return f"{count} chunks"

    @computed_field("Created")
    def created_at_display(self, obj: ArchiveItem) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at


# ===== ArchiveItemChunk Admin Config =====

archive_item_chunk_config = AdminConfig(
    model=ArchiveItemChunk,

    # Performance optimization
    select_related=['item', 'user'],

    # List display
    list_display=[
        'chunk_display',
        'archive_item_display',
        'user_display',
        'token_count_display',
        'embedding_status',
        'embedding_cost_display',
        'created_at_display'
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="chunk_index",
            title="Chunk",
            variant="info",
            icon=Icons.ARTICLE,
            ordering="chunk_index",
            header=True
        ),
        TextField(
            name="item",
            title="Archive Item",
            ordering="item__item_name"
        ),
        UserField(
            name="user",
            title="User"
        ),
        TextField(
            name="token_count",
            title="Tokens",
            ordering="token_count"
        ),
        TextField(
            name="embedding_cost",
            title="Cost (USD)",
            ordering="embedding_cost"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
        ),
    ],

    # Search and filters
    search_fields=['item__item_name', 'user__username', 'content'],
    list_filter=[
        'embedding_model',
        'created_at',
        ('user', AutocompleteSelectFilter),
        ('item', AutocompleteSelectFilter)
    ],

    # List display links
    list_display_links=['chunk_display'],

    # Autocomplete fields
    autocomplete_fields=['item', 'user'],

    # Ordering
    ordering=['-created_at'],

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


@admin.register(ArchiveItemChunk)
class ArchiveItemChunkAdmin(PydanticAdmin):
    """
    ArchiveItemChunk admin using NEW Pydantic declarative approach.
    """
    config = archive_item_chunk_config

    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm

    # Readonly fields
    readonly_fields = [
        'id', 'token_count', 'character_count', 'embedding_cost',
        'created_at', 'updated_at', 'content_preview'
    ]

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Chunk Info",
            fields=['item', 'chunk_index']
        ),
        FieldsetConfig(
            title="Content",
            fields=['content_preview', 'content']
        ),
        FieldsetConfig(
            title="Embedding",
            fields=['embedding_model', 'token_count', 'character_count', 'embedding_cost']
        ),
        FieldsetConfig(
            title="Vector",
            fields=['embedding'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'updated_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Chunk")
    def chunk_display(self, obj: ArchiveItemChunk) -> str:
        """Display chunk identifier."""
        return self.html.badge(f"Chunk {obj.chunk_index + 1}", variant="info", icon=Icons.ARTICLE)

    @computed_field("Archive Item")
    def archive_item_display(self, obj: ArchiveItemChunk) -> str:
        """Display archive item name."""
        return obj.item.item_name

    @computed_field("User")
    def user_display(self, obj: ArchiveItemChunk) -> str:
        """User display."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Tokens")
    def token_count_display(self, obj: ArchiveItemChunk) -> str:
        """Display token count with formatting."""
        tokens = obj.token_count
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @computed_field("Embedding")
    def embedding_status(self, obj: ArchiveItemChunk) -> str:
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            return self.html.badge("Vectorized", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Not vectorized", variant="danger", icon=Icons.ERROR)

    @computed_field("Cost (USD)")
    def embedding_cost_display(self, obj: ArchiveItemChunk) -> str:
        """Display embedding cost with currency formatting."""
        cost = obj.embedding_cost or 0
        return f"${cost:.6f}"

    @computed_field("Created")
    def created_at_display(self, obj: ArchiveItemChunk) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    @computed_field("Content Preview")
    def content_preview(self, obj: ArchiveItemChunk) -> str:
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
