"""
Client Generator - Generates Go HTTP client with operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .naming import to_pascal_case

if TYPE_CHECKING:
    from jinja2 import Environment

    from ...ir import IRContext
    from ..base import GeneratedFile
    from .generator import GoGenerator
    from .operations_generator import OperationsGenerator


class ClientGenerator:
    """Generates Go HTTP client code."""

    def __init__(
        self,
        jinja_env: Environment,
        context: IRContext,
        generator: GoGenerator,
        operations_gen: OperationsGenerator,
    ):
        """Initialize client generator."""
        self.jinja_env = jinja_env
        self.context = context
        self.generator = generator
        self.operations_gen = operations_gen

    def generate_client_file(self) -> GeneratedFile:
        """Generate client.go with HTTP client and all operations."""
        template = self.jinja_env.get_template("client.go.j2")

        # Generate all operation methods
        operations = []
        for op_id, operation in sorted(self.context.operations.items()):
            op_method = self.operations_gen.generate_operation_method(operation)
            operations.append(op_method)

        content = template.render(
            package_name=self.generator.package_name,
            operations=operations,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="client.go",
            content=content,
            description="HTTP API client"
        )

    def generate_main_client_file(self, ops_by_tag: dict) -> GeneratedFile:
        """Generate main client.go for namespaced structure."""
        template = self.jinja_env.get_template("main_client.go.j2")

        subclients = []
        for tag in sorted(ops_by_tag.keys()):
            folder_name = self.generator.tag_and_app_to_folder_name(tag, ops_by_tag[tag])
            subclients.append({
                "name": to_pascal_case(folder_name),
                "package": folder_name,
            })

        content = template.render(
            package_name=self.generator.package_name,
            module_name=self.generator.package_config.get("module_name", "apiclient"),
            subclients=subclients,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path="client.go",
            content=content,
            description="Main API client"
        )

    def generate_subpackage_client_file(self, tag: str, operations: list) -> GeneratedFile:
        """Generate client.go for a specific subpackage with its operations."""
        template = self.jinja_env.get_template("operations_client.go.j2")

        # Get folder name for this tag
        folder_name = self.generator.tag_and_app_to_folder_name(tag, operations)

        # Generate operation methods for this tag
        operation_methods = []
        has_request_body = False
        has_query_params = False
        has_path_params = False
        has_multipart = False

        for operation in sorted(operations, key=lambda op: op.operation_id):
            op_method = self.operations_gen.generate_operation_method(operation, remove_tag_prefix=True)
            operation_methods.append(op_method)

            # Check what imports we need
            if op_method.get("request_type"):
                has_request_body = True
            if op_method.get("is_multipart"):
                has_multipart = True
            if any(p.get("location") == "query" for p in op_method.get("parameters", [])):
                has_query_params = True
            if any(p.get("location") == "path" for p in op_method.get("parameters", [])):
                has_path_params = True

        content = template.render(
            package_name=folder_name,
            module_name=self.generator.package_config.get("module_name", "apiclient"),
            parent_package=self.generator.package_name,
            operations=operation_methods,
            has_request_body=has_request_body,
            has_query_params=has_query_params,
            has_path_params=has_path_params,
            has_multipart=has_multipart,
            generated_at=datetime.now().isoformat(),
        )

        return self.generator._create_generated_file(
            path=f"{folder_name}/client.go",
            content=content,
            description=f"HTTP client for {tag}"
        )
