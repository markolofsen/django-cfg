"""Django management command to generate Centrifugo WebSocket RPC clients.

Usage:
    python manage.py generate_centrifugo_clients --output ./clients --python --typescript --go --swift
    python manage.py generate_centrifugo_clients -o ./clients --all
    python manage.py generate_centrifugo_clients -o ./clients --swift --verbose
"""

import logging
from pathlib import Path
from typing import List

from django.core.management.base import CommandError
from django.utils.termcolors import colorize

from django_cfg.management.utils import AdminCommand

from django_cfg.apps.integrations.centrifugo.codegen.discovery import discover_rpc_methods_from_router, ChannelInfo, extract_enums_from_models
from django_cfg.apps.integrations.centrifugo.codegen.generators.python_thin import PythonThinGenerator
from django_cfg.apps.integrations.centrifugo.codegen.generators.typescript_thin import TypeScriptThinGenerator
from django_cfg.apps.integrations.centrifugo.codegen.generators.go_thin import GoThinGenerator
from django_cfg.apps.integrations.centrifugo.codegen.generators.swift_thin import SwiftThinGenerator
from django_cfg.apps.integrations.centrifugo.router import get_global_router
from django_cfg.apps.integrations.centrifugo.registry import get_global_channel_registry


class Command(AdminCommand):
    """Generate type-safe client SDKs for Centrifugo WebSocket RPC."""

    command_name = 'generate_centrifugo_clients'
    help = "Generate type-safe client SDKs for Centrifugo WebSocket RPC from @websocket_rpc handlers"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            required=False,
            default=None,
            help="Output directory for generated clients (default: ./openapi/centrifuge)",
        )
        parser.add_argument(
            "--python",
            action="store_true",
            help="Generate Python client",
        )
        parser.add_argument(
            "--typescript",
            action="store_true",
            help="Generate TypeScript client",
        )
        parser.add_argument(
            "--go",
            action="store_true",
            help="Generate Go client",
        )
        parser.add_argument(
            "--swift",
            action="store_true",
            help="Generate Swift client (iOS/macOS)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Generate all clients (Python, TypeScript, Go, Swift)",
        )
        parser.add_argument(
            "--router-path",
            type=str,
            default=None,
            help="Python import path to custom MessageRouter (default: uses global router)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output (use Django's -v for verbosity level)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Determine output directory
        if options["output"]:
            output_dir = Path(options["output"]).resolve()
        else:
            # Default to ./openapi/centrifuge in current directory
            from django.conf import settings
            base_dir = Path(settings.BASE_DIR)
            output_dir = base_dir / "openapi" / "centrifuge"
            self.stdout.write(
                f"Using default output directory: {output_dir.relative_to(base_dir)}"
            )

        verbose = options["verbose"]

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        # Determine which clients to generate
        generate_python = options["python"] or options["all"]
        generate_typescript = options["typescript"] or options["all"]
        generate_go = options["go"] or options["all"]
        generate_swift = options["swift"] or options["all"]

        if not (generate_python or generate_typescript or generate_go or generate_swift):
            raise CommandError(
                "No client languages specified. Use --python, --typescript, --go, --swift, or --all"
            )

        self.stdout.write(
            colorize("Centrifugo Client Code Generation", fg="cyan", opts=["bold"])
        )
        self.stdout.write("=" * 60)

        # Get the MessageRouter
        try:
            if options["router_path"]:
                router = self._load_custom_router(options["router_path"])
                self.stdout.write(f"Using custom router: {options['router_path']}")
            else:
                router = get_global_router()
                self.stdout.write("Using global MessageRouter")
        except Exception as e:
            raise CommandError(f"Failed to load router: {e}")

        # Discover RPC methods
        self.stdout.write("\nDiscovering RPC methods...")
        try:
            methods = discover_rpc_methods_from_router(router)
            self.stdout.write(
                colorize(f"Found {len(methods)} RPC methods", fg="green")
            )

            if verbose:
                for method in methods:
                    param_type = (
                        method.param_type.__name__ if method.param_type else "None"
                    )
                    return_type = (
                        method.return_type.__name__ if method.return_type else "None"
                    )
                    self.stdout.write(
                        f"  - {method.name}: {param_type} -> {return_type}"
                    )

        except Exception as e:
            raise CommandError(f"Failed to discover RPC methods: {e}")

        if not methods:
            self.stdout.write(
                colorize(
                    "⚠️  No RPC methods found. Will generate base RPC client without API methods.",
                    fg="yellow",
                )
            )

        # Discover channels for pub/sub subscriptions
        self.stdout.write("\nDiscovering Centrifugo channels...")
        try:
            channel_registry = get_global_channel_registry()
            registered_channels = channel_registry.get_all_channels()

            # Convert RegisteredChannel to ChannelInfo for generators
            channels = []
            for rc in registered_channels:
                channels.append(ChannelInfo(
                    name=rc.name,
                    pattern=rc.pattern,
                    event_types=rc.event_types,
                    docstring=rc.docstring,
                    params=rc.params,
                ))

            self.stdout.write(
                colorize(f"Found {len(channels)} channels", fg="green")
            )

            if verbose and channels:
                for channel in channels:
                    event_names = [et.__name__ for et in channel.event_types]
                    self.stdout.write(
                        f"  - {channel.name}: {channel.pattern} ({len(event_names)} events)"
                    )

        except Exception as e:
            self.stdout.write(
                colorize(f"⚠️  Failed to discover channels: {e}", fg="yellow")
            )
            channels = []

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        self.stdout.write(f"\nOutput directory: {output_dir}")

        # Generate clients
        generated: List[str] = []

        if generate_python:
            self.stdout.write("\nGenerating Python client...")
            try:
                python_dir = output_dir / "python"
                # Extract all unique models from methods
                models = set()
                for method in methods:
                    if method.param_type:
                        models.add(method.param_type)
                    if method.return_type:
                        models.add(method.return_type)

                generator = PythonThinGenerator(methods, list(models), python_dir)
                generator.generate()
                generated.append("Python")
                self.stdout.write(
                    colorize(f"  ✓ Generated at: {python_dir}", fg="green")
                )
            except Exception as e:
                self.stdout.write(colorize(f"  ✗ Failed: {e}", fg="red"))
                if verbose:
                    logger.exception("Python generation failed")

        if generate_typescript:
            self.stdout.write("\nGenerating TypeScript client...")
            try:
                ts_dir = output_dir / "typescript"
                # Extract all unique models from methods
                models = set()
                for method in methods:
                    if method.param_type:
                        models.add(method.param_type)
                    if method.return_type:
                        models.add(method.return_type)

                models_list = list(models)

                # Extract IntEnum types from models for TypeScript enum generation
                enums = extract_enums_from_models(models_list)
                if enums and verbose:
                    enum_names = [e.__name__ for e in enums]
                    self.stdout.write(f"  Found {len(enums)} enums: {', '.join(enum_names)}")

                generator = TypeScriptThinGenerator(methods, models_list, ts_dir, enums=enums)
                generator.generate()
                generated.append("TypeScript")
                self.stdout.write(colorize(f"  ✓ Generated at: {ts_dir}", fg="green"))
            except Exception as e:
                self.stdout.write(colorize(f"  ✗ Failed: {e}", fg="red"))
                if verbose:
                    logger.exception("TypeScript generation failed")

        if generate_go:
            self.stdout.write("\nGenerating Go client...")
            try:
                go_dir = output_dir / "go"
                # Extract all unique models from methods
                models = set()
                for method in methods:
                    if method.param_type:
                        models.add(method.param_type)
                    if method.return_type:
                        models.add(method.return_type)

                generator = GoThinGenerator(methods, list(models), go_dir)
                generator.generate()
                generated.append("Go")
                self.stdout.write(colorize(f"  ✓ Generated at: {go_dir}", fg="green"))
            except Exception as e:
                self.stdout.write(colorize(f"  ✗ Failed: {e}", fg="red"))
                if verbose:
                    logger.exception("Go generation failed")

        if generate_swift:
            self.stdout.write("\nGenerating Swift client...")
            try:
                swift_dir = output_dir / "swift"
                # Extract all unique models from methods
                models = set()
                for method in methods:
                    if method.param_type:
                        models.add(method.param_type)
                    if method.return_type:
                        models.add(method.return_type)

                # Also add channel event types to models
                for channel in channels:
                    for event_type in channel.event_types:
                        models.add(event_type)

                models_list = list(models)

                # Extract enums from models
                enums = extract_enums_from_models(models_list)
                if enums and verbose:
                    enum_names = [e.__name__ for e in enums]
                    self.stdout.write(f"  Found {len(enums)} enums: {', '.join(enum_names)}")

                generator = SwiftThinGenerator(
                    methods=methods,
                    models=models_list,
                    output_dir=swift_dir,
                    channels=channels,  # Pass channels for subscription generation
                    enums=enums,
                )
                generator.generate()
                generated.append("Swift")
                self.stdout.write(colorize(f"  ✓ Generated at: {swift_dir}", fg="green"))
                if channels:
                    self.stdout.write(colorize(f"    (includes {len(channels)} channel subscriptions)", fg="cyan"))
            except Exception as e:
                self.stdout.write(colorize(f"  ✗ Failed: {e}", fg="red"))
                if verbose:
                    import traceback
                    traceback.print_exc()

        # Summary
        self.stdout.write("\n" + "=" * 60)
        if generated:
            self.stdout.write(
                colorize(
                    f"Successfully generated {len(generated)} client(s): {', '.join(generated)}",
                    fg="green",
                    opts=["bold"],
                )
            )
            self.stdout.write("\nNext steps:")
            if "Python" in generated:
                self.stdout.write(f"  cd {output_dir}/python && pip install -r requirements.txt")
            if "TypeScript" in generated:
                self.stdout.write(f"  cd {output_dir}/typescript && npm install")
            if "Go" in generated:
                self.stdout.write(f"  cd {output_dir}/go && go mod tidy")
            if "Swift" in generated:
                self.stdout.write(f"  Add {output_dir}/swift as local package in Xcode or Package.swift")
        else:
            self.stdout.write(
                colorize("No clients were generated", fg="red", opts=["bold"])
            )

    def _load_custom_router(self, router_path: str):
        """Load a custom MessageRouter from a Python import path.

        Args:
            router_path: Python import path like 'myapp.routers.my_router'

        Returns:
            MessageRouter instance

        Raises:
            CommandError: If router cannot be loaded
        """
        try:
            from importlib import import_module

            module_path, attr_name = router_path.rsplit(".", 1)
            module = import_module(module_path)
            router = getattr(module, attr_name)
            return router
        except (ValueError, ImportError, AttributeError) as e:
            raise CommandError(f"Failed to import router from '{router_path}': {e}")
