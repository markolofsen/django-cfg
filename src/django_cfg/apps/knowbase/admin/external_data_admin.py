"""
External Data admin interfaces with Unfold optimization.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
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
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ExportMixin

from ..models.external_data import ExternalData, ExternalDataChunk, ExternalDataType, ExternalDataStatus


class ExternalDataChunkInline(TabularInline):
    """Inline for external data chunks with Unfold styling."""
    
    model = ExternalDataChunk
    verbose_name = "External Data Chunk"
    verbose_name_plural = "🔗 External Data Chunks (Read-only)"
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
        return super().get_queryset(request).select_related('external_data', 'user')


@admin.register(ExternalData)
class ExternalDataAdmin(ModelAdmin, ExportMixin):
    """Admin interface for ExternalData model with Unfold styling."""
    
    list_display = [
        'title_display', 'source_type_badge', 'source_identifier_display', 'user',
        'status_badge', 'chunks_count_display', 'tokens_display', 'cost_display',
        'visibility_badge', 'processed_at', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
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
        'id', 'user', 'status', 'total_chunks', 'total_tokens', 'processing_cost',
        'processed_at', 'source_updated_at', 'processing_error', 'content_hash',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('📝 Basic Information', {
            'fields': ('title', 'description', 'category'),
            'description': 'Main information about the external data source'
        }),
        ('📄 Content', {
            'fields': ('content',),
            'description': 'Main content for vectorization'
        }),
        ('🔗 Source Configuration', {
            'fields': ('source_type', 'source_identifier', 'source_config'),
            'description': 'Configure how data is extracted from the source'
        }),
        ('⚙️ Processing Settings', {
            'fields': ('chunk_size', 'overlap_size', 'embedding_model', 'similarity_threshold'),
            'description': 'Settings for text chunking, vectorization, and search'
        }),
        ('🔒 Access Control', {
            'fields': ('is_active', 'is_public'),
            'description': 'Control visibility and access to this data'
        }),
        ('📊 Processing Status (Read-only)', {
            'fields': ('status', 'processing_error', 'processed_at', 'source_updated_at', 'content_hash'),
            'classes': ('collapse',),
            'description': 'Current processing status and error information'
        }),
        ('📈 Statistics (Read-only)', {
            'fields': ('total_chunks', 'total_tokens', 'processing_cost'),
            'classes': ('collapse',),
            'description': 'Processing statistics and costs'
        }),
        ('📋 Additional Data (Read-only)', {
            'fields': ('metadata', 'tags'),
            'classes': ('collapse',),
            'description': 'Auto-generated metadata and tags'
        }),
        ('🔧 System Information (Read-only)', {
            'fields': ('id', 'user', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information'
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
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Custom field handling for better UX."""
        if db_field.name == 'content':
            kwargs['widget'] = WysiwygWidget()
        elif db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={
                'rows': 3,
                'cols': 80,
                'style': 'width: 100%;'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    actions = [
        'mark_for_reprocessing',
        'regenerate_embeddings',
        'activate_selected',
        'deactivate_selected',
        'make_public',
        'make_private'
    ]
    
    # Actions for detail view (individual object edit page)
    actions_detail = ["reprocess_external_data"]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = super().get_queryset(request).select_related('user', 'category')
        queryset = queryset.annotate(
            annotated_chunks_count=Count('chunks'),
            total_embedding_cost=Sum('chunks__embedding_cost')
        )
        
        # For non-superusers, filter by their own external data
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        
        return queryset
    
    def save_model(self, request, obj, form, change):
        """Automatically set user to current user when creating new external data."""
        if not change:  # Only for new external data
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    @display(description="External Data Title", ordering="title")
    def title_display(self, obj):
        """Display external data title with truncation."""
        title = obj.title or "Untitled External Data"
        if len(title) > 50:
            title = title[:47] + "..."
        return format_html(
            '<div style="font-weight: 500;">{}</div>',
            title
        )
    
    @display(
        description="Source Type",
        ordering="source_type",
        label={
            'model': 'info',      # blue for Django models
            'api': 'success',     # green for API
            'database': 'warning', # orange for database
            'file': 'secondary',  # gray for files
            'custom': 'danger'    # red for custom
        }
    )
    def source_type_badge(self, obj):
        """Display source type with color coding."""
        return obj.source_type, obj.get_source_type_display()
    
    @display(description="Source Identifier", ordering="source_identifier")
    def source_identifier_display(self, obj):
        """Display source identifier with truncation."""
        identifier = obj.source_identifier
        if len(identifier) > 30:
            identifier = identifier[:27] + "..."
        return format_html(
            '<code style="font-size: 12px;">{}</code>',
            identifier
        )
    
    @display(
        description="Status",
        ordering="status",
        label={
            'pending': 'warning',     # orange for pending
            'processing': 'info',     # blue for processing
            'completed': 'success',   # green for completed
            'failed': 'danger',       # red for failed
            'outdated': 'secondary'   # gray for outdated
        }
    )
    def status_badge(self, obj):
        """Display processing status with color coding."""
        return obj.status, obj.get_status_display()
    
    @display(
        description="Visibility",
        ordering="is_active",
        label={
            True: 'success',   # green for active
            False: 'danger'    # red for inactive
        }
    )
    def visibility_badge(self, obj):
        """Display visibility status with color coding."""
        if obj.is_active:
            status = "Active" + (" & Public" if obj.is_public else " & Private")
            return True, status
        else:
            return False, "Inactive"
    
    @display(description="Chunks", ordering="annotated_chunks_count")
    def chunks_count_display(self, obj):
        """Display chunks count with link."""
        count = getattr(obj, 'annotated_chunks_count', obj.chunks.count())
        if count > 0:
            url = f"/admin/knowbase/externaldatachunk/?external_data__id__exact={obj.id}"
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

    @display(description="Cost (USD)", ordering="processing_cost")
    def cost_display(self, obj):
        """Display cost with currency formatting."""
        return f"${obj.processing_cost:.6f}"
    
    @display(description="Content Hash")
    def content_hash_display(self, obj):
        """Display content hash for change tracking."""
        if obj.content_hash:
            return format_html(
                '<code style="font-size: 10px; color: #666;">{}</code>',
                obj.content_hash[:12] + "..."
            )
        return "-"
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}
        
        # Get summary statistics
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_external_data=Count('id'),
            active_external_data=Count('id', filter=Q(is_active=True)),
            total_chunks=Sum('total_chunks'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('processing_cost')
        )
        
        # Status breakdown
        status_counts = dict(
            queryset.values_list('status').annotate(
                count=Count('id')
            )
        )
        
        # Source type breakdown
        source_type_counts = dict(
            queryset.values_list('source_type').annotate(
                count=Count('id')
            )
        )
        
        extra_context['external_data_stats'] = {
            'total_external_data': stats['total_external_data'] or 0,
            'active_external_data': stats['active_external_data'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'status_counts': status_counts,
            'source_type_counts': source_type_counts
        }
        
        return super().changelist_view(request, extra_context)
    
    @admin.action(description='Mark selected for reprocessing')
    def mark_for_reprocessing(self, request, queryset):
        """Mark external data for reprocessing."""
        updated = queryset.update(
            status=ExternalDataStatus.PENDING,
            processing_error='',
            updated_at=timezone.now()
        )
        self.message_user(
            request,
            f"Marked {updated} external data sources for reprocessing."
        )
    
    @admin.action(description='Activate selected external data')
    def activate_selected(self, request, queryset):
        """Activate selected external data."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Activated {updated} external data sources."
        )
    
    @admin.action(description='Deactivate selected external data')
    def deactivate_selected(self, request, queryset):
        """Deactivate selected external data."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Deactivated {updated} external data sources."
        )
    
    @admin.action(description='Make selected external data public')
    def make_public(self, request, queryset):
        """Make selected external data public."""
        updated = queryset.update(is_public=True)
        self.message_user(
            request,
            f"Made {updated} external data sources public."
        )
    
    @admin.action(description='Make selected external data private')
    def make_private(self, request, queryset):
        """Make selected external data private."""
        updated = queryset.update(is_public=False)
        self.message_user(
            request,
            f"Made {updated} external data sources private."
        )
    
    @admin.action(description='🔄 Regenerate embeddings for selected external data')
    def regenerate_embeddings(self, request, queryset):
        """Regenerate embeddings for selected external data sources."""
        external_data_ids = [str(obj.id) for obj in queryset]
        
        if not external_data_ids:
            self.message_user(
                request,
                "No external data selected for regeneration.",
                level=messages.WARNING
            )
            return
        
        try:
            # Use manager method for regeneration
            result = ExternalData.objects.regenerate_external_data(external_data_ids)
            
            if result['success']:
                success_msg = (
                    f"✅ Successfully queued {result['regenerated_count']} external data sources "
                    f"for regeneration."
                )
                
                if result['failed_count'] > 0:
                    success_msg += f" {result['failed_count']} failed to queue."
                
                self.message_user(request, success_msg, level=messages.SUCCESS)
                
                # Show errors if any
                if result.get('errors'):
                    for error in result['errors'][:3]:  # Show first 3 errors
                        self.message_user(request, f"❌ {error}", level=messages.ERROR)
                    
                    if len(result['errors']) > 3:
                        self.message_user(
                            request,
                            f"... and {len(result['errors']) - 3} more errors.",
                            level=messages.WARNING
                        )
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.message_user(
                    request,
                    f"❌ Failed to regenerate external data: {error_msg}",
                    level=messages.ERROR
                )
                
        except Exception as e:
            self.message_user(
                request,
                f"❌ Error during regeneration: {str(e)}",
                level=messages.ERROR
            )
    
    @action(
        description="🔄 Reprocess External Data",
        icon="refresh",
        variant=ActionVariant.WARNING
    )
    def reprocess_external_data(self, request, object_id):
        """Force reprocessing of the external data source."""
        try:
            # Get the external data object
            external_data = self.get_object(request, object_id)
            if not external_data:
                self.message_user(
                    request, 
                    "External data not found.", 
                    level=messages.ERROR
                )
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Use manager method for regeneration
            result = ExternalData.objects.regenerate_external_data([str(external_data.id)])
            
            if result['success']:
                self.message_user(
                    request,
                    f"✅ Successfully queued '{external_data.title}' for reprocessing. "
                    f"Processing will begin shortly in the background.",
                    level=messages.SUCCESS
                )
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.message_user(
                    request,
                    f"❌ Failed to reprocess '{external_data.title}': {error_msg}",
                    level=messages.ERROR
                )
                
        except Exception as e:
            self.message_user(
                request,
                f"❌ Error during reprocessing: {str(e)}",
                level=messages.ERROR
            )
        
        # Redirect back to the same page
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    def has_add_permission(self, request):
        """Allow adding external data."""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Check change permissions."""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Check delete permissions."""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_delete_permission(request, obj)


