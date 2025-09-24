"""
Document admin interfaces with Unfold optimization.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models, IntegrityError
from django.db.models import Count, Sum, Avg
from django.db.models.fields.json import JSONField
from django.contrib import messages
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ImportExportModelAdmin, ExportMixin, ImportForm, ExportForm

from ..models import Document, DocumentChunk, DocumentCategory


class DocumentChunkInline(TabularInline):
    """Inline for document chunks with Unfold styling."""
    
    model = DocumentChunk
    verbose_name = "Document Chunk"
    verbose_name_plural = "📄 Document Chunks (Read-only)"
    extra = 0
    max_num = 0  # No new chunks allowed
    can_delete = False  # Prevent deletion through inline
    show_change_link = True  # Allow viewing individual chunks
    
    def has_add_permission(self, request, obj=None):
        """Disable adding new chunks through inline."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing chunks through inline."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting chunks through inline."""
        return False
    
    fields = [
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count', 
        'has_embedding_inline', 'embedding_cost'
    ]
    readonly_fields = [
        'short_uuid', 'chunk_index', 'content_preview_inline', 'token_count', 'character_count',
        'has_embedding_inline', 'embedding_cost', 'created_at'
    ]
    
    # Unfold specific options
    hide_title = False  # Show titles for better UX
    classes = ['collapse']  # Collapsed by default
    
    @display(description="Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "-"
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return format_html(
            '<div style="max-width: 300px; font-size: 12px; color: #666;">{}</div>',
            preview
        )
    
    @display(description="Has Embedding", boolean=True)
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('document', 'user')


@admin.register(Document)
class DocumentAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin interface for Document model with Unfold styling."""
    
    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'title_display', 'categories_display', 'user', 
        'visibility_badge', 'status_badge', 'chunks_count_display', 'vectorization_progress', 'tokens_display', 'cost_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
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
        ('Basic Information', {
            'fields': ('id', 'title', 'user', 'categories', 'is_public', 'file_type', 'file_size')
        }),
        ('Content', {
            'fields': ('content', 'content_hash', 'duplicate_check'),
        }),
        ('Processing Status', {
            'fields': (
                'processing_status', 'processing_started_at', 
                'processing_completed_at', 'processing_error'
            )
        }),
        ('Statistics', {
            'fields': ('chunks_count', 'total_tokens', 'total_cost_usd')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Auto-generated metadata (read-only)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    filter_horizontal = ['categories']
    
    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True
    
    # Form field overrides
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
        JSONField: {
            "widget": JSONEditorWidget,
        }
    }
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        # Use all_users() to show all documents in admin, then filter by user if needed
        queryset = Document.objects.all_users().select_related('user').prefetch_related('categories')
        
        # For non-superusers, filter by their own documents
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        
        return queryset
    
    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new documents."""
        if not change:  # Only for new documents
            obj.user = request.user
            
            # Check for duplicates using manager method
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
                # Don't save, just return - this will keep the form open with the error
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
            
            # Re-raise the exception to prevent saving
            raise
    
    @display(description="Document Title", ordering="title")
    def title_display(self, obj):
        """Display document title with truncation."""
        title = obj.title or "Untitled Document"
        if len(title) > 50:
            title = title[:47] + "..."
        return format_html(
            '<div style="font-weight: 500;">{}</div>',
            title
        )
    
    @display(
        description="Visibility",
        ordering="is_public",
        label={
            True: 'success',   # green for public
            False: 'danger'    # red for private
        }
    )
    def visibility_badge(self, obj):
        """Display visibility status with color coding."""
        return obj.is_public, "Public" if obj.is_public else "Private"
    
    @display(
        description="Status",
        ordering="processing_status",
        label={
            'pending': 'warning',     # orange for pending
            'processing': 'info',     # blue for processing
            'completed': 'success',   # green for completed
            'failed': 'danger',       # red for failed
            'cancelled': 'secondary'  # gray for cancelled
        }
    )
    def status_badge(self, obj):
        """Display processing status with color coding."""
        return obj.processing_status, obj.get_processing_status_display()
    
    @display(
        description="Categories",
        ordering="categories__name",
        label={
            'public': 'success',    # green for public categories
            'private': 'danger',    # red for private categories
            'mixed': 'warning',     # orange for mixed visibility
            'none': 'info'          # blue for no categories
        }
    )
    def categories_display(self, obj):
        """Display multiple categories with Unfold label styling."""
        categories = obj.categories.all()
        
        if not categories:
            return 'none', 'No categories'
        
        # Determine overall visibility status
        public_count = sum(1 for cat in categories if cat.is_public)
        private_count = len(categories) - public_count
        
        if private_count == 0:
            status = 'public'
            description = f"{len(categories)} public"
        elif public_count == 0:
            status = 'private'  
            description = f"{len(categories)} private"
        else:
            status = 'mixed'
            description = f"{public_count} public, {private_count} private"
        
        # Return tuple for label display: (status_key, display_text)
        return status, f"{', '.join(cat.name for cat in categories)} ({description})"
    
    @display(description="Category Details", dropdown=True)
    def category_dropdown(self, obj):
        """Display category details in dropdown."""
        categories = obj.categories.all()
        
        if not categories:
            return {
                "title": "No Categories",
                "content": "<p class='text-gray-500 p-4'>This document has no categories assigned.</p>"
            }
        
        # Build dropdown items for each category
        items = []
        for category in categories:
            status_icon = "🟢" if category.is_public else "🔴"
            visibility = "Public" if category.is_public else "Private"
            
            items.append({
                "title": f"{status_icon} {category.name}",
                "link": f"/admin/knowbase/documentcategory/{category.id}/change/"
            })
        
        return {
            "title": f"Categories ({len(categories)})",
            "striped": True,
            "height": 200,
            "width": 300,
            "items": items
        }

    @display(description="Chunks", ordering="chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count with link."""
        count = obj.chunks_count
        if count > 0:
            url = f"/admin/knowbase/documentchunk/?document__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="text-decoration: none;">{} chunks</a>',
                url, count
            )
        return "0 chunks"
    
    @display(description="Tokens", ordering="total_tokens")
    def tokens_display(self, obj):
        """Display token count with formatting."""
        tokens = obj.total_tokens
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @display(description="Cost (USD)", ordering="total_cost_usd")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        return f"${obj.total_cost_usd:.6f}"
    
    @display(
        description="Vectorization",
        label={
            'completed': 'success',    # green for 100%
            'partial': 'warning',      # orange for partial
            'none': 'danger',          # red for 0%
            'no_chunks': 'info'        # blue for no chunks
        }
    )
    def vectorization_progress(self, obj):
        """Display vectorization progress with color coding."""
        return Document.objects.get_vectorization_status_display(obj)
    
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
                return format_html(
                    '<span style="color: #059669;">✓ No duplicates found</span>'
                )
            return duplicate_info  # "No content hash"
        
        # Format the duplicate information for display
        duplicates_data = duplicate_info['duplicates']
        count = duplicate_info['count']
        
        duplicate_list = []
        for dup in duplicates_data:
            url = reverse('admin:django_cfg_knowbase_document_change', args=[dup.pk])
            duplicate_list.append(
                f'<a href="{url}" target="_blank">{dup.title}</a> '
                f'({dup.created_at.strftime("%Y-%m-%d")})'
            )
        
        warning_text = f"⚠️ Found {count} duplicate(s):<br>" + "<br>".join(duplicate_list)
        if count > 3:
            warning_text += f"<br>... and {count - 3} more"
        
        return format_html(
            '<div style="color: #d97706; font-weight: 500;">{}</div>',
            warning_text
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}
        
        # Get summary statistics
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_documents=Count('id'),
            total_chunks=Sum('chunks_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd')
        )
        
        # Status breakdown
        status_counts = dict(
            queryset.values_list('processing_status').annotate(
                count=Count('id')
            )
        )
        
        extra_context['summary_stats'] = {
            'total_documents': stats['total_documents'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'status_counts': status_counts
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(ModelAdmin):
    """Admin interface for DocumentChunk model with Unfold styling."""
    
    list_display = [
        'chunk_display', 'document_link', 'user', 'token_count_display', 
        'embedding_status', 'embedding_cost_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
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
        ('Basic Information', {
            'fields': ('id', 'document', 'user', 'chunk_index')
        }),
        ('Content', {
            'fields': ('content_preview', 'content')
        }),
        ('Embedding Information', {
            'fields': ('embedding_model', 'token_count', 'character_count', 'embedding_cost'),
        }),
        ('Vector Embedding', {
            'fields': ('embedding',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Auto-generated chunk metadata (read-only)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True
    
    # Form field overrides
    formfield_overrides = {
        JSONField: {
            "widget": JSONEditorWidget,
        }
    }
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('document', 'user')
    
    @display(description="Chunk", ordering="chunk_index")
    def chunk_display(self, obj):
        """Display chunk identifier."""
        return f"Chunk {obj.chunk_index + 1}"
    
    @display(description="Tokens", ordering="token_count")
    def token_count_display(self, obj):
        """Display token count with formatting."""
        tokens = obj.token_count
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(
        description="Embedding",
        label={
            True: 'success',   # green for has embedding
            False: 'danger'    # red for no embedding
        }
    )
    def embedding_status(self, obj):
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        return has_embedding, "✓ Vectorized" if has_embedding else "✗ Not vectorized"
    
    @display(description="Document", ordering="document__title")
    def document_link(self, obj):
        """Display document title with admin link."""
        url = reverse('admin:django_cfg_knowbase_document_change', args=[obj.document.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">{}</a>',
            url,
            obj.document.title
        )
    
    @display(description="Cost (USD)", ordering="embedding_cost")
    def embedding_cost_display(self, obj):
        """Display embedding cost with currency formatting."""
        return f"${obj.embedding_cost:.6f}"
    
    @display(description="Content Preview")
    def content_preview(self, obj):
        """Display content preview with truncation."""
        preview = obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
        return format_html(
            '<div style="max-width: 400px; word-wrap: break-word;">{}</div>',
            preview
        )
    
    @display(description="Has Embedding", boolean=True)
    def has_embedding(self, obj):
        """Check if chunk has embedding vector."""
        return obj.embedding is not None and len(obj.embedding) > 0
    
    @display(description="Embedding Info")
    def embedding_info(self, obj):
        """Display embedding information safely."""
        if obj.embedding is not None and len(obj.embedding) > 0:
            return format_html(
                '<span style="color: green;">✓ Vector ({} dimensions)</span>',
                len(obj.embedding)
            )
        return format_html(
            '<span style="color: red;">✗ No embedding</span>'
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add chunk statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_chunks=Count('id'),
            total_tokens=Sum('token_count'),
            total_characters=Sum('character_count'),
            total_embedding_cost=Sum('embedding_cost'),
            avg_tokens_per_chunk=Avg('token_count')
        )
        
        # Model breakdown
        model_counts = dict(
            queryset.values_list('embedding_model').annotate(
                count=Count('id')
            )
        )
        
        extra_context['chunk_stats'] = {
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_characters': stats['total_characters'] or 0,
            'total_embedding_cost': f"${(stats['total_embedding_cost'] or 0):.6f}",
            'avg_tokens_per_chunk': f"{(stats['avg_tokens_per_chunk'] or 0):.0f}",
            'model_counts': model_counts
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin interface for DocumentCategory model with Unfold styling."""
    
    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'short_uuid', 'name', 'visibility_badge', 'document_count', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Unfold configuration
    compressed_fields = True
    warn_unsaved_form = True
    
    # Form field overrides
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    
    @display(
        description="Visibility",
        ordering="is_public",
        label={
            'public': 'success',
            'private': 'danger'
        }
    )
    def visibility_badge(self, obj):
        """Display visibility status with color coding."""
        status = 'public' if obj.is_public else 'private'
        label = 'Public' if obj.is_public else 'Private'
        return status, label
    
    @display(description="Documents", ordering="document_count")
    def document_count(self, obj):
        """Display count of documents in this category."""
        count = obj.documents.count()
        if count > 0:
            url = f"/admin/knowbase/document/?categories__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="text-decoration: none;">{} documents</a>',
                url, count
            )
        return "0 documents"
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related('documents')
    
    def changelist_view(self, request, extra_context=None):
        """Add category statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_categories=Count('id'),
            public_categories=Count('id', filter=models.Q(is_public=True)),
            private_categories=Count('id', filter=models.Q(is_public=False))
        )
        
        extra_context['category_stats'] = {
            'total_categories': stats['total_categories'] or 0,
            'public_categories': stats['public_categories'] or 0,
            'private_categories': stats['private_categories'] or 0
        }
        
        return super().changelist_view(request, extra_context)
