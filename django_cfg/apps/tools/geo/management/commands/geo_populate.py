"""
Management command to populate geo database.

Usage:
    python manage.py geo_populate
    python manage.py geo_populate --force              # Re-download and repopulate
    python manage.py geo_populate --countries BB,BS,KY # Only these markets

Without a filter this imports the full dr5hn dataset (250 countries, ~5,000
states, ~150,000 cities). Projects serving a handful of markets should set
``GeoConfig(countries=[...])`` instead and keep the tables proportional to
their actual coverage.
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
        parser.add_argument(
            "--countries",
            type=str,
            default=None,
            help=(
                "Comma-separated ISO2 codes to import, e.g. 'BB,BS,KY'. "
                "Overrides GeoConfig.countries. States and cities are "
                "restricted to the selected countries."
            ),
        )

    def _resolve_countries(self, cli_value: str | None) -> list[str]:
        """CLI flag wins over ``GeoConfig.countries``; otherwise fall back to it.

        The config is the durable declaration of what a project covers; the
        flag is for a one-off import. Reading the config here means a project
        that declares its markets does not have to repeat them on every run.
        """
        if cli_value:
            return [code.strip().upper() for code in cli_value.split(",") if code.strip()]

        try:
            from django_cfg.core.state import get_current_config

            geo = getattr(get_current_config(), "geo", None)
            return list(getattr(geo, "countries", []) or [])
        except Exception:
            # No config available (bare Django, tests) — import everything,
            # which is the historical behaviour.
            return []

    def handle(self, *args, **options):
        from django_cfg.apps.tools.geo.models import Country
        from django_cfg.apps.tools.geo.services.loader import GeoDataLoader

        loader = GeoDataLoader()

        countries = self._resolve_countries(options.get("countries"))
        if countries:
            self.stdout.write(f"Country filter: {', '.join(countries)}")

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
            stats = loader.populate_database(
                force=options["force"],
                countries=countries,
            )
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
