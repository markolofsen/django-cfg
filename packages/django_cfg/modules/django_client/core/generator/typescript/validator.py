"""
TypeScript code validator for generated clients.

Performs fast syntax checks to catch common issues:
- Required parameters after optional parameters
- Required fields in optional objects
- Invalid TypeScript syntax patterns
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ValidationError:
    """A validation error found in generated code."""

    file_path: str
    line_number: int | None
    error_type: str
    message: str
    code_snippet: str | None = None

    def __str__(self) -> str:
        """Format error for display."""
        location = f"{self.file_path}"
        if self.line_number:
            location += f":{self.line_number}"

        parts = [
            f"❌ {self.error_type}: {self.message}",
            f"   📍 {location}",
        ]

        if self.code_snippet:
            parts.append(f"   💡 {self.code_snippet}")

        return "\n".join(parts)


class TypeScriptValidator:
    """
    Validates generated TypeScript code for common issues.

    Fast regex-based checks that catch TypeScript compilation errors
    before they happen.
    """

    def __init__(self):
        self.errors: list[ValidationError] = []

    def validate_file(self, file_path: str | Path, content: str) -> list[ValidationError]:
        """
        Validate a single TypeScript file.

        Args:
            file_path: Path to the file (for error reporting)
            content: File content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        self.errors = []
        file_path_str = str(file_path)

        # Split into lines for line-based checks
        lines = content.split("\n")

        # Check each line
        for line_num, line in enumerate(lines, start=1):
            # Check 1: Required parameter after optional in function signature
            self._check_required_after_optional(file_path_str, line_num, line)

            # Check 2: Required fields in optional params object
            self._check_required_in_optional_object(file_path_str, line_num, line)

        # Multi-line checks
        self._check_function_signatures(file_path_str, content)

        return self.errors

    def _check_required_after_optional(
        self, file_path: str, line_num: int, line: str
    ) -> None:
        """
        Check for required parameters after optional parameters.

        Pattern: `param1?: type, param2: type`
        This is a TypeScript error.
        """
        # Match function parameters with optional followed by required
        # Pattern: word?: type followed by word: type
        pattern = r'\w+\?:\s*[\w\[\]<>|]+\s*,\s*\w+:\s*[\w\[\]<>|]+'

        if re.search(pattern, line):
            self.errors.append(
                ValidationError(
                    file_path=file_path,
                    line_number=line_num,
                    error_type="RequiredAfterOptional",
                    message="Required parameter cannot come after optional parameter",
                    code_snippet=line.strip(),
                )
            )

    def _check_required_in_optional_object(
        self, file_path: str, line_num: int, line: str
    ) -> None:
        """
        Check for required fields in optional params object.

        Pattern: `params?: { field: type }`
        This is a TypeScript error - optional object cannot have required fields.
        """
        # Match params?: { with required field (no ? before :)
        # Look for: params?: { word: type (without ? between word and :)
        pattern = r'params\?\s*:\s*\{[^}]*\w+:\s*[\w\[\]<>|]+'

        if re.search(pattern, line):
            # Extract the required field for better error message
            field_match = re.search(r'\{[^}]*(\w+):\s*[\w\[\]<>|]+', line)
            field_name = field_match.group(1) if field_match else "unknown"

            self.errors.append(
                ValidationError(
                    file_path=file_path,
                    line_number=line_num,
                    error_type="RequiredFieldInOptionalObject",
                    message=f"Optional object 'params?' cannot contain required field '{field_name}'",
                    code_snippet=line.strip(),
                )
            )

    def _check_function_signatures(self, file_path: str, content: str) -> None:
        """
        Check function signatures for parameter ordering issues.

        Extracts multi-line function signatures and validates them.
        """
        # Pattern to match async function declarations (may span multiple lines)
        # This is a simplified check - full parsing would be more robust
        function_pattern = r'(?:export\s+)?async\s+function\s+\w+\s*\([^)]*\)'

        for match in re.finditer(function_pattern, content, re.MULTILINE):
            signature = match.group(0)

            # Extract parameters from signature
            params_match = re.search(r'\((.*)\)', signature, re.DOTALL)
            if params_match:
                params_str = params_match.group(1)

                # Split by comma, but respect nested objects
                params = self._split_params(params_str)

                # Check ordering: required should come before optional
                found_optional = False
                for param in params:
                    param = param.strip()
                    if not param or param.startswith("..."):  # Skip rest params
                        continue

                    is_optional = "?" in param.split(":")[0] if ":" in param else False

                    if is_optional:
                        found_optional = True
                    elif found_optional and ":" in param:
                        # Found required after optional
                        param_name = param.split(":")[0].strip()
                        line_num = content[:match.start()].count("\n") + 1

                        self.errors.append(
                            ValidationError(
                                file_path=file_path,
                                line_number=line_num,
                                error_type="ParameterOrderError",
                                message=f"Required parameter '{param_name}' comes after optional parameters",
                                code_snippet=signature[:100] + "...",
                            )
                        )

    def _split_params(self, params_str: str) -> list[str]:
        """
        Split parameter string by commas, respecting nested structures.

        Example:
            "id: number, params: { a: string; b: number }, data?: Data"
            -> ["id: number", "params: { a: string; b: number }", "data?: Data"]
        """
        params = []
        current = []
        depth = 0

        for char in params_str:
            if char in "{<[":
                depth += 1
                current.append(char)
            elif char in "}>[":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                params.append("".join(current))
                current = []
            else:
                current.append(char)

        # Add last parameter
        if current:
            params.append("".join(current))

        return params

    def validate_directory(self, directory: Path) -> dict[str, list[ValidationError]]:
        """
        Validate all TypeScript files in a directory.

        Args:
            directory: Directory to scan for .ts files

        Returns:
            Dict mapping file paths to their validation errors
        """
        results = {}

        for ts_file in directory.rglob("*.ts"):
            # Skip .d.ts files
            if ts_file.suffix == ".ts" and not ts_file.name.endswith(".d.ts"):
                try:
                    content = ts_file.read_text(encoding="utf-8")
                    errors = self.validate_file(ts_file, content)

                    if errors:
                        results[str(ts_file)] = errors
                except Exception as e:
                    results[str(ts_file)] = [
                        ValidationError(
                            file_path=str(ts_file),
                            line_number=None,
                            error_type="ReadError",
                            message=f"Failed to read file: {e}",
                        )
                    ]

        return results

    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return len(self.errors) > 0


def validate_generated_code(output_dir: Path) -> bool:
    """
    Validate all generated TypeScript code in output directory.

    Args:
        output_dir: Root directory containing generated clients

    Returns:
        True if validation passed, False if errors found
    """
    validator = TypeScriptValidator()
    results = validator.validate_directory(output_dir)

    if not results:
        return True

    # Print errors
    print("\n" + "=" * 60)
    print("⚠️  TypeScript Validation Errors Found")
    print("=" * 60)

    total_errors = 0
    for file_path, errors in results.items():
        print(f"\n📄 {file_path}")
        for error in errors:
            print(f"   {error}")
            total_errors += 1

    print("\n" + "=" * 60)
    print(f"❌ Found {total_errors} validation error(s) in {len(results)} file(s)")
    print("=" * 60 + "\n")

    return False


def quick_validate(content: str, file_name: str = "generated.ts") -> list[ValidationError]:
    """
    Quick validation of a code snippet.

    Useful for testing or validating generated code before writing to file.

    Args:
        content: TypeScript code to validate
        file_name: Virtual file name for error reporting

    Returns:
        List of validation errors
    """
    validator = TypeScriptValidator()
    return validator.validate_file(file_name, content)
