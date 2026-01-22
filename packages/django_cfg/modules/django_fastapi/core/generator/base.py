"""
Base generator interface and shared utilities.

All code generators inherit from BaseGenerator and use GeneratorContext
for shared state and template rendering.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from ..ir.models import GeneratedFile, ParsedModel
from ...config import FastAPIConfig


@dataclass
class GeneratorContext:
    """
    Shared context for code generators.

    Holds configuration, template environment, and collected imports.
    """

    config: FastAPIConfig
    models: list[ParsedModel]

    # Jinja2 environment
    _env: Optional[Environment] = field(default=None, init=False)

    # Collected data across generators
    imports: set[tuple[str, str]] = field(default_factory=set)

    @property
    def env(self) -> Environment:
        """Get or create Jinja2 environment."""
        if self._env is None:
            self._env = Environment(
                loader=PackageLoader(
                    "django_cfg.modules.django_fastapi.core.generator",
                    "sqlmodel/templates"
                ),
                autoescape=select_autoescape(["html", "xml"]),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )
            # Add custom filters
            self._env.filters["snake_case"] = self._to_snake_case
            self._env.filters["camel_case"] = self._to_camel_case

        return self._env

    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a Jinja2 template with context."""
        template = self.env.get_template(template_name)
        return template.render(config=self.config, **kwargs)

    def group_models_by_app(self) -> dict[str, list[ParsedModel]]:
        """Group models by app label."""
        result: dict[str, list[ParsedModel]] = {}
        for model in self.models:
            if model.app_label not in result:
                result[model.app_label] = []
            result[model.app_label].append(model)
        return result

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def _to_camel_case(name: str) -> str:
        """Convert snake_case to CamelCase."""
        components = name.split('_')
        return ''.join(x.title() for x in components)


class BaseGenerator(ABC):
    """
    Abstract base class for code generators.

    Subclasses must implement the generate() method.
    """

    def __init__(self, context: GeneratorContext):
        self.context = context
        self.config = context.config

    @abstractmethod
    def generate(self) -> list[GeneratedFile]:
        """
        Generate code files.

        Returns:
            List of generated files
        """
        pass

    def render(self, template_name: str, **kwargs) -> str:
        """Render a template."""
        return self.context.render_template(template_name, **kwargs)

    def create_file(self, path: str, content: str) -> GeneratedFile:
        """Create a GeneratedFile instance."""
        return GeneratedFile(
            path=Path(self.config.output_dir) / path,
            content=content,
        )
