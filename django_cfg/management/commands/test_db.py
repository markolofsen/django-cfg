"""
Django management command for test database management.

Usage:
    python manage.py test_db cleanup                    # Remove all test databases
    python manage.py test_db info                       # Show test database info
    python manage.py test_db reset                      # Reset specific test database
    python manage.py test_db check-extensions           # Check PostgreSQL extensions
"""

import json
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from django_cfg.management.utils.postgresql import PostgreSQLExtensionManager


class Command(BaseCommand):
    """Manage test databases - cleanup, info, reset."""

    help = 'Manage test databases (cleanup old DBs, show info, reset)'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            'action',
            type=str,
            choices=['cleanup', 'info', 'reset', 'check-extensions'],
            help='Action to perform: cleanup, info, reset, check-extensions',
        )
        parser.add_argument(
            '--database',
            default='default',
            help='Database alias (default: default)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Apply to all databases',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force action without confirmation',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )

    def handle(self, *args, **options):
        """Execute command."""
        action = options['action']

        if action == 'cleanup':
            self._handle_cleanup(options)
        elif action == 'info':
            self._handle_info(options)
        elif action == 'reset':
            self._handle_reset(options)
        elif action == 'check-extensions':
            self._handle_check_extensions(options)

    def _handle_cleanup(self, options):
        """Clean up all test databases."""
        all_dbs = options['all']
        force = options['force']
        database_alias = options['database']

        # Determine which databases to clean
        if all_dbs:
            aliases = list(connections.databases.keys())
        else:
            aliases = [database_alias]

        # Header
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('         TEST DATABASE CLEANUP'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Collect test databases
        test_dbs_to_remove = []
        for alias in aliases:
            connection = connections[alias]
            db_engine = connection.settings_dict.get('ENGINE', '')

            if 'postgresql' not in db_engine.lower():
                continue

            test_db_name = self._get_test_db_name(connection)

            # Check if exists
            if self._test_database_exists(connection, test_db_name):
                test_dbs_to_remove.append((alias, test_db_name, connection))

        if not test_dbs_to_remove:
            self.stdout.write(self.style.SUCCESS('✅ No test databases found to clean up'))
            self.stdout.write('')
            return

        # Show what will be removed
        self.stdout.write(self.style.WARNING(f'Found {len(test_dbs_to_remove)} test database(s):'))
        for alias, test_db_name, _ in test_dbs_to_remove:
            self.stdout.write(f'  • {test_db_name} (alias: {alias})')
        self.stdout.write('')

        # Confirm
        if not force:
            confirm = input(self.style.WARNING('⚠️  Remove these databases? [y/N]: '))
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE('Cancelled'))
                return

        # Remove databases
        self.stdout.write('')
        removed_count = 0
        for alias, test_db_name, connection in test_dbs_to_remove:
            try:
                self._drop_test_database(connection, test_db_name)
                self.stdout.write(self.style.SUCCESS(f'✅ Removed: {test_db_name}'))
                removed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to remove {test_db_name}: {e}'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'✅ Cleanup complete: {removed_count}/{len(test_dbs_to_remove)} databases removed'))
        self.stdout.write('')

    def _handle_info(self, options):
        """Show test database information."""
        all_dbs = options['all']
        json_output = options['json']
        database_alias = options['database']

        # Determine which databases to show
        if all_dbs:
            aliases = list(connections.databases.keys())
        else:
            aliases = [database_alias]

        info_data = []

        for alias in aliases:
            connection = connections[alias]
            db_engine = connection.settings_dict.get('ENGINE', '')

            if 'postgresql' not in db_engine.lower():
                continue

            test_db_name = self._get_test_db_name(connection)
            exists = self._test_database_exists(connection, test_db_name)

            db_info = {
                'alias': alias,
                'test_db_name': test_db_name,
                'exists': exists,
                'engine': db_engine,
            }

            if exists:
                # Get additional info
                try:
                    db_info['size'] = self._get_database_size(connection, test_db_name)
                    db_info['extensions'] = self._get_installed_extensions(connection, test_db_name)
                except Exception as e:
                    db_info['error'] = str(e)

            info_data.append(db_info)

        if json_output:
            self.stdout.write(json.dumps(info_data, indent=2))
            return

        # Pretty output
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('         TEST DATABASE INFORMATION'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        for db_info in info_data:
            self.stdout.write(self.style.HTTP_INFO(f"Database Alias: {db_info['alias']}"))
            self.stdout.write(f"  Test DB Name:    {db_info['test_db_name']}")

            if db_info['exists']:
                self.stdout.write(self.style.SUCCESS(f"  Status:          ✅ EXISTS"))
                if 'size' in db_info:
                    self.stdout.write(f"  Size:            {db_info['size']}")
                if 'extensions' in db_info:
                    self.stdout.write(f"  Extensions:      {', '.join(db_info['extensions']) if db_info['extensions'] else 'None'}")
            else:
                self.stdout.write(self.style.NOTICE(f"  Status:          ⚪ Does not exist"))

            self.stdout.write(f"  Engine:          {db_info['engine']}")
            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

    def _handle_reset(self, options):
        """Reset test database (drop and recreate)."""
        force = options['force']
        database_alias = options['database']

        connection = connections[database_alias]
        db_engine = connection.settings_dict.get('ENGINE', '')

        if 'postgresql' not in db_engine.lower():
            raise CommandError(f'Database {database_alias} is not PostgreSQL')

        test_db_name = self._get_test_db_name(connection)
        exists = self._test_database_exists(connection, test_db_name)

        # Header
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('         RESET TEST DATABASE'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')
        self.stdout.write(f'Database: {test_db_name} (alias: {database_alias})')
        self.stdout.write(f'Status:   {"EXISTS" if exists else "Does not exist"}')
        self.stdout.write('')

        # Confirm
        if not force:
            confirm = input(self.style.WARNING('⚠️  This will DROP and recreate the test database. Continue? [y/N]: '))
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE('Cancelled'))
                return

        # Drop if exists
        if exists:
            try:
                self._drop_test_database(connection, test_db_name)
                self.stdout.write(self.style.SUCCESS(f'✅ Dropped: {test_db_name}'))
            except Exception as e:
                raise CommandError(f'Failed to drop database: {e}')

        # Recreate
        try:
            self._create_test_database(connection, test_db_name)
            self.stdout.write(self.style.SUCCESS(f'✅ Created: {test_db_name}'))
        except Exception as e:
            raise CommandError(f'Failed to create database: {e}')

        # Install extensions
        try:
            manager = PostgreSQLExtensionManager()
            if manager.check_if_pgvector_needed():
                # Temporarily switch to test database
                original_db = connection.settings_dict['NAME']
                connection.settings_dict['NAME'] = test_db_name
                connection.close()

                with connection.cursor() as cursor:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

                connection.settings_dict['NAME'] = original_db
                connection.close()

                self.stdout.write(self.style.SUCCESS(f'✅ Installed extensions'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Could not install extensions: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'✅ Test database reset complete'))
        self.stdout.write('')

    def _handle_check_extensions(self, options):
        """Check PostgreSQL extensions in test database."""
        database_alias = options['database']
        json_output = options['json']

        connection = connections[database_alias]
        db_engine = connection.settings_dict.get('ENGINE', '')

        if 'postgresql' not in db_engine.lower():
            raise CommandError(f'Database {database_alias} is not PostgreSQL')

        test_db_name = self._get_test_db_name(connection)

        if not self._test_database_exists(connection, test_db_name):
            raise CommandError(f'Test database {test_db_name} does not exist')

        # Get extensions
        extensions = self._get_installed_extensions(connection, test_db_name)

        # Check what's needed
        manager = PostgreSQLExtensionManager()
        needs_pgvector = manager.check_if_pgvector_needed()

        if json_output:
            data = {
                'test_db_name': test_db_name,
                'installed_extensions': extensions,
                'needs_pgvector': needs_pgvector,
            }
            self.stdout.write(json.dumps(data, indent=2))
            return

        # Pretty output
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('         TEST DATABASE EXTENSIONS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f'Database: {test_db_name}')
        self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO('Installed Extensions:'))
        if extensions:
            for ext in extensions:
                self.stdout.write(f'  ✅ {ext}')
        else:
            self.stdout.write('  (none)')

        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Required Extensions:'))

        required = []
        if needs_pgvector:
            required = ['vector', 'pg_trgm', 'unaccent']

        if required:
            for ext in required:
                if ext in extensions:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ {ext} (installed)'))
                else:
                    self.stdout.write(self.style.ERROR(f'  ❌ {ext} (missing)'))
        else:
            self.stdout.write('  (none required)')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

    # Helper methods

    def _get_test_db_name(self, connection) -> str:
        """Get test database name."""
        test_db_name = connection.settings_dict.get('TEST', {}).get('NAME')
        if not test_db_name:
            db_name = connection.settings_dict['NAME']
            test_db_name = f'test_{db_name}'
        return test_db_name

    def _test_database_exists(self, connection, test_db_name: str) -> bool:
        """Check if test database exists."""
        try:
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = 'postgres'
            connection.close()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    [test_db_name]
                )
                exists = cursor.fetchone() is not None

            connection.settings_dict['NAME'] = original_db
            connection.close()

            return exists
        except Exception:
            return False

    def _drop_test_database(self, connection, test_db_name: str):
        """Drop test database."""
        original_db = connection.settings_dict['NAME']
        connection.settings_dict['NAME'] = 'postgres'
        connection.close()

        with connection.cursor() as cursor:
            # Terminate connections
            cursor.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
            """, [test_db_name])

            # Drop database
            cursor.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')

        connection.settings_dict['NAME'] = original_db
        connection.close()

    def _create_test_database(self, connection, test_db_name: str):
        """Create test database."""
        original_db = connection.settings_dict['NAME']
        connection.settings_dict['NAME'] = 'postgres'
        connection.close()

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE "{test_db_name}" ENCODING \'UTF8\' TEMPLATE template0')

        connection.settings_dict['NAME'] = original_db
        connection.close()

    def _get_database_size(self, connection, test_db_name: str) -> str:
        """Get database size."""
        try:
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = 'postgres'
            connection.close()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_size_pretty(pg_database_size(%s))",
                    [test_db_name]
                )
                size = cursor.fetchone()[0]

            connection.settings_dict['NAME'] = original_db
            connection.close()

            return size
        except Exception:
            return 'Unknown'

    def _get_installed_extensions(self, connection, test_db_name: str) -> List[str]:
        """Get list of installed extensions."""
        try:
            original_db = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = test_db_name
            connection.close()

            with connection.cursor() as cursor:
                cursor.execute("SELECT extname FROM pg_extension WHERE extname != 'plpgsql'")
                extensions = [row[0] for row in cursor.fetchall()]

            connection.settings_dict['NAME'] = original_db
            connection.close()

            return extensions
        except Exception:
            return []
