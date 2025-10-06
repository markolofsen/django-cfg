"""
OpenAPI Schema Postprocessor for Django Revolution

Fixes common issues with DRF Spectacular + COMPONENT_SPLIT:
- Resolves missing base type references to Readable/Writable versions
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Set, Optional
from ..utils import Logger


class SchemaPostprocessor:
    """Postprocesses OpenAPI schemas to fix COMPONENT_SPLIT issues."""

    def __init__(self, logger: Optional[Logger] = None):
        """Initialize postprocessor with optional logger."""
        self.logger = logger or Logger("schema_postprocessor")
        self.missing_refs: Set[str] = set()
        self.fixed_refs: Dict[str, str] = {}

    def process_schema_file(self, schema_path: Path) -> bool:
        """
        Process OpenAPI schema file and fix component references.

        Args:
            schema_path: Path to OpenAPI YAML schema file

        Returns:
            bool: True if processing succeeded
        """
        try:
            if not schema_path.exists():
                self.logger.error(f"Schema file not found: {schema_path}")
                return False

            # Load schema
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)

            if not schema or 'components' not in schema:
                self.logger.warning(f"No components in schema: {schema_path}")
                return True

            # Get available components
            available_components = set(schema.get('components', {}).get('schemas', {}).keys())

            # Fix references
            fixed = self._fix_references(schema, available_components)

            if fixed:
                # Write back to file
                with open(schema_path, 'w', encoding='utf-8') as f:
                    yaml.dump(schema, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

                self.logger.success(f"Fixed {len(self.fixed_refs)} component references in {schema_path.name}")
                for old_ref, new_ref in self.fixed_refs.items():
                    self.logger.debug(f"  {old_ref} → {new_ref}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to process schema {schema_path}: {e}")
            return False

    def _fix_references(self, obj: Any, available_components: Set[str], parent_readonly: bool = False, in_response: bool = False) -> bool:
        """
        Recursively fix $ref references in schema.

        Args:
            obj: Schema object (dict, list, or primitive)
            available_components: Set of available component names
            parent_readonly: Whether parent field is read-only

        Returns:
            bool: True if any references were fixed
        """
        fixed = False

        if isinstance(obj, dict):
            # Check if this is an allOf with a $ref (Spectacular uses this for properties + $ref)
            if 'allOf' in obj and isinstance(obj['allOf'], list):
                for item in obj['allOf']:
                    if self._fix_references(item, available_components, parent_readonly, in_response):
                        fixed = True

            # Check if this is a $ref
            if '$ref' in obj:
                ref = obj['$ref']
                if ref.startswith('#/components/schemas/'):
                    component_name = ref.replace('#/components/schemas/', '')

                    # Check if component exists
                    if component_name not in available_components:
                        # Try to find Readable/Writable version
                        readable_name = f"{component_name}Readable"
                        writable_name = f"{component_name}Writable"

                        # Always prefer Readable for responses and read-only fields
                        # Default to Readable if both exist
                        if readable_name in available_components:
                            obj['$ref'] = f"#/components/schemas/{readable_name}"
                            self.fixed_refs[component_name] = readable_name
                            fixed = True
                            self.logger.debug(f"Fixed missing ref: {component_name} → {readable_name}")
                        elif writable_name in available_components:
                            obj['$ref'] = f"#/components/schemas/{writable_name}"
                            self.fixed_refs[component_name] = writable_name
                            fixed = True
                            self.logger.debug(f"Fixed missing ref: {component_name} → {writable_name}")
                        else:
                            self.missing_refs.add(component_name)
                            self.logger.warning(f"Missing component: {component_name} (no Readable/Writable version found)")

            # Check for readOnly flag
            is_readonly = obj.get('readOnly', False) or parent_readonly

            # Recurse into nested objects
            for key, value in obj.items():
                if key != '$ref':
                    if self._fix_references(value, available_components, is_readonly):
                        fixed = True

        elif isinstance(obj, list):
            for item in obj:
                if self._fix_references(item, available_components, parent_readonly):
                    fixed = True

        return fixed

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get postprocessing statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "fixed_refs": len(self.fixed_refs),
            "missing_refs": len(self.missing_refs),
            "fixed_mappings": dict(self.fixed_refs),
            "missing_components": list(self.missing_refs),
        }
