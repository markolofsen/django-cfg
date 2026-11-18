"""
Base admin class factory.

Stock Django admin plus django-import-export.
"""

import logging

logger = logging.getLogger(__name__)


def get_base_admin_class():
    """
    Get the base admin class: ``import_export.admin.ImportExportModelAdmin``.

    MRO (Method Resolution Order):
        ImportExportModelAdmin
          └─ ImportExportMixin      # import/export views and buttons
               └─ django.contrib.admin.ModelAdmin

    ``ModelAdmin`` is already in the MRO of ``ImportExportModelAdmin``; listing it
    again as a separate base gives an MRO error.
    """
    from import_export.admin import ImportExportModelAdmin

    return ImportExportModelAdmin
