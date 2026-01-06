"""
Python thin wrapper client generator.

Generates Pydantic models + thin wrapper over CentrifugoRPCClient.
Uses Ws prefix for all types to avoid conflicts with REST API types.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Type
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...discovery import RPCMethodInfo
from ...utils import to_python_method_name, WS_TYPE_PREFIX, add_prefix_to_type_name

logger = logging.getLogger(__name__)


class PythonThinGenerator:
    """
    Generator for Python thin wrapper clients.

    Creates:
    - models.py: Pydantic models
    - client.py: Thin wrapper class over RPC client
    - rpc_client.py: Base CentrifugoRPCClient
    - __init__.py: Exports
    """

    def __init__(
        self,
        methods: List[RPCMethodInfo],
        models: List[Type[BaseModel]],
        output_dir: Path,
    ):
        """
        Initialize generator.

        Args:
            methods: List of discovered RPC methods
            models: List of Pydantic models
            output_dir: Output directory for generated files
        """
        self.methods = methods
        self.models = models
        self.output_dir = Path(output_dir)

        # Setup Jinja2 environment
        templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self):
        """Generate all Python files."""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate models
        self._generate_models()

        # Generate RPC client base
        self._generate_rpc_client()

        # Generate thin wrapper
        self._generate_client()

        # Generate __init__
        self._generate_init()

        # Generate config files
        self._generate_requirements()
        self._generate_readme()
        self._generate_claude_md()

        logger.info(f"✅ Generated Python client in {self.output_dir}")

    def _generate_models(self):
        """Generate models.py file with Pydantic models."""
        template = self.jinja_env.get_template("models.py.j2")

        # Collect all type names for prefix replacement
        all_type_names = {model.__name__ for model in self.models}

        # Prepare models data with Ws prefix
        models_data = []
        for model in self.models:
            model_code = self._generate_model_code(model, all_type_names)
            models_data.append({
                'name': add_prefix_to_type_name(model.__name__),
                'code': model_code,
            })

        content = template.render(models=models_data)

        output_file = self.output_dir / "models.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_model_code(self, model: Type[BaseModel], all_type_names: set) -> str:
        """Generate code for a single Pydantic model with Ws prefix."""
        schema = model.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        fields = []
        for field_name, field_info in properties.items():
            py_type = self._json_type_to_python(field_info)
            # Add Ws prefix to type references
            for type_name in all_type_names:
                py_type = re.sub(
                    rf'\b{re.escape(type_name)}\b',
                    add_prefix_to_type_name(type_name),
                    py_type
                )
            description = field_info.get('description', '')

            if field_name in required:
                if description:
                    fields.append(f"    {field_name}: {py_type} = Field(..., description='{description}')")
                else:
                    fields.append(f"    {field_name}: {py_type}")
            else:
                if description:
                    fields.append(f"    {field_name}: Optional[{py_type}] = Field(None, description='{description}')")
                else:
                    fields.append(f"    {field_name}: Optional[{py_type}] = None")

        doc = model.__doc__ or f"{model.__name__} model."
        prefixed_name = add_prefix_to_type_name(model.__name__)

        code = f'class {prefixed_name}(BaseModel):\n'
        code += f'    """{doc}"""\n'
        if fields:
            code += '\n'.join(fields)
        else:
            code += '    pass'

        return code

    def _json_type_to_python(self, field_info: dict) -> str:
        """Convert JSON schema type to Python type."""
        if "anyOf" in field_info:
            types = [self._json_type_to_python(t) for t in field_info["anyOf"]]
            return f"Union[{', '.join(types)}]"

        field_type = field_info.get("type", "Any")

        if field_type == "string":
            return "str"
        elif field_type == "integer":
            return "int"
        elif field_type == "number":
            return "float"
        elif field_type == "boolean":
            return "bool"
        elif field_type == "array":
            items = field_info.get("items", {})
            item_type = self._json_type_to_python(items)
            return f"List[{item_type}]"
        elif field_type == "object":
            return "Dict[str, Any]"
        elif field_type == "null":
            return "None"
        else:
            return "Any"

    def _generate_rpc_client(self):
        """Generate rpc_client.py base class."""
        template = self.jinja_env.get_template("rpc_client.py.j2")
        content = template.render()

        output_file = self.output_dir / "rpc_client.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_client(self):
        """Generate client.py thin wrapper."""
        template = self.jinja_env.get_template("client.py.j2")

        # Prepare methods for template
        methods_data = []
        for method in self.methods:
            param_type_raw = method.param_type.__name__ if method.param_type else None
            return_type_raw = method.return_type.__name__ if method.return_type else None
            # Add Ws prefix (skip 'dict')
            param_type = add_prefix_to_type_name(param_type_raw) if param_type_raw else "dict"
            return_type = add_prefix_to_type_name(return_type_raw) if return_type_raw else "dict"

            # Convert method name to valid Python identifier
            method_name_python = to_python_method_name(method.name)

            methods_data.append({
                'name': method.name,  # Original name for RPC call
                'name_python': method_name_python,  # Python-safe name
                'param_type': param_type,
                'return_type': return_type,
                'docstring': method.docstring or f"Call {method.name} RPC method",
            })

        # Prepare model names for imports (with Ws prefix)
        model_names = [add_prefix_to_type_name(m.__name__) for m in self.models]

        content = template.render(
            methods=methods_data,
            models=model_names,
        )

        output_file = self.output_dir / "client.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_init(self):
        """Generate __init__.py file."""
        template = self.jinja_env.get_template("__init__.py.j2")

        model_names = [add_prefix_to_type_name(m.__name__) for m in self.models]

        content = template.render(models=model_names)

        output_file = self.output_dir / "__init__.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_requirements(self):
        """Generate requirements.txt file."""
        template = self.jinja_env.get_template("requirements.txt.j2")
        content = template.render()
        output_file = self.output_dir / "requirements.txt"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_readme(self):
        """Generate README.md file."""
        template = self.jinja_env.get_template("README.md.j2")

        # Prepare methods for examples
        methods_data = []
        for method in self.methods[:3]:  # First 3 methods for examples
            methods_data.append({
                'name': method.name,
                'name_python': to_python_method_name(method.name),
            })

        model_names = [m.__name__ for m in self.models]

        content = template.render(methods=methods_data, models=model_names)
        output_file = self.output_dir / "README.md"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_claude_md(self):
        """Generate CLAUDE.md documentation file."""
        template = self.jinja_env.get_template("CLAUDE.md.j2")
        methods_data = []
        for method in self.methods:
            method_name_python = to_python_method_name(method.name)
            methods_data.append({
                'name': method.name,
                'name_python': method_name_python,
                'docstring': method.docstring or f"Call {method.name} RPC",
            })
        content = template.render(
            methods=methods_data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        output_file = self.output_dir / "CLAUDE.md"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")


__all__ = ['PythonThinGenerator']
