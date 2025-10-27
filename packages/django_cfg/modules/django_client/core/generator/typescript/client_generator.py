"""
TypeScript Client Generator - Generates TypeScript APIClient classes.
"""

from __future__ import annotations

from jinja2 import Environment

from ...ir import IROperationObject
from ..base import GeneratedFile


class ClientGenerator:
    """Generates TypeScript APIClient classes (flat and namespaced)."""

    def __init__(self, jinja_env: Environment, context, base, operations_gen):
        self.jinja_env = jinja_env
        self.context = context
        self.base = base
        self.operations_gen = operations_gen

    def generate_client_file(self):
        """Generate client.ts with APIClient class."""


        # Client class
        client_code = self._generate_client_class()

        template = self.jinja_env.get_template('client_file.ts.jinja')
        content = template.render(
            has_enums=bool(self.base.get_enum_schemas()),
            client_code=client_code
        )

        return GeneratedFile(
            path="client.ts",
            content=content,
            description="APIClient with HTTP adapter and error handling",
        )

    def _generate_client_class(self) -> str:
        """Generate APIClient class."""
        if self.base.client_structure == "namespaced":
            return self._generate_namespaced_client()
        else:
            return self._generate_flat_client()

    def _generate_flat_client(self) -> str:
        """Generate flat APIClient (all methods in one class)."""
        # Generate all operation methods
        method_codes = []
        for op_id, operation in self.context.operations.items():
            method_codes.append(self.operations_gen.generate_operation(operation))

        template = self.jinja_env.get_template('client/flat_client.ts.jinja')
        return template.render(
            api_title=self.context.openapi_info.title,
            operations=method_codes,
            has_session_auth=self.context.django_metadata.has_session_auth
        )

    def _generate_namespaced_client(self) -> str:
        """Generate namespaced APIClient (sub-clients per tag)."""
        # Group operations by tag (using base class method)
        ops_by_tag = self.base.group_operations_by_tag()

        # Generate sub-client classes
        sub_client_classes = []
        for tag, operations in sorted(ops_by_tag.items()):
            sub_client_classes.append(self._generate_sub_client_class(tag, operations))

        sub_clients_code = "\n\n".join(sub_client_classes)

        # Generate main APIClient
        main_client_code = self._generate_main_client_class(list(ops_by_tag.keys()))

        return f"{sub_clients_code}\n\n{main_client_code}"

    def _generate_sub_client_class(self, tag: str, operations: list) -> str:
        """Generate sub-client class for a specific tag."""
        class_name = self.base.tag_to_class_name(tag, suffix="")

        # Generate methods for this tag
        method_codes = []
        for operation in operations:
            method_codes.append(self.operations_gen.generate_operation(operation, remove_tag_prefix=True, in_subclient=True))

        template = self.jinja_env.get_template('client/sub_client.ts.jinja')
        return template.render(
            tag=self.base.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

    def _generate_main_client_class(self, ops_by_tag: dict) -> str:
        """Generate main APIClient with sub-clients."""
        tags = sorted(ops_by_tag.keys())

        # Prepare data for template
        tags_data = [
            {
                "class_name": self.base.tag_to_class_name(tag, suffix=""),
                "property": self.base.tag_to_property_name(tag),
                "slug": self.base.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        template = self.jinja_env.get_template('client/client.ts.jinja')
        return template.render(
            sub_clients=True,
            include_imports=False,  # Imports already in main_client_file.ts.jinja
            tags=tags_data,
            info={"title": self.context.openapi_info.title},
            has_session_auth=self.context.django_metadata.has_session_auth,
        )

    def generate_main_client_file(self, ops_by_tag: dict):
        """Generate main client.ts with APIClient."""

        tags = sorted(ops_by_tag.keys())

        # Prepare tags data for template
        tags_data = [
            {
                "class_name": self.base.tag_to_class_name(tag, suffix=""),
                "slug": self.base.tag_and_app_to_folder_name(tag, ops_by_tag[tag]),
            }
            for tag in tags
        ]

        # Generate main APIClient class
        client_code = self._generate_main_client_class(ops_by_tag)

        template = self.jinja_env.get_template('client/main_client_file.ts.jinja')
        content = template.render(
            tags=tags_data,
            client_code=client_code
        )

        return GeneratedFile(
            path="client.ts",
            content=content,
            description="Main API client with HTTP adapter and error handling",
        )

    def generate_app_client_file(self, tag: str, operations: list[IROperationObject]):
        """Generate client.ts for a specific app."""

        class_name = self.base.tag_to_class_name(tag, suffix="")

        # Generate methods
        method_codes = []
        for operation in operations:
            method_codes.append(self.operations_gen.generate_operation(operation, remove_tag_prefix=True, in_subclient=True))

        template = self.jinja_env.get_template('client/app_client.ts.jinja')
        content = template.render(
            tag=self.base.tag_to_display_name(tag),
            class_name=class_name,
            operations=method_codes
        )

        folder_name = self.base.tag_and_app_to_folder_name(tag, operations)
        return GeneratedFile(
            path=f"{folder_name}/client.ts",
            content=content,
            description=f"API client for {tag}",
        )
