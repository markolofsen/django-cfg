"""
External Data admin interfaces using Django Admin Utilities.

Enhanced external data management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.http import urlencode
from django.shortcuts import redirect
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from django.db.models.fields.json import JSONField
from django.utils import timezone
from django import forms
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
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

from ..models.external_data import ExternalData, ExternalDataChunk, ExternalDataType, ExternalDataStatus


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
    
    @display(description="Content Preview")
    def content_preview_inline(self, obj):
        """Shortened content preview for inline display."""
        if not obj.content:
            return "—"
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    
    @display(description="Has Embedding", boolean=True)
    def has_embedding_inline(self, obj):
        """Check if chunk has embedding vector for inline."""
        return obj.embedding is not None and len(obj.embedding) > 0
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('external_data', 'user')


@admin.register(ExternalData)
class ExternalDataAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ExternalData model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user', 'category']
    
    list_display = [
        'title_display', 'source_type_display', 'source_identifier_display', 'user_display',
        'status_display', 'chunks_count_display', 'tokens_display', 'cost_display',
        'visibility_display', 'processed_at_display', 'created_at_display'
    ]
    list_display_links = ['title_display']
    ordering = ['-created_at']
    inlines = [ExternalDataChunkInline]
    list_filter = [
        'source_type', 'status', 'is_active', 'is_public',
        'embedding_model', 'processed_at', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('category', AutocompleteSelectFilter)
    ]
    search_fields = ['title', 'description', 'source_identifier', 'user__username', 'user__email']
    autocomplete_fields = ['user', 'category']
    readonly_fields = [
        'id', 'user', 'source_type', 'source_identifier', 'status',
        'processed_at', 'processing_error',
        'total_chunks', 'total_tokens', 'processing_cost',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('🔗 External Data Info', {
            'fields': ('id', 'title', 'description', 'user', 'category'),
            'classes': ('tab',)
        }),
        ('📡 Source Details', {
            'fields': ('source_type', 'source_identifier', 'source_metadata'),
            'classes': ('tab',)
        }),
        ('⚙️ Processing Status', {
            'fields': ('status', 'processed_at', 'processing_error'),
            'classes': ('tab',)
        }),
        ('📊 Statistics', {
            'fields': ('total_chunks', 'total_tokens', 'processing_cost'),
            'classes': ('tab',)
        }),
        ('🔧 Settings', {
            'fields': ('is_active', 'is_public', 'embedding_model'),
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
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget}
    }
    
    actions = ['reprocess_data', 'activate_data', 'deactivate_data', 'mark_as_public', 'mark_as_private']
    
    @display(description="Title", ordering="title")
    def title_display(self, obj):
        """Display external data title."""
        title = obj.title or "Untitled External Data"
        if len(title) > 50:
            title = title[:47] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CLOUD)
        return StatusBadge.create(
            text=title,
            variant="primary",
            config=config
        )
    
    @display(description="Source Type")
    def source_type_display(self, obj):
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
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.source_type.upper(),
            variant=variant,
            config=config
        )
    
    @display(description="Source ID", ordering="source_identifier")
    def source_identifier_display(self, obj):
        """Display source identifier with truncation."""
        if not obj.source_identifier:
            return "—"
        
        identifier = obj.source_identifier
        if len(identifier) > 30:
            identifier = identifier[:27] + "..."
        
        return identifier
    
    @display(description="User")
    def user_display(self, obj):
        """User display."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
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
            icon=Icons.CHECK_CIRCLE if obj.status == 'completed' else Icons.ERROR if obj.status == 'failed' else Icons.SCHEDULE
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Chunks", ordering="chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count."""
        count = obj.chunks_count or 0
        return f"{count} chunks"
    
    @display(description="Tokens", ordering="total_tokens")
    def tokens_display(self, obj):
        """Display token count with formatting."""
        tokens = obj.total_tokens or 0
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)
    
    @display(description="Cost (USD)", ordering="processing_cost")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        config = MoneyDisplayConfig(
            currency="USD",
            decimal_places=6,
            show_sign=False
        )
        return self.display_money_amount(obj, 'processing_cost', config)
    
    @display(description="Visibility")
    def visibility_display(self, obj):
        """Display visibility status."""
        if obj.is_public:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
            return StatusBadge.create(text="Public", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.LOCK)
            return StatusBadge.create(text="Private", variant="danger", config=config)
    
    @display(description="Processed", ordering="processed_at")
    def processed_at_display(self, obj):
        """Processed time with relative display."""
        if not obj.processed_at:
            return "—"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'processed_at', config)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Reprocess data", variant=ActionVariant.INFO)
    def reprocess_data(self, request, queryset):
        """Reprocess selected external data."""
        count = queryset.count()
        messages.info(request, f"Reprocess functionality not implemented yet. {count} items selected.")
    
    @action(description="Activate data", variant=ActionVariant.SUCCESS)
    def activate_data(self, request, queryset):
        """Activate selected external data."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} external data items.")
    
    @action(description="Deactivate data", variant=ActionVariant.WARNING)
    def deactivate_data(self, request, queryset):
        """Deactivate selected external data."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} external data items.")
    
    @action(description="Mark as public", variant=ActionVariant.SUCCESS)
    def mark_as_public(self, request, queryset):
        """Mark selected data as public."""
        updated = queryset.update(is_public=True)
        messages.success(request, f"Marked {updated} items as public.")
    
    @action(description="Mark as private", variant=ActionVariant.WARNING)
    def mark_as_private(self, request, queryset):
        """Mark selected data as private."""
        updated = queryset.update(is_public=False)
        messages.warning(request, f"Marked {updated} items as private.")
    
    def changelist_view(self, request, extra_context=None):
        """Add external data statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_items=Count('id'),
            active_items=Count('id', filter=Q(is_active=True)),
            completed_items=Count('id', filter=Q(status='completed')),
            total_chunks=Sum('chunks_count'),
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


@admin.register(ExternalDataChunk)
class ExternalDataChunkAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for ExternalDataChunk model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['external_data', 'user']
    
    list_display = [
        'chunk_display', 'external_data_display', 'user_display', 'token_count_display',
        'embedding_status', 'embedding_cost_display', 'created_at_display'
    ]
    list_display_links = ['chunk_display']
    ordering = ['-created_at']
    list_filter = [
        'embedding_model', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('external_data', AutocompleteSelectFilter)
    ]
    search_fields = ['external_data__title', 'user__username', 'content']
    autocomplete_fields = ['external_data', 'user']
    readonly_fields = [
        'id', 'token_count', 'character_count', 'embedding_cost',
        'created_at', 'updated_at', 'content_preview'
    ]
    
    fieldsets = (
        ('🔗 Chunk Info', {
            'fields': ('id', 'external_data', 'user', 'chunk_index'),
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ('content_preview', 'content'),
            'classes': ('tab',)
        }),
        ('🧠 Embedding', {
            'fields': ('embedding_model', 'token_count', 'character_count', 'embedding_cost'),
            'classes': ('tab',)
        }),
        ('🔧 Vector', {
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
    
    @display(description="External Data", ordering="external_data__title")
    def external_data_display(self, obj):
        """Display external data title."""
        return obj.external_data.title or "Untitled External Data"
    
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
