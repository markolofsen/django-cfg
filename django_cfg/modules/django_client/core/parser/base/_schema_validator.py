"""
Schema name validation mixin — detects conflicts before parsing starts.
"""

from __future__ import annotations

import sys
import traceback

from ..models import ReferenceObject
from ._errors import raise_if_errors


class SchemaValidatorMixin:
    """
    Validates schema names for case-insensitive and exact-duplicate conflicts.

    Called before any parsing begins so generation is aborted immediately
    on invalid schemas.
    """

    def _validate_schema_names(self) -> None:
        """
        Validate schema names for conflicts BEFORE parsing.

        Checks:
        1. Case-insensitive duplicates (e.g., "User" and "user")
        2. Exact duplicates (e.g., "GRPCServerInfo" from two different serializers)

        Raises:
            ValueError: If schema name conflicts are detected.
        """
        if not self.spec.components or not self.spec.components.schemas:
            return

        schema_names = list(self.spec.components.schemas.keys())
        lowercase_map: dict[str, str] = {}
        exact_duplicate_sources: dict[str, dict] = {}

        for name in schema_names:
            lowercase = name.lower()

            if lowercase in lowercase_map:
                existing_name = lowercase_map[lowercase]
                error_msg = (
                    f"\n{'=' * 80}\n"
                    f"❌ SCHEMA NAME CONFLICT DETECTED\n"
                    f"{'=' * 80}\n\n"
                    f"Conflict Type: Case-insensitive duplicate\n"
                    f"Schema Names:\n"
                    f"  1. '{existing_name}'\n"
                    f"  2. '{name}'\n\n"
                    f"Problem:\n"
                    f"  These names differ only in casing and will cause conflicts on\n"
                    f"  case-insensitive filesystems (macOS, Windows).\n\n"
                    f"Solution:\n"
                    f"  Rename one of the Django serializers to make them distinct.\n"
                    f"  Example: {name}Serializer → {name}DetailSerializer\n\n"
                    f"{'=' * 80}\n"
                )
                print(error_msg, file=sys.stderr)
                print("\n🔍 Traceback (schema validation):", file=sys.stderr)
                traceback.print_stack(file=sys.stderr)
                raise ValueError(
                    f"Case-insensitive schema name conflict: '{existing_name}' vs '{name}'. "
                    f"Cannot generate client with conflicting schema names."
                )

            lowercase_map[lowercase] = name

            schema = self.spec.components.schemas.get(name)
            if schema and not isinstance(schema, ReferenceObject):
                title = getattr(schema, 'title', name)
                description = getattr(schema, 'description', '')

                if name in exact_duplicate_sources:
                    existing = exact_duplicate_sources[name]
                    error_msg = (
                        f"\n{'=' * 80}\n"
                        f"❌ SCHEMA NAME CONFLICT DETECTED\n"
                        f"{'=' * 80}\n\n"
                        f"Conflict Type: Exact duplicate schema name\n"
                        f"Schema Name: '{name}'\n\n"
                        f"Sources:\n"
                        f"  1. {existing['title']}\n"
                        f"     Description: {existing['description'][:100]}\n"
                        f"  2. {title}\n"
                        f"     Description: {description[:100]}\n\n"
                        f"Problem:\n"
                        f"  Multiple serializers are generating the same schema name '{name}'.\n\n"
                        f"Solution:\n"
                        f"  Rename one of the serializers to make them unique.\n"
                        f"  Examples:\n"
                        f"    - HealthCheckSerializer → GRPCHealthCheckSerializer\n\n"
                        f"{'=' * 80}\n"
                    )
                    print(error_msg, file=sys.stderr)
                    print("\n🔍 Traceback (schema validation):", file=sys.stderr)
                    traceback.print_stack(file=sys.stderr)
                    raise ValueError(
                        f"Duplicate schema name detected: '{name}'. "
                        f"Multiple serializers are generating this schema. "
                        f"Cannot generate client with conflicting schemas."
                    )

                exact_duplicate_sources[name] = {'title': title, 'description': description}
