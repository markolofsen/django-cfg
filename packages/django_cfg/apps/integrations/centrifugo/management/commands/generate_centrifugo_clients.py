"""Django management command to generate Centrifugo WebSocket RPC clients.

Usage:
    python manage.py generate_centrifugo_clients --output ./clients --python --typescript --go
    python manage.py generate_centrifugo_clients -o ./clients --all
    python manage.py generate_centrifugo_clients -o ./clients --python --verbose
"""

import logging
from pathlib import Path
from typing import List

from django.core.management.base import CommandError
from django.utils.termcolors import colorize

from django_cfg.management.utils import AdminCommand

from django_cfg.apps.integrations.centrifugo.codegen.discovery import discover_rpc_methods_from_router
from django_cfg.apps.integrations.centrifugo.codegen.generators.python_thin import PythonThinGenerator
from django_cfg.apps.integrations.centrifugo.codegen.generators.typescript_thin import TypeScriptThinGenerator
from django_cfg.apps.integrations.centrifugo.codegen.generators.go_thin import GoThinGenerator
from django_cfg.apps.integrations.centrifugo.router import get_global_router


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
            required=True,
            help="Output directory for generated clients",
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
            "--all",
            action="store_true",
            help="Generate all clients (Python, TypeScript, Go)",
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
        output_dir = Path(options["output"]).resolve()
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

        if not (generate_python or generate_typescript or generate_go):
            raise CommandError(
                "No client languages specified. Use --python, --typescript, --go, or --all"
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

                generator = TypeScriptThinGenerator(methods, list(models), ts_dir)
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
