"""
Sync Client Generator - Generates sync Python clients.

Handles:
- Main SyncAPIClient class (httpx.Client)
- Sync sub-client classes (per tag/app)
- Mirrors async client structure without async/await
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject
from ..base import GeneratedFile


class SyncClientGenerator:
    """Generates sync Python client files."""

    def __init__(self, jinja_env: Environment, base_generator, operations_gen):
        """
        Initialize sync client generator.

        Args:
            jinja_env: Jinja2 environment for templates
            base_generator: Reference to base generator
            operations_gen: Operations generator instance
        """
        self.jinja_env = jinja_env
        self.base = base_generator
        self.operations_gen = operations_gen

    def generate_app_sync_client_file(self, tag: str, operations: list[IROperationObject]) -> GeneratedFile:
        """Generate sync_client.py for a specific app."""
        class_name = self.base.tag_to_class_name(tag)

        # Collect model names used in operations
        model_names = self.base.get_model_names_for_operations(operations)

        # Generate sync methods
        method_codes = []
        for operation in operations:
            method_codes.append(self.operations_gen.generate_sync_operation(operation, remove_tag_prefix=True))

        template = self.jinja_env.get_template('client/sync_sub_client.py.jinja')
        content = template.render(
            tag=self.base.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes,
            model_names=sorted(model_names),
        )

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/sync_client.py",
            content=content,
            description=f"Sync API client for {tag}",
        )

    def generate_sync_main_client_file(self, ops_by_tag: dict) -> GeneratedFile:
        """Generate sync_client.py with SyncAPIClient."""
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template (with Sync prefix for imports)
        tags_data = [
            {
                "class_name": f"Sync{self.base.tag_to_class_name(tag)}",  # Add Sync prefix
                "slug": f"{self.base.tag_and_app_to_folder_name(tag, ops_by_tag[tag])}.sync_client",  # Import from sync_client module
            }
            for tag in tags
        ]

        # Generate sync APIClient class
        sync_client_code = self._generate_sync_main_client_class(ops_by_tag)

        template = self.jinja_env.get_template('client/sync_main_client_file.py.jinja')
        content = template.render(
            tags=tags_data,
            client_code=sync_client_code
        )

        return GeneratedFile(
            path="sync_client.py",
            content=content,
            description="Main sync API client",
        )

    def _generate_sync_main_client_class(self, ops_by_tag: dict) -> str:
        """Generate main SyncAPIClient with sync sub-clients."""
        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.base.tag_to_class_name(tag),
                "property": self.base.tag_to_property_name(tag),
            }
            for tag in tags
        ]

        template = self.jinja_env.get_template('client/sync_main_client.py.jinja')
        return template.render(
            api_title=self.base.context.openapi_info.title,
            tags=tags_data
        )
