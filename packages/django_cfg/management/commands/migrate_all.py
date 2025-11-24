"""
Simple Migration Command for Django Config Toolkit
Migrate all databases based on django-cfg configuration.
"""

from django_cfg.management.utils import AdminCommand, MigrationManager


class Command(AdminCommand):
    """
    Migrate all databases - destructive but non-interactive admin command.

    This command is marked as destructive because it modifies the database schema,
    but it doesn't require user input during execution.
    """

    command_name = 'migrate_all'

    # Override AdminCommand defaults
    web_executable = False  # Too risky for web execution
    is_destructive = True   # Modifies database schema

    help = "Migrate all databases based on django-cfg configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-makemigrations",
            action="store_true",
            help="Skip makemigrations step"
        )

    def handle(self, *args, **options):
        """Run migrations for all configured databases."""
        self.logger.info("Starting migrate_all command")
        skip_makemigrations = options.get("skip_makemigrations", False)

        # Initialize migration manager
        manager = MigrationManager(self.stdout, self.style, self.logger)

        # Create migrations if needed
        if not skip_makemigrations:
            manager.create_migrations()

        # Migrate all databases
        manager.migrate_all_databases()

        # Migrate constance
        manager.migrate_constance_if_needed()

        self.stdout.write(self.style.SUCCESS("\n✅ All migrations completed!"))
