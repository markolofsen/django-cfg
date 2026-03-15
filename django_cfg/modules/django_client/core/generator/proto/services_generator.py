"""
Proto Services Generator - Generates gRPC service definitions from IR operations.

Converts IROperationObject instances into proto3 service and rpc definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .type_mapper import ProtoTypeMapper

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir.operation import IROperationObject
    from django_cfg.modules.django_client.core.ir.schema import IRSchemaObject


class ProtoServicesGenerator:
    """
    Generates gRPC service definitions from IR operations.

    Handles:
    - Service grouping by tags
    - RPC method definitions
    - Request/Response message generation
    - Empty responses (google.protobuf.Empty)
    - Stream annotations (if needed in future)
    """

    def __init__(self, type_mapper: ProtoTypeMapper, context: IRContext | None = None):
        self.type_mapper = type_mapper
        self.context = context  # Need context to resolve schema references
        self.services: dict[str, list[str]] = {}  # service_name -> [rpc_definitions]
        self.request_messages: dict[str, str] = {}  # Track generated request messages

    def generate_rpc(self, operation: IROperationObject) -> tuple[str, list[str]]:
        """
        Generate an RPC definition from an IR operation.

        Args:
            operation: IR operation object

        Returns:
            Tuple of (service_name, [request_message_defs, response_message_defs, rpc_def])
        """
        # Determine service name from tags (first tag or "Default")
        service_name = self._get_service_name(operation)

        # Generate RPC method name
        rpc_name = self._get_rpc_name(operation)

        # Generate request message
        request_message_name, request_msg_def = self._generate_request_message(
            operation, rpc_name
        )

        # Generate response message
        response_message_name, response_msg_def = self._generate_response_message(
            operation, rpc_name
        )

        # Generate RPC definition
        rpc_def = f"  rpc {rpc_name}({request_message_name}) returns ({response_message_name});"

        # Add comment if operation has description
        if operation.description:
            # Sanitize description for proto comment
            desc = operation.description.strip().replace("\n", "\n  // ")
            rpc_def = f"  // {desc}\n{rpc_def}"

        # Collect all definitions
        definitions = []
        if request_msg_def:
            definitions.append(request_msg_def)
        if response_msg_def:
            definitions.append(response_msg_def)
        definitions.append(rpc_def)

        return service_name, definitions

    def _get_service_name(self, operation: IROperationObject) -> str:
        """Get service name from operation tags."""
        if operation.tags and len(operation.tags) > 0:
            service_name = operation.tags[0]
        else:
            service_name = "Default"

        # Convert to PascalCase and add "Service" suffix
        return self.type_mapper.get_message_name(service_name) + "Service"

    def _get_rpc_name(self, operation: IROperationObject) -> str:
        """Get RPC method name from operation."""
        if operation.operation_id:
            # Use operation_id (already should be camelCase from OpenAPI)
            name = operation.operation_id
        else:
            # Fallback: method + path
            path_parts = [p for p in operation.path.split("/") if p and not p.startswith("{")]
            name = operation.method + "_" + "_".join(path_parts)

        # Ensure PascalCase for RPC method name
        return self.type_mapper.get_message_name(name)

    def _generate_request_message(
        self, operation: IROperationObject, rpc_name: str
    ) -> tuple[str, str]:
        """
        Generate request message for an RPC.

        Args:
            operation: IR operation
            rpc_name: RPC method name

        Returns:
            Tuple of (message_name, message_definition)
        """
        message_name = f"{rpc_name}Request"

        # Check if we need a request message at all
        has_patch_body = hasattr(operation, 'patch_request_body') and operation.patch_request_body
        has_params = bool(
            operation.parameters
            or operation.request_body
            or has_patch_body
        )

        if not has_params:
            # No parameters - use empty message or google.protobuf.Empty
            self.type_mapper.imported_types.add("google.protobuf.Empty")
            return "google.protobuf.Empty", ""

        # Build request message
        lines = [f"message {message_name} {{"]
        field_number = 1

        # Add path/query parameters
        if operation.parameters:
            for param in operation.parameters:
                if param.location in ("path", "query"):
                    field_name = self.type_mapper.sanitize_field_name(param.name)
                    field_type = self.type_mapper.map_type(
                        param.schema_type,
                        None,  # IRParameterObject doesn't have format
                    )
                    is_required = param.required
                    is_nullable = False  # Parameters don't have nullable in IR

                    label = self.type_mapper.get_field_label(
                        is_required, is_nullable, False
                    )

                    if label:
                        lines.append(
                            f"  {label} {field_type} {field_name} = {field_number};"
                        )
                    else:
                        lines.append(f"  {field_type} {field_name} = {field_number};")

                    field_number += 1

        # Add request body as a single field referencing the schema
        if operation.request_body:
            content_type = operation.request_body.content_type or ""
            # Check if this is binary data (file upload, octet-stream, multipart)
            is_binary = (
                "multipart" in content_type
                or "octet-stream" in content_type
            )

            if is_binary:
                # For binary/file uploads, use bytes type directly
                # Note: In real gRPC, file uploads should use streaming (not implemented here)
                field_name = "file_data"
                field_type = "bytes"
                is_required = operation.request_body.required
                label = self.type_mapper.get_field_label(is_required, False, False)

                if label:
                    lines.append(f"  {label} {field_type} {field_name} = {field_number};")
                else:
                    lines.append(f"  {field_type} {field_name} = {field_number};")
            else:
                # Use schema_name to reference the request body schema
                schema_name = operation.request_body.schema_name
                field_name = "body"
                field_type = self.type_mapper.get_message_name(schema_name)

                is_required = operation.request_body.required
                label = self.type_mapper.get_field_label(is_required, False, False)

                if label:
                    lines.append(f"  {label} {field_type} {field_name} = {field_number};")
                else:
                    lines.append(f"  {field_type} {field_name} = {field_number};")
        elif has_patch_body:
            # PATCH operations have optional body
            schema_name = operation.patch_request_body.schema_name
            field_name = "body"
            field_type = self.type_mapper.get_message_name(schema_name)

            # PATCH body is always optional
            label = "optional"
            lines.append(f"  {label} {field_type} {field_name} = {field_number};")

        lines.append("}")

        return message_name, "\n".join(lines)

    def _generate_response_message(
        self, operation: IROperationObject, rpc_name: str
    ) -> tuple[str, str]:
        """
        Generate response message for an RPC.

        Args:
            operation: IR operation
            rpc_name: RPC method name

        Returns:
            Tuple of (message_name, message_definition)
        """
        message_name = f"{rpc_name}Response"

        # Get successful response (200, 201, etc.)
        response_schema_name = None
        for status_code, response in operation.responses.items():
            if isinstance(status_code, int) and 200 <= status_code < 300:
                # Found successful response
                if response.schema_name:
                    response_schema_name = response.schema_name
                    break

        # No response body - use Empty
        if not response_schema_name:
            self.type_mapper.imported_types.add("google.protobuf.Empty")
            return "google.protobuf.Empty", ""

        # Build response message - simply reference the schema
        lines = [f"message {message_name} {{"]

        # Reference the response schema as a single field
        field_type = self.type_mapper.get_message_name(response_schema_name)
        lines.append(f"  {field_type} data = 1;")

        lines.append("}")

        return message_name, "\n".join(lines)

    def generate_all_services(
        self, operations: list[IROperationObject]
    ) -> dict[str, str]:
        """
        Generate all service definitions from operations.

        Args:
            operations: List of IR operations

        Returns:
            Dictionary of service_name -> service_definition
        """
        self.services.clear()
        self.request_messages.clear()

        # Group operations by service
        messages_by_service: dict[str, list[str]] = {}
        rpcs_by_service: dict[str, list[str]] = {}

        for operation in operations:
            service_name, definitions = self.generate_rpc(operation)

            if service_name not in messages_by_service:
                messages_by_service[service_name] = []
                rpcs_by_service[service_name] = []

            # Separate messages from RPC definitions
            for definition in definitions:
                if definition.startswith("message "):
                    messages_by_service[service_name].append(definition)
                elif definition.strip().startswith("rpc ") or definition.strip().startswith("//"):
                    rpcs_by_service[service_name].append(definition)

        # Build service definitions
        service_definitions = {}
        for service_name in rpcs_by_service:
            lines = []

            # Add messages first
            if service_name in messages_by_service:
                lines.extend(messages_by_service[service_name])
                lines.append("")  # Blank line between messages and service

            # Add service definition
            lines.append(f"service {service_name} {{")
            lines.extend(rpcs_by_service[service_name])
            lines.append("}")

            service_definitions[service_name] = "\n".join(lines)

        return service_definitions
