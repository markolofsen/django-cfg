#!/usr/bin/env python3
"""
Django Revolution CLI

Interactive command-line interface for Django Revolution API client generator.
"""

import sys
import json
import yaml
import argparse
import logging
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional
from io import StringIO

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from django_revolution.config import get_settings
from django_revolution.openapi.generator import OpenAPIGenerator
from django_revolution.utils import Logger, auto_install_dependencies, check_dependency


console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Django Revolution - Zone-based API Client Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  django-revolution                    # Interactive mode
  django-revolution --generate         # Generate all clients
  django-revolution --zones public private --typescript  # Generate specific zones
  django-revolution --status           # Show status
  django-revolution --list-zones       # List zones
  django-revolution --validate-zones   # Validate zones
  django-revolution --show-urls        # Show URL patterns
  django-revolution --test-schemas     # Test schema generation
        """,
    )

    # Generation options
    parser.add_argument(
        "--generate", "-g", action="store_true", help="Generate API clients"
    )
    parser.add_argument(
        "--zones",
        "-z",
        nargs="*",
        help="Specific zones to generate (default: all zones)",
    )
    parser.add_argument(
        "--typescript",
        "-t",
        action="store_true",
        help="Generate TypeScript clients only",
    )
    parser.add_argument(
        "--python", "-p", action="store_true", help="Generate Python clients only"
    )
    parser.add_argument(
        "--no-typescript", action="store_true", help="Skip TypeScript client generation"
    )
    parser.add_argument(
        "--no-python", action="store_true", help="Skip Python client generation"
    )
    parser.add_argument(
        "--no-archive", action="store_true", help="Skip archiving generated clients"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directories before generation",
    )
    parser.add_argument(
        "--no-multithreading",
        action="store_true",
        help="Disable multithreaded generation",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=20,
        help="Maximum number of worker threads (default: 20)",
    )

    # Information options
    parser.add_argument(
        "--status", action="store_true", help="Show current status and configuration"
    )
    parser.add_argument(
        "--list-zones", action="store_true", help="List all available zones"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate environment and configuration"
    )
    parser.add_argument(
        "--show-urls", action="store_true", help="Show URL patterns for each zone"
    )
    parser.add_argument(
        "--validate-zones",
        action="store_true",
        help="Validate each zone with detailed logging",
    )
    parser.add_argument(
        "--test-schemas",
        action="store_true",
        help="Test schema generation for each zone",
    )

    # Utility options
    parser.add_argument(
        "--install-deps", action="store_true", help="Install required dependencies"
    )
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    try:
        # Setup debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Get configuration
        config = get_settings()

        # Override output directory if provided
        if args.output_dir:
            config.output.base_directory = str(Path(args.output_dir).resolve())

        # Override multithreading settings if provided
        if args.no_multithreading:
            config.enable_multithreading = False
        if args.max_workers:
            config.max_workers = args.max_workers

        # Initialize generator
        generator = OpenAPIGenerator(config)

        # Handle different commands
        if args.status:
            return handle_status(generator)
        elif args.list_zones:
            return handle_list_zones(generator)

        elif args.validate:
            return handle_validate_environment(generator)
        elif args.install_deps:
            return handle_install_dependencies()
        elif args.show_urls:
            return handle_show_urls(generator)
        elif args.validate_zones:
            return handle_validate_zones_detailed(generator)
        elif args.test_schemas:
            return handle_test_schemas(generator)
        elif args.generate or args.zones or args.typescript or args.python:
            return handle_generate(generator, args)
        elif args.interactive:
            return handle_interactive_mode(generator)
        else:
            # Default to interactive mode
            return handle_interactive_mode(generator)

    except Exception as e:
        console.print(f"❌ Error: {e}")
        if args.debug:
            console.print(f"Traceback: {traceback.format_exc()}")
        return 1


def handle_interactive_mode(generator):
    """Run in interactive CLI-like mode."""
    try:
        show_welcome()

        # Main menu
        action = questionary.select(
            "What would you like to do?",
            choices=[
                {"name": "🚀 Generate API Clients", "value": "generate"},
                {"name": "📋 List Zones", "value": "list_zones"},
                {"name": "🔧 Show Configuration", "value": "config"},
                {"name": "📊 Show Status", "value": "status"},
                {"name": "✅ Validate Environment", "value": "validate"},
                {"name": "🔗 Show URLs", "value": "show_urls"},
                {"name": "🧪 Validate Zones", "value": "validate_zones"},
                {"name": "🧪 Test Schemas", "value": "test_schemas"},
                {"name": "📦 Install Dependencies", "value": "install_deps"},
                {"name": "📊 Show Version Info", "value": "version"},
                {"name": "❌ Exit", "value": "exit"},
            ],
        ).ask()

        if action == "generate":
            return handle_generate_interactive(generator)
        elif action == "list_zones":
            return handle_list_zones(generator)
        elif action == "config":
            return handle_config_interactive()
        elif action == "status":
            return handle_status(generator)
        elif action == "validate":
            return handle_validate_environment(generator)
        elif action == "show_urls":
            return handle_show_urls(generator)
        elif action == "validate_zones":
            return handle_validate_zones_detailed(generator)
        elif action == "test_schemas":
            return handle_test_schemas(generator)
        elif action == "install_deps":
            return handle_install_dependencies()
        elif action == "version":
            return handle_version()
        elif action == "exit":
            console.print("👋 Goodbye!")
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        console.print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        console.print(f"❌ Error: {e}")
        return 1


def show_welcome():
    """Show welcome message."""
    welcome_text = """
