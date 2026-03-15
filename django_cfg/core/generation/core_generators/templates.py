"""
Django TEMPLATES settings generator.

Handles template configuration with auto-discovery of django-cfg app templates.
Size: ~90 lines (focused on template settings)
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig


class TemplateSettingsGenerator:
    """
    Generates Django TEMPLATES setting.

    Responsibilities:
    - Configure Django template backend
    - Set up template directories
    - Auto-discover django-cfg app templates
    - Configure context processors

    Example:
        ```python
        generator = TemplateSettingsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate TEMPLATES setting.

        Returns:
            Dictionary with TEMPLATES configuration

        Example:
            >>> generator = TemplateSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "TEMPLATES" in settings
            True
        """
        template_dirs = self._discover_template_directories()

        return {
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": template_dirs,
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ]
        }

    def _discover_template_directories(self) -> List[Path]:
        """
        Discover template directories from django-cfg and project.

        Returns:
            List of Path objects pointing to template directories
        """
        template_dirs = []

        # Add project templates directory
        project_templates = self.config.base_dir / "templates"
        template_dirs.append(project_templates)

        # Add django-cfg templates directory
        django_cfg_templates = Path(__file__).parent.parent.parent.parent / "templates"
        template_dirs.append(django_cfg_templates)

        # Auto-discover app template directories
        app_templates = self._discover_app_templates()
        template_dirs.extend(app_templates)

        return template_dirs

    def _discover_app_templates(self) -> List[Path]:
        """
        Auto-discover template directories from django-cfg apps and modules.

        Looks for:
        - app/templates/
        - app/admin_interface/templates/
        - app/frontend/templates/
        - modules/*/templates/

        Returns:
            List of discovered template directory paths
        """
        app_templates = []

        # Find django-cfg directory
        django_cfg_dir = Path(__file__).parent.parent.parent.parent

        # Scan apps directory
        apps_dir = django_cfg_dir / 'apps'
        if apps_dir.exists():
            for app_dir in apps_dir.iterdir():
                if not app_dir.is_dir():
                    continue

                # Skip special directories
                if app_dir.name.startswith(('@', '_', '.')):
                    continue

                # Look for common template directory patterns
                possible_template_dirs = [
                    app_dir / 'templates',
                    app_dir / 'admin_interface' / 'templates',
                    app_dir / 'frontend' / 'templates',
                ]

                for template_dir in possible_template_dirs:
                    if template_dir.exists() and template_dir.is_dir():
                        app_templates.append(template_dir)

        # Scan modules directory for templates
        modules_dir = django_cfg_dir / 'modules'
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if not module_dir.is_dir():
                    continue

                # Skip special directories
                if module_dir.name.startswith(('@', '_', '.')):
                    continue

                # Check if module has templates directory
                template_dir = module_dir / 'templates'
                if template_dir.exists() and template_dir.is_dir():
                    app_templates.append(template_dir)

        return app_templates


__all__ = ["TemplateSettingsGenerator"]
