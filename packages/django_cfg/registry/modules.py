"""
Django-CFG modules and utilities registry.
"""

MODULES_REGISTRY = {
    # URL integration
    "add_django_cfg_urls": ("django_cfg.core.integration", "add_django_cfg_urls"),
    "get_django_cfg_urls_info": ("django_cfg.core.integration", "get_django_cfg_urls_info"),

    # Configuration utilities
    "set_current_config": ("django_cfg.core.config", "set_current_config"),

    # IPC/RPC module
    "DjangoCfgRPCConfig": ("django_cfg.apps.ipc", "DjangoCfgRPCConfig"),

    # Import/Export integration (simple re-exports)
    "ImportForm": ("django_cfg.modules.django_import_export", "ImportForm"),
    "ExportForm": ("django_cfg.modules.django_import_export", "ExportForm"),
    "SelectableFieldsExportForm": ("django_cfg.modules.django_import_export", "SelectableFieldsExportForm"),
    "ImportExportMixin": ("django_cfg.modules.django_import_export", "ImportExportMixin"),
    "ImportExportModelAdmin": ("django_cfg.modules.django_import_export", "ImportExportModelAdmin"),
    "ExportMixin": ("django_cfg.modules.django_import_export", "ExportMixin"),
    "ImportMixin": ("django_cfg.modules.django_import_export", "ImportMixin"),
    "BaseResource": ("django_cfg.modules.django_import_export", "BaseResource"),

    # Django Admin - Declarative Pydantic2 Configuration
    # Note: PydanticAdmin is not in registry - import directly from .base to avoid AppRegistryNotReady
    "AdminConfig": ("django_cfg.modules.django_admin", "AdminConfig"),
    "FieldConfig": ("django_cfg.modules.django_admin", "FieldConfig"),
    "FieldsetConfig": ("django_cfg.modules.django_admin", "FieldsetConfig"),
    "ActionConfig": ("django_cfg.modules.django_admin", "ActionConfig"),
    "WidgetRegistry": ("django_cfg.modules.django_admin", "WidgetRegistry"),
}
