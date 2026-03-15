"""
Management command to populate geo database.

Usage:
    python manage.py geo_populate
    python manage.py geo_populate --force  # Re-download and repopulate
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populate geo database from dr5hn repository"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force repopulate even if data exists"
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear cached JSON files before downloading"
        )

    def handle(self, *args, **options):
        from django_cfg.apps.tools.geo.models import Country
        from django_cfg.apps.tools.geo.services.loader import GeoDataLoader

        loader = GeoDataLoader()

        # Clear cache if requested
        if options["clear_cache"]:
            loader.clear_cache()
            self.stdout.write(self.style.SUCCESS("Cache cleared"))

        # Check if data exists
        if not options["force"] and Country.objects.exists():
            count = Country.objects.count()
            self.stdout.write(
                self.style.WARNING(
                    f"Geo data already exists ({count} countries). "
                    "Use --force to repopulate."
                )
            )
            return

        # Populate database
        self.stdout.write("Populating geo database...")
        try:
            stats = loader.populate_database(force=options["force"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Geo database populated: "
                    f"{stats['countries']} countries, "
                    f"{stats['states']} states, "
                    f"{stats['cities']} cities"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to populate: {e}"))
            raise
