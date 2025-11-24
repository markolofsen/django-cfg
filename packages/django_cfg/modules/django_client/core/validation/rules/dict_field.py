"""
DictField validation rule - enforces JSONField usage for TypeScript compatibility.

This rule detects DictField and ListField usage in DRF serializers that cause
TypeScript type mismatches in generated clients.
"""

import ast
import re
from pathlib import Path
from typing import List

from .base import Issue, Severity, ValidationRule


class DictFieldRule(ValidationRule):
    """
    Recommends JSONField over DictField for better clarity and documentation.

    UPDATE (2025-11): TypeScript generator now safely handles DictField by always
    generating Record<string, any> instead of Record<string, string>, so DictField
    no longer causes validation errors. However, JSONField is still recommended
    for clarity and better OpenAPI schema documentation.

    Why JSONField is preferred:
        1. More explicit intent (arbitrary JSON data)
        2. Cleaner OpenAPI schema (additionalProperties: true)
        3. Better self-documentation

    Generator behavior:
        - DictField() → Record<string, any> (safe, but implicit)
        - JSONField() → Record<string, any> (explicit and clear)

    This rule now emits WARNING (not ERROR) since generator handles both safely.
    """

    @property
    def rule_id(self) -> str:
        return "dict-field-001"

    @property
    def name(self) -> str:
        return "DictField Best Practices"

    @property
    def description(self) -> str:
        return (
            "DictField is handled safely by TypeScript generator (uses Record<string, any>), "
            "but JSONField is recommended for clarity and better OpenAPI schema documentation"
        )

    def check(self, file_path: Path) -> List[Issue]:
        """Check file for DictField and ListField usage."""
        issues = []

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            # Find all Serializer classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_serializer_class(node):
                        class_issues = self._check_serializer_class(
                            node, file_path, content
                        )
                        issues.extend(class_issues)

        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not parse {file_path}: {e}")

        return issues

    def _is_serializer_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a DRF Serializer."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if "Serializer" in base.id:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr == "Serializer" or "Serializer" in base.attr:
                    return True
        return False

    def _check_serializer_class(
        self, node: ast.ClassDef, file_path: Path, content: str
    ) -> List[Issue]:
        """Check serializer class fields."""
        issues = []
        lines = content.split("\n")

        for item in node.body:
            # Check field assignments
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id  # Fixed: ast.Name has 'id', not 'name'
                        issue = self._check_field_assignment(
                            field_name, item.value, file_path, item.lineno, lines
                        )
                        if issue:
                            issues.append(issue)

        return issues

    def _check_field_assignment(
        self,
        field_name: str,
        value_node: ast.expr,
        file_path: Path,
        line_no: int,
        lines: List[str],
    ) -> Issue | None:
        """Check if field assignment uses problematic field types."""

        # Check for DictField usage
        if self._is_dict_field(value_node):
            # Check if it has explicit child parameter
            has_child = self._has_child_parameter(value_node)

            if not has_child:
                return Issue(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,  # Changed from ERROR - generator handles this safely
                    file=file_path,
                    line=line_no,
                    column=0,
                    message=f"Field '{field_name}' uses DictField without child - JSONField is recommended for clarity",
                    suggestion=(
                        f"Recommended: {field_name} = serializers.JSONField(default=dict)\n"
                        "   Why: JSONField is more explicit and generates cleaner OpenAPI schema.\n"
                        "   Note: TypeScript generator automatically uses Record<string, any> for DictField,\n"
                        "         so this won't cause validation errors, but JSONField is clearer."
                    ),
                    auto_fixable=True,
                    context={
                        "field_name": field_name,
                        "field_type": "DictField",
                        "line_content": lines[line_no - 1] if line_no <= len(lines) else "",
                    },
                )

        # Check for ListField without child
        elif self._is_list_field(value_node):
            has_child = self._has_child_parameter(value_node)

            if not has_child:
                return Issue(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    file=file_path,
                    line=line_no,
                    column=0,
                    message=f"Field '{field_name}' uses ListField without child - ambiguous for TypeScript",
                    suggestion=(
                        f"Recommended fix:\n"
                        f"   {field_name} = serializers.ListField(child=serializers.JSONField())  # For arrays with any values\n"
                        f"   OR\n"
                        f"   {field_name} = serializers.ListField(child=serializers.CharField())  # For typed arrays\n"
                        f"\n"
                        f"Alternative (with smart detection):\n"
                        f"   {field_name} = serializers.JSONField(default=list)  # Generator will detect default=[] and create Array<any>"
                    ),
                    auto_fixable=True,
                    context={
                        "field_name": field_name,
                        "field_type": "ListField",
                        "line_content": lines[line_no - 1] if line_no <= len(lines) else "",
                    },
                )

        return None

    def _is_dict_field(self, node: ast.expr) -> bool:
        """Check if node is a DictField call."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                return node.func.attr == "DictField"
            elif isinstance(node.func, ast.Name):
                return node.func.id == "DictField"
        return False

    def _is_list_field(self, node: ast.expr) -> bool:
        """Check if node is a ListField call."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                return node.func.attr == "ListField"
            elif isinstance(node.func, ast.Name):
                return node.func.id == "ListField"
        return False

    def _has_child_parameter(self, node: ast.Call) -> bool:
        """Check if Call node has 'child' keyword argument."""
        for keyword in node.keywords:
            if keyword.arg == "child":
                return True
        return False

    def can_fix(self, issue: Issue) -> bool:
        """Check if issue can be auto-fixed."""
        return issue.auto_fixable and issue.rule_id == self.rule_id

    def fix(self, issue: Issue) -> bool:
        """
        Apply automatic fix to replace DictField/ListField with JSONField.

        Returns:
            True if fix was successful
        """
        try:
            file_path = issue.file
            content = file_path.read_text()
            lines = content.split("\n")

            # Get the problematic line
            line_idx = issue.line - 1
            if line_idx >= len(lines):
                return False

            original_line = lines[line_idx]
            field_name = issue.context["field_name"]
            field_type = issue.context["field_type"]

            # Generate replacement
            if field_type == "DictField":
                # Replace DictField with JSONField
                fixed_line = self._replace_dict_field(original_line, field_name)
            elif field_type == "ListField":
                # Replace ListField with JSONField
                fixed_line = self._replace_list_field(original_line, field_name)
            else:
                return False

            if fixed_line == original_line:
                # No change made
                return False

            # Apply fix
            lines[line_idx] = fixed_line
            new_content = "\n".join(lines)
            file_path.write_text(new_content)

            return True

        except Exception as e:
            print(f"Error fixing {issue.file}:{issue.line}: {e}")
            return False

    def _replace_dict_field(self, line: str, field_name: str) -> str:
        """Replace DictField with JSONField in line."""
        # Pattern: field_name = serializers.DictField(...)
        pattern = r"(serializers\.)DictField\("

        # Keep all parameters except transform child
        def replace_fn(match):
            return match.group(1) + "JSONField("

        fixed = re.sub(pattern, replace_fn, line)

        # If no default parameter, add it
        if "default=" not in fixed:
            # Insert default=dict before closing paren
            fixed = fixed.replace(")", ", default=dict)")

        return fixed

    def _replace_list_field(self, line: str, field_name: str) -> str:
        """Replace ListField with JSONField in line."""
        # Pattern: field_name = serializers.ListField(...)
        pattern = r"(serializers\.)ListField\("

        def replace_fn(match):
            return match.group(1) + "JSONField("

        fixed = re.sub(pattern, replace_fn, line)

        # If no default parameter, add it
        if "default=" not in fixed:
            # Insert default=list before closing paren
            fixed = fixed.replace(")", ", default=list)")

        return fixed
