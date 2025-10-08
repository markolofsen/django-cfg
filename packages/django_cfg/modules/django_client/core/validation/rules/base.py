"""Base classes for validation rules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """Represents a validation issue."""
    rule_id: str
    severity: Severity
    file: Path
    line: int
    column: int
    message: str
    suggestion: str
    auto_fixable: bool
    context: dict  # Additional context for fixing

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column} [{self.severity.value}] {self.message}"


class ValidationRule(ABC):
    """Base class for all validation rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'type-hint-001')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable rule name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this rule checks."""
        pass

    @abstractmethod
    def check(self, file_path: Path) -> List[Issue]:
        """
        Check file for issues.

        Args:
            file_path: Path to Python file to check

        Returns:
            List of found issues
        """
        pass

    @abstractmethod
    def can_fix(self, issue: Issue) -> bool:
        """
        Check if this issue can be auto-fixed.

        Args:
            issue: Issue to check

        Returns:
            True if auto-fixable
        """
        pass

    @abstractmethod
    def fix(self, issue: Issue) -> bool:
        """
        Apply fix for this issue.

        Args:
            issue: Issue to fix

        Returns:
            True if fix was successful

        Note:
            This method modifies files directly!
            Caller is responsible for backups/rollback.
        """
        pass
