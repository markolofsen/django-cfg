"""
Geographic data loader.

Downloads and populates geo data from dr5hn/countries-states-cities-database.
"""

import gzip
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DR5HN_BASE = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master"


class GeoDataLoader:
    """
    Load geo data from dr5hn repository.

    Downloads JSON files from GitHub and populates PostgreSQL database.
    Caches downloaded files locally for faster subsequent loads.

    Usage:
        loader = GeoDataLoader()
        loader.populate_database()
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize loader.

        Args:
            cache_dir: Directory for caching downloaded files.
                      Defaults to geo/data/ directory.
        """
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "data"
        self.cache_dir.mkdir(exist_ok=True)

    def download_json(self, filename: str, force: bool = False) -> list:
        """
        Download JSON file from dr5hn repo.

        Supports both regular .json and compressed .json.gz files.
        If regular file is not found, tries .gz version.

        Args:
            filename: JSON filename (e.g., 'countries.json')
            force: Force re-download even if cached

        Returns:
            Parsed JSON data as list
        """
        import httpx

        cache_path = self.cache_dir / filename

        # Try cache first
        if not force and cache_path.exists():
            logger.info(f"Loading {filename} from cache")
            return json.loads(cache_path.read_text(encoding="utf-8"))

        # Try regular JSON first, then gzipped
        urls_to_try = [
            f"{DR5HN_BASE}/json/{filename}",
            f"{DR5HN_BASE}/json/{filename}.gz",
        ]

        data = None
        for url in urls_to_try:
            try:
                logger.info(f"Downloading from {url}")
                response = httpx.get(url, timeout=120, follow_redirects=True)
                response.raise_for_status()

                if url.endswith(".gz"):
                    # Decompress gzipped content
                    data = json.loads(gzip.decompress(response.content).decode("utf-8"))
                else:
                    data = response.json()

                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.debug(f"Not found: {url}, trying next...")
                    continue
                raise

        if data is None:
            raise RuntimeError(f"Could not download {filename} from any source")

        # Cache
        cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Cached {filename} ({len(data)} records)")

        return data

    def populate_database(self, force: bool = False) -> dict:
        """
        Populate database from dr5hn data.

        Args:
            force: Force re-download of JSON files

        Returns:
            Statistics dict with counts
        """
        from ..models import City, Country, State

        stats = {"countries": 0, "states": 0, "cities": 0}

        # Load countries
        countries_data = self.download_json("countries.json", force=force)
        logger.info(f"Loading {len(countries_data)} countries...")

        for c in countries_data:
            Country.objects.update_or_create(
                id=c["id"],
                defaults={
                    "name": c["name"],
                    "iso2": c["iso2"],
                    "iso3": c.get("iso3"),
                    "numeric_code": c.get("numeric_code"),
                    "phonecode": c.get("phone_code"),
                    "capital": c.get("capital"),
                    "currency": c.get("currency"),
                    "currency_name": c.get("currency_name"),
                    "currency_symbol": c.get("currency_symbol"),
                    "tld": c.get("tld"),
                    "native": c.get("native"),
                    "region": c.get("region"),
                    "subregion": c.get("subregion"),
                    "nationality": c.get("nationality"),
                    "timezones": c.get("timezones"),
                    "translations": c.get("translations"),
                    "latitude": float(c["latitude"]) if c.get("latitude") else None,
                    "longitude": float(c["longitude"]) if c.get("longitude") else None,
                    "emoji": c.get("emoji"),
                    "is_active": True,
                }
            )
            stats["countries"] += 1

        logger.info(f"Loaded {stats['countries']} countries")

        # Load states
        states_data = self.download_json("states.json", force=force)
        logger.info(f"Loading {len(states_data)} states...")

        for s in states_data:
            State.objects.update_or_create(
                id=s["id"],
                defaults={
                    "name": s["name"],
                    "country_id": s["country_id"],
                    "iso2": s.get("state_code") or s.get("iso2"),
                    "type": s.get("type"),
                    "latitude": float(s["latitude"]) if s.get("latitude") else None,
                    "longitude": float(s["longitude"]) if s.get("longitude") else None,
                    "is_active": True,
                }
            )
            stats["states"] += 1

        logger.info(f"Loaded {stats['states']} states")

        # Load cities
        cities_data = self.download_json("cities.json", force=force)
        logger.info(f"Loading {len(cities_data)} cities...")

        # Batch insert for better performance
        batch_size = 1000
        for i in range(0, len(cities_data), batch_size):
            batch = cities_data[i:i + batch_size]
            for c in batch:
                City.objects.update_or_create(
                    id=c["id"],
                    defaults={
                        "name": c["name"],
                        "state_id": c.get("state_id"),
                        "country_id": c["country_id"],
                        "latitude": float(c["latitude"]),
                        "longitude": float(c["longitude"]),
                        "is_active": True,
                    }
                )
                stats["cities"] += 1

            if i % 10000 == 0 and i > 0:
                logger.info(f"Loaded {i} cities...")

        logger.info(f"Loaded {stats['cities']} cities")
        logger.info("Geo database populated successfully")

        return stats

    def clear_cache(self) -> None:
        """Clear downloaded cache files."""
        for filename in ["countries.json", "states.json", "cities.json"]:
            cache_path = self.cache_dir / filename
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Removed cache: {filename}")


__all__ = ["GeoDataLoader"]
