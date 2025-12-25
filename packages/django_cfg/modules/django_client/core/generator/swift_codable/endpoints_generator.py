"""
Swift Endpoints Generator - Generates APIEndpoints enum from IR operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import re

from .naming import to_pascal_case, to_camel_case

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

        for pattern, ops in sorted(path_groups.items()):
            # Determine if this is a list or detail endpoint
            has_id_param = "{" in pattern

            if has_id_param:
                # Detail endpoint - generate function
                func_lines = self._generate_detail_endpoint(pattern, ops)
                lines.extend(func_lines)
            else:
                # List endpoint - generate static property
                prop_lines = self._generate_list_endpoint(pattern, ops)
                lines.extend(prop_lines)

        lines.append("    }")
        lines.append("")

        return lines

    def _generate_list_endpoint(
        self,
        path: str,
        operations: list[IROperationObject],
    ) -> list[str]:
        """Generate static property for list endpoint."""
        # Determine property name from path
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
    ) -> list[str]:
        """Generate function for detail endpoint with path parameters."""
        # Extract path parameters
        params = re.findall(r"\{(\w+)\}", path)

        # Generate function name
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
        """Normalize path to base pattern."""
        # Remove action suffixes like /update-role/, /activate/, etc.
        # Keep the main resource path
        parts = path.rstrip("/").split("/")

        # Find the last path parameter or resource name
        normalized_parts = []
        for part in parts:
            normalized_parts.append(part)
            # Stop after path parameter (e.g., {id})
            if part.startswith("{") and part.endswith("}"):
                break

        return "/".join(normalized_parts) + "/"

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
            return to_camel_case(last)
        return "list"

    def _path_to_function_name(self, path: str, params: list[str]) -> str:
        """Convert path with params to function name."""
        # /api/workspaces/workspaces/{id}/ -> detail
        # /api/workspaces/workspaces/{id}/members/ -> members
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if len(parts) >= 2:
            last = parts[-1]
            second_last = parts[-2] if len(parts) > 1 else ""
            if last == second_last or last == "":
                return "detail"
            return to_camel_case(last)
        return "detail"
