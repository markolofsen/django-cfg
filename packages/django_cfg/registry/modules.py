"""
Django-CFG modules and utilities registry.
"""

MODULES_REGISTRY = {
    # Logging utilities
    "get_logger": ("django_cfg.modules.django_logging", "get_logger"),

    # URL integration
    "add_django_cfg_urls": ("django_cfg.core.integration", "add_django_cfg_urls"),
    "get_django_cfg_urls_info": ("django_cfg.core.integration", "get_django_cfg_urls_info"),

    # Configuration utilities
    "set_current_config": ("django_cfg.core.config", "set_current_config"),

    # Centrifugo module
    "DjangoCfgCentrifugoConfig": ("django_cfg.apps.integrations.centrifugo.services.client.config", "DjangoCfgCentrifugoConfig"),

    # Web Push module
    "send_push": ("django_cfg.apps.integrations.webpush", "send_push"),
    "send_push_to_many": ("django_cfg.apps.integrations.webpush", "send_push_to_many"),
    "WebPushConfig": ("django_cfg.models.api.webpush", "WebPushConfig"),

    # gRPC module (uses flat API - no nested config imports needed)
    "GRPCConfig": ("django_cfg.models.api.grpc", "GRPCConfig"),
    "GRPCServerConfig": ("django_cfg.models.api.grpc", "GRPCServerConfig"),
    "GRPCKeepaliveConfig": ("django_cfg.models.api.grpc", "GRPCKeepaliveConfig"),
    "GRPCConnectionLimitsConfig": ("django_cfg.models.api.grpc", "GRPCConnectionLimitsConfig"),

    # Next.js Admin Integration
    "NextJsAdminConfig": ("django_cfg.modules.nextjs_admin", "NextJsAdminConfig"),

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
