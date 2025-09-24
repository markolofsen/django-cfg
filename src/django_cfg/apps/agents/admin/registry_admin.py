"""
Registry admin interfaces with Unfold optimization.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.db.models.fields.json import JSONField
from datetime import timedelta
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ImportExportModelAdmin, ExportMixin, ImportForm, ExportForm

from ..models.registry import AgentDefinition, AgentTemplate
from ..models.execution import AgentExecution


class AgentExecutionInline(TabularInline):
    """Inline for agent executions with Unfold styling."""
    
    model = AgentExecution
    verbose_name = "Agent Execution"
    verbose_name_plural = "🚀 Recent Executions (Read-only)"
    extra = 0
    max_num = 5  # Show only last 5 executions
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fields = [
        'user', 'status_badge_inline', 'execution_time_display', 
        'tokens_used', 'cost_display_inline', 'created_at'
    ]
    readonly_fields = [
        'user', 'status_badge_inline', 'execution_time_display',
        'tokens_used', 'cost_display_inline', 'created_at'
    ]
    
    # Unfold specific options
    hide_title = False
    classes = ['collapse']
    
    @display(description="Status")
    def status_badge_inline(self, obj):
        """Status badge for inline display."""
        colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'running': 'bg-blue-100 text-blue-800', 
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800'
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color_class, obj.get_status_display()
        )
    
    @display(description="Execution Time")
    def execution_time_display(self, obj):
        """Execution time display for inline."""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "-"
    
    @display(description="Cost")
    def cost_display_inline(self, obj):
        """Cost display for inline."""
        if obj.cost:
            return f"${obj.cost:.4f}"
        return "-"
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('user').order_by('-created_at')


@admin.register(AgentDefinition)
class AgentDefinitionAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin interface for AgentDefinition with Unfold styling."""
    
    # Import/Export configuration
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'display_name', 'category_badge', 'status_badges',
        'usage_stats', 'performance_indicator', 'created_by', 'created_at'
    ]
    ordering = ['-created_at']
    inlines = [AgentExecutionInline]
    list_filter = [
        'is_active', 'is_public', 'category', 'enable_caching', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'display_name', 'description', 'instructions']
    autocomplete_fields = ['created_by', 'allowed_users', 'allowed_groups']
    readonly_fields = [
        'usage_count', 'last_used_at', 'created_at', 'updated_at',
        'performance_metrics', 'recent_executions_summary'
    ]
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🤖 Basic Information", {
            'fields': ('name', 'display_name', 'description', 'category', 'tags'),
            'classes': ('tab',)
        }),
        ("⚙️ Configuration", {
            'fields': ('instructions', 'deps_type', 'output_type', 'model'),
            'classes': ('tab',)
        }),
        ("🔧 Execution Settings", {
            'fields': ('timeout', 'max_retries', 'enable_caching'),
            'classes': ('tab',)
        }),
        ("🛠️ Tools & Advanced", {
            'fields': ('tools_config',),
            'classes': ('tab', 'collapse')
        }),
        ("🔐 Access Control", {
            'fields': ('is_active', 'is_public', 'allowed_users', 'allowed_groups'),
            'classes': ('tab',)
        }),
        ("📊 Statistics", {
            'fields': ('usage_count', 'last_used_at', 'performance_metrics', 'recent_executions_summary'),
            'classes': ('tab', 'collapse')
        }),
        ("📝 Metadata", {
            'fields': ('version', 'created_by', 'created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    # Unfold actions
    actions = ['activate_agents', 'deactivate_agents', 'make_public', 'make_private']
    
    @display(description="Agent Name")
    def name_display(self, obj):
        """Enhanced name display with icon."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-blue-600 font-medium">{}</span>'
            '</div>',
            obj.name
        )
    
    @display(description="Category")
    def category_badge(self, obj):
        """Category with badge styling."""
        if not obj.category:
            return "-"
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">{}</span>',
            obj.category
        )
    
    @display(description="Status")
    def status_badges(self, obj):
        """Combined status badges."""
        badges = []
        
        if obj.is_active:
            badges.append('<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Active</span>')
        else:
            badges.append('<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Inactive</span>')
            
        if obj.is_public:
            badges.append('<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Public</span>')
        else:
            badges.append('<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Private</span>')
            
        if obj.enable_caching:
            badges.append('<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Cached</span>')
        
        return format_html('<div class="space-y-1">{}</div>', ''.join(badges))
    
    @display(description="Usage Stats")
    def usage_stats(self, obj):
        """Usage statistics display."""
        return format_html(
            '<div class="text-sm">'
            '<div class="font-medium text-gray-900">{} executions</div>'
            '<div class="text-gray-500">{}</div>'
            '</div>',
            obj.usage_count,
            f"Last used: {obj.last_used_at.strftime('%m/%d %H:%M')}" if obj.last_used_at else "Never used"
        )
    
    @display(description="Performance")
    def performance_indicator(self, obj):
        """Performance indicator based on recent executions."""
        # This would need to be calculated from related executions
        return format_html(
            '<div class="flex items-center space-x-1">'
            '<div class="w-2 h-2 bg-green-400 rounded-full"></div>'
            '<span class="text-xs text-gray-600">Good</span>'
            '</div>'
        )
    
    @display(description="Performance Metrics")
    def performance_metrics(self, obj):
        """Detailed performance metrics."""
        # This would calculate from related AgentExecution objects
        return format_html(
            '<div class="space-y-2">'
            '<div>Avg Execution Time: <span class="font-mono">-</span></div>'
            '<div>Success Rate: <span class="font-mono">-</span></div>'
            '<div>Avg Cost: <span class="font-mono">-</span></div>'
            '</div>'
        )
    
    @display(description="Recent Executions")
    def recent_executions_summary(self, obj):
        """Summary of recent executions."""
        return format_html(
            '<div class="text-sm text-gray-600">'
            'See inline executions below for recent activity'
            '</div>'
        )
    
    @action(description="Activate selected agents", icon="play_arrow", variant=ActionVariant.SUCCESS)
    def activate_agents(self, request, queryset):
        """Activate selected agents."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} agents.")
    
    @action(description="Deactivate selected agents", icon="pause", variant=ActionVariant.WARNING)
    def deactivate_agents(self, request, queryset):
        """Deactivate selected agents."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} agents.")
    
    @action(description="Make public", icon="public", variant=ActionVariant.INFO)
    def make_public(self, request, queryset):
        """Make selected agents public."""
        updated = queryset.update(is_public=True)
        messages.info(request, f"Made {updated} agents public.")
    
    @action(description="Make private", icon="lock", variant=ActionVariant.DEFAULT)
    def make_private(self, request, queryset):
        """Make selected agents private."""
        updated = queryset.update(is_public=False)
        messages.info(request, f"Made {updated} agents private.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('created_by').prefetch_related('allowed_users', 'allowed_groups')
    
    def save_model(self, request, obj, form, change):
        """Set created_by on new objects."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AgentTemplate)
class AgentTemplateAdmin(ModelAdmin, ExportMixin):
    """Admin interface for AgentTemplate with Unfold styling."""
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = ['name_display', 'category_badge', 'status_badge', 'use_cases_preview', 'created_by', 'created_at']
    ordering = ['-created_at']
    list_filter = [
        'category', 'is_active', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'description', 'use_cases']
    autocomplete_fields = ['created_by']
    readonly_fields = ['created_at', 'updated_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("📋 Template Information", {
            'fields': ('name', 'description', 'category', 'use_cases'),
            'classes': ('tab',)
        }),
        ("⚙️ Template Configuration", {
            'fields': ('template_config', 'default_instructions', 'recommended_model'),
            'classes': ('tab',)
        }),
        ("🔧 Settings", {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('tab',)
        }),
    )
    
    actions = ['activate_templates', 'deactivate_templates']
    
    @display(description="Template Name")
    def name_display(self, obj):
        """Enhanced name display."""
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-purple-600 font-medium">{}</span>'
            '</div>',
            obj.name
        )
    
    @display(description="Category")
    def category_badge(self, obj):
        """Category badge."""
        if not obj.category:
            return "-"
        return format_html(
            '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">{}</span>',
            obj.category
        )
    
    @display(description="Status", boolean=True)
    def status_badge(self, obj):
        """Status badge."""
        return obj.is_active
    
    @display(description="Use Cases")
    def use_cases_preview(self, obj):
        """Preview of use cases."""
        if not obj.use_cases:
            return "-"
        preview = obj.use_cases[:100] + "..." if len(obj.use_cases) > 100 else obj.use_cases
        return format_html(
            '<div class="text-sm text-gray-600 max-w-xs truncate">{}</div>',
            preview
        )
    
    @action(description="Activate templates", icon="play_arrow", variant=ActionVariant.SUCCESS)
    def activate_templates(self, request, queryset):
        """Activate selected templates."""
        updated = queryset.update(is_active=True)
        messages.success(request, f"Activated {updated} templates.")
    
    @action(description="Deactivate templates", icon="pause", variant=ActionVariant.WARNING)
    def deactivate_templates(self, request, queryset):
        """Deactivate selected templates."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} templates.")
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('created_by')
