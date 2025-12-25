"""
Proto Type Mapper - Maps IR types to Protocol Buffer types.

Handles type conversion from OpenAPI/IR types to proto3 types.
"""

from __future__ import annotations


class ProtoTypeMapper:
    """
    Maps IR schema types to Protocol Buffer types.

    Supports proto3 with proper handling of:
    - Basic types (string, int32, int64, double, bool)
    - Complex types (message, repeated)
    - Special types (bytes for binary, google.protobuf.Timestamp for datetime)
    - Nullable fields (optional in proto3)
    """

    # Core type mappings
    TYPE_MAP = {
        "string": "string",
        "integer": "int64",  # Default to int64 for safety
        "number": "double",
        "boolean": "bool",
    }

    # Format-specific mappings
    FORMAT_MAP = {
        "int32": "int32",
        "int64": "int64",
        "float": "float",
        "double": "double",
        "byte": "bytes",
        "binary": "bytes",
        "date": "string",  # ISO 8601 date string
        "date-time": "google.protobuf.Timestamp",
        "password": "string",
        "email": "string",
        "uri": "string",
        "uuid": "string",
    }

    def __init__(self):
        self.imported_types = set()  # Track which google types we need to import

    def map_type(self, ir_type: str, ir_format: str | None = None) -> str:
        """
        Map IR type to proto type.

        Args:
            ir_type: IR schema type (string, integer, number, boolean, array, object)
            ir_format: Optional format specifier (int32, date-time, binary, etc.)

        Returns:
            Proto type string (e.g., "string", "int64", "bytes")
        """
        # Check format first (more specific)
        if ir_format and ir_format in self.FORMAT_MAP:
            proto_type = self.FORMAT_MAP[ir_format]

            # Track google imports
            if proto_type.startswith("google.protobuf."):
                self.imported_types.add(proto_type)

            return proto_type

        # Fall back to base type
        return self.TYPE_MAP.get(ir_type, "string")

    def get_field_label(self, required: bool, nullable: bool, is_repeated: bool) -> str:
        """
        Get proto field label (optional, repeated, or none).

        In proto3:
        - repeated: for arrays
        - optional: for nullable or non-required fields
        - (no label): for required non-repeated fields

        Args:
            required: Whether field is required
            nullable: Whether field can be null
            is_repeated: Whether field is an array

        Returns:
            Field label ("optional", "repeated", or "")
        """
        if is_repeated:
            return "repeated"

        if nullable or not required:
            return "optional"

        return ""

    def get_required_imports(self) -> list[str]:
        """
        Get list of proto files that need to be imported.

        Returns:
            List of import statements (e.g., ["google/protobuf/timestamp.proto"])
        """
        imports = []

        if "google.protobuf.Timestamp" in self.imported_types:
            imports.append("google/protobuf/timestamp.proto")

        if "google.protobuf.Empty" in self.imported_types:
            imports.append("google/protobuf/empty.proto")

        return imports

    def sanitize_field_name(self, name: str) -> str:
        """
        Sanitize field name for proto compatibility.

        Proto3 field names should be snake_case.

        Args:
            name: Original field name

        Returns:
            Sanitized field name
        """
        # Convert camelCase to snake_case
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

        # Reserved proto keywords that cannot be used as field names
        # Note: "message", "service", "rpc" CAN be used as field names in proto3
        reserved = {
            "syntax", "import", "package", "option",
            "repeated", "optional", "required", "enum"
        }

        if name in reserved:
            return f"{name}_value"

        return name

    def get_message_name(self, name: str) -> str:
        """
        Get proto message name (PascalCase).

        Args:
            name: Original name

        Returns:
            Proto-compatible message name
        """
        # Ensure PascalCase
        parts = name.replace("_", " ").replace("-", " ").split()
        return "".join(word.capitalize() for word in parts)