[bold blue]Django Revolution[/bold blue]
[italic]Zone-based API Client Generator[/italic]

Generate TypeScript and Python clients from your Django REST Framework APIs
organized by zones with automatic OpenAPI schema generation.
    """
    console.print(Panel(welcome_text, title="🎯 Welcome", border_style="blue"))


def handle_generate_interactive(generator):
    """Interactive generation flow."""
    console.print("\n[bold]🚀 API Client Generation[/bold]")

    # Zone selection - use all available zones
    available_zones = list(generator.zone_manager.zones.keys())

    if not available_zones:
        console.print("❌ No zones configured")
        return 1

    # Use all zones by default
    selected_zones = available_zones
    console.print(f"📋 Generating clients for zones: {', '.join(selected_zones)}")

    # Client type selection - use both by default
    client_types = ["typescript", "python"]
    console.print(f"📦 Generating client types: {', '.join(client_types)}")

    # Archive option
    create_archive = questionary.confirm(
        "Create archive of generated clients?", default=True
    ).ask()

    # Multithreading options
    use_multithreading = questionary.confirm(
        "Enable multithreaded generation?",
        default=generator.config.enable_multithreading,
    ).ask()

    max_workers = generator.config.max_workers
    if use_multithreading:
        max_workers = questionary.text(
            f"Maximum number of worker threads (current: {generator.config.max_workers}):",
            default=str(generator.config.max_workers),
        ).ask()
        try:
            max_workers = int(max_workers)
        except ValueError:
            max_workers = generator.config.max_workers

    # Verbose mode
    verbose = questionary.confirm("Enable verbose logging?", default=False).ask()

    # Confirm generation
    summary_text = f"""
