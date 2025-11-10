"""
TypeScript Files Generator - Generates utility files (index, http, errors, logger, etc.).
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject
from ..base import GeneratedFile


class FilesGenerator:
    """Generates TypeScript utility files."""

    def __init__(self, jinja_env: Environment, context, base):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base
        self.openapi_schema = getattr(base, 'openapi_schema', None)

    def generate_index_file(self):
        """Generate index.ts with exports."""

        template = self.jinja_env.get_template('index.ts.jinja')
        content = template.render(
            has_enums=bool(self.base.get_enum_schemas())
        )

        return GeneratedFile(
            path="index.ts",
            content=content,
            description="Module exports",
        )

    def generate_app_index_file(self, tag: str, operations: list[IROperationObject]):
        """Generate index.ts for a specific app."""
        from ..base import GeneratedFile

        template = self.jinja_env.get_template('app_index.ts.jinja')
        content = template.render()

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/index.ts",
            content=content,
            description=f"Module exports for {tag}",
        )

    def generate_main_index_file(self):
        """Generate main index.ts with API class and JWT management."""

        ops_by_tag = self.base.group_operations_by_tag()
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.base.tag_to_class_name(tag, suffix=""),
                "property": self.base.tag_to_property_name(tag),
                "slug": self.base.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Check if we have enums
        all_schemas = self.context.schemas
        all_enums = self.base._collect_enums_from_schemas(all_schemas)

        template = self.jinja_env.get_template('main_index.ts.jinja')
        content = template.render(
            api_title=self.context.openapi_info.title,
            tags=tags_data,
            has_enums=bool(all_enums),
            generate_zod_schemas=getattr(self.base, 'generate_zod_schemas', False),
            generate_fetchers=getattr(self.base, 'generate_fetchers', False),
            generate_swr_hooks=getattr(self.base, 'generate_swr_hooks', False),
        )

        return GeneratedFile(
            path="index.ts",
            content=content,
            description="Main index with API class and JWT management",
        )

    def generate_http_adapter_file(self):
        """Generate http.ts with HttpClient adapter interface."""

        template = self.jinja_env.get_template('utils/http.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="http.ts",
            content=content,
            description="HTTP client adapter interface and implementations",
        )

    def generate_errors_file(self):
        """Generate errors.ts with APIError class."""

        template = self.jinja_env.get_template('utils/errors.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="errors.ts",
            content=content,
            description="API error classes",
        )

    def generate_storage_file(self):
        """Generate storage.ts with StorageAdapter implementations."""

        template = self.jinja_env.get_template('utils/storage.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="storage.ts",
            content=content,
            description="Storage adapters for cross-platform support",
        )

    def generate_logger_file(self):
        """Generate logger.ts with Consola integration."""

        template = self.jinja_env.get_template('utils/logger.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="logger.ts",
            content=content,
            description="API Logger with Consola",
        )

    def generate_retry_file(self):
        """Generate retry.ts with p-retry integration."""

        template = self.jinja_env.get_template('utils/retry.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="retry.ts",
            content=content,
            description="Retry utilities with p-retry",
        )

    def generate_validation_events_file(self):
        """Generate validation-events.ts with browser CustomEvent integration."""

        template = self.jinja_env.get_template('utils/validation-events.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="validation-events.ts",
            content=content,
            description="Zod validation error events for browser integration",
        )

    def generate_api_instance_file(self):
        """Generate api-instance.ts with global singleton."""

        template = self.jinja_env.get_template('api_instance.ts.jinja')
        content = template.render()

        return GeneratedFile(
            path="api-instance.ts",
            content=content,
            description="Global API singleton for universal configuration",
        )

    def generate_package_json_file(self, package_config: dict = None):
        """Generate package.json for npm publishing."""
        if package_config is None:
            package_config = {}

        # Default configuration
        defaults = {
            "package_name": package_config.get("name", "api-client"),
            "version": package_config.get("version", "1.0.0"),
            "description": package_config.get("description") or f"Auto-generated TypeScript client for {self.context.openapi_info.title}",
            "author": package_config.get("author"),
            "license": package_config.get("license", "MIT"),
            "repository_url": package_config.get("repository_url"),
            "keywords": package_config.get("keywords", ["api", "client", "typescript", "openapi"]),
            "private": package_config.get("private", False),
        }

        # Add Zod flag
        defaults["generate_zod_schemas"] = self.base.generate_zod_schemas

        template = self.jinja_env.get_template('package.json.jinja')
        content = template.render(**defaults)

        return GeneratedFile(
            path="package.json",
            content=content,
            description="NPM package configuration",
        )

    def generate_tsconfig_file(self):
        """Generate tsconfig.json for TypeScript compilation."""
        template = self.jinja_env.get_template('tsconfig.json.jinja')
        content = template.render()

        return GeneratedFile(
            path="tsconfig.json",
            content=content,
            description="TypeScript compiler configuration",
        )

    def generate_schema_file(self):
        """Generate schema.json with OpenAPI schema."""
        import json

        # Generate JSON file with proper formatting
        content = json.dumps(self.openapi_schema, indent=2, ensure_ascii=False)

        return GeneratedFile(
            path="schema.json",
            content=content,
            description="OpenAPI Schema (JSON format)",
        )
