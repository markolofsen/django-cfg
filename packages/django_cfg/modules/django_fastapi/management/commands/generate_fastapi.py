"""
Django management command for FastAPI ORM generation.

Usage:
    python manage.py generate_fastapi [apps...]
    python manage.py generate_fastapi --output-dir=fastapi/
    python manage.py generate_fastapi users products --no-crud --dry-run
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Generate FastAPI ORM code from Django models.

    Creates SQLModel models, Pydantic schemas, and async CRUD repositories.
    """

    help = "Generate FastAPI ORM models from Django models"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Positional: apps to process
        parser.add_argument(
            "apps",
            nargs="*",
            help="Apps to generate (default: all apps)",
        )

        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output-dir", "-o",
            default="fastapi_orm/",
            help="Output directory for generated files (default: fastapi_orm/)",
        )
        output_group.add_argument(
            "--format", "-f",
            choices=["sqlmodel", "pydantic", "sqlalchemy"],
            default="sqlmodel",
            help="ORM format to generate (default: sqlmodel)",
        )

        # Generation options
        gen_group = parser.add_argument_group("Generation Options")
        gen_group.add_argument(
            "--no-crud",
            action="store_true",
            help="Skip CRUD repository generation",
        )
        gen_group.add_argument(
            "--no-schemas",
            action="store_true",
            help="Skip Pydantic schema generation",
        )
        gen_group.add_argument(
            "--no-database-config",
            action="store_true",
            help="Skip database.py generation",
        )
        gen_group.add_argument(
            "--include-alembic",
            action="store_true",
            help="Generate Alembic migration configuration",
        )
        gen_group.add_argument(
            "--sync-mode",
            action="store_true",
            help="Generate sync code instead of async",
        )

        # PostgreSQL options
        pg_group = parser.add_argument_group("PostgreSQL Options")
        pg_group.add_argument(
            "--no-jsonb",
            action="store_true",
            help="Use JSON instead of JSONB for JSONField",
        )
        pg_group.add_argument(
            "--no-array",
            action="store_true",
            help="Don't use native ARRAY types",
        )

        # Exclusion options
        exclude_group = parser.add_argument_group("Exclusion Options")
        exclude_group.add_argument(
            "--exclude-apps",
            nargs="*",
            default=[],
            help="Apps to exclude from generation",
        )
        exclude_group.add_argument(
            "--exclude-models",
            nargs="*",
            default=[],
            help="Models to exclude (format: app.Model)",
        )

        # Execution options
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be generated without writing files",
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Verbose output",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        from django_cfg.modules.django_fastapi.config import FastAPIConfig
        from django_cfg.modules.django_fastapi.core.orchestrator import FastAPIOrchestrator

        # Build configuration
        config = FastAPIConfig(
            enabled=True,
            output_dir=options["output_dir"],
            format=options["format"],
            include_crud=not options["no_crud"],
            include_schemas=not options["no_schemas"],
            include_database_config=not options["no_database_config"],
            include_alembic=options["include_alembic"],
            async_mode=not options["sync_mode"],
            apps=options["apps"] or [],
            exclude_apps=list(set(
                FastAPIConfig.model_fields["exclude_apps"].default_factory()
                + options["exclude_apps"]
            )),
            exclude_models=options["exclude_models"],
            use_jsonb=not options["no_jsonb"],
            use_array_fields=not options["no_array"],
        )

        # Create orchestrator
        orchestrator = FastAPIOrchestrator(
            config=config,
            dry_run=options["dry_run"],
        )

        # Run generation
        self.stdout.write(
            self.style.HTTP_INFO("Starting FastAPI ORM generation...")
        )

        try:
            result = orchestrator.generate(apps=options["apps"] or None)
        except Exception as e:
            raise CommandError(f"Generation failed: {e}")

        # Handle errors
        if result.errors:
            for error in result.errors:
                self.stdout.write(self.style.ERROR(f"Error: {error}"))
            raise CommandError("Generation completed with errors")

        # Handle warnings
        for warning in result.warnings:
            self.stdout.write(self.style.WARNING(f"Warning: {warning}"))

        # Display results
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No files written"))
            self.stdout.write("\nWould generate:")
        else:
            self.stdout.write("\nGenerated files:")

        # Group files by app
        files_by_app: dict[str, list] = {}
        for file in result.files:
            parts = file.path.parts
            if len(parts) > 1:
                app = parts[-2] if parts[-1].endswith(".py") else str(file.path)
            else:
                app = "root"
            if app not in files_by_app:
                files_by_app[app] = []
            files_by_app[app].append(file)

        for app, files in sorted(files_by_app.items()):
            self.stdout.write(f"\n  {app}/")
            for file in files:
                status = "would create" if options["dry_run"] else "created"
                if options["verbose"]:
                    self.stdout.write(f"    - {file.path.name} ({status})")
                else:
                    self.stdout.write(f"    - {file.path.name}")

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Generated {result.files_count} files for {result.models_count} models"
        ))
        self.stdout.write(f"Output directory: {config.output_dir}")
