"""
Import/Export resource class generation.

Auto-generates ModelResource classes for import/export functionality.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...config import AdminConfig

logger = logging.getLogger(__name__)


def generate_resource_class(config: 'AdminConfig'):
    """
    Auto-generate a ModelResource class for import/export.

    Includes every concrete, non-M2M model field except password fields.

    Args:
        config: AdminConfig instance

    Returns:
        Generated ModelResource class
    """
    from import_export import resources

    target_model = config.model

    model_fields = [
        field.name
        for field in target_model._meta.get_fields()
        if field.concrete and not field.many_to_many and 'password' not in field.name.lower()
    ]

    meta_attrs = {
        'model': target_model,
        'fields': tuple(model_fields),
        'import_id_fields': ['id'] if 'id' in model_fields else [],
        'skip_unchanged': True,
        'report_skipped': True,
    }

    return type(
        f'{target_model.__name__}Resource',
        (resources.ModelResource,),
        {'Meta': type('Meta', (), meta_attrs)},
    )
