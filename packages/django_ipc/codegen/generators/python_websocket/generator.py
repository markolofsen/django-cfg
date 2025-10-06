"""
Python WebSocket client generator.

Generates type-safe Python client from RPC methods.
"""

import logging
from pathlib import Path
from typing import List, Type
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...discovery import RPCMethodInfo
from ...utils import to_python_method_name

logger = logging.getLogger(__name__)


class PythonWebSocketGenerator:
    """
    Generator for Python WebSocket clients.

    Creates type-safe Python client with WebSocket transport.
    """

    def __init__(
        self,
        methods: List[RPCMethodInfo],
        models: List[Type[BaseModel]],
        output_dir: Path,
        config=None,
    ):
        """
        Initialize generator.

        Args:
            methods: List of discovered RPC methods
            models: List of Pydantic models to generate types for
            output_dir: Output directory for generated files
            config: Optional RPCServerConfig for environment-aware clients
        """
        self.methods = methods
        self.models = models
        self.output_dir = Path(output_dir)
        self.config = config

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

        # Generate client
        self._generate_client()

        # Generate logger
        self._generate_logger()

        # Generate __init__
        self._generate_init()

        # Generate config files
        self._generate_requirements()
        self._generate_setup()
        self._generate_pyproject()
        self._generate_readme()
        self._generate_gitignore()
        self._generate_editorconfig()

        logger.debug(f"Generated Python client in {self.output_dir}")

    def _generate_models(self):
        """Generate models.py file."""
        template = self.jinja_env.get_template("models.py.j2")

        # Prepare models data
        models_data = []
        for model in self.models:
            model_code = self._generate_model_code(model)
            models_data.append({
                'name': model.__name__,
                'code': model_code,
            })

        content = template.render(models=models_data)

        output_file = self.output_dir / "models.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_model_code(self, model: Type[BaseModel]) -> str:
        """Generate code for a single Pydantic model."""
        schema = model.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        fields = []
        for field_name, field_info in properties.items():
            py_type = self._json_type_to_python(field_info)
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

        code = f'class {model.__name__}(BaseModel):\n'
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

    def _generate_client(self):
        """Generate client.py file."""
        template = self.jinja_env.get_template("client.py.j2")

        # Prepare methods for template
        methods_data = []
        for method in self.methods:
            param_type = method.param_type.__name__ if method.param_type else "Any"
            return_type = method.return_type.__name__ if method.return_type else "Any"

            # Convert method name to valid Python identifier
            method_name_python = to_python_method_name(method.name)

            methods_data.append({
                'name': method.name,  # Original name for RPC call
                'name_python': method_name_python,  # Python-safe name
                'param_type': param_type,
                'return_type': return_type,
                'docstring': method.docstring or f"Call {method.name} RPC method",
            })

        # Prepare model names for imports
        model_names = [m.__name__ for m in self.models]

        content = template.render(
            methods=methods_data,
            models=model_names,
            config=self.config,
        )

        output_file = self.output_dir / "client.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_logger(self):
        """Generate logger.py file."""
        # Copy logger template from templates directory
        templates_base = Path(__file__).parent.parent.parent / "templates"
        logger_template = templates_base / "python_client_logger.py"

        if logger_template.exists():
            import shutil
            output_file = self.output_dir / "logger.py"
            shutil.copy(logger_template, output_file)
            logger.debug(f"Generated {output_file}")
        else:
            logger.warning(f"Logger template not found: {logger_template}")

    def _generate_init(self):
        """Generate __init__.py file."""
        template = self.jinja_env.get_template("__init__.py.j2")

        model_names = [m.__name__ for m in self.models]

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

    def _generate_setup(self):
        """Generate setup.py file."""
        template = self.jinja_env.get_template("setup.py.j2")
        content = template.render()
        output_file = self.output_dir / "setup.py"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_pyproject(self):
        """Generate pyproject.toml file."""
        template = self.jinja_env.get_template("pyproject.toml.j2")
        content = template.render()
        output_file = self.output_dir / "pyproject.toml"
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
            })

        model_names = [m.__name__ for m in self.models]

        content = template.render(methods=methods_data, models=model_names)
        output_file = self.output_dir / "README.md"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_gitignore(self):
        """Generate .gitignore file."""
        template = self.jinja_env.get_template(".gitignore.j2")
        content = template.render()
        output_file = self.output_dir / ".gitignore"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_editorconfig(self):
        """Generate .editorconfig file."""
        template = self.jinja_env.get_template(".editorconfig.j2")
        content = template.render()
        output_file = self.output_dir / ".editorconfig"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")


__all__ = ['PythonWebSocketGenerator']
