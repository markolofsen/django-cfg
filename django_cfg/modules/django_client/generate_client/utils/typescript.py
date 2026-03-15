"""
TypeScript Utilities.

Handles TypeScript type checking.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable


class TypeScriptUtils:
    """
    Utilities for TypeScript operations.

    Handles:
    - Running tsc --noEmit for type checking
    - Parsing TypeScript errors
    """

    def __init__(
        self,
        log: Callable[[str], None] | None = None,
        log_success: Callable[[str], None] | None = None,
        log_warning: Callable[[str], None] | None = None,
        log_error: Callable[[str], None] | None = None,
    ):
        self.log = log or print
        self.log_success = log_success or self.log
        self.log_warning = log_warning or self.log
        self.log_error = log_error or self.log

    def check_types(
        self,
        project_path: Path,
        *,
        timeout: int = 60,
        max_errors: int = 20,
    ) -> tuple[bool, list[str]]:
        """
        Run TypeScript type check on a project.

        Args:
            project_path: Path to project with tsconfig.json
            timeout: Timeout in seconds
            max_errors: Maximum number of errors to return

        Returns:
            Tuple of (success, error_lines)
        """
        self.log("\n🔍 Running TypeScript type check...")

        pnpm_path = shutil.which('pnpm')
        if not pnpm_path:
            self.log_warning("⚠️  pnpm not found. Skipping type check.")
            return True, []

        try:
            result = subprocess.run(
                [pnpm_path, 'exec', 'tsc', '--noEmit'],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                self.log_success("✅ TypeScript types are valid")
                return True, []

            # Parse errors
            errors = []
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                lines = output.split('\n')
                errors = lines[:max_errors]
                if len(lines) > max_errors:
                    errors.append(f"... and {len(lines) - max_errors} more errors")

            self.log_error("❌ TypeScript type errors found:")
            for error in errors:
                self.log_error(f"   {error}")

            return False, errors

        except subprocess.TimeoutExpired:
            self.log_warning(f"⚠️  Type check timed out ({timeout}s)")
            return True, []  # Don't block on timeout

    def format_diagnostic_help(self) -> str:
        """Return diagnostic help message."""
        return """
🔍 Diagnostic tools:
   • python manage.py validate_openapi --fix
     → Auto-fix missing type hints in Django serializers
   • python manage.py validate_openapi
     → Check OpenAPI schema quality issues
"""


__all__ = ["TypeScriptUtils"]
