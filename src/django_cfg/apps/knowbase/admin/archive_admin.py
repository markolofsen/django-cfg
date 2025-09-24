"""
Admin interface for archive models with Unfold optimization.
"""

import hashlib
import logging
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from django.db.models.fields.json import JSONField
from django.shortcuts import redirect
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ExportMixin

from ..models.archive import DocumentArchive, ArchiveItem, ArchiveItemChunk

logger = logging.getLogger(__name__)


class ArchiveItemInline(TabularInline):
    """Inline for archive items with Unfold styling."""
    
    model = ArchiveItem
    verbose_name = "Archive Item"
    verbose_name_plural = "📁 Archive Items (Read-only)"
    extra = 0
    max_num = 0  # No new items allowed
    can_delete = False  # Prevent deletion through inline
    show_change_link = True  # Allow viewing individual items
    
    def has_add_permission(self, request, obj=None):
        """Disable adding new items through inline."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing items through inline."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting items through inline."""
        return False
    
    fields = [
        'item_name', 'content_type', 'file_size_display_inline', 
        'is_processable', 'chunks_count', 'created_at'
    ]
    readonly_fields = [
        'item_name', 'content_type', 'file_size_display_inline',
        'is_processable', 'chunks_count', 'created_at'
    ]
    
    # Unfold specific options
    hide_title = False  # Show titles for better UX
    classes = ['collapse']  # Collapsed by default
    
    @display(description="File Size")
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


