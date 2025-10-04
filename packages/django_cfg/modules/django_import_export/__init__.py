"""
Django Import/Export Integration for Django CFG

Simple re-export of django-import-export components through django-cfg registry.
Provides seamless integration without unnecessary wrappers.
"""

# Re-export original classes through django-cfg registry
from import_export.admin import ImportExportMixin as BaseImportExportMixin, ImportExportModelAdmin as BaseImportExportModelAdmin, ExportMixin as BaseExportMixin, ImportMixin as BaseImportMixin
from import_export.resources import ModelResource as BaseResource
# Use Unfold styled forms instead of default ones
from unfold.contrib.import_export.forms import ImportForm, ExportForm, SelectableFieldsExportForm


class ImportExportMixin(BaseImportExportMixin):
    """Django-CFG enhanced ImportExportMixin with custom templates and Unfold forms."""
    change_list_template = 'admin/import_export/change_list_import_export.html'
    import_form_class = ImportForm
    export_form_class = ExportForm


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