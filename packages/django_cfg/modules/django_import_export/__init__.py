"""
Django Import/Export Integration for Django CFG

Simple re-export of django-import-export components through django-cfg registry.
Provides seamless integration without unnecessary wrappers.
"""

# Re-export original classes through django-cfg registry
from import_export.admin import ExportMixin as BaseExportMixin
from import_export.admin import ImportExportMixin as BaseImportExportMixin
from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
from import_export.admin import ImportMixin as BaseImportMixin
from import_export.resources import ModelResource as BaseResource

# Use Unfold styled forms instead of default ones
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm


class ImportExportMixin(BaseImportExportMixin):
    """Django-CFG enhanced ImportExportMixin with custom templates and Unfold forms."""
    change_list_template = 'admin/import_export/change_list_import_export.html'
    import_form_class = ImportForm
    export_form_class = ExportForm

    def changelist_view(self, request, extra_context=None):
        """Add import/export permissions to context."""
        if extra_context is None:
            extra_context = {}
        extra_context['has_import_permission'] = self.has_import_permission(request)
        extra_context['has_export_permission'] = self.has_export_permission(request)
        return super().changelist_view(request, extra_context)


class ImportExportModelAdmin(BaseImportExportModelAdmin):
    """Django-CFG enhanced ImportExportModelAdmin with custom templates and Unfold forms."""
    change_list_template = 'admin/import_export/change_list_import_export.html'
    import_form_class = ImportForm
    export_form_class = ExportForm


class ExportMixin(BaseExportMixin):
    """Django-CFG enhanced ExportMixin with custom templates and Unfold forms."""
    change_list_template = 'admin/import_export/change_list_export.html'
    export_form_class = ExportForm


class ImportMixin(BaseImportMixin):
    """Django-CFG enhanced ImportMixin with custom templates and Unfold forms."""
    change_list_template = 'admin/import_export/change_list_import.html'
    import_form_class = ImportForm


__all__ = [
    'ImportExportMixin',
    'ImportExportModelAdmin',
    'ExportMixin',
    'ImportMixin',
    'BaseResource',
    'ImportForm',
    'ExportForm',
    'SelectableFieldsExportForm',
]
