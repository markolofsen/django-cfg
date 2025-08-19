#!/usr/bin/env python3
"""
Auto-generate Django Revolution clients
Simple command to generate TypeScript and Python clients
"""

import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand

# Django Revolution
from django_revolution.openapi.generator import OpenAPIGenerator


class Command(BaseCommand):
    help = "Generate Django Revolution clients (TypeScript and Python)"

    def add_arguments(self, parser):
        parser.add_argument("--zones", nargs="*", help="Specific zones to generate (default: all zones)")
        parser.add_argument(
            "--typescript-only",
            action="store_true",
            help="Generate TypeScript clients only",
        )
        parser.add_argument("--python-only", action="store_true", help="Generate Python clients only")
        parser.add_argument("--no-archive", action="store_true", help="Skip archiving generated clients")
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean output directories before generation",
        )

    def handle(self, *args, **options):
        zones = options["zones"]
        typescript_only = options["typescript_only"]
        python_only = options["python_only"]
        no_archive = options["no_archive"]
        clean = options["clean"]

        self.stdout.write(self.style.SUCCESS("🚀 Starting Django Revolution client generation..."))

        if zones:
            self.stdout.write(f"📁 Generating zones: {', '.join(zones)}")
        else:
            self.stdout.write("📁 Generating all zones")

        if typescript_only:
            self.stdout.write("🔷 TypeScript clients only")
        elif python_only:
            self.stdout.write("🐍 Python clients only")
        else:
            self.stdout.write("🔷🐍 TypeScript and Python clients")

        try:
            # Initialize generator
            generator = OpenAPIGenerator()

            # Configure generators
            if typescript_only:
                generator.config.generators.typescript.enabled = True
                generator.config.generators.python.enabled = False
            elif python_only:
                generator.config.generators.typescript.enabled = False
                generator.config.generators.python.enabled = True

            # Clean if requested
            if clean:
                self.stdout.write("🧹 Cleaning output directories...")
                success = generator.clean_output()
                if not success:
                    self.stdout.write(self.style.WARNING("⚠️  Failed to clean output directories"))

            # Generate clients
            archive = not no_archive
            summary = generator.generate_all(zones=zones, archive=archive)

            # Display results
            self.stdout.write(self.style.SUCCESS("✅ Generation completed!"))
            self.stdout.write(f"📊 Generated {summary.total_files_generated} files in {summary.duration_seconds:.1f}s")
            self.stdout.write(f"🎯 Processed {summary.total_zones} zones")

            # Show detailed results
            if summary.typescript_results:
                self.stdout.write("\n🔷 TypeScript Results:")
                for zone_name, result in summary.typescript_results.items():
                    status = "✅" if result.success else "❌"
                    self.stdout.write(f"  {status} {zone_name}: {result.files_generated} files")
                    if not result.success and result.error_message:
                        self.stdout.write(f"    Error: {result.error_message}")

            if summary.python_results:
                self.stdout.write("\n🐍 Python Results:")
                for zone_name, result in summary.python_results.items():
                    status = "✅" if result.success else "❌"
                    self.stdout.write(f"  {status} {zone_name}: {result.files_generated} files")
                    if not result.success and result.error_message:
                        self.stdout.write(f"    Error: {result.error_message}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error generating clients: {e}"))
            raise
