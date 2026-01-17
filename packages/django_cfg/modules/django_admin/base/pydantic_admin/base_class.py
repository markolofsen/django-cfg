"""
Base admin class factory.

Combines Unfold UI with Import/Export functionality.
"""

import logging

logger = logging.getLogger(__name__)


def get_base_admin_class():
    """
    Get the base admin class with Unfold + Import/Export functionality.

    Since unfold and import_export are always available in django-cfg,
    we always return a combined class that inherits from both.

    MRO (Method Resolution Order):
        UnfoldImportExportModelAdmin
          └─ UnfoldModelAdmin        # Unfold UI (first for template priority)
          └─ ImportExportMixin       # Import/Export functionality (django_cfg custom)
               └─ Django ModelAdmin

    This ensures both Unfold UI and Import/Export work together seamlessly.

    Uses django_cfg's custom ImportExportMixin which includes:
    - Custom templates for proper Unfold styling
    - Unfold forms (ImportForm, ExportForm)
    - Properly styled import/export buttons
    """
    # Use original ImportExportModelAdmin with Unfold
    from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
    from unfold.admin import ModelAdmin as UnfoldModelAdmin

    class UnfoldImportExportModelAdmin(BaseImportExportModelAdmin, UnfoldModelAdmin):
        """Combined Import/Export + Unfold admin base class."""
        # Import/Export should come FIRST in MRO to get its get_urls() method
        pass

    return UnfoldImportExportModelAdmin
