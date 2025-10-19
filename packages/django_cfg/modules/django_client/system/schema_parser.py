"""
OpenAPI schema parser for extracting operation and type information.
"""

import re
from typing import Any, Dict, List, Optional


class SchemaParser:
    """Parse OpenAPI schema to extract operation and type information."""

    def __init__(self, schema: Dict[str, Any]):
        """Initialize with OpenAPI schema."""
        self.schema = schema
        self.components = schema.get('components', {})
        self.schemas = self.components.get('schemas', {})

    def extract_app_from_path(self, path: str) -> str:
        """Extract app name from API path."""
        # Pattern: /cfg/{app_name}/...
        match = re.match(r'/cfg/([^/]+)/', path)
        if match:
            return match.group(1)
        return 'core'  # Default for paths without clear app

    def extract_method_name(self, operation_id: str) -> str:
        """Extract clean method name from operation ID."""
        # Remove common prefixes
        for prefix in ['cfg__', 'api_', 'cfg_']:
            if operation_id.startswith(prefix):
                operation_id = operation_id[len(prefix):]

        # Handle double underscores
        operation_id = operation_id.replace('__', '_')

        return operation_id

    def group_operations_by_app(self) -> Dict[str, List[Dict]]:
        """Group API operations by Django app based on path patterns."""
        grouped = {}

        for path, path_item in self.schema.get('paths', {}).items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    # Extract app name from path
                    app_name = self.extract_app_from_path(path)

                    # Add operation info
                    op_info = {
                        'path': path,
                        'method': method,
                        'operationId': operation.get('operationId', ''),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': operation.get('parameters', []),
                        'requestBody': operation.get('requestBody'),
                        'responses': operation.get('responses', {}),
                        'tags': operation.get('tags', [])
                    }

                    if app_name not in grouped:
                        grouped[app_name] = []
                    grouped[app_name].append(op_info)

        return grouped

    def extract_parameter_info(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed parameter information."""
        param_info = {
            'name': parameter.get('name'),
            'in': parameter.get('in'),
            'required': parameter.get('required', False),
            'description': parameter.get('description', ''),
            'schema': parameter.get('schema', {})
        }

        # Extract type information
        schema = parameter.get('schema', {})
        param_info['type'] = self.get_js_type(schema)
        param_info['format'] = schema.get('format')

        return param_info

    def extract_request_body_info(self, request_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract request body information."""
        if not request_body:
            return None

        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})

        return {
            'required': request_body.get('required', False),
            'description': request_body.get('description', ''),
            'schema': schema,
            'type': self.get_js_type(schema)
        }

    def get_js_type(self, schema: Dict[str, Any]) -> str:
        """Convert OpenAPI schema to JavaScript/TypeScript type."""
        if not schema:
            return 'any'

        # Handle references
        if '$ref' in schema:
            ref_name = schema['$ref'].split('/')[-1]
            return ref_name

        # Handle arrays
        if schema.get('type') == 'array':
            items_type = self.get_js_type(schema.get('items', {}))
            return f'{items_type}[]'

        # Handle objects
        if schema.get('type') == 'object':
            # Check if it has specific properties
            if 'properties' in schema:
                # Could generate an interface here
                return 'Object'
            # Check for additionalProperties (dictionary-like)
            if 'additionalProperties' in schema:
                value_type = self.get_js_type(schema['additionalProperties'])
                return f'Record<string, {value_type}>'
            return 'Object'

        # Handle enums
        if 'enum' in schema:
            # Create a union type from enum values
            values = schema['enum']
            if all(isinstance(v, str) for v in values):
                return ' | '.join(f'"{v}"' for v in values)
            return 'string'

        # Handle primitive types
        type_mapping = {
            'string': 'string',
            'integer': 'number',
            'number': 'number',
            'boolean': 'boolean',
            'null': 'null'
        }

        openapi_type = schema.get('type', 'any')

        # Handle special formats
        format_type = schema.get('format')
        if openapi_type == 'string' and format_type:
            format_mapping = {
                'date': 'string',  # Could be Date
                'date-time': 'string',  # Could be Date
                'uuid': 'string',
                'email': 'string',
                'uri': 'string',
                'binary': 'Blob',
                'byte': 'string'
            }
            return format_mapping.get(format_type, 'string')

        return type_mapping.get(openapi_type, 'any')

    def get_response_type(self, responses: Dict[str, Any]) -> str:
        """Extract the response type from operation responses."""
        # Look for successful response (200, 201, etc.)
        for status in ['200', '201', '202']:
            if status in responses:
                response = responses[status]
                content = response.get('content', {})

                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    return self.get_js_type(schema)

        # Check for 204 No Content
        if '204' in responses:
            return 'void'

        # Default to any
        return 'any'

    def resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a $ref to its schema definition."""
        if not ref.startswith('#/'):
            return None

        parts = ref[2:].split('/')
        current = self.schema

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current
