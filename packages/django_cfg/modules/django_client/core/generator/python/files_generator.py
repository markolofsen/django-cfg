"""
Files Generator - Generates auxiliary files (__init__.py, logger.py, schema.py).

Handles:
- Package __init__.py files
- Logger configuration
- OpenAPI schema embedding
- API wrapper classes
"""

from __future__ import annotations

import json
import re

from jinja2 import Environment

from ...ir import IROperationObject
from ..base import GeneratedFile


class FilesGenerator:
    """Generates auxiliary Python files."""

    def __init__(self, jinja_env: Environment, context, base_generator):
        """
        Initialize files generator.

        Args:
            jinja_env: Jinja2 environment for templates
            context: Generation context
            base_generator: Reference to base generator
        """
        self.jinja_env = jinja_env
        self.context = context
        self.base = base_generator

    def generate_init_file(self) -> GeneratedFile:
        """Generate __init__.py with exports (flat structure)."""
        template = self.jinja_env.get_template('__init__.py.jinja')
        content = template.render(
            has_enums=bool(self.base.get_enum_schemas())
        )

        return GeneratedFile(
            path="__init__.py",
            content=content,
            description="Package exports",
        )

    def generate_app_init_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate __init__.py for a specific app."""
        class_name = self.base.tag_to_class_name(tag)

        # Collect model names used in operations
        model_names = self.base.get_model_names_for_operations(operations)

        template = self.jinja_env.get_template('app_init.py.jinja')
        content = template.render(
            class_name=class_name,
            model_names=sorted(model_names),
        )

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/__init__.py",
            content=content,
            description=f"Package exports for {tag}",
        )

    def generate_main_init_file(self) -> GeneratedFile:
        """Generate main __init__.py with API class and JWT management."""
        ops_by_tag = self.base.group_operations_by_tag()
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.base.tag_to_class_name(tag),
                "slug": self.base.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Check if we have enums
        all_schemas = self.context.schemas
        all_enums = self.base._collect_enums_from_schemas(all_schemas)

        # Sanitize enum names (convert dotted names to PascalCase)
        sanitized_enum_names = [
            self.base.sanitize_enum_name(name) for name in all_enums.keys()
        ] if all_enums else []

        # API class
        api_class = self.generate_api_wrapper_class_python(tags)

        template = self.jinja_env.get_template('main_init.py.jinja')
        content = template.render(
            api_title=self.context.openapi_info.title,
            tags=tags_data,
            has_enums=bool(all_enums),
            enum_names=sorted(sanitized_enum_names),
            api_class=api_class
        )

        return GeneratedFile(
            path="__init__.py",
            content=content,
            description="Package exports with API class and JWT management",
        )

    def generate_api_wrapper_class_python(self, tags: list[str]) -> str:
        """Generate API wrapper class with JWT management for Python."""
        # Prepare property data
        properties_data = []
        for tag in tags:
            properties_data.append({
                "tag": tag,
                "class_name": self.base.tag_to_class_name(tag),
                "property": self.base.tag_to_property_name(tag),
            })

        template = self.jinja_env.get_template('api_wrapper.py.jinja')
        return template.render(properties=properties_data)

    def generate_helpers_init_file(self) -> GeneratedFile:
        """Generate helpers/__init__.py with exports."""
        template = self.jinja_env.get_template('helpers/__init__.py.jinja')
        content = template.render()

        return GeneratedFile(
            path="helpers/__init__.py",
            content=content,
            description="Helpers package exports",
        )

    def generate_logger_file(self) -> GeneratedFile:
        """Generate helpers/logger.py with Rich integration."""
        template = self.jinja_env.get_template('helpers/logger.py.jinja')
        content = template.render()

        return GeneratedFile(
            path="helpers/logger.py",
            content=content,
            description="API Logger with Rich",
        )

    def generate_retry_file(self) -> GeneratedFile:
        """Generate helpers/retry.py with tenacity integration."""
        template = self.jinja_env.get_template('helpers/retry.py.jinja')
        content = template.render()

        return GeneratedFile(
            path="helpers/retry.py",
            content=content,
            description="Retry utilities with tenacity",
        )

    def generate_pyproject_toml_file(self, package_config: dict = None) -> GeneratedFile:
        """Generate pyproject.toml for Poetry/PyPI publishing."""
        if package_config is None:
            package_config = {}

        # Default configuration
        defaults = {
            "package_name": package_config.get("name", "api-client"),
            "version": package_config.get("version", "1.0.0"),
            "description": package_config.get("description") or f"Auto-generated Python client for {self.context.openapi_info.title}",
            "authors": package_config.get("authors", ["Author <author@example.com>"]),
            "license": package_config.get("license", "MIT"),
            "repository_url": package_config.get("repository_url"),
            "keywords": package_config.get("keywords", ["api", "client", "python", "openapi"]),
            "python_version": package_config.get("python_version", "^3.12"),
        }

        template = self.jinja_env.get_template('pyproject.toml.jinja')
        content = template.render(**defaults)

        return GeneratedFile(
            path="pyproject.toml",
            content=content,
            description="Poetry package configuration",
        )

    def generate_schema_file(self, openapi_schema: dict) -> GeneratedFile:
        """Generate schema.json with OpenAPI schema."""
        # Generate JSON file with proper formatting
        content = json.dumps(openapi_schema, indent=4, ensure_ascii=False)

        return GeneratedFile(
            path="schema.json",
            content=content,
            description="OpenAPI Schema (JSON format)",
        )
