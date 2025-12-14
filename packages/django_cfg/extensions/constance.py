"""
Extension Constance Fields Discovery

Auto-discovers and collects constance fields from all enabled extensions.
"""

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, List

from django_cfg.utils import get_logger

if TYPE_CHECKING:
    from django_cfg.models.django.constance import ConstanceField

logger = get_logger(__name__)


def get_extension_constance_fields() -> List["ConstanceField"]:
    """
    Collect constance fields from all discovered extensions.

    Reads constance_fields from each extension's __cfg__.py settings.

    Returns:
        List of ConstanceField from all extensions

    Example:
        In extension's __cfg__.py:
        ```python
        from django_cfg.models.django.constance import ConstanceField

        class KnowbaseSettings(BaseKnowbaseSettings):
            constance_fields = [
                ConstanceField(
                    name="KNOWBASE_DEFAULT_MODEL",
                    default="gpt-4o-mini",
                    field_type="str",
                    group="Knowledge Base",
                ),
            ]
        ```
    """
    fields: List["ConstanceField"] = []

    try:
        from django_cfg.extensions import get_extension_loader
        from django_cfg.core.state import get_current_config

        config = get_current_config()
        if not config:
            return fields

        loader = get_extension_loader(base_path=Path(config.base_dir))
        extensions = loader.scanner.discover_all()

        for ext in extensions:
            if ext.type != "app" or not ext.is_valid:
                continue

            # Try to load __cfg__.py and get constance_fields
            try:
                config_module = importlib.import_module(f"extensions.apps.{ext.name}.__cfg__")
                settings = getattr(config_module, "settings", None)

                if settings and hasattr(settings, "constance_fields"):
                    ext_fields = settings.constance_fields
                    if ext_fields:
                        fields.extend(ext_fields)
                        logger.debug(f"Loaded {len(ext_fields)} constance fields from {ext.name}")

            except ImportError as e:
                logger.debug(f"No __cfg__.py for extension {ext.name}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load constance fields from {ext.name}: {e}")

    except Exception as e:
        logger.error(f"Failed to collect extension constance fields: {e}")

    return fields
