"""
Smart Migration Command for Django Config Toolkit
Simple and reliable migration for all databases.
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder
from django.conf import settings
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Smart migration command with interactive menu for multiple databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Run automatic migration without prompts'
        )
        parser.add_argument(
            '--database',
            type=str,
            help='Migrate specific database only'
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Migrate specific app only'
        )

    def handle(self, *args, **options):
        if options['auto']:
            self.run_automatic_migration()
        elif options['database']:
            self.migrate_database(options['database'])
        elif options['app']:
            self.migrate_app(options['app'])
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with options"""
        self.stdout.write(self.style.SUCCESS('\n🚀 Smart Migration Tool - Django Config Toolkit\n'))

        databases = self.get_all_database_names()

        choices = [
            questionary.Choice('🔄 Run Full Migration (All Databases)', value='full'),
            questionary.Choice('📝 Create Migrations Only', value='makemigrations'),
            questionary.Choice('🔍 Show Database Status', value='status'),
            questionary.Choice('⚙️  Show ConfigToolkit Info', value='config'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        # Add individual database options
        for db_name in databases:
            display_name = f'📊 Migrate {db_name.title()} Database Only'
            choices.insert(-1, questionary.Choice(display_name, value=f'migrate_{db_name}'))

        choice = questionary.select(
            'Select an option:',
            choices=choices
        ).ask()

        if choice == 'full':
            self.run_full_migration()
        elif choice == 'makemigrations':
            self.create_migrations()
        elif choice == 'status':
            self.show_database_status()
        elif choice == 'config':
            self.show_config_toolkit_info()
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return
        elif choice.startswith('migrate_'):
            db_name = choice.replace('migrate_', '')
            self.migrate_database(db_name)

    def run_full_migration(self):
        """Run migration for all databases"""
        self.stdout.write(self.style.SUCCESS('🔄 Starting full migration...'))

        # First migrate default database
        self.stdout.write('📊 Migrating default database...')
        self.migrate_database('default')

        # Then migrate other databases (excluding default)
        databases = self.get_all_database_names()
        for db_name in databases:
            if db_name != 'default':
                self.stdout.write(f'🔄 Migrating {db_name}...')
                self.migrate_database(db_name)

        self.stdout.write(self.style.SUCCESS('✅ Full migration completed!'))

    def run_automatic_migration(self):
        """Run automatic migration for all databases"""
        self.stdout.write(self.style.SUCCESS('🚀 Running automatic migration...'))

        # Create migrations
        self.create_migrations()

        # Run full migration
        self.run_full_migration()

    def create_migrations(self):
        """Create migrations for all apps"""
        self.stdout.write(self.style.SUCCESS('📝 Creating migrations...'))

        try:
            call_command('makemigrations', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Migrations created'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Warning creating migrations: {e}'))

    def migrate_database(self, db_name):
        """Migrate specific database"""
        try:
            self.stdout.write(f'🔄 Migrating {db_name}...')

            # Get apps for this database
            apps = self.get_apps_for_database(db_name)
            
            # Debug info
            self.stdout.write(f'  📋 Apps for {db_name}: {apps}')

            if not apps:
                self.stdout.write(self.style.WARNING(f'  ⚠️  No apps configured for {db_name}'))
                return

            # Migrate each app
            for app in apps:
                try:
                    # Skip apps without migrations
                    if not self.app_has_migrations(app):
                        self.stdout.write(f'  ⚠️  Skipping {app} - no migrations')
                        continue
                        
                    self.stdout.write(f'  📦 Migrating {app}...')
                    call_command('migrate', app, database=db_name, verbosity=1)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  Warning migrating {app}: {e}'))

            self.stdout.write(self.style.SUCCESS(f'✅ {db_name} migration completed!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error migrating {db_name}: {e}'))

    def migrate_app(self, app_name):
        """Migrate specific app across all databases"""
        self.stdout.write(f'🔄 Migrating app {app_name}...')
        
        databases = self.get_all_database_names()
        for db_name in databases:
            apps = self.get_apps_for_database(db_name)
            if app_name in apps:
                self.stdout.write(f'  📊 Migrating {app_name} on {db_name}...')
                try:
                    call_command('migrate', app_name, database=db_name, verbosity=1)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  Warning: {e}'))

    def show_database_status(self):
        """Show status of all databases and their apps"""
        self.stdout.write(self.style.SUCCESS('\n📊 Database Status Report\n'))
        
        # Get database info from ConfigToolkit
        db_info = self.get_database_info()
        databases = self.get_all_database_names()
        
        for db_name in databases:
            self.stdout.write(f'\n🗄️  Database: {db_name}')
            
            # Show database info from ConfigToolkit
            if db_name in db_info:
                info = db_info[db_name]
                self.stdout.write(f'  🔧 Engine: {info["engine"]}')
                self.stdout.write(f'  🔗 URL: {info["url"][:50]}...')
            
            # Test connection
            try:
                with connections[db_name].cursor() as cursor:
                    cursor.execute("SELECT 1")
                self.stdout.write(f'  ✅ Connection: OK')
            except Exception as e:
                self.stdout.write(f'  ❌ Connection: FAILED - {e}')
            
            # Show apps
            apps = self.get_apps_for_database(db_name)
            if apps:
                self.stdout.write(f'  📦 Apps: {", ".join(apps)}')
            else:
                self.stdout.write(f'  📦 Apps: None configured')

    def show_config_toolkit_info(self):
        """Show ConfigToolkit configuration information"""
        self.stdout.write(self.style.SUCCESS('\n⚙️  ConfigToolkit Information\n'))
        
        try:
            config = ConfigToolkit()
            
            # Environment info
            self.stdout.write(f'🌍 Environment: {config.environment}')
            self.stdout.write(f'🔧 Debug: {config.debug}')
            self.stdout.write(f'🗄️ Database Engine: {config.database_engine}')
            self.stdout.write(f'🔗 Database URL: {config.database_url[:50]}...')
            
            # Multiple databases
            if config._db_config.has_multiple_databases:
                self.stdout.write(f'📊 Multiple Databases: Yes')
                
                # Show additional databases
                additional_dbs = config._db_config._get_additional_databases()
                if additional_dbs:
                    self.stdout.write(f'  📋 Additional Databases:')
                    for db_name, db_url in additional_dbs.items():
                        self.stdout.write(f'    - {db_name}: {db_url[:50]}...')
                
                # Show routing rules
                routing_rules = config._db_config.get_database_routing_rules()
                if routing_rules:
                    self.stdout.write(f'  🔀 Routing Rules:')
                    for app, db in routing_rules.items():
                        self.stdout.write(f'    - {app} → {db}')
            else:
                self.stdout.write(f'📊 Multiple Databases: No')
            
            # Database connection info
            self.stdout.write(f'🔌 Max Connections: {config.database_max_connections}')
            self.stdout.write(f'⏱️  Connection Age: {config._db_config.conn_max_age}s')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error getting ConfigToolkit info: {e}'))

    def get_apps_for_database(self, db_name: str):
        """Get apps for specific database with smart logic for default"""
        if db_name == 'default':
            # For default database, get all apps that are not in other databases
            all_apps = self.get_all_installed_apps()
            apps_in_other_dbs = self.get_apps_in_other_databases()
            return [app for app in all_apps if app not in apps_in_other_dbs]
        else:
            # For other databases, use configured apps from routing rules
            routing_rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
            
            # Also check ConfigToolkit routing rules
            try:
                config = ConfigToolkit()
                toolkit_rules = config._db_config.get_database_routing_rules()
                routing_rules.update(toolkit_rules)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️  Error getting ConfigToolkit routing: {e}'))
            
            return [app for app, db in routing_rules.items() if db == db_name]

    def get_all_installed_apps(self):
        """Get all installed Django apps."""
        apps = []
        for app in settings.INSTALLED_APPS:
            # Handle different app formats
            if app.startswith('src.'):
                # src.data_proxy -> data_proxy
                apps.append(app.split('.')[-1])
            elif '.' in app:
                # django.contrib.admin -> admin
                apps.append(app.split('.')[-1])
            else:
                # Simple app name
                apps.append(app)
        return apps

    def get_apps_in_other_databases(self) -> set:
        """Get all apps that are configured for non-default databases."""
        routing_rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        
        # Also check ConfigToolkit routing rules
        try:
            config = ConfigToolkit()
            toolkit_rules = config._db_config.get_database_routing_rules()
            routing_rules.update(toolkit_rules)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Error getting ConfigToolkit routing: {e}'))
        
        return set(routing_rules.keys())

    def get_all_database_names(self):
        """Get all database names."""
        return list(connections.databases.keys())

    def get_database_info(self):
        """Get database information from ConfigToolkit"""
        try:
            config = ConfigToolkit()
            
            # Get database info from ConfigToolkit
            db_info = {
                'default': {
                    'url': config.database_url,
                    'engine': config.database_engine,
                    'apps': []  # Will be populated by routing logic
                }
            }
            
            # Check for additional databases from environment
            additional_dbs = config._db_config._get_additional_databases()
            for db_name, db_url in additional_dbs.items():
                db_info[db_name] = {
                    'url': db_url,
                    'engine': self._get_engine_from_url(db_url),
                    'apps': []
                }
            
            return db_info
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Error getting database info: {e}'))
            return {}

    def _get_engine_from_url(self, url: str) -> str:
        """Get database engine from URL"""
        if url.startswith('postgresql'):
            return 'postgresql'
        elif url.startswith('mysql'):
            return 'mysql'
        elif url.startswith('sqlite'):
            return 'sqlite'
        else:
            return 'unknown'

    def app_has_migrations(self, app_label: str) -> bool:
        """Simple check if an app has migrations."""
        try:
            # Get the app config
            app_config = apps.get_app_config(app_label)
            if not app_config:
                return False
            
            # Check if migrations directory exists and has files
            migrations_dir = Path(app_config.path) / 'migrations'
            if not migrations_dir.exists():
                return False
            
            # Check if there are any migration files (excluding __init__.py)
            migration_files = [f for f in migrations_dir.glob('*.py') if f.name != '__init__.py']
            
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
                
        except Exception as e:
            # Debug info
            print(f"Error checking migrations for {app_label}: {e}")
            return False
