"""
Archive admin interfaces using Django Admin Utilities.

Enhanced archive management with Material Icons and optimized queries.
"""

import hashlib
import logging
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from django.db.models.fields.json import JSONField
from django.shortcuts import redirect
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget
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

from ..models.archive import DocumentArchive, ArchiveItem, ArchiveItemChunk

logger = logging.getLogger(__name__)


class ArchiveItemInline(TabularInline):
    """Inline for archive items with Unfold styling."""
    
    model = ArchiveItem
    verbose_name = "Archive Item"
    verbose_name_plural = "📁 Archive Items (Read-only)"
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
class DocumentArchiveAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for DocumentArchive using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    list_display = [
        'title_display', 'user_display', 'archive_type_display', 'status_display',
        'items_count', 'chunks_count', 'vectorization_progress', 'file_size_display',
        'progress_display', 'created_at_display'
    ]
    list_display_links = ['title_display']
    ordering = ['-created_at']
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
        'vectorized_chunks', 'total_cost_usd', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('📁 Archive Info', {
            'fields': ('id', 'title', 'description', 'user', 'categories', 'is_public'),
            'classes': ('tab',)
        }),
        ('📄 File Details', {
            'fields': ('original_filename', 'file_size', 'archive_type', 'content_hash'),
            'classes': ('tab',)
        }),
        ('⚙️ Processing Status', {
            'fields': (
                'processing_status', 'processed_at', 'processing_duration_ms',
                'processing_error'
            ),
            'classes': ('tab',)
        }),
        ('📊 Statistics', {
            'fields': ('total_items', 'processed_items', 'total_chunks', 'vectorized_chunks', 'total_cost_usd'),
            'classes': ('tab',)
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
    
    actions = ['reprocess_archives', 'mark_as_public', 'mark_as_private']
    
    @display(description="Archive Title", ordering="title")
    def title_display(self, obj):
        """Display archive title."""
        title = obj.title or "Untitled Archive"
        if len(title) > 50:
            title = title[:47] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.ARCHIVE)
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
    
    @display(description="Archive Type")
    def archive_type_display(self, obj):
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
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.FOLDER_ZIP)
        return StatusBadge.create(
            text=obj.archive_type.upper(),
            variant=variant,
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Display processing status."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'processing': 'info',
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            },
            show_icons=True,
            icon=Icons.CHECK_CIRCLE if obj.processing_status == 'completed' else Icons.ERROR if obj.processing_status == 'failed' else Icons.SCHEDULE
        )
        return self.display_status_auto(obj, 'processing_status', status_config)
    
    @display(description="Items", ordering="total_items")
    def items_count(self, obj):
        """Display items count."""
        total = obj.total_items or 0
        processed = obj.processed_items or 0
        return f"{processed}/{total} items"
    
    @display(description="Chunks", ordering="total_chunks")
    def chunks_count(self, obj):
        """Display chunks count."""
        total = obj.total_chunks or 0
        vectorized = obj.vectorized_chunks or 0
        return f"{vectorized}/{total} chunks"
    
    @display(description="Vectorization")
    def vectorization_progress(self, obj):
        """Display vectorization progress."""
        total = obj.total_chunks or 0
        vectorized = obj.vectorized_chunks or 0
        
        if total == 0:
            return "No chunks"
        
        percentage = (vectorized / total) * 100
        
        if percentage == 100:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="100%", variant="success", config=config)
        elif percentage > 0:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.SCHEDULE)
            return StatusBadge.create(text=f"{percentage:.1f}%", variant="warning", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ERROR)
            return StatusBadge.create(text="0%", variant="danger", config=config)
    
    @display(description="File Size", ordering="file_size")
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"
    
    @display(description="Progress")
    def progress_display(self, obj):
        """Display overall progress."""
        total_items = obj.total_items or 0
        processed_items = obj.processed_items or 0
        
        if total_items == 0:
            return "No items"
        
        percentage = (processed_items / total_items) * 100
        return f"{percentage:.1f}%"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Reprocess archives", variant=ActionVariant.INFO)
    def reprocess_archives(self, request, queryset):
        """Reprocess selected archives."""
        count = queryset.count()
        messages.info(request, f"Reprocess functionality not implemented yet. {count} archives selected.")
    
    @action(description="Mark as public", variant=ActionVariant.SUCCESS)
    def mark_as_public(self, request, queryset):
        """Mark selected archives as public."""
        updated = queryset.update(is_public=True)
        messages.success(request, f"Marked {updated} archives as public.")
    
    @action(description="Mark as private", variant=ActionVariant.WARNING)
    def mark_as_private(self, request, queryset):
        """Mark selected archives as private."""
        updated = queryset.update(is_public=False)
        messages.warning(request, f"Marked {updated} archives as private.")
    
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


