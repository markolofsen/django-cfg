"""Download Material Icons data from Google sources."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import requests

from .models import IconCodepoints, IconMeta, IconMetaMap

logger = logging.getLogger(__name__)

SOURCES = {
    "codepoints": "https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIcons-Regular.codepoints",
    "metadata": "https://fonts.google.com/metadata/icons",
    "svg": "https://fonts.gstatic.com/s/i/materialicons/{name}/v{version}/24px.svg",
}

# Output dir for bundled SVG icons consumed by django_ogimage
OGIMAGE_ICONS_DIR = (
    Path(__file__).parents[3] / "django_ogimage" / "core" / "assets" / "icons"
)
# Curated SaaS-themed icons bundled with django_ogimage
OGIMAGE_ICONS = [
    "dashboard",      # Overview / home
    "analytics",      # Metrics, reports
    "people",         # Team, users
    "payments",       # Billing, subscriptions
    "security",       # Access control, compliance
    "rocket_launch",  # Onboarding, launch
    "support_agent",  # Support, help center
    "cloud",          # Infrastructure, hosting
    "verified",       # Trust, quality
    "auto_awesome",   # AI features, automation
]


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


def download_top_svgs(metadata: IconMetaMap) -> int:
    """Download curated SaaS icons into OGIMAGE_ICONS_DIR, replacing existing files.

    Returns the number of successfully saved icons.
    """
    if not metadata:
        logger.warning("⚠️ No metadata — skipping SVG download")
        return 0

    # Clear existing icons so stale files don't accumulate
    OGIMAGE_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    for existing in OGIMAGE_ICONS_DIR.glob("*.svg"):
        existing.unlink()

    logger.info("📥 Downloading %d SaaS icons to %s...", len(OGIMAGE_ICONS), OGIMAGE_ICONS_DIR)

    saved = 0
    for name in OGIMAGE_ICONS:
        meta = metadata.get(name)
        if meta is None:
            logger.warning("  ⚠️ %r not found in metadata — skipping", name)
            continue
        url = SOURCES["svg"].format(name=name, version=meta.version)
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            (OGIMAGE_ICONS_DIR / f"{name}.svg").write_bytes(resp.content)
            saved += 1
        except Exception as exc:
            logger.warning("  ⚠️ Failed to download %r: %s", name, exc)

    logger.info("✅ Saved %d/%d SVG icons", saved, len(OGIMAGE_ICONS))
    return saved
