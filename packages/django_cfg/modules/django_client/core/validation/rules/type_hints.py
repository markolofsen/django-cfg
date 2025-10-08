"""Type hint validation rule for SerializerMethodField."""

import ast
from pathlib import Path
from typing import List

from .base import Issue, Severity, ValidationRule


class TypeHintRule(ValidationRule):
    """
    Add type hints to SerializerMethodField methods.

    Checks: get_* methods without return type annotations
    Fixes: Adds inferred type hints based on method name patterns
    """

    @property
    def rule_id(self) -> str:
        return "type-hint-001"

    @property
    def name(self) -> str:
        return "SerializerMethodField Type Hints"

    @property
    def description(self) -> str:
        return "Ensures all get_* methods have return type hints"

    def check(self, file_path: Path) -> List[Issue]:
        """Find methods missing type hints."""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors or encoding issues
            return []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Only process get_* methods
            if not node.name.startswith('get_'):
                continue

            # Skip if already has type hint
            if node.returns is not None:
                continue

            # Skip private methods
            if node.name.startswith('_get_'):
                continue

            # Infer type hint
            inferred_type = self._infer_type(node)

            issues.append(Issue(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                file=file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Method {node.name}() missing return type hint",
                suggestion=f"Add: -> {inferred_type}",
                auto_fixable=True,
                context={
                    'method_name': node.name,
                    'inferred_type': inferred_type,
                    'line_number': node.lineno,
                }
            ))

        return issues

    def can_fix(self, issue: Issue) -> bool:
        """All type hint issues are auto-fixable."""
        return issue.auto_fixable and issue.rule_id == self.rule_id

    def fix(self, issue: Issue, skip_imports: bool = False) -> bool:
        """
        Add type hint to method.

        Args:
            issue: Issue to fix
            skip_imports: If True, skip adding imports (for batch processing)
        """
        file_path = issue.file
        inferred_type = issue.context['inferred_type']
        line_number = issue.context['line_number']

        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines(keepends=True)

            # Ensure line exists
            if line_number > len(lines):
                return False

            # Find method definition line
            target_line = lines[line_number - 1]

            # Add type hint (preserve indentation and formatting)
            if ')' in target_line and ':' in target_line:
                # def method(self, obj): → def method(self, obj) -> Type:
                modified_line = target_line.replace('):', f") -> {inferred_type}:", 1)
                lines[line_number - 1] = modified_line

                # Add imports if needed (unless skipping for batch mode)
                if not skip_imports:
                    imports_needed = self._get_required_imports(inferred_type)
                    if imports_needed:
                        lines = self._add_imports(lines, imports_needed)

                # Write back
                file_path.write_text(''.join(lines), encoding='utf-8')
                return True

        except Exception as e:
            print(f"Error fixing {issue.context['method_name']}: {e}")
            return False

        return False

    def fix_batch(self, issues: list[Issue]) -> bool:
        """
        Fix multiple issues in same file at once.
        This prevents line number shifting from import additions.
        """
        if not issues:
            return True

        file_path = issues[0].file

        try:
            # Read file once
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines(keepends=True)

            # Sort issues by line number in reverse order
            sorted_issues = sorted(issues, key=lambda i: i.context['line_number'], reverse=True)

            # Collect all required imports
            all_imports = set()

            # Fix all methods (from bottom to top)
            for issue in sorted_issues:
                inferred_type = issue.context['inferred_type']
                line_number = issue.context['line_number']

                if line_number > len(lines):
                    continue

                target_line = lines[line_number - 1]

                if ')' in target_line and ':' in target_line:
                    # Add type hint
                    modified_line = target_line.replace('):', f") -> {inferred_type}:", 1)
                    lines[line_number - 1] = modified_line

                    # Collect imports
                    imports_needed = self._get_required_imports(inferred_type)
                    for imp in imports_needed:
                        all_imports.add(imp)

            # Add all imports at once
            if all_imports:
                lines = self._add_imports(lines, list(all_imports))

            # Write back once
            file_path.write_text(''.join(lines), encoding='utf-8')
            return True

        except Exception as e:
            print(f"Error in batch fix: {e}")
            return False

    def _infer_type(self, node: ast.FunctionDef) -> str:
        """Infer return type from method name and body."""
        name = node.name

        # Pattern matching for common cases
        if any(pattern in name for pattern in ['can_', 'is_', 'has_']):
            return 'bool'

        if name.endswith('_count') or name.endswith('_total'):
            return 'int'

        if any(pattern in name for pattern in ['get_children', 'get_items', 'get_replies', 'get_list']):
            return 'List[Dict[str, Any]]'

        if name.endswith('_display') or name.endswith('_text'):
            return 'str'

        # Analyze return statements
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                # Constant values
                if isinstance(child.value, ast.Constant):
                    if isinstance(child.value.value, bool):
                        return 'bool'
                    elif isinstance(child.value.value, int):
                        return 'int'
                    elif isinstance(child.value.value, str):
                        return 'str'
                    elif child.value.value is None:
                        return 'Optional[Any]'

                # List/Dict literals
                elif isinstance(child.value, ast.List):
                    return 'List[Any]'
                elif isinstance(child.value, ast.Dict):
                    return 'Dict[str, Any]'

                # Method calls that suggest serializer
                elif isinstance(child.value, ast.Call):
                    # SomeSerializer(...).data pattern
                    if hasattr(child.value.func, 'attr') and child.value.func.attr == 'data':
                        # Check if many=True in call
                        for keyword in getattr(child.value, 'keywords', []):
                            if keyword.arg == 'many' and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    return 'List[Dict[str, Any]]'
                        return 'Dict[str, Any]'

        # Default fallback
        return 'Any'

    def _get_required_imports(self, type_hint: str) -> List[str]:
        """Get required imports for type hint."""
        imports = set()

        if 'List' in type_hint:
            imports.add('List')
        if 'Dict' in type_hint:
            imports.add('Dict')
        if 'Optional' in type_hint:
            imports.add('Optional')
        if 'Any' in type_hint or not imports:
            imports.add('Any')

        if imports:
            return [f"from typing import {', '.join(sorted(imports))}"]
        return []

    def _add_imports(self, lines: List[str], imports: List[str]) -> List[str]:
        """Add imports to file if not already present."""
        content = ''.join(lines)

        for import_line in imports:
            # Skip if import already exists
            if import_line in content:
                continue

            # Check if similar import exists
            import_parts = set(import_line.split('import ')[1].replace(' ', '').split(','))

            # Try to merge with existing typing imports
            merged = False
            for i, line in enumerate(lines):
                if line.strip().startswith('from typing import'):
                    existing_parts = set(line.split('import ')[1].replace(' ', '').replace('\n', '').split(','))
                    combined = sorted(existing_parts | import_parts)
                    lines[i] = f"from typing import {', '.join(combined)}\n"
                    merged = True
                    break

            if merged:
                continue

            # Find where to insert (after other imports)
            insert_idx = 0
            found_import = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    found_import = True
                    insert_idx = i + 1
                elif found_import and stripped and not stripped.startswith('#'):
                    # Found first non-import, non-comment line
                    break

            lines.insert(insert_idx, import_line + '\n')

        return lines
