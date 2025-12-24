"""
Proto Generator - Main Protocol Buffer code generator.

Generates .proto files from IR (Intermediate Representation) for gRPC client generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import BaseGenerator, GeneratedFile
from ..claude_generator import ClaudeGenerator
from .messages_generator import ProtoMessagesGenerator
from .services_generator import ProtoServicesGenerator
from .type_mapper import ProtoTypeMapper

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRContext, IROperationObject, IRSchemaObject


class ProtoGenerator(BaseGenerator):
    """
    Protocol Buffer generator for gRPC clients.

    Generates:
    - messages.proto: Message definitions (models)
    - services.proto: Service and RPC definitions (API endpoints)
    - Or combined api.proto with both messages and services

    The generated .proto files can be used with protoc to generate:
    - Python gRPC client (via grpc_tools.protoc)
    - Go gRPC client (via protoc-gen-go and protoc-gen-go-grpc)
    - TypeScript gRPC client (via protoc-gen-ts)
    - Any other language with protoc support
    """

    def __init__(
        self,
        context: IRContext,
        split_files: bool = True,
        package_name: str | None = None,
        **kwargs,
    ):
        """
        Initialize Proto generator.

        Args:
            context: IRContext from parser
            split_files: If True, generate separate messages.proto and services.proto
                        If False, generate single api.proto
            package_name: Proto package name (e.g., "myapi.v1")
                         Defaults to "api.v1"
            **kwargs: Additional arguments passed to BaseGenerator
        """
        super().__init__(context, **kwargs)

        self.split_files = split_files
        self.package_name = package_name or "api.v1"

        # Initialize sub-generators
        self.type_mapper = ProtoTypeMapper()
        self.messages_generator = ProtoMessagesGenerator(self.type_mapper)
        self.services_generator = ProtoServicesGenerator(self.type_mapper, context)

    def generate(self) -> list[GeneratedFile]:
        """
        Generate all proto files.

        Returns:
            List of GeneratedFile objects organized by service/tag
        """
        files = []

        # Group operations by tag (similar to other generators)
        ops_by_tag = self.group_operations_by_tag()

        # Generate proto files for each tag/service
        for tag, operations in sorted(ops_by_tag.items()):
            folder_name = self.tag_and_app_to_folder_name(tag, operations)

            # Get schemas used by this service
            service_schemas = self._get_schemas_for_operations(operations)

            # Generate messages.proto for this service
            messages_file = self._generate_service_messages_file(
                folder_name, tag, service_schemas
            )
            files.append(messages_file)

            # Generate service.proto for this service
            service_file = self._generate_service_file(
                folder_name, tag, operations
            )
            files.append(service_file)

        # Generate root README.md with protoc compilation instructions
        readme_file = self._generate_readme_file(ops_by_tag)
        files.append(readme_file)

        # Generate CLAUDE.md
        files.append(ClaudeGenerator(self.context, "proto", group_name=self.group_name).generate())

        return files

    def _get_schemas_for_operations(self, operations: list[IROperationObject]) -> dict[str, IRSchemaObject]:
        """
        Get all schemas used by given operations.

        This resolves all schema dependencies to ensure nested schemas are included.
        """
        schemas = {}

        def add_schema(schema_name: str):
            """Recursively add schema and its dependencies."""
            if schema_name in schemas or schema_name not in self.context.schemas:
                return

            schema = self.context.schemas[schema_name]
            schemas[schema_name] = schema

            # Recursively add referenced schemas
            if schema.properties:
                for prop_schema in schema.properties.values():
                    if prop_schema.ref and prop_schema.ref in self.context.schemas:
                        add_schema(prop_schema.ref)
                    elif prop_schema.type == "array" and prop_schema.items:
                        if prop_schema.items.ref:
                            add_schema(prop_schema.items.ref)

        for operation in operations:
            # Request body schemas
            if operation.request_body and operation.request_body.schema_name:
                schema_name = operation.request_body.schema_name
                # Check in schemas, request_models, and response_models
                if schema_name in self.context.schemas:
                    add_schema(schema_name)
                elif schema_name in self.context.request_models:
                    schemas[schema_name] = self.context.request_models[schema_name]

            # Patch request body schemas (important for PATCH operations!)
            if hasattr(operation, 'patch_request_body') and operation.patch_request_body and operation.patch_request_body.schema_name:
                schema_name = operation.patch_request_body.schema_name
                # Check in schemas, request_models, patch_models
                if schema_name in self.context.schemas:
                    add_schema(schema_name)
                elif schema_name in self.context.patch_models:
                    schemas[schema_name] = self.context.patch_models[schema_name]
                elif schema_name in self.context.request_models:
                    schemas[schema_name] = self.context.request_models[schema_name]

            # Response schemas
            for response in operation.responses.values():
                if response.schema_name:
                    schema_name = response.schema_name
                    if schema_name in self.context.schemas:
                        add_schema(schema_name)
                    elif schema_name in self.context.response_models:
                        schemas[schema_name] = self.context.response_models[schema_name]

            # Parameter schemas (if they reference components)
            for param in operation.parameters:
                if hasattr(param, 'schema_name') and param.schema_name:
                    if param.schema_name in self.context.schemas:
                        add_schema(param.schema_name)

        return schemas

    def _generate_service_messages_file(
        self, folder_name: str, tag: str, schemas: dict[str, IRSchemaObject]
    ) -> GeneratedFile:
        """Generate messages.proto file for a specific service.

        File naming uses folder_name prefix to ensure unique Swift output files.
        Example: activity/activity_messages.proto -> activity_messages.pb.swift
        """
        # Generate message definitions for these schemas
        self.messages_generator.generate_all_messages(schemas)
        messages_content = self.messages_generator.get_all_definitions()

        # Use folder_name as prefix for unique Swift file names
        file_prefix = folder_name.replace("/", "_")
        proto_filename = f"{file_prefix}_messages.proto"

        # Build proto file content
        content = self._build_proto_header(f"{folder_name}/{proto_filename}", tag)

        if messages_content:
            content += "\n\n" + messages_content

        return GeneratedFile(
            path=f"{folder_name}/{proto_filename}",
            content=content,
            description=f"Protocol Buffer message definitions for {tag}",
        )

    def _generate_service_file(
        self, folder_name: str, tag: str, operations: list[IROperationObject]
    ) -> GeneratedFile:
        """Generate service.proto file for a specific service.

        File naming uses folder_name prefix to ensure unique Swift output files.
        Example: activity/activity_service.proto -> activity_service.pb.swift
        """
        # Generate service definitions from operations
        service_definitions = self.services_generator.generate_all_services(operations)

        # Use folder_name as prefix for unique Swift file names
        file_prefix = folder_name.replace("/", "_")
        messages_filename = f"{file_prefix}_messages.proto"
        service_filename = f"{file_prefix}_service.proto"

        # Build proto file content
        content = self._build_proto_header(f"{folder_name}/{service_filename}", tag)
        # Import messages.proto with prefixed name
        content += f'\nimport "{messages_filename}";\n'

        # Add all service definitions
        for service_name, service_def in service_definitions.items():
            content += "\n\n" + service_def

        return GeneratedFile(
            path=f"{folder_name}/{service_filename}",
            content=content,
            description=f"gRPC service definitions for {tag}",
        )

    def _generate_readme_file(self, ops_by_tag: dict[str, list[IROperationObject]]) -> GeneratedFile:
        """Generate README.md with protoc compilation instructions."""
        lines = [
            "# Protocol Buffer Definitions",
            "",
            f"Generated from OpenAPI specification for package `{self.package_name}`",
            "",
            "## Structure",
            "",
            "Each service has its own folder containing prefixed proto files:",
            "- `{prefix}_messages.proto` - Message definitions (models)",
            "- `{prefix}_service.proto` - Service and RPC definitions",
            "",
            "File names are prefixed with folder name to ensure unique Swift output.",
            "",
            "## Services",
            "",
        ]

        for tag in sorted(ops_by_tag.keys()):
            operations = ops_by_tag[tag]
            folder_name = self.tag_and_app_to_folder_name(tag, operations)
            lines.append(f"- **{tag}**: `{folder_name}/` ({len(operations)} operations)")

        lines.extend([
            "",
            "## Compilation",
            "",
            "### Python (grpc_tools)",
            "```bash",
            "# Install dependencies",
            "pip install grpcio grpcio-tools",
            "",
            "# Compile each service",
        ])

        for tag in sorted(ops_by_tag.keys()):
            operations = ops_by_tag[tag]
            folder_name = self.tag_and_app_to_folder_name(tag, operations)
            lines.append(f"python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. {folder_name}/*.proto")

        lines.extend([
            "```",
            "",
            "### Go",
            "```bash",
            "# Install dependencies",
            "go install google.golang.org/protobuf/cmd/protoc-gen-go@latest",
            "go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest",
            "",
            "# Compile each service",
        ])

        for tag in sorted(ops_by_tag.keys()):
            operations = ops_by_tag[tag]
            folder_name = self.tag_and_app_to_folder_name(tag, operations)
            lines.append(f"protoc -I. --go_out=. --go-grpc_out=. {folder_name}/*.proto")

        lines.extend([
            "```",
            "",
            "### TypeScript (ts-proto)",
            "```bash",
            "# Install dependencies",
            "npm install ts-proto",
            "",
            "# Compile each service",
        ])

        for tag in sorted(ops_by_tag.keys()):
            operations = ops_by_tag[tag]
            folder_name = self.tag_and_app_to_folder_name(tag, operations)
            lines.append(f"protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. {folder_name}/*.proto")

        lines.extend([
            "```",
            "",
            "## Usage Example",
            "",
            "After compilation, you can use the generated clients in your application.",
            "",
            "### Python",
            "```python",
            "import grpc",
            f"from {self.package_name.replace('.', '_')} import service_pb2, service_pb2_grpc",
            "",
            "# Create channel",
            "channel = grpc.insecure_channel('localhost:50051')",
            "",
            "# Create stub",
            "stub = service_pb2_grpc.YourServiceStub(channel)",
            "",
            "# Make request",
            "request = service_pb2.YourRequest(field='value')",
            "response = stub.YourMethod(request)",
            "```",
            "",
            "---",
            "",
            "*Generated by django-cfg django_client module*",
        ])

        return GeneratedFile(
            path="README.md",
            content="\n".join(lines),
            description="Protocol Buffer compilation and usage instructions",
        )

    def _generate_messages_file(self) -> GeneratedFile:
        """Generate messages.proto file with all message definitions."""
        # Collect all schemas from context
        all_schemas = {
            **self.context.schemas,
            **self.context.request_models,
            **self.context.response_models,
            **self.context.patch_models,
        }

        # Generate message definitions
        self.messages_generator.generate_all_messages(all_schemas)
        messages_content = self.messages_generator.get_all_definitions()

        # Build proto file content
        content = self._build_proto_header("messages.proto")

        if messages_content:
            content += "\n\n" + messages_content

        return GeneratedFile(
            path="messages.proto",
            content=content,
            description="Protocol Buffer message definitions",
        )

    def _generate_services_file(self) -> GeneratedFile:
        """Generate services.proto file with all service definitions."""
        # Generate service definitions from operations
        operations = list(self.context.operations.values())
        service_definitions = self.services_generator.generate_all_services(operations)

        # Build proto file content
        content = self._build_proto_header("services.proto")
        content += '\nimport "messages.proto";\n'

        # Add all service definitions
        for service_name, service_def in service_definitions.items():
            content += "\n\n" + service_def

        return GeneratedFile(
            path="services.proto",
            content=content,
            description="gRPC service definitions",
        )

    def _generate_combined_file(self) -> GeneratedFile:
        """Generate single api.proto file with both messages and services."""
        # Collect all schemas
        all_schemas = {
            **self.context.schemas,
            **self.context.request_models,
            **self.context.response_models,
            **self.context.patch_models,
        }

        # Generate message definitions
        self.messages_generator.generate_all_messages(all_schemas)
        messages_content = self.messages_generator.get_all_definitions()

        # Generate service definitions
        operations = list(self.context.operations.values())
        service_definitions = self.services_generator.generate_all_services(operations)

        # Build combined proto file
        content = self._build_proto_header("api.proto")

        # Add messages first
        if messages_content:
            content += "\n\n// ===== Messages =====\n\n"
            content += messages_content

        # Add services
        if service_definitions:
            content += "\n\n// ===== Services =====\n\n"
            for service_name, service_def in service_definitions.items():
                content += service_def + "\n\n"

        return GeneratedFile(
            path="api.proto",
            content=content,
            description="Combined Protocol Buffer definitions",
        )

    def _build_proto_header(
        self,
        file_name: str,
        tag: str | None = None,
        swift_prefix: str | None = "API",
    ) -> str:
        """
        Build proto file header with syntax, package, and imports.

        Args:
            file_name: Name of the proto file
            tag: Optional service tag for package naming
            swift_prefix: Base prefix for Swift generated types (avoids conflicts with SwiftUI)
                         If tag provided, uses tag-specific prefix like "APITerminal"
                         to ensure unique types across services.

        Returns:
            Header string with syntax declaration, package, and imports
        """
        # Use tag-specific package if provided
        package_name = f"{self.package_name}.{self.tag_to_property_name(tag)}" if tag else self.package_name

        lines = [
            f'// {file_name}',
            '// Generated by django-cfg django_client module',
            '// DO NOT EDIT - This file is auto-generated',
            '',
            'syntax = "proto3";',
            '',
            f'package {package_name};',
        ]

        # Add Swift-specific option to prefix generated types
        # Use tag-specific prefix to avoid collisions between services
        # e.g., "terminal" -> "APITerminal", "shared_terminal" -> "APISharedTerminal"
        if swift_prefix:
            if tag:
                # Convert tag to PascalCase and append to base prefix
                # Handle spaces, underscores, and hyphens
                import re
                tag_clean = re.sub(r'[^a-zA-Z0-9]', ' ', tag)
                tag_pascal = ''.join(word.capitalize() for word in tag_clean.split())
                service_prefix = f"{swift_prefix}{tag_pascal}"
            else:
                service_prefix = swift_prefix

            lines.append('')
            lines.append(f'// Swift type prefix to avoid conflicts (unique per service)')
            lines.append(f'option swift_prefix = "{service_prefix}";')

        lines.append('')

        # Add required imports
        imports = self.type_mapper.get_required_imports()
        if imports:
            for import_path in imports:
                lines.append(f'import "{import_path}";')
            lines.append('')

        return '\n'.join(lines)

    # ===== Abstract Method Implementations (Not used for proto) =====

    def generate_schema(self, schema: IRSchemaObject) -> str:
        """
        Generate proto message for a single schema.

        Note: This is called by BaseGenerator abstract method requirement,
        but proto generation works differently - we generate all messages at once.
        """
        return self.messages_generator.generate_message(schema)

    def generate_enum(self, schema: IRSchemaObject) -> str:
        """
        Generate proto enum from schema.

        Note: This is called by BaseGenerator abstract method requirement,
        but enums are generated as part of message generation in proto.
        """
        if not schema.enum or not schema.name:
            return ""

        return self.messages_generator._generate_enum(schema, schema.name)

    def generate_operation(self, operation: IROperationObject) -> str:
        """
        Generate RPC definition for a single operation.

        Note: This is called by BaseGenerator abstract method requirement,
        but proto generation works differently - we generate all services at once.
        """
        service_name, definitions = self.services_generator.generate_rpc(operation)
        return '\n'.join(definitions)