@admin.register(DocumentArchive)
class DocumentArchiveAdmin(ExportMixin, ModelAdmin):
    """Admin interface for DocumentArchive."""
    
    list_display = [
        'title_display', 'user', 'archive_type_badge', 'status_badge',
        'items_count', 'chunks_count', 'vectorization_progress', 'file_size_display',
        'progress_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    inlines = [ArchiveItemInline]
    list_filter = [
        'processing_status', 'archive_type', 'is_public',
        'created_at', 'processed_at',
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = ['title', 'description', 'original_filename', 'user__username']
    autocomplete_fields = ['user', 'categories']
    readonly_fields = [
        'id', 'user', 'content_hash', 'original_filename', 'file_size', 'archive_type',
        'processing_status', 'processed_at', 'processing_duration_ms', 
        'processing_error', 'total_items', 'processed_items', 'total_chunks', 
        'vectorized_chunks', 'total_tokens', 'total_cost_usd', 'created_at', 
        'updated_at', 'progress_display', 'vectorization_progress_display',
        'items_link', 'chunks_link'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'user', 'categories', 'is_public')
        }),
        ('Archive Details', {
            'fields': (
                'archive_file', 'original_filename', 'file_size', 'archive_type',
                'content_hash'
            )
        }),
        ('Processing Status', {
            'fields': (
                'processing_status', 'processed_at', 'processing_duration_ms',
                'processing_error', 'progress_display',
                'vectorization_progress_display'
            )
        }),
        ('Statistics', {
            'fields': (
                'total_items', 'processed_items', 'total_chunks',
                'vectorized_chunks', 'total_tokens', 'total_cost_usd'
            )
        }),
        ('Related Data', {
            'fields': ('items_link', 'chunks_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
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
    
    @display(description="Archive Title", ordering="title")
    def title_display(self, obj):
        """Display archive title with truncation."""
        title = obj.title or "Untitled Archive"
        if len(title) > 50:
            title = title[:47] + "..."
        return format_html(
            '<div style="font-weight: 500;">{}</div>',
            title
        )
    
    @display(
        description="Archive Type",
        ordering="archive_type",
        label={
            'DOCUMENTS': 'info',     # blue for documents
            'CODE': 'success',       # green for code
            'MIXED': 'warning',      # orange for mixed
            'OTHER': 'danger'        # red for other
        }
    )
    def archive_type_badge(self, obj):
        """Display archive type with color coding."""
        return obj.archive_type, obj.get_archive_type_display()
    
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
    
    @display(description="File Size", ordering="file_size")
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @display(description="Items", ordering="total_items")
    def items_count(self, obj):
        """Display items count with link."""
        count = obj.total_items
        if count > 0:
            url = f"/admin/knowbase/archiveitem/?archive__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="text-decoration: none;">{} items</a>',
                url, count
            )
        return "0 items"
    
    @display(description="Chunks", ordering="total_chunks")
    def chunks_count(self, obj):
        """Display chunks count with link."""
        count = obj.total_chunks
        if count > 0:
            url = f"/admin/knowbase/archiveitemchunk/?archive__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="text-decoration: none;">{} chunks</a>',
                url, count
            )
        return "0 chunks"
    
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
        try:
            # Check processing status first
            if obj.processing_status == 'pending':
                return 'no_chunks', 'Pending'
            elif obj.processing_status == 'processing':
                return 'partial', 'Processing...'
            elif obj.processing_status == 'failed':
                return 'none', 'Failed'
            
            progress = DocumentArchive.objects.get_vectorization_progress(obj.id)
            total = progress['total']
            vectorized = progress['vectorized']
            percentage = progress['percentage']
            
            if total == 0:
                return 'no_chunks', 'No chunks'
            elif percentage == 100:
                return 'completed', f'{vectorized}/{total} (100%)'
            elif percentage > 0:
                return 'partial', f'{vectorized}/{total} ({percentage}%)'
            else:
                return 'none', f'{vectorized}/{total} (0%)'
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting vectorization progress for archive {obj.id}: {e}")
            return 'no_chunks', 'Not ready'
    
    @display(description="Overall Progress")
    def progress_display(self, obj):
        """Display overall progress including processing and vectorization."""
        from ..models.base import ProcessingStatus
        
        # Calculate overall progress: 50% for processing, 50% for vectorization
        processing_progress = obj.processing_progress
        
        # Get vectorization progress
        try:
            vectorization_stats = DocumentArchive.objects.get_vectorization_progress(obj.id)
            vectorization_progress = vectorization_stats.get('percentage', 0)
        except Exception:
            vectorization_progress = 0
        
        # Overall progress: processing (50%) + vectorization (50%)
        overall_progress = (processing_progress * 0.5) + (vectorization_progress * 0.5)
        
        # Determine color based on status and progress
        if obj.processing_status == ProcessingStatus.COMPLETED and vectorization_progress == 100:
            color_class = "bg-green-500"  # Fully complete
        elif obj.processing_status == ProcessingStatus.FAILED:
            color_class = "bg-red-500"    # Failed
        elif overall_progress > 0:
            color_class = "bg-blue-500"   # In progress
        else:
            color_class = "bg-gray-300"   # Not started
        
        return format_html(
            '<div class="w-24 bg-gray-200 rounded-full h-2 dark:bg-gray-700">'
            '<div class="{} h-2 rounded-full transition-all duration-300" style="width: {}%"></div>'
            '</div>'
            '<span class="text-xs text-gray-600 dark:text-gray-400 ml-2">{}%</span>',
            color_class, overall_progress, int(overall_progress)
        )
    
    def vectorization_progress_display(self, obj: DocumentArchive) -> str:
        """Display vectorization progress with progress bar."""
        progress = obj.vectorization_progress
        color = 'green' if progress == 100 else 'blue' if progress > 0 else 'gray'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: {}; border-radius: 3px; '
            'text-align: center; line-height: 20px; color: white; font-size: 12px;">'
            '{}%</div></div>',
            progress, color, round(progress, 1)
        )
    vectorization_progress_display.short_description = "Vectorization Progress"
    
    def items_link(self, obj: DocumentArchive) -> str:
        """Link to archive items."""
        if obj.pk:
            url = reverse('admin:django_cfg_knowbase_archiveitem_changelist')
            return format_html(
                '<a href="{}?archive__id__exact={}">View {} Items</a>',
                url, obj.pk, obj.total_items
            )
        return "No items yet"
    items_link.short_description = "Items"
    
    def chunks_link(self, obj: DocumentArchive) -> str:
        """Link to archive chunks."""
        if obj.pk:
            url = reverse('admin:django_cfg_knowbase_archiveitemchunk_changelist')
            return format_html(
                '<a href="{}?archive__id__exact={}">View {} Chunks</a>',
                url, obj.pk, obj.total_chunks
            )
        return "No chunks yet"
    chunks_link.short_description = "Chunks"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        # Use all_users() to show all archives in admin, then filter by user if needed
        queryset = DocumentArchive.objects.all_users().select_related('user').prefetch_related('categories')
        
        # For non-superusers, filter by their own archives
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        
        return queryset
    
    def save_model(self, request, obj, form, change):
        """Automatically set user and file metadata when creating new archives."""
        if not change:  # Only for new archives
            obj.user = request.user
            
            # Auto-populate metadata from uploaded file
            if obj.archive_file:
                import hashlib
                import os
                
                # Set original filename
                if not obj.original_filename:
                    obj.original_filename = obj.archive_file.name
                
                # Set file size
                if not obj.file_size and hasattr(obj.archive_file, 'size'):
                    obj.file_size = obj.archive_file.size
                
                # Check for duplicates using manager method
                is_duplicate, existing_archive = DocumentArchive.objects.check_duplicate_before_save(
                    user=obj.user,
                    title=obj.title,
                    file_size=obj.file_size
                )
                
                if is_duplicate and existing_archive:
                    messages.error(
                        request,
                        f'❌ An archive with the same title and file size already exists: "{existing_archive.title}" '
                        f'(created {existing_archive.created_at.strftime("%Y-%m-%d %H:%M")}). '
                        f'Please use a different title or check if this is a duplicate upload.'
                    )
                    # Don't save, just return - this will keep the form open with the error
                    return
                
                # Set archive type based on file extension
                if not obj.archive_type:
                    filename = obj.archive_file.name.lower()
                    
                    # ZIP formats
                    if filename.endswith(('.zip', '.jar', '.war', '.ear')):
                        obj.archive_type = 'zip'
                    # TAR.GZ formats
                    elif filename.endswith(('.tar.gz', '.tgz')):
                        obj.archive_type = 'tar.gz'
                    # TAR.BZ2 formats  
                    elif filename.endswith(('.tar.bz2', '.tbz2', '.tar.bzip2')):
                        obj.archive_type = 'tar.bz2'
                    # TAR formats
                    elif filename.endswith('.tar'):
                        obj.archive_type = 'tar'
                    else:
                        # Default to zip for unknown formats
                        obj.archive_type = 'zip'
                
                # Generate content hash
                if not obj.content_hash and hasattr(obj.archive_file, 'read'):
                    obj.archive_file.seek(0)
                    content = obj.archive_file.read()
                    obj.content_hash = hashlib.sha256(content).hexdigest()
                    obj.archive_file.seek(0)
        
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}
        
        # Get summary statistics
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_archives=Count('id'),
            total_items=Sum('total_items'),
            total_chunks=Sum('total_chunks'),
            total_cost=Sum('total_cost_usd')
        )
        
        # Status breakdown
        status_counts = dict(
            queryset.values_list('processing_status').annotate(
                count=Count('id')
            )
        )
        
        extra_context['archive_stats'] = {
            'total_archives': stats['total_archives'] or 0,
            'total_items': stats['total_items'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'status_counts': status_counts
        }
        
        return super().changelist_view(request, extra_context)
    
    # Actions for detail view
    actions_detail = ["reprocess_archive"]
    
    @action(
        description="🔄 Reprocess Archive",
        icon="refresh",
        variant=ActionVariant.WARNING
    )
    def reprocess_archive(self, request, object_id):
        """Force reprocessing of the archive."""
        try:
            # Get the archive object to get its title for the message
            archive = self.get_object(request, object_id)
            if not archive:
                self.message_user(request, "Archive not found.", level='error')
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Use custom manager method to reprocess
            DocumentArchive.objects.reprocess(object_id)
            
            self.message_user(
                request, 
                f"Archive '{archive.title}' has been reset and queued for reprocessing.", 
                level='success'
            )
            
        except ValueError as e:
            self.message_user(
                request, 
                f"Error reprocessing archive: {e}", 
                level='error'
            )
        except Exception as e:
            logger.exception(f"Unexpected error reprocessing archive {object_id}")
            self.message_user(
                request, 
                f"Unexpected error reprocessing archive: {e}", 
                level='error'
            )
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@admin.register(ArchiveItem)
class ArchiveItemAdmin(ExportMixin, ModelAdmin):
    """Admin interface for ArchiveItem."""
    
    list_display = [
        'item_name_display', 'archive_link', 'content_type_badge', 'language_badge',
        'processable_badge', 'chunks_count_display', 'file_size_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    list_filter = [
        'content_type', 'is_processable', 'language', 'created_at',
        'archive__processing_status',
        ('archive', AutocompleteSelectFilter)
    ]
    search_fields = [
        'item_name', 'relative_path', 'archive__title',
        'language', 'archive__user__username'
    ]
    autocomplete_fields = ['archive']
    readonly_fields = [
        'id', 'user', 'content_hash', 'chunks_count', 'total_tokens',
        'processing_cost', 'created_at', 'updated_at',
        'archive_link', 'chunks_link', 'content_preview'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'archive_link', 'user', 'relative_path', 'item_name')
        }),
        ('File Details', {
            'fields': (
                'item_type', 'content_type', 'file_size',
                'content_hash', 'language', 'encoding'
            )
        }),
        ('Processing', {
            'fields': (
                'is_processable', 'chunks_count', 'total_tokens',
                'processing_cost'
            )
        }),
        ('Content', {
            'fields': ('content_preview',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Related Data', {
            'fields': ('chunks_link',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    
    @display(description="Item Name", ordering="item_name")
    def item_name_display(self, obj):
        """Display item name with truncation."""
        name = obj.item_name or "Unnamed Item"
        if len(name) > 40:
            name = name[:37] + "..."
        return format_html(
            '<div style="font-weight: 500;">{}</div>',
            name
        )
    
    @display(description="Archive", ordering="archive__title")
    def archive_link(self, obj):
        """Link to parent archive."""
        if obj.archive:
            url = reverse('admin:django_cfg_knowbase_documentarchive_change', args=[obj.archive.pk])
            title = obj.archive.title[:30] + "..." if len(obj.archive.title) > 30 else obj.archive.title
            return format_html('<a href="{}" style="text-decoration: none;">{}</a>', url, title)
        return "No archive"
    
    @display(
        description="Content Type",
        ordering="content_type",
        label={
            'TEXT': 'info',      # blue for text
            'CODE': 'success',   # green for code
            'BINARY': 'warning', # orange for binary
            'OTHER': 'secondary' # gray for other
        }
    )
    def content_type_badge(self, obj):
        """Display content type with color coding."""
        return obj.content_type, obj.get_content_type_display()
    
    @display(
        description="Language",
        ordering="language",
        label=True
    )
    def language_badge(self, obj):
        """Display language with badge."""
        return obj.language or "Unknown"
    
    @display(
        description="Processable",
        ordering="is_processable",
        label={
            True: 'success',   # green for processable
            False: 'danger'    # red for not processable
        }
    )
    def processable_badge(self, obj):
        """Display processable status."""
        return obj.is_processable, "Yes" if obj.is_processable else "No"
    
    @display(description="Chunks", ordering="chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count with link."""
        count = obj.chunks_count
        if count > 0:
            url = f"/admin/knowbase/archiveitemchunk/?item__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="text-decoration: none;">{} chunks</a>',
                url, count
            )
        return "0 chunks"
    
    @display(description="File Size", ordering="file_size")
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"
    
    def chunks_link(self, obj: ArchiveItem) -> str:
        """Link to item chunks."""
        if obj.pk:
            url = reverse('admin:django_cfg_knowbase_archiveitemchunk_changelist')
            return format_html(
                '<a href="{}?item__id__exact={}">View {} Chunks</a>',
                url, obj.pk, obj.chunks_count
            )
        return "No chunks yet"
    chunks_link.short_description = "Chunks"
    
    def content_preview(self, obj: ArchiveItem) -> str:
        """Show content preview."""
        if obj.raw_content:
            preview = obj.raw_content[:500]
            if len(obj.raw_content) > 500:
                preview += "..."
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', preview)
        return "No content"
    content_preview.short_description = "Content Preview"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        # Use all_users() to show all archive items in admin, then filter by user if needed
        queryset = ArchiveItem.objects.all_users().select_related('archive', 'user')
        
        # For non-superusers, filter by their own items
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        
        return queryset
    
    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new archive items."""
        if not change:  # Only for new items
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(ArchiveItemChunk)
class ArchiveItemChunkAdmin(ModelAdmin):
    """Admin interface for ArchiveItemChunk."""
    
    list_display = [
        'chunk_display', 'archive_link', 'item_link', 'chunk_type_badge',
        'token_count_display', 'embedding_status', 'cost_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    list_filter = [
        'chunk_type', 'created_at', 'embedding_model',
        'item__content_type', 'item__language',
        ('item', AutocompleteSelectFilter),
        ('archive', AutocompleteSelectFilter)
    ]
    search_fields = [
        'content', 'item__item_name', 'item__relative_path',
        'archive__title', 'item__archive__user__username'
    ]
    autocomplete_fields = ['item', 'archive']
    readonly_fields = [
        'id', 'user', 'token_count', 'character_count', 'embedding_model',
        'embedding_cost', 'created_at', 'updated_at',
        'archive_link', 'item_link', 'content_preview',
        'context_summary', 'embedding_status'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'archive_link', 'item_link', 'user', 'chunk_index', 'chunk_type')
        }),
        ('Content', {
            'fields': ('content_preview',)
        }),
        ('Context', {
            'fields': ('context_summary',),
            'classes': ('collapse',)
        }),
        ('Vectorization', {
            'fields': (
                'embedding_status', 'token_count', 'character_count',
                'embedding_model', 'embedding_cost'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
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
    
    @display(description="Chunk", ordering="chunk_index")
    def chunk_display(self, obj):
        """Display chunk identifier."""
        return f"Chunk {obj.chunk_index + 1}"
    
    @display(
        description="Chunk Type",
        ordering="chunk_type",
        label={
            'CONTENT': 'info',     # blue for content
            'HEADER': 'success',   # green for header
            'FOOTER': 'warning',   # orange for footer
            'METADATA': 'secondary' # gray for metadata
        }
    )
    def chunk_type_badge(self, obj):
        """Display chunk type with color coding."""
        return obj.chunk_type, obj.get_chunk_type_display()
    
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
    
    @display(description="Cost (USD)", ordering="embedding_cost")
    def cost_display(self, obj):
        """Display embedding cost with currency formatting."""
        return f"${obj.embedding_cost:.6f}"
    
    def archive_link(self, obj: ArchiveItemChunk) -> str:
        """Link to parent archive."""
        if obj.archive:
            url = reverse('admin:django_cfg_knowbase_documentarchive_change', args=[obj.archive.pk])
            return format_html('<a href="{}">{}</a>', url, obj.archive.title)
        return "No archive"
    archive_link.short_description = "Archive"
    
    def item_link(self, obj: ArchiveItemChunk) -> str:
        """Link to parent item."""
        if obj.item:
            url = reverse('admin:django_cfg_knowbase_archiveitem_change', args=[obj.item.pk])
            return format_html('<a href="{}">{}</a>', url, obj.item.item_name)
        return "No item"
    item_link.short_description = "Item"
    
    def changelist_view(self, request, extra_context=None):
        """Add chunk statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_chunks=Count('id'),
            vectorized_chunks=Count('id', filter=Q(embedding__isnull=False)),
            total_tokens=Sum('token_count'),
            total_characters=Sum('character_count'),
            total_embedding_cost=Sum('embedding_cost'),
            avg_tokens_per_chunk=Avg('token_count')
        )
        
        # Type breakdown
        type_counts = dict(
            queryset.values_list('chunk_type').annotate(
                count=Count('id')
            )
        )
        
        extra_context['chunk_stats'] = {
            'total_chunks': stats['total_chunks'] or 0,
            'vectorized_chunks': stats['vectorized_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_characters': stats['total_characters'] or 0,
            'total_embedding_cost': f"${(stats['total_embedding_cost'] or 0):.6f}",
            'avg_tokens_per_chunk': f"{(stats['avg_tokens_per_chunk'] or 0):.0f}",
            'type_counts': type_counts
        }
        
        return super().changelist_view(request, extra_context)
    
    def content_preview(self, obj: ArchiveItemChunk) -> str:
        """Show content preview."""
        preview = obj.content[:300]
        if len(obj.content) > 300:
            preview += "..."
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', preview)
    content_preview.short_description = "Content Preview"
    
    def context_summary(self, obj: ArchiveItemChunk) -> str:
        """Show context summary."""
        context = obj.get_context_summary()
        return format_html('<pre>{}</pre>', 
                          '\n'.join(f"{k}: {v}" for k, v in context.items()))
    context_summary.short_description = "Context Summary"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        # Use all_users() to show all archive item chunks in admin, then filter by user if needed
        queryset = ArchiveItemChunk.objects.all_users().select_related(
            'archive', 'item', 'user'
        )
        
        # For non-superusers, filter by their own chunks
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        
        return queryset
    
    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new archive item chunks."""
        if not change:  # Only for new chunks
            obj.user = request.user
        super().save_model(request, obj, form, change)
