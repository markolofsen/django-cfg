"""
Smart Migration Command for Django Config Toolkit
Simple and reliable migration for all databases.
"""

import questionary
from django.conf import settings
from django.core.management import call_command
from django.db import connections

from django_cfg.management.utils import DestructiveCommand, MigrationManager


class Command(DestructiveCommand):
    command_name = 'migrator'
    help = "Smart migration command with interactive menu for multiple databases"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = None

    def add_arguments(self, parser):
        parser.add_argument("--auto", action="store_true", help="Run automatic migration without prompts")
        parser.add_argument("--database", type=str, help="Migrate specific database only")
        parser.add_argument("--app", type=str, help="Migrate specific app only")

    def handle(self, *args, **options):
        # Initialize migration manager
        self.manager = MigrationManager(self.stdout, self.style, self.logger)
        
        if options["auto"]:
            self.run_automatic_migration()
        elif options["database"]:
            self.manager.migrate_database(options["database"])
        elif options["app"]:
            self.migrate_app(options["app"])
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with options"""
        self.stdout.write(self.style.SUCCESS("\n🚀 Smart Migration Tool - Django Config Toolkit\n"))

        databases = self.manager.get_all_database_names()

        choices = [
            questionary.Choice("🔄 Run Full Migration (All Databases)", value="full"),
            questionary.Choice("📝 Create Migrations Only", value="makemigrations"),
            questionary.Choice("🔍 Show Database Status", value="status"),
            questionary.Choice("⚙️  Show Django Config Info", value="config"),
            questionary.Choice("❌ Exit", value="exit"),
        ]

        # Add individual database options
        for db_name in databases:
            display_name = f"📊 Migrate {db_name.title()} Database Only"
            choices.insert(-1, questionary.Choice(display_name, value=f"migrate_{db_name}"))

        choice = questionary.select("Select an option:", choices=choices).ask()

        if choice == "full":
            self.run_full_migration()
        elif choice == "makemigrations":
            self.manager.create_migrations()
        elif choice == "status":
            self.show_database_status()
        elif choice == "config":
            self.show_config_info()
        elif choice == "exit":
            self.stdout.write("Goodbye! 👋")
            return
        elif choice.startswith("migrate_"):
            db_name = choice.replace("migrate_", "")
            self.manager.migrate_database(db_name)

    def run_full_migration(self):
        """Run migration for all databases"""
        self.manager.migrate_all_databases()

    def run_automatic_migration(self):
        """Run automatic migration for all databases"""
        self.stdout.write(self.style.SUCCESS("🚀 Running automatic migration..."))

        # Create migrations
        self.manager.create_migrations()

        # Run full migration
        self.manager.migrate_all_databases()

        # Always migrate constance (required for django-cfg)
        self.manager.migrate_constance_if_needed()


    def migrate_app(self, app_name):
        """Migrate specific app across all databases"""
        self.stdout.write(f"🔄 Migrating app {app_name}...")

        databases = self.manager.get_all_database_names()
        for db_name in databases:
            apps = self.manager.get_apps_for_database(db_name)
            if app_name in apps:
                self.stdout.write(f"  📊 Migrating {app_name} on {db_name}...")
                try:
                    call_command("migrate", app_name, database=db_name, verbosity=1)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Migration failed for {app_name} on {db_name}: {e}"))
                    self.logger.error(f"Migration failed for {app_name} on {db_name}: {e}")
                    raise SystemExit(1)

    def show_database_status(self):
        """Show status of all databases and their apps"""
        self.stdout.write(self.style.SUCCESS("\n📊 Database Status Report\n"))

        # Get database info from Django settings
        db_info = self.manager.get_database_info()
        databases = self.manager.get_all_database_names()

        for db_name in databases:
            self.stdout.write(f"\n🗄️  Database: {db_name}")

            # Show database info from Django settings
            if db_name in db_info:
                info = db_info[db_name]
                self.stdout.write(f'  🔧 Engine: {info["engine"]}')
                self.stdout.write(f'  🔗 Name: {info["name"]}')

            # Test connection
            if self.manager.check_database_connection(db_name):
                self.stdout.write("  ✅ Connection: OK")

            # Show apps
            apps = self.manager.get_apps_for_database(db_name)
            if apps:
                self.stdout.write(f'  📦 Apps: {", ".join(apps)}')
            else:
                self.stdout.write("  📦 Apps: None configured")

    def show_config_info(self):
        """Show Django configuration information"""
        self.stdout.write(self.style.SUCCESS("\n⚙️  Django Configuration Information\n"))

        try:
            # Environment info
            self.stdout.write(f'🌍 Environment: {getattr(settings, "ENVIRONMENT", "unknown")}')
            self.stdout.write(f"🔧 Debug: {settings.DEBUG}")

            # Database info
            databases = settings.DATABASES
            self.stdout.write(f"🗄️ Databases: {len(databases)}")

            for db_name, db_config in databases.items():
                engine = db_config.get("ENGINE", "unknown")
                name = db_config.get("NAME", "unknown")
                self.stdout.write(f"  📊 {db_name}: {engine} -> {name}")

            # Multiple databases
            if len(databases) > 1:
                self.stdout.write("📊 Multiple Databases: Yes")

                # Show routing rules
                routing_rules = getattr(settings, "DATABASE_ROUTING_RULES", {})
                if routing_rules:
                    self.stdout.write("  🔀 Routing Rules:")
                    for app, db in routing_rules.items():
                        self.stdout.write(f"    - {app} → {db}")
                else:
                    self.stdout.write("  🔀 Routing Rules: None configured")
            else:
                self.stdout.write("📊 Multiple Databases: No")

            # Other settings
            self.stdout.write(f'🔑 Secret Key: {"*" * 20}...')
            self.stdout.write(f"🌐 Allowed Hosts: {settings.ALLOWED_HOSTS}")
            self.stdout.write(f"📦 Installed Apps: {len(settings.INSTALLED_APPS)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error getting Django config info: {e}"))
            self.logger.error(f"Error getting Django config info: {e}")
