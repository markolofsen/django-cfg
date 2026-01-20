# Geo Data Cache

This folder stores cached JSON files from [dr5hn/countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

## Files (downloaded on demand)

- `countries.json` (~330 KB) - 250 countries
- `states.json` (~4.4 MB) - 5,000+ states/regions  
- `cities.json` (~133 MB) - 150,000+ cities with coordinates

## How it works

1. Files are **not** included in the package (too large for PyPI)
2. On first run of `python manage.py geo_populate`, files are downloaded from GitHub
3. Downloaded files are cached here for subsequent runs

## Manual download

If automatic download fails, download manually:

```bash
cd /path/to/geo/data/
curl -O https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/countries.json
curl -O https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/states.json
curl -O https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/cities.json
```

## Clear cache

```bash
python manage.py geo_populate --clear-cache
```
