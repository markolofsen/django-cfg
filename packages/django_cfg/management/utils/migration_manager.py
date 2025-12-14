"""
Migration Management Utilities

Provides centralized migration logic for Django commands.
Commands should use these utilities instead of implementing migration logic directly.
"""

from pathlib import Path
from typing import List, Optional, Set

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder

from .postgresql import ensure_postgresql_extensions

# Default Django apps to exclude from migrations
DEFAULT_APPS = {
    'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
    'staticfiles', 'sites', 'postgres', 'mysql', 'sqlite3', 'oracle'
}


class MigrationManager:
    """
    Centralized migration management for Django commands.
    
    Handles:
    - Creating migrations
    - Migrating databases
    - Managing database routing
    - PostgreSQL extensions
    - App discovery
    
    Usage:
        manager = MigrationManager(stdout, style, logger)
        manager.migrate_database('default')
    """
    
    def __init__(self, stdout=None, style=None, logger=None):
        """
        Initialize migration manager.
        
        Args:
            stdout: Django command stdout for output
            style: Django command style for colored output
            logger: Logger instance for logging
        """
        self.stdout = stdout
        self.style = style
        self.logger = logger
    
    def create_migrations(self):
        """Create migrations for all apps"""
        self._log_info("📝 Creating migrations...")
        
        try:
            # First try global makemigrations
            call_command("makemigrations", verbosity=1)
            
            # Then try for each app that has models but no migrations
            all_apps = self.get_all_installed_apps()
            for app in all_apps:
                if self.app_has_models(app) and not self.app_has_migrations(app):
                    try:
                        self._log_info(f"  📝 Creating migrations for {app}...")
                        call_command("makemigrations", app, verbosity=1)
                    except Exception as e:
                        self._log_warning(f"  ⚠️  Could not create migrations for {app}: {e}")
            
            self._log_success("✅ Migrations created")
        except Exception as e:
            self._log_warning(f"⚠️  Warning creating migrations: {e}")
    
    def migrate_database(self, db_name: str):
        """
        Migrate specific database.
        
        Args:
            db_name: Database alias name
        """
        try:
            self._log_info(f"🔄 Migrating {db_name}...")
            
            # Install required PostgreSQL extensions before migrations
            ensure_postgresql_extensions(db_name, self.stdout, self.style, self.logger)
            
            # Get apps for this database
            apps_list = self.get_apps_for_database(db_name)
            
            # Debug info
            self._log_info(f"  📋 Apps for {db_name}: {apps_list}")
            
            if not apps_list:
                self._log_warning(f"  ⚠️  No apps configured for {db_name}")
                return
            
            # Create migrations for all apps
            self.create_migrations()
            
            # Migrate each app
            for app in apps_list:
                try:
                    # Skip apps without migrations
                    if not self.app_has_migrations(app):
                        continue
                    
                    self._log_info(f"  📦 Migrating {app}...")
                    call_command("migrate", app, database=db_name, verbosity=1)
                except Exception as e:
                    self._raise_error(f"Migration failed for {app} on {db_name}: {e}")
            
            self._log_success(f"✅ {db_name} migration completed!")
            
        except Exception as e:
            self._raise_error(f"Error migrating {db_name}: {e}")
    
    def migrate_all_databases(self):
        """Migrate all configured databases"""
        self._log_success("🔄 Starting full migration...")
        
        # First migrate default database
        self._log_info("📊 Migrating default database...")
        self.migrate_database("default")
        
        # Then migrate other databases (excluding default)
        databases = self.get_all_database_names()
        for db_name in databases:
            if db_name != "default":
                self._log_info(f"🔄 Migrating {db_name}...")
                self.migrate_database(db_name)
        
        self._log_success("✅ Full migration completed!")
    
    def migrate_constance_if_needed(self):
        """Always migrate constance app if it's installed"""
        try:
            # Check if constance is in INSTALLED_APPS
            if 'constance' in settings.INSTALLED_APPS:
                self._log_success("🔧 Migrating constance (django-cfg requirement)...")
                
                # Try to migrate constance on default database
                try:
                    call_command("migrate", "constance", database="default", verbosity=1)
                    self._log_success("✅ Constance migration completed!")
                except Exception as e:
                    self._raise_error(f"Constance migration failed: {e}")
            else:
                self._log_warning("⚠️  Constance not found in INSTALLED_APPS")
        
        except Exception as e:
            self._raise_error(f"Could not migrate constance: {e}")
    
    def get_apps_for_database(self, db_name: str) -> List[str]:
        """
        Get apps for specific database with smart logic for default.
        
        Args:
            db_name: Database alias name
            
        Returns:
            List of app labels
        """
        if db_name == "default":
            # For default database, get all apps that are not in other databases
            all_apps = self.get_all_installed_apps()
            apps_in_other_dbs = self.get_apps_in_other_databases()
            return [app for app in all_apps if app not in apps_in_other_dbs]
        else:
            # For other databases, use configured apps from routing rules
            routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
            return [app for app, db in routing_rules.items() if db == db_name]
    
    def get_all_installed_apps(self) -> List[str]:
        """Get all installed Django apps by checking for apps.py files."""
        apps_list = []
        
        # Get all Django app configs
        for app_config in apps.get_app_configs():
            app_label = app_config.label
            app_path = Path(app_config.path)
            
            # Check if apps.py exists in the app directory
            apps_py_path = app_path / "apps.py"
            if apps_py_path.exists():
                if app_label not in DEFAULT_APPS:
                    apps_list.append(app_label)
                continue
            
            # Fallback: check if it's a standard Django app (has models.py or admin.py)
            if (app_path / "models.py").exists() or (app_path / "admin.py").exists():
                apps_list.append(app_label)
        
        return apps_list
    
    def get_apps_in_other_databases(self) -> Set[str]:
        """Get all apps that are configured for non-default databases."""
        routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
        return set(routing_rules.keys())
    
    def get_all_database_names(self) -> List[str]:
        """Get all database names."""
        return list(connections.databases.keys())
    
    def get_database_info(self) -> dict:
        """Get database information from Django settings"""
        try:
            db_info = {}
            
            # Get database info from Django settings
            for db_name, db_config in settings.DATABASES.items():
                db_info[db_name] = {
                    "name": db_config.get("NAME", "unknown"),
                    "engine": db_config.get("ENGINE", "unknown"),
                    "host": db_config.get("HOST", ""),
                    "port": db_config.get("PORT", ""),
                    "apps": []  # Will be populated by routing logic
                }
            
            return db_info
            
        except Exception as e:
            self._log_warning(f"⚠️  Error getting database info: {e}")
            return {}
    
    def app_has_migrations(self, app_label: str) -> bool:
        """Simple check if an app has migrations."""
        try:
            # Get the app config
            app_config = apps.get_app_config(app_label)
            if not app_config:
                return False
            
            # Check if migrations directory exists and has files
            migrations_dir = Path(app_config.path) / "migrations"
            if not migrations_dir.exists():
                return False
            
            # Check if there are any migration files (excluding __init__.py)
            migration_files = [f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"]
            
            # Also check if there are any applied migrations in the database
            # Check all databases for this app's migrations
            for db_name in connections.databases.keys():
                try:
                    recorder = MigrationRecorder(connections[db_name])
                    applied_migrations = recorder.migration_qs.filter(app=app_label)
                    if applied_migrations.exists():
                        return True
                except Exception:
                    continue
            
            # If no applied migrations found, check if there are migration files
            return len(migration_files) > 0
            
        except Exception:
            # Silently return False for apps that don't exist or have issues
            return False
    
    def app_has_models(self, app_label: str) -> bool:
        """Check if an app has models defined."""
        try:
            # Get the app config
            app_config = apps.get_app_config(app_label)
            if not app_config:
                return False
            
            # Check if models.py exists and has content
            models_file = Path(app_config.path) / "models.py"
            if models_file.exists():
                # Read the file and check if it has model definitions
                content = models_file.read_text()
                # Simple check for model definitions
                if "class " in content and "models.Model" in content:
                    return True
            
            # Also check if the app has any registered models
            models = app_config.get_models()
            return len(models) > 0
            
        except Exception:
            # Silently return False for apps that don't exist or have issues
            return False
    
    def check_database_connection(self, db_name: str) -> bool:
        """
        Check if database connection is working.

        Args:
            db_name: Database alias name

        Returns:
            True if connection is OK, False otherwise
        """
        try:
            with connections[db_name].cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self._log_error(f"  ❌ Connection: FAILED - {e}")
            return False

    def migrate_test_database(self, db_name: str, auto_fix: bool = True):
        """
        Migrate test database with automatic error fixing.

        Automatically fixes:
        - Inconsistent migration history
        - Missing extensions
        - Dependency order issues

        Args:
            db_name: Database alias name
            auto_fix: Automatically fix migration errors (default: True)
        """
        try:
            self._log_info(f"🧪 Migrating test database {db_name}...")

            # Step 1: Install extensions first
            ensure_postgresql_extensions(db_name, self.stdout, self.style, self.logger)

            # Step 2: Check for inconsistent migrations
            has_issues = self.check_migration_consistency(db_name)

            if has_issues and auto_fix:
                self._log_warning(f"⚠️  Inconsistent migrations detected, auto-fixing...")
                self.fix_inconsistent_migrations(db_name)

            # Step 3: Run migrations with bypass
            self._migrate_with_bypass(db_name)

            self._log_success(f"✅ Test database {db_name} migrated successfully!")

        except Exception as e:
            if auto_fix:
                self._log_warning(f"⚠️  Migration failed, attempting auto-fix: {e}")
                try:
                    self.fix_inconsistent_migrations(db_name)
                    self._migrate_with_bypass(db_name)
                    self._log_success(f"✅ Auto-fix successful!")
                except Exception as fix_error:
                    self._raise_error(f"Auto-fix failed: {fix_error}")
            else:
                self._raise_error(f"Migration failed: {e}")

    def check_migration_consistency(self, db_name: str) -> bool:
        """
        Check if migrations are consistent.

        Args:
            db_name: Database alias name

        Returns:
            True if issues found, False if consistent
        """
        try:
            from django.db.migrations.loader import MigrationLoader

            connection = connections[db_name]
            loader = MigrationLoader(connection)

            try:
                loader.check_consistent_history(connection)
                return False  # No issues
            except Exception as e:
                if 'InconsistentMigrationHistory' in str(type(e).__name__):
                    self._log_warning(f"⚠️  Found inconsistent migrations: {e}")
                    return True
                raise

        except Exception as e:
            self._log_warning(f"⚠️  Could not check consistency: {e}")
            return False

    def fix_inconsistent_migrations(self, db_name: str):
        """
        Automatically fix inconsistent migration history.

        Fixes:
        - Removes problematic migration records
        - Reapplies migrations in correct order
        - Handles swappable dependency issues

        Args:
            db_name: Database alias name
        """
        try:
            self._log_info(f"🔧 Fixing inconsistent migrations for {db_name}...")

            connection = connections[db_name]
            recorder = MigrationRecorder(connection)

            # Get all applied migrations
            applied = recorder.migration_qs.all().values_list('app', 'name', 'id')
            applied_list = list(applied)

            if not applied_list:
                self._log_info("  No migrations to fix")
                return

            # Find problematic migrations (admin before django_cfg_accounts)
            admin_migrations = [m for m in applied_list if m[0] == 'admin']
            auth_migrations = [m for m in applied_list if m[0] == 'django_cfg_accounts']

            if admin_migrations and auth_migrations:
                admin_min_id = min(m[2] for m in admin_migrations)
                auth_min_id = min(m[2] for m in auth_migrations)

                if admin_min_id < auth_min_id:
                    self._log_warning(f"  ⚠️  Detected: admin migrations before django_cfg_accounts")
                    self._log_info(f"  🔧 Removing admin migration records...")

                    # Remove admin migration records
                    recorder.migration_qs.filter(app='admin').delete()

                    self._log_success(f"  ✅ Removed problematic admin migrations")
                    self._log_info(f"  ℹ️  Will be reapplied in correct order during migration")

        except Exception as e:
            self._log_error(f"  ❌ Could not fix migrations: {e}")
            raise

    def _migrate_with_bypass(self, db_name: str):
        """
        Run migrations with consistency check bypass.

        Args:
            db_name: Database alias name
        """
        from django.db.migrations import loader as migrations_loader

        original_check = migrations_loader.MigrationLoader.check_consistent_history

        def patched_check(self, connection):
            """Bypass consistency check."""
            try:
                return original_check(self, connection)
            except Exception as e:
                if 'InconsistentMigrationHistory' in str(type(e).__name__):
                    # Log but don't fail
                    if self.stdout:
                        self.stdout.write(f"⚠️  Bypassed: {e}")
                    return
                raise

        # Temporarily patch
        migrations_loader.MigrationLoader.check_consistent_history = patched_check

        try:
            # Run migrations
            call_command("migrate", database=db_name, verbosity=1)
        finally:
            # Restore original
            migrations_loader.MigrationLoader.check_consistent_history = original_check
    
    def _log_info(self, message: str):
        """Log info message."""
        if self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message."""
        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.info(message)
    
    def _log_warning(self, message: str):
        """Log warning message."""
        if self.stdout and self.style:
            self.stdout.write(self.style.WARNING(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.warning(message)
    
    def _log_error(self, message: str):
        """Log error message."""
        if self.stdout and self.style:
            self.stdout.write(self.style.ERROR(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.error(message)
    
    def _raise_error(self, message: str):
        """Raise error with logging."""
        if self.stdout and self.style:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))
        elif self.stdout:
            self.stdout.write(f"❌ {message}")
        if self.logger:
            self.logger.error(message)
        # Note: Not raising SystemExit here to allow caller to decide
        raise Exception(message)