@admin.register(ArchiveItem)
class ArchiveItemAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ArchiveItem using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['archive', 'user']
    
    list_display = [
        'item_name_display', 'archive_display', 'user_display', 'content_type_display',
        'file_size_display', 'processable_display', 'chunks_count_display', 'created_at_display'
    ]
    list_display_links = ['item_name_display']
    ordering = ['-created_at']
    list_filter = [
        'content_type', 'is_processable', 'created_at',
        ('archive', AutocompleteSelectFilter),
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = ['item_name', 'content_type', 'archive__title', 'user__username']
    autocomplete_fields = ['archive', 'user']
    readonly_fields = [
        'id', 'user', 'file_size', 'content_type', 'is_processable',
        'chunks_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('📄 Item Info', {
            'fields': ('id', 'item_name', 'archive', 'user'),
            'classes': ('tab',)
        }),
        ('📁 File Details', {
            'fields': ('content_type', 'file_size', 'is_processable'),
            'classes': ('tab',)
        }),
        ('📊 Processing', {
            'fields': ('chunks_count',),
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )
    
    actions = ['mark_as_processable', 'mark_as_not_processable']
    
    @display(description="Item Name", ordering="item_name")
    def item_name_display(self, obj):
        """Display item name."""
        name = obj.item_name
        if len(name) > 50:
            name = name[:47] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.INSERT_DRIVE_FILE)
        return StatusBadge.create(
            text=name,
            variant="primary",
            config=config
        )
    
    @display(description="Archive", ordering="archive__title")
    def archive_display(self, obj):
        """Display archive title."""
        return obj.archive.title or "Untitled Archive"
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Content Type")
    def content_type_display(self, obj):
        """Display content type with badge."""
        if not obj.content_type:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
        return StatusBadge.create(
            text=obj.content_type,
            variant="info",
            config=config
        )
    
    @display(description="File Size", ordering="file_size")
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"
    
    @display(description="Processable")
    def processable_display(self, obj):
        """Display processable status."""
        if obj.is_processable:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Yes", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(text="No", variant="danger", config=config)
    
    @display(description="Chunks", ordering="chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count."""
        count = obj.chunks_count or 0
        return f"{count} chunks"
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Mark as processable", variant=ActionVariant.SUCCESS)
    def mark_as_processable(self, request, queryset):
        """Mark selected items as processable."""
        updated = queryset.update(is_processable=True)
        messages.success(request, f"Marked {updated} items as processable.")
    
    @action(description="Mark as not processable", variant=ActionVariant.WARNING)
    def mark_as_not_processable(self, request, queryset):
        """Mark selected items as not processable."""
        updated = queryset.update(is_processable=False)
        messages.warning(request, f"Marked {updated} items as not processable.")


@admin.register(ArchiveItemChunk)
class ArchiveItemChunkAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ArchiveItemChunk using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['archive_item', 'user']
    
    list_display = [
        'chunk_display', 'archive_item_display', 'user_display', 'token_count_display',
        'embedding_status', 'embedding_cost_display', 'created_at_display'
    ]
    list_display_links = ['chunk_display']
    ordering = ['-created_at']
    list_filter = [
        'embedding_model', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('archive_item', AutocompleteSelectFilter)
    ]
    search_fields = ['archive_item__item_name', 'user__username', 'content']
    autocomplete_fields = ['item', 'user']
    readonly_fields = [
        'id', 'token_count', 'character_count', 'embedding_cost',
        'created_at', 'updated_at', 'content_preview'
    ]
    
    fieldsets = (
        ('📄 Chunk Info', {
            'fields': ('id', 'archive_item', 'user', 'chunk_index'),
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ('content_preview', 'content'),
            'classes': ('tab',)
        }),
        ('🔗 Embedding', {
            'fields': ('embedding_model', 'token_count', 'character_count', 'embedding_cost'),
            'classes': ('tab',)
        }),
        ('🧠 Vector', {
            'fields': ('embedding',),
            'classes': ('tab', 'collapse')
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        })
    )
    
    actions = ['regenerate_embeddings', 'clear_embeddings']
    
    @display(description="Chunk", ordering="chunk_index")
    def chunk_display(self, obj):
        """Display chunk identifier."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.ARTICLE)
        return StatusBadge.create(
            text=f"Chunk {obj.chunk_index + 1}",
            variant="info",
            config=config
        )
    
    @display(description="Archive Item", ordering="archive_item__item_name")
    def archive_item_display(self, obj):
        """Display archive item name."""
        return obj.archive_item.item_name
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Tokens", ordering="token_count")
    def token_count_display(self, obj):
        """Display token count with formatting."""
        tokens = obj.token_count
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Embedding")
    def embedding_status(self, obj):
        """Display embedding status."""
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="✓ Vectorized", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.ERROR)
            return StatusBadge.create(text="✗ Not vectorized", variant="danger", config=config)
    
    @display(description="Cost (USD)", ordering="embedding_cost")
    def embedding_cost_display(self, obj):
        """Display embedding cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return self.display_money_amount(obj, 'embedding_cost', config)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Content Preview")
    def content_preview(self, obj):
        """Display content preview with truncation."""
        return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
    
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
