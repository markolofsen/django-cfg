"""
Document admin interfaces using Django Admin Utilities.

Enhanced document management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.db import models, IntegrityError
from django.db.models.fields.json import JSONField
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ImportExportModelAdmin, ImportForm, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import Document, DocumentChunk, DocumentCategory
from .helpers import (
    DocumentDisplayHelpers,
    DocumentStatistics,
    ChunkStatistics,
    CategoryStatistics,
    DocumentAdminConfigs
)
from .actions import VisibilityActions


class DocumentChunkInline(TabularInline):
    """Inline for document chunks with Unfold styling."""

    model = DocumentChunk
    verbose_name = "Document Chunk"
    verbose_name_plural = "📄 Document Chunks (Read-only)"
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

    @display(description="Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        return DocumentDisplayHelpers.display_content_preview(obj, max_length=100)

    @display(description="Has Embedding", boolean=True)
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0

    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('document', 'user')


@admin.register(Document)
class DocumentAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for Document model using Django Admin Utilities."""

    # Performance optimization
    select_related_fields = ['user']

    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = [
        'title_display', 'categories_display', 'user_display',
        'visibility_display', 'status_display', 'chunks_count_display',
        'vectorization_progress', 'tokens_display', 'cost_display', 'created_at_display'
    ]
    list_display_links = ['title_display']
    ordering = ['-created_at']
    inlines = [DocumentChunkInline]
    list_filter = [
        'processing_status', 'is_public', 'file_type', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('categories', AutocompleteSelectMultipleFilter)
    ]
    search_fields = ['title', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'categories']
    readonly_fields = [
        'id', 'user', 'content_hash', 'file_size', 'processing_started_at',
        'processing_completed_at', 'chunks_count', 'total_tokens',
        'processing_error', 'processing_duration', 'processing_status',
        'total_cost_usd', 'created_at', 'updated_at', 'duplicate_check'
    ]

    fieldsets = (
        ('📄 Basic Information', {
            'fields': ('id', 'title', 'user', 'categories', 'is_public', 'file_type', 'file_size'),
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ('content', 'content_hash', 'duplicate_check'),
            'classes': ('tab',)
        }),
        ('⚙️ Processing Status', {
            'fields': (
                'processing_status', 'processing_started_at',
                'processing_completed_at', 'processing_error'
            ),
            'classes': ('tab',)
        }),
        ('📊 Statistics', {
            'fields': ('chunks_count', 'total_tokens', 'total_cost_usd'),
            'classes': ('tab',)
        }),
        ('🔧 Metadata', {
            'fields': ('metadata',),
            'classes': ('tab', 'collapse'),
            'description': 'Auto-generated metadata (read-only)'
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )
    filter_horizontal = ['categories']

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    }

    actions = ['reprocess_documents', 'mark_as_public', 'mark_as_private']

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = Document.objects.all_users().select_related('user').prefetch_related('categories')

        # Staff users see all documents, regular users see only their own
        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        return queryset

    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new documents."""
        if not change:
            obj.user = request.user

            is_duplicate, existing_doc = Document.objects.check_duplicate_before_save(
                user=obj.user,
                content=obj.content
            )

            if is_duplicate and existing_doc:
                messages.error(
                    request,
                    f'❌ A document with identical content already exists: "{existing_doc.title}" '
                    f'(created {existing_doc.created_at.strftime("%Y-%m-%d %H:%M")}). '
                    f'Please modify the content or update the existing document.'
                )
                return

        try:
            super().save_model(request, obj, form, change)
        except IntegrityError as e:
            if 'unique_user_document' in str(e):
                messages.error(
                    request,
                    'A document with identical content already exists for this user. '
                    'Please modify the content or update the existing document.'
                )
            else:
                messages.error(request, f'Database error: {str(e)}')
            raise

    @display(description="Document Title", ordering="title")
    def title_display(self, obj):
        """Display document title with truncation."""
        title = obj.title or "Untitled Document"
        if len(title) > 50:
            title = title[:47] + "..."

        return StatusBadge.create(
            text=title,
            variant="primary",
            config=DocumentAdminConfigs.DOCUMENT_TITLE
        )

    def user_display(self, obj):
        """User display (delegates to helper)."""
        return DocumentDisplayHelpers.display_user(obj, self)

    def visibility_display(self, obj):
        """Visibility display (delegates to helper)."""
        return DocumentDisplayHelpers.display_visibility(obj)

    @display(description="Status")
    def status_display(self, obj):
        """Display processing status."""
        icon = DocumentAdminConfigs.get_processing_status_icon(obj.processing_status)
        status_config = DocumentAdminConfigs.PROCESSING_STATUS
        status_config.icon = icon
        return self.display_status_auto(obj, 'processing_status', status_config)

    @display(description="Categories")
    def categories_display(self, obj):
        """Display categories count."""
        categories = obj.categories.all()

        if not categories:
            return "No categories"

        public_count = sum(1 for cat in categories if cat.is_public)
        private_count = len(categories) - public_count

        if private_count == 0:
            return f"{len(categories)} public"
        elif public_count == 0:
            return f"{len(categories)} private"
        else:
            return f"{public_count} public, {private_count} private"

    @display(description="Chunks", ordering="chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count."""
        count = obj.chunks_count
        if count > 0:
            return f"{count} chunks"
        return "0 chunks"

    def tokens_display(self, obj):
        """Token count display (delegates to helper)."""
        return DocumentDisplayHelpers.display_token_count(obj, 'total_tokens')

    def cost_display(self, obj):
        """Cost display (delegates to helper)."""
        return DocumentDisplayHelpers.display_cost_usd(obj, self, 'total_cost_usd')

    @display(description="Vectorization")
    def vectorization_progress(self, obj):
        """Display vectorization progress."""
        return Document.objects.get_vectorization_status_display(obj)

    def created_at_display(self, obj):
        """Created time display (delegates to helper)."""
        return DocumentDisplayHelpers.display_created_at(obj, self)

    @display(description="Processing Duration")
    def processing_duration_display(self, obj):
        """Display processing duration in readable format."""
        duration = obj.processing_duration
        if duration is None:
            return "N/A"

        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            minutes = duration / 60
            return f"{minutes:.1f}m"
        else:
            hours = duration / 3600
            return f"{hours:.1f}h"

    @display(description="Duplicate Check")
    def duplicate_check(self, obj):
        """Check for duplicate documents with same content."""
        duplicate_info = Document.objects.get_duplicate_info(obj)

        if isinstance(duplicate_info, str):
            if "No duplicates found" in duplicate_info:
                return "✓ No duplicates found"
            return duplicate_info

        duplicates_data = duplicate_info['duplicates']
        count = duplicate_info['count']

        duplicate_names = [dup.title for dup in duplicates_data[:3]]
        result = f"⚠️ Found {count} duplicate(s): " + ", ".join(duplicate_names)
        if count > 3:
            result += f" and {count - 3} more"

        return result

    @action(description="Reprocess documents", variant=ActionVariant.INFO)
    def reprocess_documents(self, request, queryset):
        """Reprocess selected documents."""
        count = queryset.count()
        messages.info(request, f"Reprocessing functionality not implemented yet. {count} documents selected.")

    # Visibility actions (delegate to shared actions)
    mark_as_public = VisibilityActions.mark_as_public
    mark_as_private = VisibilityActions.mark_as_private

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['summary_stats'] = DocumentStatistics.get_document_stats(queryset)
        return super().changelist_view(request, extra_context)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin interface for DocumentChunk model using Django Admin Utilities."""

    # Performance optimization
    select_related_fields = ['document', 'user']

    list_display = [
        'chunk_display', 'document_display', 'user_display', 'token_count_display',
        'embedding_status', 'embedding_cost_display', 'created_at_display'
    ]
    list_display_links = ['chunk_display']
    ordering = ['-created_at']
    list_filter = [
        'embedding_model', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('document', AutocompleteSelectFilter)
    ]
    search_fields = ['document__title', 'user__username', 'content']
    readonly_fields = [
        'id', 'embedding_info', 'token_count', 'character_count',
        'embedding_cost', 'created_at', 'updated_at', 'content_preview'
    ]

    fieldsets = (
        ('📄 Basic Information', {
            'fields': ('id', 'document', 'user', 'chunk_index'),
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ('content_preview', 'content'),
            'classes': ('tab',)
        }),
        ('🔗 Embedding Information', {
            'fields': ('embedding_model', 'token_count', 'character_count', 'embedding_cost'),
            'classes': ('tab',)
        }),
        ('🧠 Vector Embedding', {
            'fields': ('embedding',),
            'classes': ('tab', 'collapse')
        }),
        ('🔧 Metadata', {
            'fields': ('metadata',),
            'classes': ('tab', 'collapse'),
            'description': 'Auto-generated chunk metadata (read-only)'
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Form field overrides
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget}
    }

    actions = ['regenerate_embeddings', 'clear_embeddings']

    @display(description="Chunk", ordering="chunk_index")
    def chunk_display(self, obj):
        """Display chunk identifier."""
        return StatusBadge.create(
            text=f"Chunk {obj.chunk_index + 1}",
            variant="info",
            config=DocumentAdminConfigs.CHUNK
        )

    @display(description="Document", ordering="document__title")
    def document_display(self, obj):
        """Display document title."""
        return obj.document.title

    def user_display(self, obj):
        """User display (delegates to helper)."""
        return DocumentDisplayHelpers.display_user(obj, self)

    def token_count_display(self, obj):
        """Token count display (delegates to helper)."""
        return DocumentDisplayHelpers.display_token_count(obj, 'token_count')

    def embedding_status(self, obj):
        """Embedding status display (delegates to helper)."""
        return DocumentDisplayHelpers.display_embedding_status(obj)

    def embedding_cost_display(self, obj):
        """Embedding cost display (delegates to helper)."""
        return DocumentDisplayHelpers.display_cost_usd(obj, self, 'embedding_cost')

    def created_at_display(self, obj):
        """Created time display (delegates to helper)."""
        return DocumentDisplayHelpers.display_created_at(obj, self)

    def content_preview(self, obj):
        """Content preview display (delegates to helper)."""
        return DocumentDisplayHelpers.display_content_preview(obj, max_length=200)

    @display(description="Embedding Info")
    def embedding_info(self, obj):
        """Display embedding information safely."""
        if obj.embedding is not None and len(obj.embedding) > 0:
            return f"✓ Vector ({len(obj.embedding)} dimensions)"
        return "✗ No embedding"

    @action(description="Regenerate embeddings", variant=ActionVariant.INFO)
    def regenerate_embeddings(self, request, queryset):
        """Regenerate embeddings for selected chunks."""
        count = queryset.count()
        messages.info(request, f"Regenerate embeddings functionality not implemented yet. {count} chunks selected.")

    @action(description="Clear embeddings", variant=ActionVariant.WARNING)
    def clear_embeddings(self, request, queryset):
        """Clear embeddings for selected chunks."""
        updated = queryset.update(embedding=None)
        messages.warning(request, f"Cleared embeddings for {updated} chunks.")

    def changelist_view(self, request, extra_context=None):
        """Add chunk statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['chunk_stats'] = ChunkStatistics.get_chunk_stats(queryset)
        return super().changelist_view(request, extra_context)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for DocumentCategory model using Django Admin Utilities."""

    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = [
        'short_uuid', 'name_display', 'visibility_display', 'document_count', 'created_at_display'
    ]
    list_display_links = ['name_display']
    ordering = ['-created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('📁 Basic Information', {
            'fields': ('id', 'name', 'description', 'is_public'),
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )

    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True

    # Form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget}
    }

    actions = ['make_public', 'make_private']

    @display(description="Category Name")
    def name_display(self, obj):
        """Display category name."""
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=DocumentAdminConfigs.CATEGORY
        )

    def visibility_display(self, obj):
        """Visibility display (delegates to helper)."""
        return DocumentDisplayHelpers.display_visibility(obj)

    @display(description="Documents", ordering="document_count")
    def document_count(self, obj):
        """Display count of documents in this category."""
        count = obj.documents.count()
        return f"{count} documents"

    def created_at_display(self, obj):
        """Created time display (delegates to helper)."""
        return DocumentDisplayHelpers.display_created_at(obj, self)

    # Visibility actions (delegate to shared actions, using make_* aliases)
    make_public = VisibilityActions.mark_as_public
    make_private = VisibilityActions.mark_as_private

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related('documents')

    def changelist_view(self, request, extra_context=None):
        """Add category statistics to changelist."""
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        extra_context['category_stats'] = CategoryStatistics.get_category_stats(queryset)
        return super().changelist_view(request, extra_context)
