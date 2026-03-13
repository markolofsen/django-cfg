"""Orchestrates the full icon generation pipeline."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from .categorizer import categorize_icons
from .downloader import download_codepoints, download_metadata, download_top_svgs
from .generator import generate_constants_file, generate_readme

logger = logging.getLogger(__name__)

# Default output: the icons/ directory (parent of manager/)
DEFAULT_OUTPUT_DIR = Path(__file__).parents[1]


def run(output_dir: Path = DEFAULT_OUTPUT_DIR) -> bool:
    """Run the complete icon generation pipeline.

    1. Download codepoints (name → codepoint)
    2. Download metadata  (popularity, categories, version)
    3. Categorize icons
    4. Generate constants.py + README.md
    5. Download top-50 SVGs into django_ogimage assets

    Returns True on success, False if codepoints download failed.
    """
    logger.info("🚀 Starting Material Icons generation...")

    icons_data = download_codepoints()
    if not icons_data:
        logger.error("❌ Failed to download icons data")
        return False

    metadata = download_metadata()
    categories = categorize_icons(icons_data, metadata)

    generate_constants_file(output_dir, icons_data, categories)
    generate_readme(output_dir, icons_data, categories)
    download_top_svgs(metadata)

    logger.info("🎉 Icon generation completed successfully!")
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    success = run()
    if success:
        print("\n✅ Material Icons updated successfully!")
        print(f"   constants.py + README.md → {DEFAULT_OUTPUT_DIR}")
        print("   SVG icons → django_ogimage/core/assets/icons/")
        print("\n💡 Don't forget to commit the changes!")
    else:
        print("\n❌ Icon generation failed!")
        sys.exit(1)
