"""Font resolution for django_ogimage.

No fonts are bundled with the package. All fonts are resolved in this order:

1. Already-downloaded cache  (~/.cache/django_cfg/fonts/)
2. System fonts              (/usr/share/fonts, /System/Library/Fonts, etc.)
3. Lazy download from Google Fonts CDN (on first use per locale)

Font URLs are defined in font_sources.py — edit that file to update them.
Set ``DJANGO_CFG_FONTS_DIR`` env var to override the download cache directory.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import NamedTuple

from django_cfg.core.utils.cache import LazyFileResource

from .font_sources import SOURCES

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(
    os.environ.get("DJANGO_CFG_FONTS_DIR", Path.home() / ".cache" / "django_cfg" / "fonts")
)


def _lazy(filename: str) -> LazyFileResource:
    return LazyFileResource(url=SOURCES[filename], dest=_CACHE_DIR / filename)


_L_INTER_REGULAR = _lazy("Inter-Regular.ttf")
_L_INTER_BOLD    = _lazy("Inter-Bold.ttf")
_L_NOTO_AR       = _lazy("NotoSansArabic.ttf")
_L_NOTO_HE       = _lazy("NotoSansHebrew.ttf")
_L_NOTO_KR       = _lazy("NotoSansKR.ttf")
_L_NOTO_JP       = _lazy("NotoSansJP.ttf")
_L_NOTO_SC       = _lazy("NotoSansSC.ttf")


# ---------------------------------------------------------------------------
# System font detection
# ---------------------------------------------------------------------------

_SYSTEM_FONT_DIRS: list[Path] = [
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path("/System/Library/Fonts"),      # macOS
    Path("/Library/Fonts"),             # macOS
    Path.home() / "Library" / "Fonts", # macOS user
    Path("C:/Windows/Fonts"),           # Windows
]

_SYSTEM_FONT_NAMES = [
    "DejaVuSans.ttf",
    "LiberationSans-Regular.ttf",
    "Arial.ttf",
    "Helvetica.ttf",
    "FreeSans.ttf",
    "NotoSans-Regular.ttf",
]


def _find_system_font() -> str | None:
    """Return path to a usable system font, or None."""
    for font_dir in _SYSTEM_FONT_DIRS:
        if not font_dir.exists():
            continue
        for name in _SYSTEM_FONT_NAMES:
            for match in font_dir.rglob(name):
                return str(match)
    return None


def _default_font_path() -> str:
    """Return the best available default font path.

    Priority: cached Inter-Regular → system font → lazy download.
    """
    if _L_INTER_REGULAR.is_cached():
        return str(_L_INTER_REGULAR.dest)
    system = _find_system_font()
    if system:
        return system
    return str(_L_INTER_REGULAR.resolve())


# ---------------------------------------------------------------------------
# FontSpec
# ---------------------------------------------------------------------------

class FontSpec(NamedTuple):
    regular: str
    bold: str
    is_rtl: bool = False
    is_cjk: bool = False


_LOCALE_MAP: dict[str, tuple[LazyFileResource, dict]] = {
    "ko": (_L_NOTO_KR, {"is_cjk": True}),
    "ja": (_L_NOTO_JP, {"is_cjk": True}),
    "zh": (_L_NOTO_SC, {"is_cjk": True}),
    "ar": (_L_NOTO_AR, {"is_rtl": True}),
    "he": (_L_NOTO_HE, {"is_rtl": True}),
}


def prefetch_all() -> None:
    """Start background daemon threads to pre-download all fonts.

    Call once at Django startup so fonts are ready by the time the first
    OG image request arrives. Never blocks the main thread.
    """
    for resource in [_L_INTER_REGULAR, _L_INTER_BOLD, *[r for r, _ in _LOCALE_MAP.values()]]:
        resource.prefetch()


def get_font_spec(locale: str) -> FontSpec:
    """Return FontSpec for the given BCP 47 locale tag.

    Falls back to the default font if a locale-specific font can't be resolved.
    """
    lang = locale.split("-")[0].lower()

    if lang in _LOCALE_MAP:
        resource, kwargs = _LOCALE_MAP[lang]
        try:
            p = str(resource.resolve())
            return FontSpec(regular=p, bold=p, **kwargs)
        except Exception:
            logger.warning("fonts: could not resolve font for locale %r, using default", locale)

    regular = _default_font_path()
    try:
        bold = str(_L_INTER_BOLD.resolve())
    except Exception:
        bold = regular
    return FontSpec(regular=regular, bold=bold)


def get_all_fallback_fonts(primary: str) -> list[str]:
    """Return already-downloaded fallback fonts except *primary*."""
    candidates = [_L_NOTO_AR, _L_NOTO_HE, _L_NOTO_KR, _L_NOTO_JP, _L_NOTO_SC]
    return [str(r.dest) for r in candidates if r.is_cached() and str(r.dest) != primary]
