"""
Swift Endpoints Generator - Generates APIEndpoints enum from IR operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import re

from .naming import to_pascal_case, to_camel_case, sanitize_swift_identifier

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IROperationObject


class SwiftEndpointsGenerator:
    """Generates Swift APIEndpoints enum from IR operations."""

    def generate_endpoints(
        self,
        operations_by_tag: dict[str, list[IROperationObject]],
        group_name: str = "API",
    ) -> str:
        """
        Generate APIEndpoints.swift content.

        Args:
            operations_by_tag: Operations grouped by tag
            group_name: API group name for the enum

        Returns:
            Swift source code string
        """
        enum_name = to_pascal_case(group_name) + "API"

        lines = [
            f"// {enum_name}.swift",
            "// Auto-generated from OpenAPI schema - DO NOT EDIT",
            "",
            "import Foundation",
            "",
            "/// API endpoint paths organized by resource",
            f"public enum {enum_name} {{",
            "",
        ]

        for tag, operations in sorted(operations_by_tag.items()):
            tag_lines = self._generate_tag_enum(tag, operations)
            lines.extend(tag_lines)

        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def _generate_tag_enum(
        self,
        tag: str,
        operations: list[IROperationObject],
    ) -> list[str]:
        """Generate enum for a single tag/resource."""
        enum_name = to_pascal_case(tag)

        lines = [
            f"    /// {tag.title()} API endpoints",
            f"    public enum {enum_name} {{",
        ]

        # Group operations by path pattern
        path_groups = self._group_by_path_pattern(operations)

        # Track used names to avoid duplicates
        used_names: dict[str, int] = {}  # name -> count of usage

        # First pass: collect all names and detect collisions
        path_name_map: dict[str, str] = {}
        for pattern in sorted(path_groups.keys()):
            has_id_param = "{" in pattern
            params = re.findall(r"\{(\w+)\}", pattern)

            if has_id_param:
                base_name = self._path_to_function_name(pattern, params)
            else:
                base_name = self._path_to_property_name(pattern)

            # Track the signature (name + param count) for functions
            signature = f"{base_name}_{len(params)}" if has_id_param else base_name
            used_names[signature] = used_names.get(signature, 0) + 1
            path_name_map[pattern] = base_name

        # Second pass: generate endpoints with unique names
        name_counters: dict[str, int] = {}
        for pattern, ops in sorted(path_groups.items()):
            has_id_param = "{" in pattern
            params = re.findall(r"\{(\w+)\}", pattern)
            base_name = path_name_map[pattern]

            signature = f"{base_name}_{len(params)}" if has_id_param else base_name

            # If this name is used multiple times, make it unique
            if used_names.get(signature, 0) > 1:
                # Use parent path segment to disambiguate
                final_name = self._make_unique_name(pattern, base_name, params)
            else:
                final_name = base_name

            if has_id_param:
                # Detail endpoint - generate function
                func_lines = self._generate_detail_endpoint(pattern, ops, final_name)
                lines.extend(func_lines)
            else:
                # List endpoint - generate static property
                prop_lines = self._generate_list_endpoint(pattern, ops, final_name)
                lines.extend(prop_lines)

        lines.append("    }")
        lines.append("")

        return lines

    def _make_unique_name(self, path: str, base_name: str, params: list[str]) -> str:
        """Make a unique name by incorporating parent path segments.

        Distinguishes between:
        - Nested resources: /machines/{id}/logs/ -> machineLogs (singular parent)
        - Direct resources: /machines/logs/{id}/ -> machinesLogs (plural parent)
        """
        path_parts = path.split("/")

        # Find the index of the first path parameter
        first_param_idx = None
        for i, p in enumerate(path_parts):
            if p.startswith("{"):
                first_param_idx = i
                break

        # Find where base_name appears in the path
        base_name_idx = None
        for i, p in enumerate(path_parts):
            normalized = to_camel_case(p.replace("-", "_"))
            if p == base_name or normalized == base_name:
                base_name_idx = i
                break

        if first_param_idx is not None and base_name_idx is not None:
            if base_name_idx > first_param_idx:
                # NESTED resource: /machines/{id}/logs/
                # The resource is after the parameter, so it's nested
                # Use the parent resource name in singular form
                parent_idx = first_param_idx - 1
                if parent_idx >= 0:
                    parent = path_parts[parent_idx]
                    # Singularize: machines -> machine
                    if parent.endswith("s") and len(parent) > 1:
                        parent = parent[:-1]
                    return to_camel_case(parent) + to_pascal_case(base_name)
            else:
                # DIRECT resource: /machines/logs/{id}/
                # The resource is before the parameter
                # Use the group name as prefix (stay plural)
                parts = [p for p in path.split("/") if p and not p.startswith("{")]
                if len(parts) >= 2:
                    # Skip 'api' prefix if present
                    group_idx = 1 if parts[0] == "api" else 0
                    if group_idx < len(parts) - 1:
                        group = parts[group_idx]
                        return to_camel_case(group) + to_pascal_case(base_name)

        # Fallback: use parent path segment
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if len(parts) >= 2:
            parent = parts[-2]
            if parent != base_name:
                return to_camel_case(parent) + to_pascal_case(base_name)

        return base_name

    def _generate_list_endpoint(
        self,
        path: str,
        operations: list[IROperationObject],
        prop_name: str | None = None,
    ) -> list[str]:
        """Generate static property for list endpoint."""
        # Determine property name from path if not provided
        if prop_name is None:
            prop_name = self._path_to_property_name(path)
        clean_path = path.lstrip("/")

        # Get HTTP methods supported
        methods = [op.http_method.upper() for op in operations]
        methods_comment = ", ".join(methods)

        return [
            f"        /// {methods_comment} {path}",
            f'        public static let {prop_name} = "{clean_path}"',
        ]

    def _generate_detail_endpoint(
        self,
        path: str,
        operations: list[IROperationObject],
        func_name: str | None = None,
    ) -> list[str]:
        """Generate function for detail endpoint with path parameters."""
        # Extract path parameters
        params = re.findall(r"\{(\w+)\}", path)

        # Generate function name if not provided
        if func_name is None:
            func_name = self._path_to_function_name(path, params)

        # Generate function signature
        param_list = ", ".join(f"_ {p}: String" for p in params)

        # Generate path with interpolation
        interpolated_path = path.lstrip("/")
        for param in params:
            interpolated_path = interpolated_path.replace(f"{{{param}}}", f"\\({param})")

        # Get HTTP methods supported
        methods = [op.http_method.upper() for op in operations]
        methods_comment = ", ".join(methods)

        return [
            f"        /// {methods_comment} {path}",
            f"        public static func {func_name}({param_list}) -> String {{",
            f'            "{interpolated_path}"',
            "        }",
        ]

    def _group_by_path_pattern(
        self,
        operations: list[IROperationObject],
    ) -> dict[str, list[IROperationObject]]:
        """Group operations by their path pattern."""
        groups: dict[str, list[IROperationObject]] = {}
        for op in operations:
            # Normalize path - remove trailing actions like /update-role/
            base_path = self._normalize_path(op.path)
            if base_path not in groups:
                groups[base_path] = []
            groups[base_path].append(op)
        return groups

    def _normalize_path(self, path: str) -> str:
        """Normalize path to base pattern.

        Keeps the full path including action suffixes like /stream/, /activate/.
        This ensures each unique endpoint gets its own entry.
        """
        # Just ensure trailing slash for consistency
        return path.rstrip("/") + "/"

    def _path_to_property_name(self, path: str) -> str:
        """Convert path to Swift property name."""
        # /api/workspaces/workspaces/ -> list
        # /api/workspaces/members/ -> members
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if len(parts) >= 2:
            # Use last part as name
            last = parts[-1]
            if last == parts[-2]:
                return "list"
            # Sanitize: remove dots, braces, etc. and convert to camelCase
            sanitized = sanitize_swift_identifier(last)
            return to_camel_case(sanitized)
        return "list"

    def _path_to_function_name(self, path: str, params: list[str]) -> str:
        """Convert path with params to function name."""
        # /api/workspaces/workspaces/{id}/ -> detail
        # /api/workspaces/workspaces/{id}/members/ -> members
        # /api/terminal/hls/{id}/master.m3u8/ -> masterM3u8
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if len(parts) >= 2:
            last = parts[-1]
            second_last = parts[-2] if len(parts) > 1 else ""
            if last == second_last or last == "":
                return "detail"
            # Sanitize: remove dots, braces, etc. and convert to camelCase
            sanitized = sanitize_swift_identifier(last)
            return to_camel_case(sanitized)
        return "detail"
