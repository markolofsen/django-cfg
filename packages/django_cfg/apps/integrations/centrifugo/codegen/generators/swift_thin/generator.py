"""
Swift thin wrapper client generator.

Generates type-safe Swift clients for Centrifugo RPC methods.
Supports iOS 13.0+ with native async/await.
Supports IntEnum to Swift enum conversion.
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List, Type

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

from ...discovery import RPCMethodInfo, ChannelInfo
from ...utils import to_swift_method_name, get_safe_swift_type_name
from ...utils.converters import pydantic_to_swift_with_nested, int_enum_to_swift

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


class SwiftThinGenerator:
    """
    Generator for Swift thin wrapper clients.

    Generates:
    - Package.swift: SPM manifest
    - Sources/CentrifugoClient/CentrifugoTypes.swift: Codable models
    - Sources/CentrifugoClient/AnyCodable.swift: Dynamic JSON handling
    - Sources/CentrifugoClient/CentrifugoRPCClient.swift: Base RPC client
    - Sources/CentrifugoClient/CentrifugoClient.swift: Thin wrapper with typed methods
    - Sources/CentrifugoClient/CentrifugoSubscriptions.swift: Channel subscription support
    - README.md: Usage documentation
    - CLAUDE.md: AI assistance documentation
    """

    def __init__(
        self,
        methods: List[RPCMethodInfo],
        models: List[Type[BaseModel]],
        output_dir: Path,
        package_name: str = "CentrifugoClient",
        minimum_ios_version: str = "13.0",
        minimum_macos_version: str = "10.15",
        channels: List[ChannelInfo] = None,
        enums: List[Type[IntEnum]] = None,
    ):
        """
        Initialize Swift generator.

        Args:
            methods: List of RPC method info objects
            models: List of Pydantic model classes
            output_dir: Output directory for generated files
            package_name: Swift package name (default: CentrifugoClient)
            minimum_ios_version: Minimum iOS version (default: 13.0)
            minimum_macos_version: Minimum macOS version (default: 10.15)
            channels: List of channel info for subscription generation
            enums: List of IntEnum classes to generate Swift enums from
        """
        self.methods = methods
        self.models = models
        self.channels = channels or []
        self.enums = enums or []
        self.output_dir = Path(output_dir)
        self.package_name = package_name
        self.minimum_ios_version = minimum_ios_version
        self.minimum_macos_version = minimum_macos_version
        self.api_version = compute_api_version(methods, models)

        templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self) -> None:
        """Generate all Swift files."""
        # Create directory structure
        sources_dir = self.output_dir / "Sources" / self.package_name
        sources_dir.mkdir(parents=True, exist_ok=True)

        # Generate files
        self._generate_package_swift()
        self._generate_types(sources_dir)
        self._generate_any_codable(sources_dir)
        self._generate_rpc_client(sources_dir)
        self._generate_api_client(sources_dir)
        if self.channels:
            self._generate_subscriptions(sources_dir)
        self._generate_readme()
        self._generate_claude_md()

        logger.info(f"✅ Generated Swift client in {self.output_dir}")

    def _generate_package_swift(self) -> None:
        """Generate Package.swift SPM manifest."""
        template = self.jinja_env.get_template("Package.swift.j2")
        content = template.render(
            package_name=self.package_name,
            minimum_ios_version=self.minimum_ios_version,
            minimum_macos_version=self.minimum_macos_version,
        )
        (self.output_dir / "Package.swift").write_text(content)

    def _generate_types(self, sources_dir: Path) -> None:
        """Generate Types.swift with Codable models and enums."""
        template = self.jinja_env.get_template("Types.swift.j2")

        # Generate enums first
        enums_data = []
        enum_names = set()
        for enum_class in self.enums:
            enum_code = int_enum_to_swift(enum_class)
            enums_data.append({
                'name': enum_class.__name__,
                'code': enum_code,
            })
            enum_names.add(enum_class.__name__)

        # Collect all types, avoiding duplicates
        # Include enum names to prevent generating them as structs
        types_data = []
        generated_names = set(enum_names)

        # Add RPC param/result models
        for model in self.models:
            result = pydantic_to_swift_with_nested(model)

            # Add nested types first
            for nested in result["nested"]:
                if nested["name"] not in generated_names:
                    types_data.append(nested)
                    generated_names.add(nested["name"])

            # Add main type
            main = result["main"]
            if main["name"] not in generated_names:
                types_data.append(main)
                generated_names.add(main["name"])

        # Add channel event types
        for channel in self.channels:
            for event_type in channel.event_types:
                if event_type.__name__ not in generated_names:
                    result = pydantic_to_swift_with_nested(event_type)

                    # Add nested types first
                    for nested in result["nested"]:
                        if nested["name"] not in generated_names:
                            types_data.append(nested)
                            generated_names.add(nested["name"])

                    # Add main type
                    main = result["main"]
                    if main["name"] not in generated_names:
                        types_data.append(main)
                        generated_names.add(main["name"])

        content = template.render(
            types=types_data,
            enums=enums_data,
            generated_at=datetime.now().isoformat(),
        )
        (sources_dir / "CentrifugoTypes.swift").write_text(content)

    def _generate_any_codable(self, sources_dir: Path) -> None:
        """Generate AnyCodable.swift for dynamic JSON handling."""
        template = self.jinja_env.get_template("AnyCodable.swift.j2")
        content = template.render()
        (sources_dir / "AnyCodable.swift").write_text(content)

    def _generate_rpc_client(self, sources_dir: Path) -> None:
        """Generate CentrifugoRPCClient.swift base class."""
        template = self.jinja_env.get_template("RPCClient.swift.j2")
        content = template.render()
        (sources_dir / "CentrifugoRPCClient.swift").write_text(content)

    def _generate_api_client(self, sources_dir: Path) -> None:
        """Generate CentrifugoClient.swift thin wrapper."""
        template = self.jinja_env.get_template("CentrifugoClient.swift.j2")

        methods_data = []
        for method in self.methods:
            # Apply safe naming to avoid Swift/SwiftUI conflicts
            param_type_raw = method.param_type.__name__ if method.param_type else "EmptyParams"
            return_type_raw = method.return_type.__name__ if method.return_type else "EmptyResult"
            param_type = get_safe_swift_type_name(param_type_raw)
            return_type = get_safe_swift_type_name(return_type_raw)
            method_name_swift = to_swift_method_name(method.name)

            # Extract first line of docstring
            docstring = method.docstring or f"Call {method.name} RPC method."
            docstring_first_line = docstring.split('\n')[0].strip()

            methods_data.append({
                "rpc_name": method.name,
                "swift_name": method_name_swift,
                "param_type": param_type,
                "return_type": return_type,
                "docstring": docstring_first_line,
                "full_docstring": docstring,
                "no_wait": method.no_wait,
            })

        model_names = [m.__name__ for m in self.models]

        # Prepare channel data for template
        channels_data = []
        for channel in self.channels:
            # Convert channel name to Swift method name (e.g., "ai_chat" -> "aiChat")
            parts = channel.name.split('_')
            swift_name = parts[0] + ''.join(p.capitalize() for p in parts[1:])

            # Get event type names
            event_type_names = [et.__name__ for et in channel.event_types]

            # Create enum name for events (e.g., "AIChatEvent")
            enum_name = ''.join(p.capitalize() for p in channel.name.split('_')) + 'Event'

            channels_data.append({
                "name": channel.name,
                "swift_name": swift_name,
                "pattern": channel.pattern,
                "params": channel.params,
                "event_types": event_type_names,
                "event_enum": enum_name,
                "docstring": channel.docstring or f"Subscribe to {channel.name} channel.",
            })

        content = template.render(
            methods=methods_data,
            models=model_names,
            channels=channels_data,
            package_name=self.package_name,
            api_version=self.api_version,
            generated_at=datetime.now().isoformat(),
        )
        (sources_dir / "CentrifugoClient.swift").write_text(content)

    def _generate_subscriptions(self, sources_dir: Path) -> None:
        """Generate CentrifugoSubscriptions.swift with channel event enums."""
        template = self.jinja_env.get_template("Subscriptions.swift.j2")

        channels_data = []
        for channel in self.channels:
            # Convert channel name to Swift enum name
            enum_name = ''.join(p.capitalize() for p in channel.name.split('_')) + 'Event'

            # Collect event cases
            event_cases = []
            for event_type in channel.event_types:
                # Get the 'type' field value from the model
                type_value = None
                for field_name, field_info in event_type.model_fields.items():
                    if field_name == 'type':
                        # Get default value
                        type_value = field_info.default
                        break

                if type_value:
                    # Convert to Swift case name (e.g., "message_start" -> "messageStart")
                    parts = type_value.split('_')
                    case_name = parts[0] + ''.join(p.capitalize() for p in parts[1:])

                    event_cases.append({
                        "case_name": case_name,
                        "type_value": type_value,
                        "type_name": event_type.__name__,
                    })

            channels_data.append({
                "name": channel.name,
                "enum_name": enum_name,
                "event_cases": event_cases,
                "docstring": channel.docstring or f"Events for {channel.name} channel.",
            })

        content = template.render(
            channels=channels_data,
            generated_at=datetime.now().isoformat(),
        )
        (sources_dir / "CentrifugoSubscriptions.swift").write_text(content)

    def _generate_readme(self) -> None:
        """Generate README.md file."""
        template = self.jinja_env.get_template("README.md.j2")

        methods_data = []
        for method in self.methods[:5]:  # Show first 5 methods as examples
            method_name_swift = to_swift_method_name(method.name)
            param_type = method.param_type.__name__ if method.param_type else "EmptyParams"
            return_type = method.return_type.__name__ if method.return_type else "EmptyResult"
            methods_data.append({
                "rpc_name": method.name,
                "swift_name": method_name_swift,
                "param_type": param_type,
                "return_type": return_type,
            })

        model_names = [m.__name__ for m in self.models]

        content = template.render(
            package_name=self.package_name,
            methods=methods_data,
            total_methods=len(self.methods),
            models=model_names,
            minimum_ios_version=self.minimum_ios_version,
            minimum_macos_version=self.minimum_macos_version,
        )
        (self.output_dir / "README.md").write_text(content)

    def _generate_claude_md(self) -> None:
        """Generate CLAUDE.md documentation file."""
        template = self.jinja_env.get_template("CLAUDE.md.j2")

        methods_data = []
        for method in self.methods:
            method_name_swift = to_swift_method_name(method.name)
            param_type = method.param_type.__name__ if method.param_type else "EmptyParams"
            return_type = method.return_type.__name__ if method.return_type else "EmptyResult"
            methods_data.append({
                "rpc_name": method.name,
                "swift_name": method_name_swift,
                "param_type": param_type,
                "return_type": return_type,
                "docstring": method.docstring or f"Call {method.name} RPC",
                "no_wait": method.no_wait,
            })

        model_names = [m.__name__ for m in self.models]

        # Prepare channel data for documentation
        channels_data = []
        for channel in self.channels:
            parts = channel.name.split('_')
            swift_name = parts[0] + ''.join(p.capitalize() for p in parts[1:])
            enum_name = ''.join(p.capitalize() for p in channel.name.split('_')) + 'Event'

            channels_data.append({
                "name": channel.name,
                "swift_name": swift_name,
                "pattern": channel.pattern,
                "params": channel.params,
                "event_enum": enum_name,
                "docstring": channel.docstring or f"Subscribe to {channel.name} channel.",
            })

        content = template.render(
            package_name=self.package_name,
            methods=methods_data,
            models=model_names,
            channels=channels_data,
            api_version=self.api_version,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        (self.output_dir / "CLAUDE.md").write_text(content)


__all__ = ["SwiftThinGenerator"]
