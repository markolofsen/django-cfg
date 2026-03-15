"""
Django settings generation module.

Provides settings generation from DjangoConfig instances.

Main Components:
- SettingsGenerator: Main facade for settings generation
- SettingsOrchestrator: Coordinates specialized generators
- Specialized generators: Core, Data, Integration, Utility

Architecture:
    DjangoConfig
        |
        v
    SettingsGenerator (facade)
        |
        v
    SettingsOrchestrator
        |
        +-> CoreSettingsGenerator
        +-> TemplateSettingsGenerator
        +-> StaticFilesGenerator
        +-> DatabaseSettingsGenerator
        +-> CacheSettingsGenerator
        +-> SecuritySettingsGenerator
        +-> EmailSettingsGenerator
        +-> LoggingSettingsGenerator
        +-> I18nSettingsGenerator
        +-> LimitsSettingsGenerator
        +-> SessionSettingsGenerator
        +-> ThirdPartyIntegrationsGenerator
        +-> APIFrameworksGenerator
        +-> TasksSettingsGenerator

Example:
    ```python
    from django_cfg import DjangoConfig
    from django_cfg.core.generation import SettingsGenerator

    config = DjangoConfig(project_name="MyProject", secret_key="x"*50)
    settings = SettingsGenerator.generate(config)
    ```
"""

from .generation import SettingsGenerator
from .orchestrator import SettingsOrchestrator

__all__ = [
    "SettingsGenerator",
    "SettingsOrchestrator",
]
