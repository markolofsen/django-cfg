"""
PostgreSQL Extension Management Utilities

Provides utilities for managing PostgreSQL extensions during migrations,
including automatic detection and installation of required extensions like pgvector.
"""

from pathlib import Path
from typing import Optional

from django.apps import apps
from django.db import connections


class PostgreSQLExtensionManager:
    """
    Manager for PostgreSQL extensions with automatic detection and installation.
    
    Handles:
    - Detection of required extensions by scanning migrations
    - Installation of extensions (pgvector, pg_trgm, etc.)
    - Helpful error messages when extensions are not available
    
    Usage:
        manager = PostgreSQLExtensionManager(stdout, style, logger)
        manager.ensure_extensions(db_name='default')
    """
    
    def __init__(self, stdout=None, style=None, logger=None):
        """
        Initialize extension manager.
        
        Args:
            stdout: Django command stdout for output
            style: Django command style for colored output
            logger: Logger instance for logging
        """
        self.stdout = stdout
        self.style = style
        self.logger = logger
    
    def ensure_extensions(self, db_name: str):
        """
        Ensure required PostgreSQL extensions are installed.
        
        Automatically detects database type from Django connection settings.
        Works with any Django configuration (django-cfg, settings.py, etc.)
        as connection.settings_dict contains the full database configuration
        from settings.DATABASES[db_name].
        
        Args:
            db_name: Database alias name
            
        Raises:
            SystemExit: If required extension is not available
        """
        try:
            # Get database connection and engine type from Django settings
            # This works because Django has already processed the configuration
            # (whether from django-cfg or settings.py) into connections
            connection = connections[db_name]
            db_engine = connection.settings_dict.get("ENGINE", "")
            
            # Only process PostgreSQL databases
            if "postgresql" not in db_engine.lower():
                return
            
            self._log_info(f"🔌 Checking PostgreSQL extensions for {db_name}...")
            
            # Check if we need pgvector by inspecting migrations
            needs_pgvector = self.check_if_pgvector_needed()
            
            if not needs_pgvector:
                self._log_info("✓ No vector extensions needed")
                return
            
            # Install pgvector extension
            self._install_pgvector(connection)
            
        except Exception as e:
            if "postgresql" in str(e).lower() or "vector" in str(e).lower():
                self._raise_error(f"Failed to setup PostgreSQL extensions: {e}")
            # Silently ignore errors for non-PostgreSQL databases
    
    def _install_pgvector(self, connection):
        """Install pgvector extension on PostgreSQL database."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self._log_success("✅ pgvector extension enabled")
        except Exception as e:
            # Try to provide helpful error message
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                pg_version = self._get_pg_version(connection)
                self._log_warning(
                    f"⚠️  pgvector extension not available. "
                    f"Install it with: apt-get install postgresql-{pg_version}-pgvector"
                )
                self._raise_error(f"pgvector extension required but not installed: {e}")
            else:
                raise
    
    def check_if_pgvector_needed(self) -> bool:
        """
        Check if any migrations require pgvector by scanning for vector field usage.
        
        Returns:
            True if pgvector is needed, False otherwise
        """
        try:
            # Check if pgvector is imported anywhere in the project
            for app_config in apps.get_app_configs():
                migrations_dir = Path(app_config.path) / "migrations"
                if not migrations_dir.exists():
                    continue
                
                # Scan migration files for pgvector usage
                for migration_file in migrations_dir.glob("*.py"):
                    if migration_file.name == "__init__.py":
                        continue
                    
                    try:
                        content = migration_file.read_text()
                        if self._has_vector_field(content):
                            return True
                    except Exception:
                        continue
            
            return False
        except Exception:
            # If we can't check, assume it's not needed
            return False
    
    def _has_vector_field(self, content: str) -> bool:
        """
        Check if migration content contains vector field references.
        
        Args:
            content: Migration file content
            
        Returns:
            True if vector fields are found
        """
        indicators = [
            "pgvector",
            "VectorField",
            "vector(",
            "vector.VectorField",
        ]
        
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in indicators)
    
    def _get_pg_version(self, connection) -> str:
        """
        Get PostgreSQL major version number.
        
        Args:
            connection: Django database connection
            
        Returns:
            Major version string (e.g., "15")
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW server_version;")
                version = cursor.fetchone()[0]
                # Extract major version (e.g., "15.3" -> "15")
                major_version = version.split(".")[0]
                return major_version
        except Exception:
            return "15"  # Default fallback
    
    def _log_info(self, message: str):
        """Log info message."""
        if self.stdout:
            self.stdout.write(f"  {message}")
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message."""
        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(f"  {message}"))
        elif self.stdout:
            self.stdout.write(f"  {message}")
        if self.logger:
            self.logger.info(message)
    
    def _log_warning(self, message: str):
        """Log warning message."""
        if self.stdout and self.style:
            self.stdout.write(self.style.WARNING(f"  {message}"))
        elif self.stdout:
            self.stdout.write(f"  {message}")
        if self.logger:
            self.logger.warning(message)
    
    def _raise_error(self, message: str):
        """Raise error with logging."""
        if self.stdout and self.style:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))
        elif self.stdout:
            self.stdout.write(f"❌ {message}")
        if self.logger:
            self.logger.error(message)
        raise SystemExit(1)


def ensure_postgresql_extensions(db_name: str, stdout=None, style=None, logger=None):
    """
    Convenience function to ensure PostgreSQL extensions are installed.
    
    Args:
        db_name: Database alias name
        stdout: Django command stdout for output
        style: Django command style for colored output
        logger: Logger instance for logging
        
    Example:
        from django_cfg.management.utils.postgresql import ensure_postgresql_extensions
        
        ensure_postgresql_extensions('default', self.stdout, self.style, self.logger)
    """
    manager = PostgreSQLExtensionManager(stdout, style, logger)
    manager.ensure_extensions(db_name)

