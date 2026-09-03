"""Download Material Icons data from Google sources."""
from __future__ import annotations

import json
import logging

import requests

from .models import IconCodepoints, IconMeta, IconMetaMap

logger = logging.getLogger(__name__)

SOURCES = {
    "codepoints": "https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIcons-Regular.codepoints",
    "metadata": "https://fonts.google.com/metadata/icons",
}


def download_codepoints() -> IconCodepoints:
    """Download icon name → codepoint mapping from GitHub. Returns {} on failure."""
    logger.info("📥 Downloading Material Icons codepoints...")
    try:
        resp = requests.get(SOURCES["codepoints"], timeout=30)
        resp.raise_for_status()
        icons: IconCodepoints = {}
        for line in resp.text.strip().splitlines():
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    icons[parts[0]] = parts[1]
        logger.info("✅ Downloaded %d icons from codepoints", len(icons))
        return icons
    except Exception as exc:
        logger.error("❌ Failed to download codepoints: %s", exc)
        return {}


def download_metadata() -> IconMetaMap:
    """Download icon metadata (categories, tags, popularity, version). Returns {} on failure."""
    logger.info("📥 Downloading Material Icons metadata...")
    try:
        resp = requests.get(SOURCES["metadata"], timeout=30)
        resp.raise_for_status()
        content = resp.text
        if content.startswith(")]}'"):
            content = content[4:]
        raw = json.loads(content)
        result: IconMetaMap = {}
        for icon in raw.get("icons", []):
            name: str = icon.get("name", "")
            if name:
                result[name] = IconMeta(
                    categories=icon.get("categories", []),
                    tags=icon.get("tags", []),
                    version=icon.get("version", 1),
                    popularity=icon.get("popularity", 0),
                )
        logger.info("✅ Downloaded metadata for %d icons", len(result))
        return result
    except Exception as exc:
        logger.warning("⚠️ Failed to download metadata: %s", exc)
        return {}
