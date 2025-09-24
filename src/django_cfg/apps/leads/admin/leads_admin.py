from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from unfold.admin import ModelAdmin
from unfold.decorators import action
from django_cfg import ImportExportModelAdmin, ImportForm, ExportForm

from ..models import Lead
from .resources import LeadResource


@admin.register(Lead)
class LeadAdmin(ModelAdmin, ImportExportModelAdmin):
    # Import/Export configuration
    resource_class = LeadResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = [
        'name', 'email', 'company', 'contact_type', 'contact_value',
        'subject', 'status_display', 'created_at'
    ]
    list_display_links = ['name', 'email']
    list_filter = [
        'status', 'contact_type', 'company', 'created_at'
    ]
    search_fields = [
        'name', 'email', 'company', 'company_site', 
        'message', 'subject', 'admin_notes'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'company', 'company_site')
        }),
        ('Contact Information', {
            'fields': ('contact_type', 'contact_value')
        }),
        ('Message', {
            'fields': ('subject', 'message', 'extra')
        }),
        ('Metadata', {
            'fields': ('site_url', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Status and Processing', {
            'fields': ('status', 'user', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        status_colors = {
            'new': '#17a2b8',
            'contacted': '#ffc107',
            'qualified': '#28a745',
            'converted': '#007bff',
            'rejected': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
