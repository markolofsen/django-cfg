"""
Leads admin interfaces using Django Admin Utilities.

Enhanced lead management with Material Icons and optimized queries.
"""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.db import models
from django.db.models import Count, Q
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from django_cfg import ImportExportModelAdmin, ImportForm, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import Lead
from .resources import LeadResource


@admin.register(Lead)
class LeadAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for Lead model using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user']
    
    # Import/Export configuration
    resource_class = LeadResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'name_display', 'email_display', 'company_display', 'contact_type_display', 
        'contact_value_display', 'subject_display', 'status_display', 'user_display', 'created_at_display'
    ]
    list_display_links = ['name_display', 'email_display']
    ordering = ['-created_at']
    list_filter = [
        'status', 'contact_type', 'company', 'created_at',
        ('user', AutocompleteSelectFilter)
    ]
    search_fields = [
        'name', 'email', 'company', 'company_site', 
        'message', 'subject', 'admin_notes'
    ]
    autocomplete_fields = ['user']
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent'
    ]
    
    fieldsets = (
        ('👤 Basic Information', {
            'fields': ('name', 'email', 'company', 'company_site'),
            'classes': ('tab',)
        }),
        ('📞 Contact Information', {
            'fields': ('contact_type', 'contact_value'),
            'classes': ('tab',)
        }),
        ('💬 Message', {
            'fields': ('subject', 'message', 'extra'),
            'classes': ('tab',)
        }),
        ('🔧 Metadata', {
            'fields': ('site_url', 'ip_address', 'user_agent'),
            'classes': ('tab', 'collapse')
        }),
        ('⚙️ Status and Processing', {
            'fields': ('status', 'user', 'admin_notes'),
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab', 'collapse')
        }),
    )
    
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_contacted', 'mark_as_qualified', 'mark_as_converted', 'mark_as_rejected']
    
    @display(description="Name", ordering="name")
    def name_display(self, obj):
        """Display lead name."""
        if not obj.name:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PERSON)
        return StatusBadge.create(
            text=obj.name,
            variant="primary",
            config=config
        )
    
    @display(description="Email", ordering="email")
    def email_display(self, obj):
        """Display lead email."""
        if not obj.email:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
        return StatusBadge.create(
            text=obj.email,
            variant="info",
            config=config
        )
    
    @display(description="Company", ordering="company")
    def company_display(self, obj):
        """Display company name."""
        if not obj.company:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.BUSINESS)
        return StatusBadge.create(
            text=obj.company,
            variant="secondary",
            config=config
        )
    
    @display(description="Contact Type")
    def contact_type_display(self, obj):
        """Display contact type with badge."""
        if not obj.contact_type:
            return "—"
        
        type_variants = {
            'email': 'info',
            'phone': 'success',
            'telegram': 'primary',
            'whatsapp': 'success',
            'other': 'secondary'
        }
        variant = type_variants.get(obj.contact_type, 'secondary')
        
        type_icons = {
            'email': Icons.EMAIL,
            'phone': Icons.PHONE,
            'telegram': Icons.TELEGRAM,
            'whatsapp': Icons.WHATSAPP,
            'other': Icons.CONTACT_PHONE
        }
        icon = type_icons.get(obj.contact_type, Icons.CONTACT_PHONE)
        
        config = StatusBadgeConfig(show_icons=True, icon=icon)
        return StatusBadge.create(
            text=obj.get_contact_type_display(),
            variant=variant,
            config=config
        )
    
    @display(description="Contact Value")
    def contact_value_display(self, obj):
        """Display contact value."""
        if not obj.contact_value:
            return "—"
        return obj.contact_value
    
    @display(description="Subject", ordering="subject")
    def subject_display(self, obj):
        """Display subject with truncation."""
        if not obj.subject:
            return "—"
        
        subject = obj.subject
        if len(subject) > 50:
            subject = subject[:47] + "..."
        
        return subject
    
    @display(description="Status")
    def status_display(self, obj):
        """Display lead status with color coding."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'new': 'info',
                'contacted': 'warning',
                'qualified': 'primary',
                'converted': 'success',
                'rejected': 'danger'
            },
            show_icons=True,
            icon=Icons.FLAG if obj.status == 'new' else Icons.PHONE if obj.status == 'contacted' else Icons.VERIFIED if obj.status == 'qualified' else Icons.CHECK_CIRCLE if obj.status == 'converted' else Icons.CANCEL
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Assigned User")
    def user_display(self, obj):
        """Display assigned user."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Created")
    def created_at_display(self, obj):
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Mark as contacted", variant=ActionVariant.WARNING)
    def mark_as_contacted(self, request, queryset):
        """Mark selected leads as contacted."""
        updated = queryset.update(status='contacted')
        messages.warning(request, f"Marked {updated} leads as contacted.")
    
    @action(description="Mark as qualified", variant=ActionVariant.PRIMARY)
    def mark_as_qualified(self, request, queryset):
        """Mark selected leads as qualified."""
        updated = queryset.update(status='qualified')
        messages.info(request, f"Marked {updated} leads as qualified.")
    
    @action(description="Mark as converted", variant=ActionVariant.SUCCESS)
    def mark_as_converted(self, request, queryset):
        """Mark selected leads as converted."""
        updated = queryset.update(status='converted')
        messages.success(request, f"Marked {updated} leads as converted.")
    
    @action(description="Mark as rejected", variant=ActionVariant.DANGER)
    def mark_as_rejected(self, request, queryset):
        """Mark selected leads as rejected."""
        updated = queryset.update(status='rejected')
        messages.error(request, f"Marked {updated} leads as rejected.")
    
    def changelist_view(self, request, extra_context=None):
        """Add lead statistics to changelist."""
        extra_context = extra_context or {}
        
        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_leads=Count('id'),
            new_leads=Count('id', filter=Q(status='new')),
            contacted_leads=Count('id', filter=Q(status='contacted')),
            qualified_leads=Count('id', filter=Q(status='qualified')),
            converted_leads=Count('id', filter=Q(status='converted')),
            rejected_leads=Count('id', filter=Q(status='rejected'))
        )
        
        # Contact type breakdown
        contact_type_counts = dict(
            queryset.values_list('contact_type').annotate(
                count=Count('id')
            )
        )
        
        # Company breakdown (top 10)
        company_counts = dict(
            queryset.exclude(company__isnull=True).exclude(company='')
            .values_list('company').annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        extra_context['lead_stats'] = {
            'total_leads': stats['total_leads'] or 0,
            'new_leads': stats['new_leads'] or 0,
            'contacted_leads': stats['contacted_leads'] or 0,
            'qualified_leads': stats['qualified_leads'] or 0,
            'converted_leads': stats['converted_leads'] or 0,
            'rejected_leads': stats['rejected_leads'] or 0,
            'contact_type_counts': contact_type_counts,
            'company_counts': company_counts
        }
        
        return super().changelist_view(request, extra_context)
