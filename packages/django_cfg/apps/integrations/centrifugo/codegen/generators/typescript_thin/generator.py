"""
TypeScript thin wrapper client generator.

Supports:
- Interface generation from Pydantic models
- Enum generation from IntEnum classes
- Channel subscription event types
- Ws prefix for all types to avoid conflicts with REST API types
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List, Literal, Type, get_type_hints, get_origin, get_args, Union
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...discovery import RPCMethodInfo, ChannelInfo
from ...utils import to_typescript_method_name, pydantic_to_typescript, int_enum_to_typescript, WS_TYPE_PREFIX, add_prefix_to_type_name

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
        channels: List[ChannelInfo] | None = None,
    ):
        self.methods = methods
        self.models = models
        self.enums = enums or []
        self.channels = channels or []
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
        if self.channels:
            self._generate_subscriptions()
        self._generate_index()
        self._generate_package_json()
        self._generate_tsconfig()
        self._generate_readme()
        self._generate_claude_md()

        logger.info(f"✅ Generated TypeScript client in {self.output_dir}")

    def _generate_types(self):
        """Generate types.ts file."""
        template = self.jinja_env.get_template("types.ts.j2")

        # Step 1: Collect all type names (models + enums)
        all_type_names = set()
        for model in self.models:
            all_type_names.add(model.__name__)
        for enum_class in self.enums:
            all_type_names.add(enum_class.__name__)

        # Step 2: Generate all interfaces first (without prefixing)
        # and collect any additional nested type names
        generated_interfaces = set()
        raw_blocks = []

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
                    all_type_names.add(name)  # Add nested types to the set
                    raw_blocks.append((name, block))

        # Step 3: Generate enums (with Ws prefix)
        enums_data = []
        for enum_class in self.enums:
            enum_code = int_enum_to_typescript(enum_class)
            prefixed_name = add_prefix_to_type_name(enum_class.__name__)
            enum_code = enum_code.replace(
                f"enum {enum_class.__name__}",
                f"enum {prefixed_name}"
            )
            enums_data.append({
                'name': prefixed_name,
                'code': enum_code,
            })

        # Step 4: Apply Ws prefix to all interfaces and type references
        types_data = []
        for name, block in raw_blocks:
            prefixed_name = add_prefix_to_type_name(name)
            prefixed_block = block

            # Replace all type references (including the interface name itself)
            for type_name in all_type_names:
                prefixed_block = re.sub(
                    rf'\b{re.escape(type_name)}\b',
                    add_prefix_to_type_name(type_name),
                    prefixed_block
                )

            types_data.append({
                'name': prefixed_name,
                'code': prefixed_block,
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
            param_type_raw = method.param_type.__name__ if method.param_type else "any"
            return_type_raw = method.return_type.__name__ if method.return_type else "any"
            # Add Ws prefix (skip 'any')
            param_type = add_prefix_to_type_name(param_type_raw) if param_type_raw != "any" else "any"
            return_type = add_prefix_to_type_name(return_type_raw) if return_type_raw != "any" else "any"
            method_name_ts = to_typescript_method_name(method.name)

            methods_data.append({
                'name': method.name,
                'name_ts': method_name_ts,
                'param_type': param_type,
                'return_type': return_type,
                'docstring': method.docstring or f"Call {method.name} RPC method",
                'no_wait': method.no_wait,
            })

        model_names = [add_prefix_to_type_name(m.__name__) for m in self.models]

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
        model_names = [add_prefix_to_type_name(m.__name__) for m in self.models]
        enum_names = [add_prefix_to_type_name(e.__name__) for e in self.enums]

        # Prepare channels data for index exports
        channels_data = []
        for channel in self.channels:
            enum_name = WS_TYPE_PREFIX + ''.join(p.capitalize() for p in channel.name.split('_')) + 'Event'
            event_cases = []
            for event_type in channel.event_types:
                type_value = None
                for field_name, field_info in event_type.model_fields.items():
                    if field_name == 'type':
                        type_value = field_info.default
                        break
                if type_value:
                    event_cases.append({'type_name': add_prefix_to_type_name(event_type.__name__)})
            channels_data.append({
                'enum_name': enum_name,
                'event_cases': event_cases,
            })

        content = template.render(models=model_names, enums=enum_names, channels=channels_data)
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

    def _generate_subscriptions(self):
        """Generate subscriptions.ts with channel event types."""
        template = self.jinja_env.get_template("subscriptions.ts.j2")

        channels_data = []
        nested_types = {}  # Collect nested types to generate

        for channel in self.channels:
            # Convert channel name to TypeScript enum name with Ws prefix (e.g., "ai_chat" -> "WsAiChatEvent")
            enum_name = WS_TYPE_PREFIX + ''.join(p.capitalize() for p in channel.name.split('_')) + 'Event'

            # Collect event cases
            event_cases = []
            for event_type in channel.event_types:
                # Get the 'type' field value from the model
                type_value = None
                for field_name, field_info in event_type.model_fields.items():
                    if field_name == 'type':
                        type_value = field_info.default
                        break

                if type_value:
                    # Get additional fields (exclude common ones)
                    fields = []
                    for field_name, field_info in event_type.model_fields.items():
                        if field_name in ('type', 'message_id', 'client_message_id'):
                            continue

                        # Get TypeScript type and collect nested types
                        ts_type, nested = self._python_type_to_ts_with_nested(field_info.annotation)
                        is_optional = not field_info.is_required()

                        for nested_model in nested:
                            if nested_model.__name__ not in nested_types:
                                nested_types[nested_model.__name__] = nested_model

                        fields.append({
                            'name': field_name,
                            'ts_type': ts_type,
                            'optional': is_optional,
                        })

                    event_cases.append({
                        'type_name': add_prefix_to_type_name(event_type.__name__),
                        'type_value': type_value,
                        'fields': fields,
                    })

            channels_data.append({
                'name': channel.name,
                'enum_name': enum_name,
                'event_cases': event_cases,
                'docstring': channel.docstring or f"Events for {channel.name} channel.",
            })

        # Generate nested types as interfaces (with Ws prefix)
        nested_types_data = []
        for type_name, model in nested_types.items():
            fields = []
            for field_name, field_info in model.model_fields.items():
                ts_type = self._python_type_to_ts(field_info.annotation)
                is_optional = not field_info.is_required()
                fields.append({
                    'name': field_name,
                    'ts_type': ts_type,
                    'optional': is_optional,
                })
            nested_types_data.append({
                'name': add_prefix_to_type_name(type_name),
                'fields': fields,
            })

        content = template.render(
            channels=channels_data,
            nested_types=nested_types_data,
            generated_at=datetime.now().isoformat(),
        )
        (self.output_dir / "subscriptions.ts").write_text(content)

    def _python_type_to_ts(self, python_type) -> str:
        """Convert Python type annotation to TypeScript type."""
        ts_type, _ = self._python_type_to_ts_with_nested(python_type)
        return ts_type

    def _python_type_to_ts_with_nested(self, python_type) -> tuple[str, list]:
        """Convert Python type annotation to TypeScript type, returning nested models."""
        if python_type is None:
            return 'any', []

        origin = get_origin(python_type)
        args = get_args(python_type)
        nested = []

        # Handle Optional (Union with None)
        if origin is Union:
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                ts_type, nested = self._python_type_to_ts_with_nested(non_none_args[0])
                return ts_type, nested
            types = []
            for a in non_none_args:
                ts_type, n = self._python_type_to_ts_with_nested(a)
                types.append(ts_type)
                nested.extend(n)
            return ' | '.join(types), nested

        # Handle List
        if origin is list:
            if args:
                ts_type, nested = self._python_type_to_ts_with_nested(args[0])
                return f'{ts_type}[]', nested
            return 'any[]', []

        # Handle Literal (string union)
        if origin is Literal:
            string_values = [f"'{v}'" for v in args]
            return ' | '.join(string_values), []

        # Handle basic types
        if python_type is str:
            return 'string', []
        if python_type is int:
            return 'number', []
        if python_type is float:
            return 'number', []
        if python_type is bool:
            return 'boolean', []

        # Handle Pydantic models - add Ws prefix
        if isinstance(python_type, type) and issubclass(python_type, BaseModel):
            return add_prefix_to_type_name(python_type.__name__), [python_type]

        # Fallback
        return 'any', []


__all__ = ['TypeScriptThinGenerator']
