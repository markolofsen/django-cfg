"""
Simple Migration Command for Django Config Toolkit
Migrate all databases based on django-cfg configuration.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps

from django_cfg.core.config import get_current_config


class Command(BaseCommand):
    help = "Migrate all databases based on django-cfg configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", 
            action="store_true", 
            help="Show what would be migrated without executing"
        )
        parser.add_argument(
            "--skip-makemigrations",
            action="store_true",
            help="Skip makemigrations step"
        )

    def handle(self, *args, **options):
        """Run migrations for all configured databases."""
        dry_run = options.get("dry_run", False)
        skip_makemigrations = options.get("skip_makemigrations", False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN - No changes will be made"))
        
        self.stdout.write(self.style.SUCCESS("🚀 Migrating all databases..."))

        # Step 1: Create migrations if needed
        if not skip_makemigrations:
            self.stdout.write("📝 Creating migrations...")
            if not dry_run:
                call_command("makemigrations", verbosity=1)
            else:
                self.stdout.write("  Would run: makemigrations")

        # Step 2: Get database configuration
        try:
            config = get_current_config()
            if not config or not hasattr(config, 'databases'):
                self.stdout.write(self.style.ERROR("❌ No django-cfg configuration found"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error loading configuration: {e}"))
            return

        # Step 3: Migrate each database
        for db_name, db_config in config.databases.items():
            self.stdout.write(f"\n🔄 Migrating database: {db_name}")
            
            if hasattr(db_config, 'apps') and db_config.apps:
                # Migrate specific apps for this database
                for app_path in db_config.apps:
                    app_label = self._get_app_label(app_path)
                    if app_label:
                        self.stdout.write(f"  📦 Migrating {app_label}...")
                        if not dry_run:
                            try:
                                call_command("migrate", app_label, database=db_name, verbosity=1)
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"  ⚠️  Warning: {e}"))
                        else:
                            self.stdout.write(f"  Would run: migrate {app_label} --database={db_name}")
            else:
                # Migrate all apps for this database (usually default)
                self.stdout.write(f"  📦 Migrating all apps...")
                if not dry_run:
                    try:
                        call_command("migrate", database=db_name, verbosity=1)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠️  Warning: {e}"))
                else:
                    self.stdout.write(f"  Would run: migrate --database={db_name}")

        # Step 4: Migrate constance if needed
        self.stdout.write(f"\n🔧 Migrating constance...")
        if not dry_run:
            try:
                call_command("migrate", "constance", database="default", verbosity=1)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Constance warning: {e}"))
        else:
            self.stdout.write("  Would run: migrate constance --database=default")

        self.stdout.write(self.style.SUCCESS("\n✅ All migrations completed!"))

    def _get_app_label(self, app_path: str) -> str:
        """Convert full module path to Django app_label."""
        try:
            # Try to get app config by full path first
            try:
                app_config = apps.get_app_config(app_path)
                return app_config.label
            except LookupError:
                pass
            
            # Fallback: extract last part of the path as potential app_label
            potential_label = app_path.split('.')[-1]
            try:
                app_config = apps.get_app_config(potential_label)
                return app_config.label
            except LookupError:
                pass
                
            return app_path
            
        except Exception:
            return app_path