[bold]Generation Summary:[/bold]
• Zones: {', '.join(selected_zones)}
• Clients: {', '.join(client_types)}
• Archive: {'Yes' if create_archive else 'No'}
• Multithreading: {'Yes' if use_multithreading else 'No'}
• Max Workers: {max_workers if use_multithreading else 'N/A'}
• Verbose: {'Yes' if verbose else 'No'}
    """
    console.print(Panel(summary_text, title="📋 Summary", border_style="green"))

    proceed = questionary.confirm("Proceed with generation?", default=True).ask()
    if not proceed:
        console.print("❌ Generation cancelled.")
        return 0

    # Configure generator
    generator.config.generators.typescript.enabled = "typescript" in client_types
    generator.config.generators.python.enabled = "python" in client_types
    generator.config.enable_multithreading = use_multithreading
    generator.config.max_workers = max_workers

    # Generate with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating API clients...", total=None)

        try:
            summary = generator.generate_all(
                zones=selected_zones, archive=create_archive
            )
            progress.update(task, description="✅ Generation completed!")

            # Show results
            show_generation_results(summary)
            return 0

        except Exception as e:
            progress.update(task, description="❌ Generation failed!")
            console.print(f"Error: {e}")
            return 1


def handle_generate(generator, args):
    """Handle generation with command line arguments."""
    # Determine what to generate
    generate_typescript = not args.no_typescript and (
        args.typescript or not args.python
    )
    generate_python = not args.no_python and (args.python or not args.typescript)

    if not generate_typescript and not generate_python:
        console.print(
            "❌ Nothing to generate. Both TypeScript and Python generation are disabled."
        )
        return 1

    # Configure generator
    generator.config.generators.typescript.enabled = generate_typescript
    generator.config.generators.python.enabled = generate_python

    # Clean if requested
    if args.clean:
        console.print("🧹 Cleaning output directories...")
        success = generator.clean_output()
        if not success:
            console.print("⚠️  Failed to clean output directories")

    # Generate
    zones = args.zones
    archive = not args.no_archive

    console.print("🚀 Starting generation...")
    summary = generator.generate_all(zones=zones, archive=archive)

    # Display results
    show_generation_results(summary)
    return 0


def show_generation_results(summary):
    """Display generation results in a nice table."""
    table = Table(title="📊 Generation Results")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Zones Processed", str(summary.total_zones))
    table.add_row("Duration", f"{summary.duration_seconds:.1f}s")
    table.add_row("Total Files", str(summary.total_files_generated))

    # TypeScript results
    if summary.typescript_results:
        successful_ts = sum(1 for r in summary.typescript_results.values() if r.success)
        failed_ts = len(summary.typescript_results) - successful_ts
        table.add_row(
            "TypeScript Clients", f"{successful_ts} successful, {failed_ts} failed"
        )

    # Python results
    if summary.python_results:
        successful_py = sum(1 for r in summary.python_results.values() if r.success)
        failed_py = len(summary.python_results) - successful_py
        table.add_row(
            "Python Clients", f"{successful_py} successful, {failed_py} failed"
        )

    console.print(table)

    # Show detailed results
    if summary.typescript_results:
        console.print("\n[bold]TypeScript Results:[/bold]")
        for zone_name, result in summary.typescript_results.items():
            status = "✅" if result.success else "❌"
            console.print(f"  {status} {zone_name}: {result.files_generated} files")
            if not result.success and result.error_message:
                console.print(f"    Error: {result.error_message}")

    if summary.python_results:
        console.print("\n[bold]Python Results:[/bold]")
        for zone_name, result in summary.python_results.items():
            status = "✅" if result.success else "❌"
            console.print(f"  {status} {zone_name}: {result.files_generated} files")
            if not result.success and result.error_message:
                console.print(f"    Error: {result.error_message}")


def handle_status(generator):
    """Show current status and configuration."""
    console.print(
        Panel("Django Revolution Status", title="📊 Status", border_style="blue")
    )
    console.print("=" * 50)

    status = generator.get_status()

    # Basic info
    console.print(f"Zones detected: {status['zones_detected']}")
    console.print(f"Output directory: {status['output_dir']}")
    console.print(f"TypeScript available: {status['typescript_available']}")
    console.print(f"Python available: {status['python_available']}")
    # Multithreading info
    multithreading = status.get("multithreading", {})
    console.print(f"Multithreading enabled: {multithreading.get('enabled', False)}")
    console.print(f"Max workers: {multithreading.get('max_workers', 20)}")

    # Zone details
    if status["zones"]:
        console.print("\n[bold]Configured Zones:[/bold]")
        for zone_name, zone_info in status["zones"].items():
            apps = ", ".join(zone_info.get("apps", []))
            console.print(f"  📦 {zone_name}: {apps}")

    # Configuration details
    config = status.get("config", {})
    if config:
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"  API Prefix: {config.get('api_prefix', 'apix')}")
        console.print(f"  Debug Mode: {config.get('debug', False)}")
        console.print(
            f"  Auto Install Dependencies: {config.get('auto_install_deps', True)}"
        )

    console.print("\n" + "=" * 50)
    return 0


def handle_list_zones(generator):
    """List all available zones."""
    zones = generator.zone_manager.zones

    if not zones:
        console.print("⚠️  No zones configured")
        return 0

    console.print(Panel("Available Zones", title="📋 Zones", border_style="green"))
    console.print("=" * 50)

    for zone_name, zone in zones.items():
        console.print(f"\n[bold]{zone_name}:[/bold]")
        console.print(f"  Title: {zone.title}")
        console.print(f"  Apps: {', '.join(zone.apps)}")
        console.print(f"  Public: {zone.public}")
        console.print(f"  Auth Required: {zone.auth_required}")
        if zone.description:
            console.print(f"  Description: {zone.description}")

    return 0


def handle_validate_environment(generator):
    """Validate environment and dependencies."""
    console.print(
        Panel("Validating Environment", title="✅ Validation", border_style="yellow")
    )
    console.print("=" * 50)

    # Basic validation
    is_valid = generator.validate_environment()

    if is_valid:
        console.print("✅ Environment validation passed")
    else:
        console.print("❌ Environment validation failed")

    # Check dependencies
    deps = [
        ("TypeScript Generator", ["npx", "@hey-api/openapi-ts", "--version"]),
        ("Python Generator", ["datamodel-codegen", "--version"]),
        ("Django", ["python", "-c", "import django; print(django.VERSION)"]),
    ]

    console.print("\n[bold]Dependency Check:[/bold]")
    for name, cmd in deps:
        available = check_dependency(cmd)
        status = "✅" if available else "❌"
        console.print(f"  {status} {name}")

    return 0


def handle_install_dependencies():
    """Install required dependencies."""
    console.print(
        Panel("Installing Dependencies", title="📦 Dependencies", border_style="cyan")
    )
    console.print("=" * 50)

    success = auto_install_dependencies()

    if success:
        console.print("✅ All dependencies installed")
    else:
        console.print("❌ Some dependencies failed to install")

    return 0


def handle_show_urls(generator):
    """Show URL patterns for each zone."""
    console.print(Panel("Zone URL Patterns", title="🔗 URLs", border_style="magenta"))
    console.print("=" * 50)

    zones = generator.zone_manager.zones
    if not zones:
        console.print("⚠️  No zones configured")
        return 0

    for zone_name, zone in zones.items():
        console.print(f"\n[bold]{zone_name.upper()} ZONE:[/bold]")
        console.print(f"  Title: {zone.title}")
        console.print(f"  Apps: {', '.join(zone.apps)}")
        console.print(f"  Public: {zone.public}")
        console.print(f"  Auth Required: {zone.auth_required}")

        # Show app URL patterns
        try:
            app_patterns = generator.zone_manager.get_app_urls(zone.apps)
            if app_patterns:
                console.print("  [bold]App URLs:[/bold]")
                for pattern in app_patterns:
                    console.print(f"    • {pattern.pattern}")
        except Exception as e:
            console.print(f"  ❌ App URLs: {e}")

        # Show schema URL patterns
        try:
            schema_patterns = generator.zone_manager.create_zone_schema_patterns(
                zone_name, zone
            )
            if schema_patterns:
                console.print("  [bold]Schema URLs:[/bold]")
                for pattern in schema_patterns:
                    console.print(f"    • {pattern.pattern} -> {pattern.name}")
        except Exception as e:
            console.print(f"  ❌ Schema URLs: {e}")

    return 0


def handle_validate_zones_detailed(generator):
    """Validate each zone with detailed logging."""
    console.print(
        Panel("Detailed Zone Validation", title="🧪 Validation", border_style="red")
    )
    console.print("=" * 50)

    zones = generator.zone_manager.zones
    if not zones:
        console.print("⚠️  No zones configured")
        return 0

    total_valid = 0
    total_invalid = 0

    for zone_name, zone in zones.items():
        console.print(f"\n🔍 Validating zone: {zone_name}")
        console.print("-" * 30)

        zone_valid = True

        # Check zone configuration
        console.print(f"  ✅ Zone configuration: {zone.title}")

        # Check apps
        console.print(f"  Apps ({len(zone.apps)}):")
        for app in zone.apps:
            try:
                from django.apps import apps

                if apps.is_installed(app):
                    console.print(f"    ✅ {app}")
                else:
                    console.print(f"    ❌ {app} (not installed)")
                    zone_valid = False
            except Exception as e:
                console.print(f"    ❌ {app} (error: {e})")
                zone_valid = False

        # Check URL patterns
        try:
            app_patterns = generator.zone_manager.get_app_urls(zone.apps)
            console.print(f"  ✅ URL patterns: {len(app_patterns)} patterns")
        except Exception as e:
            console.print(f"  ❌ URL patterns: {e}")
            zone_valid = False

        # Check schema patterns
        try:
            schema_patterns = generator.zone_manager.create_zone_schema_patterns(
                zone_name, zone
            )
            console.print(f"  ✅ Schema patterns: {len(schema_patterns)} patterns")
        except Exception as e:
            console.print(f"  ❌ Schema patterns: {e}")
            zone_valid = False

        # Summary for this zone
        if zone_valid:
            console.print(f"  ✅ Zone '{zone_name}' is valid")
            total_valid += 1
        else:
            console.print(f"  ❌ Zone '{zone_name}' has issues")
            total_invalid += 1

    # Overall summary
    console.print(f"\n📊 Validation Summary:")
    console.print(f"  Valid zones: {total_valid}")
    console.print(f"  Invalid zones: {total_invalid}")

    if total_invalid == 0:
        console.print("🎉 All zones are valid!")
    else:
        console.print(f"⚠️  {total_invalid} zones have issues")

    return 0


def handle_test_schemas(generator):
    """Test schema generation for each zone."""
    console.print(
        Panel("Testing Schema Generation", title="🧪 Schema Tests", border_style="blue")
    )
    console.print("=" * 50)

    zones = generator.zone_manager.zones
    if not zones:
        console.print("⚠️  No zones configured")
        return 0

    total_success = 0
    total_failed = 0

    for zone_name, zone in zones.items():
        console.print(f"\n🧪 Testing schema generation for: {zone_name}")
        console.print("-" * 40)

        try:
            # Test dynamic module creation
            module = generator.zone_manager.create_dynamic_urlconf_module(
                zone_name, zone
            )
            if module:
                console.print(f"  ✅ Dynamic module created: {module.__name__}")
                console.print(f"  ✅ URL patterns: {len(module.urlpatterns)}")
            else:
                console.print("  ❌ Failed to create dynamic module")
                total_failed += 1
                continue

            # Test schema generation
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
                schema_file = Path(tmp_file.name)

            try:
                # Generate schema using drf-spectacular
                from django.core.management import call_command

                out = StringIO()
                call_command(
                    "spectacular",
                    "--file",
                    str(schema_file),
                    "--api-version",
                    zone.version,
                    "--urlconf",
                    module.__name__,
                    stdout=out,
                    stderr=out,
                )

                if schema_file.exists() and schema_file.stat().st_size > 0:
                    console.print(
                        f"  ✅ Schema generated: {schema_file.stat().st_size} bytes"
                    )
                    total_success += 1
                else:
                    console.print("  ❌ Schema generation failed")
                    total_failed += 1

            except Exception as e:
                console.print(f"  ❌ Schema generation error: {e}")
                total_failed += 1
            finally:
                # Cleanup
                if schema_file.exists():
                    schema_file.unlink()

        except Exception as e:
            console.print(f"  ❌ Zone test failed: {e}")
            total_failed += 1

    # Summary
    console.print(f"\n📊 Schema Test Summary:")
    console.print(f"  Successful: {total_success}")
    console.print(f"  Failed: {total_failed}")

    if total_failed == 0:
        console.print("🎉 All schema tests passed!")
    else:
        console.print(f"⚠️  {total_failed} schema tests failed")

    return 0


def handle_config_interactive():
    """Interactive configuration display."""
    console.print(Panel("Configuration", title="🔧 Config", border_style="green"))
    console.print("=" * 50)

    config = get_settings()

    # Format selection
    format_choice = questionary.select(
        "Select output format:",
        choices=[
            {"name": "Pretty (Rich)", "value": "pretty"},
            {"name": "JSON", "value": "json"},
            {"name": "YAML", "value": "yaml"},
        ],
    ).ask()

    if format_choice == "pretty":
        show_config_pretty(config)
    elif format_choice == "json":
        console.print(json.dumps(config.model_dump(), indent=2))
    elif format_choice == "yaml":
        console.print(yaml.dump(config.model_dump(), default_flow_style=False))

    return 0


def show_config_pretty(config):
    """Display configuration in a pretty format."""
    table = Table(title="🔧 Django Revolution Configuration")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Base URL", config.base_url)
    table.add_row("Output Directory", str(config.output.base_directory))
    table.add_row("Zones", ", ".join(config.zones.keys()))
    table.add_row("TypeScript", "✅" if config.generators.typescript.enabled else "❌")
    table.add_row("Python", "✅" if config.generators.python.enabled else "❌")
    table.add_row("Archive", "✅" if config.output.archive.enabled else "❌")

    console.print(table)


def handle_version():
    """Show version information."""
    from django_revolution import __version__, __author__, __description__

    version_text = f"""
[bold blue]Django Revolution[/bold blue]
Version: [green]{__version__}[/green]
Author: [yellow]{__author__}[/yellow]
Description: [italic]{__description__}[/italic]
    """

    console.print(Panel(version_text, title="📦 Version Info", border_style="blue"))
    return 0





if __name__ == "__main__":
    sys.exit(main())
