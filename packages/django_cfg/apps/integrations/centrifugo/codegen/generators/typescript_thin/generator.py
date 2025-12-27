"""
TypeScript thin wrapper client generator.

Supports:
- Interface generation from Pydantic models
- Enum generation from IntEnum classes
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List, Type
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...discovery import RPCMethodInfo
from ...utils import to_typescript_method_name, pydantic_to_typescript, int_enum_to_typescript

logger = logging.getLogger(__name__)


def compute_api_version(methods: List[RPCMethodInfo], models: List[Type[BaseModel]]) -> str:
    """
    Compute a stable hash of the API contract.

    The hash is based on:
    - Method names and signatures
    - Model field names and types

    Returns a short hex hash (8 chars) that changes when the contract changes.
    """
    contract_data = {
        "methods": [],
        "models": [],
    }

    # Add method signatures
    for method in sorted(methods, key=lambda m: m.name):
        contract_data["methods"].append({
            "name": method.name,
            "param_type": method.param_type.__name__ if method.param_type else None,
            "return_type": method.return_type.__name__ if method.return_type else None,
            "no_wait": method.no_wait,
        })

    # Add model schemas
    for model in sorted(models, key=lambda m: m.__name__):
        schema = model.model_json_schema()
        # Only include stable parts of schema
        contract_data["models"].append({
            "name": model.__name__,
            "properties": list(schema.get("properties", {}).keys()),
            "required": schema.get("required", []),
        })

    # Compute hash
    contract_json = json.dumps(contract_data, sort_keys=True)
    full_hash = hashlib.sha256(contract_json.encode()).hexdigest()

    return full_hash[:8]


class TypeScriptThinGenerator:
    """Generator for TypeScript thin wrapper clients."""

    def __init__(
        self,
        methods: List[RPCMethodInfo],
        models: List[Type[BaseModel]],
        output_dir: Path,
        enums: List[Type[IntEnum]] | None = None,
    ):
        self.methods = methods
        self.models = models
        self.enums = enums or []
        self.output_dir = Path(output_dir)
        self.api_version = compute_api_version(methods, models)

        templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self):
        """Generate all TypeScript files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._generate_types()
        self._generate_rpc_client()
        self._generate_client()
        self._generate_index()
        self._generate_package_json()
        self._generate_tsconfig()
        self._generate_readme()
        self._generate_claude_md()

        logger.info(f"✅ Generated TypeScript client in {self.output_dir}")

    def _generate_types(self):
        """Generate types.ts file."""
        template = self.jinja_env.get_template("types.ts.j2")

        # Generate enums first
        enums_data = []
        for enum_class in self.enums:
            enum_code = int_enum_to_typescript(enum_class)
            enums_data.append({
                'name': enum_class.__name__,
                'code': enum_code,
            })

        # Track generated interfaces to avoid duplicates
        generated_interfaces = set()
        types_data = []

        for model in self.models:
            ts_interface = pydantic_to_typescript(model)

            # Split into individual interfaces and deduplicate
            for block in ts_interface.split("\n\nexport interface "):
                if not block.strip():
                    continue

                # Add "export interface " back if it was stripped
                if not block.startswith("export interface "):
                    block = "export interface " + block

                # Extract interface name
                name = block.split("{")[0].replace("export interface ", "").strip()

                if name not in generated_interfaces:
                    generated_interfaces.add(name)
                    types_data.append({
                        'name': name,
                        'code': block,
                    })

        content = template.render(types=types_data, enums=enums_data)
        (self.output_dir / "types.ts").write_text(content)

    def _generate_rpc_client(self):
        """Generate rpc-client.ts base class."""
        template = self.jinja_env.get_template("rpc-client.ts.j2")
        content = template.render()
        (self.output_dir / "rpc-client.ts").write_text(content)

    def _generate_client(self):
        """Generate client.ts thin wrapper."""
        template = self.jinja_env.get_template("client.ts.j2")

        methods_data = []
        for method in self.methods:
            param_type = method.param_type.__name__ if method.param_type else "any"
            return_type = method.return_type.__name__ if method.return_type else "any"
            method_name_ts = to_typescript_method_name(method.name)

            methods_data.append({
                'name': method.name,
                'name_ts': method_name_ts,
                'param_type': param_type,
                'return_type': return_type,
                'docstring': method.docstring or f"Call {method.name} RPC method",
                'no_wait': method.no_wait,
            })

        model_names = [m.__name__ for m in self.models]

        content = template.render(
            methods=methods_data,
            models=model_names,
            api_version=self.api_version,
            generated_at=datetime.now().isoformat(),
        )
        (self.output_dir / "client.ts").write_text(content)

    def _generate_index(self):
        """Generate index.ts file."""
        template = self.jinja_env.get_template("index.ts.j2")
        model_names = [m.__name__ for m in self.models]
        enum_names = [e.__name__ for e in self.enums]
        content = template.render(models=model_names, enums=enum_names)
        (self.output_dir / "index.ts").write_text(content)

    def _generate_package_json(self):
        """Generate package.json file."""
        template = self.jinja_env.get_template("package.json.j2")
        content = template.render()
        (self.output_dir / "package.json").write_text(content)

    def _generate_tsconfig(self):
        """Generate tsconfig.json file."""
        template = self.jinja_env.get_template("tsconfig.json.j2")
        content = template.render()
        (self.output_dir / "tsconfig.json").write_text(content)

    def _generate_readme(self):
        """Generate README.md file."""
        template = self.jinja_env.get_template("README.md.j2")
        methods_data = [{'name': m.name, 'name_ts': to_typescript_method_name(m.name)} for m in self.methods[:3]]
        model_names = [m.__name__ for m in self.models]
        content = template.render(methods=methods_data, models=model_names)
        (self.output_dir / "README.md").write_text(content)

    def _generate_claude_md(self):
        """Generate CLAUDE.md documentation file."""
        template = self.jinja_env.get_template("CLAUDE.md.j2")
        methods_data = []
        for method in self.methods:
            method_name_ts = to_typescript_method_name(method.name)
            methods_data.append({
                'name': method.name,
                'name_ts': method_name_ts,
                'docstring': method.docstring or f"Call {method.name} RPC",
            })
        content = template.render(
            methods=methods_data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        (self.output_dir / "CLAUDE.md").write_text(content)


__all__ = ['TypeScriptThinGenerator']
