"""Validation checker orchestrating all rules."""

from pathlib import Path
from typing import List, Optional

from .rules import DictFieldRule, Issue, ValidationRule
from .rules.type_hints import TypeHintRule


# Directories to exclude from scanning
EXCLUDE_DIRS = {'.venv', 'venv', 'env', 'site-packages', 'node_modules', '__pycache__', '.git', '.validation_backups'}


def should_skip_path(path: Path) -> bool:
    """
    Check if path should be skipped during scanning.

    Args:
        path: Path to check

    Returns:
        True if path should be skipped
    """
    return any(part in EXCLUDE_DIRS for part in path.parts)


class ValidationChecker:
    """
    Checks code against all validation rules.

    Example:
        >>> checker = ValidationChecker()
        >>> issues = checker.check_directory(Path('apps/'))
        >>> for issue in issues:
        ...     print(issue)
    """

    def __init__(self, rules: Optional[List[ValidationRule]] = None):
        """
        Initialize checker.

        Args:
            rules: List of validation rules. If None, uses default rules.
        """
        if rules is None:
            # Default rules
            self.rules = [
                DictFieldRule(),  # Check for DictField/ListField usage
                TypeHintRule(),
                # Future: ResponseSchemaRule(),
                # Future: EnumConflictRule(),
            ]
        else:
            self.rules = rules

    def check_file(self, file_path: Path) -> List[Issue]:
        """
        Check single file against all rules.

        Args:
            file_path: Path to Python file

        Returns:
            List of issues found
        """
        all_issues = []

        for rule in self.rules:
            try:
                issues = rule.check(file_path)
                all_issues.extend(issues)
            except Exception as e:
                print(f"Error in rule {rule.rule_id} for {file_path}: {e}")

        return all_issues

    def check_directory(
        self,
        directory: Path,
        pattern: str = "*serializers.py",
        recursive: bool = True
    ) -> List[Issue]:
        """
        Check all matching files in directory.

        Args:
            directory: Directory to search
            pattern: File pattern to match (default: *serializers.py)
            recursive: If True, search recursively

        Returns:
            List of all issues found
        """
        all_issues = []

        if recursive:
            files = directory.rglob(pattern)
        else:
            files = directory.glob(pattern)

        for file_path in files:
            # Skip excluded directories (venv, node_modules, etc.)
            if should_skip_path(file_path):
                continue

            if file_path.is_file():
                issues = self.check_file(file_path)
                all_issues.extend(issues)

        return all_issues

    def check_files(self, file_paths: List[Path]) -> List[Issue]:
        """
        Check specific list of files.

        Args:
            file_paths: List of file paths to check

        Returns:
            List of all issues found
        """
        all_issues = []

        for file_path in file_paths:
            if file_path.is_file():
                issues = self.check_file(file_path)
                all_issues.extend(issues)

        return all_issues

    def get_fixable_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Filter issues to only auto-fixable ones.

        Args:
            issues: List of issues

        Returns:
            List of auto-fixable issues
        """
        fixable = []

        for issue in issues:
            # Find rule for this issue
            rule = self._get_rule(issue.rule_id)
            if rule and rule.can_fix(issue):
                fixable.append(issue)

        return fixable

    def _get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """Get rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
