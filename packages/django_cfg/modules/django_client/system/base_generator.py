"""
Base generator class for MJS clients.
Handles schema loading and common utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Environment, FileSystemLoader


class BaseGenerator:
    """Base class for API client generation."""

    def __init__(self, schema_path: Path, output_dir: Path):
        """Initialize the generator with schema and output directory."""
        self.schema_path = schema_path
        self.output_dir = output_dir
        self.schema = self._load_schema()

        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

    def _load_schema(self) -> Dict[str, Any]:
        """Load OpenAPI schema from JSON/YAML file."""
        with open(self.schema_path) as f:
            if self.schema_path.suffix == '.yaml':
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        snake_str = snake_str.replace(' ', '_').replace('-', '_')
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        snake_str = snake_str.replace(' ', '_').replace('-', '_')
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def sanitize_identifier(self, name: str) -> str:
        """Sanitize a name to be a valid JavaScript identifier."""
        # Replace spaces and special chars with underscores
        sanitized = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        # Remove any remaining invalid characters
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', sanitized)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized
        return sanitized

    def get_type_from_schema(self, schema: Dict[str, Any]) -> str:
        """Extract JavaScript type from OpenAPI schema."""
        if not schema:
            return 'any'

        # Handle references
        if '$ref' in schema:
            ref_name = schema['$ref'].split('/')[-1]
            return ref_name

        # Handle arrays
        if schema.get('type') == 'array':
            items_type = self.get_type_from_schema(schema.get('items', {}))
            return f'{items_type}[]'

        # Handle objects
        if schema.get('type') == 'object':
            # If it has properties, we could generate an interface
            # For now, just return a generic object type
            if 'properties' in schema:
                return 'Object'
            return 'any'

        # Handle primitive types
        type_mapping = {
            'string': 'string',
            'integer': 'number',
            'number': 'number',
            'boolean': 'boolean',
            'null': 'null'
        }

        openapi_type = schema.get('type', 'any')
        return type_mapping.get(openapi_type, 'any')

    def extract_response_type(self, operation: Dict[str, Any]) -> str:
        """Extract the response type from an operation."""
        responses = operation.get('responses', {})

        # Look for successful response (200, 201, etc.)
        for status in ['200', '201', '202', '204']:
            if status in responses:
                response = responses[status]

                # Handle 204 No Content
                if status == '204':
                    return 'void'

                # Extract content type
                content = response.get('content', {})
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    return self.get_type_from_schema(schema)

        # Default to any if we can't determine the type
        return 'any'

    def render_template(self, template_name: str, **context) -> str:
        """Render a Jinja2 template with the given context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
