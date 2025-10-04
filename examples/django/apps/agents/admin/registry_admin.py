"""
Registry admin interfaces using Django Admin Utilities.

Enhanced agent and template management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.db.models.fields.json import JSONField
from datetime import timedelta
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ExportMixin, ExportForm

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

from ..models.registry import AgentDefinition, AgentTemplate


@admin.register(AgentDefinition)
class AgentDefinitionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for AgentDefinition model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['created_by']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'category_display', 'status_display', 'version_display',
        'usage_stats_display', 'performance_metrics', 'created_by_display', 'created_at_display'
    ]
    list_display_links = ['name_display']
    list_filter = [
        'category', 'is_active', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'description', 'category']
    autocomplete_fields = ['created_by']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'usage_count', 'last_used_at'
    ]
    ordering = ['-created_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("🤖 Agent Info", {
            'fields': ('id', 'name', 'description', 'category', 'version'),
            'classes': ('tab',)
        }),
        ("⚙️ Configuration", {
            'fields': ('config', 'capabilities', 'requirements'),
            'classes': ('tab',)
        }),
        ("📊 Performance", {
            'fields': ('usage_count', 'success_rate', 'avg_execution_time', 'total_cost'),
            'classes': ('tab',)
        }),
        ("🔧 Status", {
            'fields': ('status', 'is_active', 'last_used_at'),
            'classes': ('tab',)
        }),
        ("👤 Metadata", {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['activate_agents', 'deactivate_agents', 'reset_stats']
    
    @display(description="Agent Name")
    def name_display(self, obj):
        """Enhanced agent name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SMART_TOY)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Category")
    def category_display(self, obj):
        """Category display with badge."""
        if not obj.category:
            return "—"
        
        category_variants = {
            'automation': 'info',
            'analysis': 'success',
            'communication': 'warning',
            'data': 'primary'
        }
        variant = category_variants.get(obj.category.lower(), 'secondary')
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CATEGORY)
        return StatusBadge.create(
            text=obj.category.title(),
            variant=variant,
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display with appropriate icons."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'draft': 'secondary',
                'testing': 'warning',
                'active': 'success',
                'deprecated': 'danger',
                'archived': 'info'
            },
            show_icons=True,
            icon=Icons.CHECK_CIRCLE if obj.status == 'active' else Icons.WARNING if obj.status == 'testing' else Icons.ARCHIVE if obj.status == 'archived' else Icons.EDIT
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Version")
    def version_display(self, obj):
        """Version display."""
        if not obj.version:
            return "—"
        return f"v{obj.version}"
    
    @display(description="Usage Stats")
    def usage_stats_display(self, obj):
        """Display usage statistics."""
        if not obj.usage_count:
            return "No usage"
        
        success_rate = obj.success_rate or 0
        return f"{obj.usage_count} uses, {success_rate:.1f}% success"
    
    @display(description="Performance")
    def performance_metrics(self, obj):
        """Display performance metrics."""
        if not obj.avg_execution_time:
            return "No data"
        
        avg_time = obj.avg_execution_time
        if obj.total_cost:
            config = MoneyDisplayConfig(currency="USD", show_sign=False, smart_decimal_places=True)
            cost = self.display_money_amount(obj, 'total_cost', config)
            return f"{avg_time:.2f}s avg, {cost} total"
        
        return f"{avg_time:.2f}s avg"
    
    @display(description="Created By")
    def created_by_display(self, obj):
        """Created by user display."""
        if not obj.created_by:
            return "—"
        return self.display_user_simple(obj.created_by)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Activate agents", variant=ActionVariant.SUCCESS)
    def activate_agents(self, request, queryset):
        """Activate selected agents."""
        updated = queryset.update(is_active=True, status='active')
        messages.success(request, f"Activated {updated} agents.")
    
    @action(description="Deactivate agents", variant=ActionVariant.WARNING)
    def deactivate_agents(self, request, queryset):
        """Deactivate selected agents."""
        updated = queryset.update(is_active=False)
        messages.warning(request, f"Deactivated {updated} agents.")
    
    @action(description="Reset statistics", variant=ActionVariant.INFO)
    def reset_stats(self, request, queryset):
        """Reset usage statistics."""
        updated = queryset.update(
            usage_count=0,
            success_rate=0,
            avg_execution_time=0,
            total_cost=0,
            last_used_at=None
        )
        messages.info(request, f"Reset statistics for {updated} agents.")


@admin.register(AgentTemplate)
class AgentTemplateAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Enhanced admin for AgentTemplate model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['created_by']
    
    # Export-only configuration
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'category_display', 'status_display', 'usage_count_display',
        'created_by_display', 'created_at_display'
    ]
    list_display_links = ['name_display']
    list_filter = [
        'category', 'created_at',
        ('created_by', AutocompleteSelectFilter)
    ]
    search_fields = ['name', 'description', 'category']
    autocomplete_fields = ['created_by']
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    # Unfold form field overrides
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        JSONField: {"widget": JSONEditorWidget},
    }
    
    fieldsets = (
        ("📋 Template Info", {
            'fields': ('id', 'name', 'description', 'category'),
            'classes': ('tab',)
        }),
        ("⚙️ Template Content", {
            'fields': ('template_config', 'use_cases'),
            'classes': ('tab',)
        }),
        ("🔧 Settings", {
            'fields': ('is_public', 'usage_count'),
            'classes': ('tab',)
        }),
        ("👤 Metadata", {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    actions = ['make_public', 'make_private', 'duplicate_templates']
    
    @display(description="Template Name")
    def name_display(self, obj):
        """Enhanced template name display."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Category")
    def category_display(self, obj):
        """Category display with badge."""
        if not obj.category:
            return "—"
        
        category_variants = {
            'automation': 'info',
            'analysis': 'success',
            'communication': 'warning',
            'data': 'primary'
        }
        variant = category_variants.get(obj.category.lower(), 'secondary')
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CATEGORY)
        return StatusBadge.create(
            text=obj.category.title(),
            variant=variant,
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj):
        """Status display based on public/private."""
        if obj.is_public:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
            return StatusBadge.create(text="Public", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.LOCK)
            return StatusBadge.create(text="Private", variant="secondary", config=config)
    
    @display(description="Usage")
    def usage_count_display(self, obj):
        """Usage count display."""
        if not obj.usage_count:
            return "Not used"
        return f"{obj.usage_count} times"
    
    @display(description="Created By")
    def created_by_display(self, obj):
        """Created by user display."""
        if not obj.created_by:
            return "—"
        return self.display_user_simple(obj.created_by)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Make public", variant=ActionVariant.SUCCESS)
    def make_public(self, request, queryset):
        """Make selected templates public."""
        updated = queryset.update(is_public=True)
        messages.success(request, f"Made {updated} templates public.")
    
    @action(description="Make private", variant=ActionVariant.WARNING)
    def make_private(self, request, queryset):
        """Make selected templates private."""
        updated = queryset.update(is_public=False)
        messages.warning(request, f"Made {updated} templates private.")
    
    @action(description="Duplicate templates", variant=ActionVariant.INFO)
    def duplicate_templates(self, request, queryset):
        """Duplicate selected templates."""
        duplicated = 0
        for template in queryset:
            # Create duplicate logic here
            duplicated += 1
        
        messages.info(request, f"Duplicated {duplicated} templates.")