@admin.register(ExternalDataChunk)
class ExternalDataChunkAdmin(ModelAdmin):
    """Admin interface for ExternalDataChunk model with Unfold styling."""
    
    list_display = [
        'chunk_display', 'external_data_link', 'user', 'token_count_display',
        'embedding_status', 'embedding_cost_display', 'created_at'
    ]
    ordering = ['-created_at']  # Newest first
    list_filter = [
        'embedding_model', 'external_data__source_type',
        'external_data__status', 'created_at',
        ('user', AutocompleteSelectFilter),
        ('external_data', AutocompleteSelectFilter)
    ]
    search_fields = ['external_data__title', 'external_data__source_identifier', 'content', 'user__username']
    readonly_fields = [
        'id', 'user', 'external_data', 'chunk_index', 'embedding_info', 
        'token_count', 'character_count', 'embedding_cost', 'embedding_model',
        'created_at', 'updated_at', 'content_preview'
    ]
    
    fieldsets = (
        ('📄 Content', {
            'fields': ('content_preview', 'content'),
            'description': 'Text content of this chunk'
        }),
        ('🔗 Relationships (Read-only)', {
            'fields': ('external_data', 'user', 'chunk_index'),
            'description': 'Links to parent external data and owner'
        }),
        ('📊 Metrics (Read-only)', {
            'fields': ('embedding_info', 'token_count', 'character_count', 'embedding_cost'),
            'description': 'Processing metrics and costs'
        }),
        ('🧠 Vector Embedding (Read-only)', {
            'fields': ('embedding_model', 'embedding'),
            'classes': ('collapse',),
            'description': 'Vector representation for semantic search'
        }),
        ('📋 Metadata (Read-only)', {
            'fields': ('chunk_metadata',),
            'classes': ('collapse',),
            'description': 'Auto-generated chunk metadata'
        }),
        ('🔧 System Information (Read-only)', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated information'
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
        return super().get_queryset(request).select_related('external_data', 'user')
    
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
    
    @display(description="External Data", ordering="external_data__title")
    def external_data_link(self, obj):
        """Display external data title with admin link."""
        url = reverse('admin:django_cfg_knowbase_externaldata_change', args=[obj.external_data.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">{}</a>',
            url,
            obj.external_data.title
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
    
    def has_add_permission(self, request):
        """Chunks are created automatically."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Chunks are read-only."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup."""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_delete_permission(request, obj)
