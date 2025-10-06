"""
TypeScript WebSocket client generator.

Generates type-safe TypeScript client from RPC methods.
"""

import logging
from pathlib import Path
from typing import List, Type
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...discovery import RPCMethodInfo
from ...utils import pydantic_to_typescript, to_typescript_method_name

logger = logging.getLogger(__name__)


class TypeScriptWebSocketGenerator:
    """
    Generator for TypeScript WebSocket clients.

    Creates type-safe TypeScript client with WebSocket transport.
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
        """Generate all TypeScript files."""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate types
        self._generate_types()

        # Generate client
        self._generate_client()

        # Generate logger
        self._generate_logger()

        # Generate index
        self._generate_index()

        # Generate config files
        self._generate_tsconfig()
        self._generate_package_json()
        self._generate_readme()
        self._generate_gitignore()
        self._generate_editorconfig()
        self._generate_prettierrc()
        self._generate_eslintrc()

        logger.debug(f"Generated TypeScript client in {self.output_dir}")

    def _generate_types(self):
        """Generate types.ts file."""
        template = self.jinja_env.get_template("types.ts.j2")

        # Convert models to TypeScript interfaces
        interfaces = []
        for model in self.models:
            interface = pydantic_to_typescript(model)
            interfaces.append(interface)

        content = template.render(
            interfaces=interfaces,
        )

        output_file = self.output_dir / "types.ts"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_client(self):
        """Generate client.ts file."""
        template = self.jinja_env.get_template("client.ts.j2")

        # Prepare methods for template
        methods_data = []
        for method in self.methods:
            param_type = method.param_type.__name__ if method.param_type else "any"
            return_type = method.return_type.__name__ if method.return_type else "any"

            # Convert snake_case to camelCase for method name
            method_name_camel = self._snake_to_camel(method.name)

            methods_data.append({
                'name': method.name,  # Original name (send_email)
                'name_camel': method_name_camel,  # Camel case (sendEmail)
                'param_type': param_type,
                'return_type': return_type,
                'docstring': method.docstring or f"Call {method.name} RPC method",
            })

        content = template.render(
            methods=methods_data,
            config=self.config,
        )

        output_file = self.output_dir / "client.ts"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_logger(self):
        """Generate logger.ts file."""
        # Copy logger template from templates directory
        templates_base = Path(__file__).parent.parent.parent / "templates"
        logger_template = templates_base / "typescript_client_logger.ts"

        if logger_template.exists():
            import shutil
            output_file = self.output_dir / "logger.ts"
            shutil.copy(logger_template, output_file)
            logger.debug(f"Generated {output_file}")
        else:
            logger.warning(f"Logger template not found: {logger_template}")

    def _generate_index(self):
        """Generate index.ts file."""
        template = self.jinja_env.get_template("index.ts.j2")

        content = template.render()

        output_file = self.output_dir / "index.ts"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_tsconfig(self):
        """Generate tsconfig.json file."""
        template = self.jinja_env.get_template("tsconfig.json.j2")
        content = template.render()
        output_file = self.output_dir / "tsconfig.json"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_package_json(self):
        """Generate package.json file."""
        template = self.jinja_env.get_template("package.json.j2")
        content = template.render()
        output_file = self.output_dir / "package.json"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_readme(self):
        """Generate README.md file."""
        template = self.jinja_env.get_template("README.md.j2")

        # Prepare methods for examples
        methods_data = []
        for method in self.methods[:3]:  # First 3 methods for examples
            method_name_camel = self._snake_to_camel(method.name)
            methods_data.append({
                'name': method.name,
                'name_camel': method_name_camel,
            })

        content = template.render(methods=methods_data)
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

    def _generate_prettierrc(self):
        """Generate .prettierrc file."""
        template = self.jinja_env.get_template(".prettierrc.j2")
        content = template.render()
        output_file = self.output_dir / ".prettierrc"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _generate_eslintrc(self):
        """Generate .eslintrc.json file."""
        template = self.jinja_env.get_template(".eslintrc.json.j2")
        content = template.render()
        output_file = self.output_dir / ".eslintrc.json"
        output_file.write_text(content)
        logger.debug(f"Generated {output_file}")

    def _snake_to_camel(self, snake_str: str) -> str:
        """
        Convert snake_case to camelCase, handling namespaced methods.

        Examples:
            workspace.file_changed -> workspaceFileChanged
            send_email -> sendEmail
            user.update_profile -> userUpdateProfile
        """
        return to_typescript_method_name(snake_str)


__all__ = ['TypeScriptWebSocketGenerator']
