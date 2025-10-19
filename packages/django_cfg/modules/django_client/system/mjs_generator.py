"""
MJS (ES Module) client generator for Django CFG.
Generates JavaScript modules with JSDoc type annotations.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List

from base_generator import BaseGenerator
from schema_parser import SchemaParser


class MJSGenerator(BaseGenerator):
    """Generate MJS API clients with JSDoc type annotations."""

    def __init__(self, schema_path: Path, output_dir: Path):
        """Initialize the MJS generator."""
        super().__init__(schema_path, output_dir)
        self.parser = SchemaParser(self.schema)

    def generate(self) -> int:
        """Generate all MJS client files organized by apps."""
        # Clean and create output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate base client
        self._generate_base_client()

        # Generate type definitions
        self._generate_types()

        # Group operations by app
        operations_by_app = self.parser.group_operations_by_app()

        # Generate client for each app
        generated_apps = []
        for app_name, operations in sorted(operations_by_app.items()):
            # Skip certain apps
            if app_name in ['default', 'endpoints', 'health']:
                continue

            self._generate_app_client(app_name, operations)
            generated_apps.append(app_name)

        # Generate main index file
        self._generate_main_index(generated_apps)

        # Count generated files
        file_count = len(generated_apps) * 2 + 3  # apps * (client + index) + base + types + main index
        return file_count

    def _generate_base_client(self):
        """Generate the base API client class."""
        content = self.render_template('base_client.js.j2')

        base_file = self.output_dir / 'base.mjs'
        base_file.write_text(content)
        print(f"  ✅ Generated: {base_file}")

    def _generate_types(self):
        """Generate type definitions from schema components."""
        # Extract all schema definitions
        schemas = self.schema.get('components', {}).get('schemas', {})

        # Convert schemas to JSDoc typedef format
        typedefs = []
        for schema_name, schema_def in schemas.items():
            typedef = self._schema_to_typedef(schema_name, schema_def)
            if typedef:
                typedefs.append(typedef)

        content = self.render_template('types.js.j2', typedefs=typedefs)

        types_file = self.output_dir / 'types.mjs'
        types_file.write_text(content)
        print(f"  ✅ Generated: {types_file}")

    def _schema_to_typedef(self, name: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an OpenAPI schema to a JSDoc typedef."""
        if schema.get('type') != 'object':
            return None

        properties = []
        required_props = schema.get('required', [])

        for prop_name, prop_schema in schema.get('properties', {}).items():
            prop_type = self.parser.get_js_type(prop_schema)
            is_required = prop_name in required_props

            properties.append({
                'name': prop_name,
                'type': prop_type,
                'required': is_required,
                'description': prop_schema.get('description', '')
            })

        return {
            'name': name,
            'description': schema.get('description', ''),
            'properties': properties
        }

    def _generate_app_client(self, app_name: str, operations: List[Dict]):
        """Generate client files for a specific app."""
        # Create app directory
        app_dir = self.output_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        # Prepare operations data
        methods = []
        for op in operations:
            method_data = self._prepare_method_data(op)
            if method_data:
                methods.append(method_data)

        # Generate client file
        class_name = self.to_pascal_case(app_name) + 'API'
        instance_name = self.to_camel_case(app_name) + 'API'

        content = self.render_template(
            'api_client.js.j2',
            app_name=app_name,
            class_name=class_name,
            instance_name=instance_name,
            methods=methods
        )

        client_file = app_dir / 'client.mjs'
        client_file.write_text(content)
        print(f"  ✅ Generated: {client_file}")

        # Generate app index
        index_content = self.render_template(
            'app_index.js.j2',
            app_name=app_name,
            class_name=class_name,
            instance_name=instance_name
        )

        index_file = app_dir / 'index.mjs'
        index_file.write_text(index_content)
        print(f"  ✅ Generated: {index_file}")

    def _prepare_method_data(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare method data for template rendering."""
        operation_id = operation.get('operationId', '')
        if not operation_id:
            return None

        method_name = self.parser.extract_method_name(operation_id)
        method_name = self.to_camel_case(method_name)

        # Extract parameters
        path_params = []
        query_params = []

        for param in operation.get('parameters', []):
            param_info = self.parser.extract_parameter_info(param)

            if param_info['in'] == 'path':
                path_params.append(param_info)
            elif param_info['in'] == 'query':
                query_params.append(param_info)

        # Extract request body
        request_body = self.parser.extract_request_body_info(
            operation.get('requestBody')
        )

        # Extract response type
        response_type = self.parser.get_response_type(
            operation.get('responses', {})
        )

        # Build path with template literals
        api_path = operation['path']
        for param in path_params:
            api_path = api_path.replace(
                f"{{{param['name']}}}",
                f"${{{param['name']}}}"
            )

        return {
            'name': method_name,
            'http_method': operation['method'].upper(),
            'path': api_path,
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'path_params': path_params,
            'query_params': query_params,
            'request_body': request_body,
            'response_type': response_type
        }

    def _generate_main_index(self, apps: List[str]):
        """Generate the main index file."""
        # Prepare app data for template
        app_imports = []
        for app_name in sorted(apps):
            class_name = self.to_pascal_case(app_name) + 'API'
            instance_name = self.to_camel_case(app_name) + 'API'

            app_imports.append({
                'app_name': app_name,
                'class_name': class_name,
                'instance_name': instance_name
            })

        content = self.render_template(
            'main_index.js.j2',
            apps=app_imports
        )

        index_file = self.output_dir / 'index.mjs'
        index_file.write_text(content)
        print(f"  ✅ Generated: {index_file}")
