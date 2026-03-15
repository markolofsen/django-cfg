from __future__ import annotations

import re


# ─────────────────────────────────────────────────────────────────────────────
# User-Agent parser
#
# Detection order matters — Chromium browsers pile tokens onto each other.
# Rule: check most-specific tokens first, generic ones last.
#
# Known limitations (by design, not fixable via UA string alone):
#   - Brave is indistinguishable from Chrome (spoofs UA intentionally)
#   - Arc, Dia, Comet (Perplexity) clone Chrome's UA
#   - Windows 10 vs Windows 11 are identical ("Windows NT 10.0" for both)
#   - macOS 11–15 all report "10_15_7" (frozen since Chrome 107 / Safari 15)
#   - iPads in Desktop Mode (default since iPadOS 13) appear as macOS
#   - Android UA-Reduction: device model replaced by "K", OS frozen at "Android 10"
# ─────────────────────────────────────────────────────────────────────────────

# Regex for bot/crawler detection — checked first
_BOT_RE = re.compile(
    r"bot|spider|crawl|slurp|mediapartners|googlebot|bingbot|yandex|duckduck"
    r"|gptbot|claudebot|claude-user|perplexitybot|bytespider|applebot|amazonbot"
    r"|meta-externalagent|externalagent|facebookexternalhit|twitterbot|linkedinbot"
    r"|semrushbot|ahrefsbot|mj12bot|dotbot",
    re.IGNORECASE,
)

# Regex for TV/SmartTV detection
_TV_RE = re.compile(r"SMART-TV|SmartTV|Web0S|Tizen.*TV|Android TV|GoogleTV|HbbTV|CrKey", re.IGNORECASE)

# Regex for mobile detection (must also contain "Mobile" token or known mobile indicators)
_MOBILE_RE = re.compile(r"Mobile|Android.*Mobile|iPhone|iPod|CriOS|FxiOS|EdgiOS|UCWEB", re.IGNORECASE)

# Regex for tablet detection
_TABLET_RE = re.compile(r"iPad|Tablet|Kindle|Silk|PlayBook|SCH-I800|GT-P", re.IGNORECASE)


def _detect_browser(ua: str) -> str:
    """Detect browser name from UA string. Order is critical."""
    # Samsung Internet (contains Chrome/ — must be before Chrome)
    if "SamsungBrowser/" in ua:
        return "Samsung Internet"

    # Edge mobile variants
    if "EdgA/" in ua:
        return "Edge"
    if "EdgiOS/" in ua:
        return "Edge"

    # Edge desktop (modern Chromium-based, token is "Edg/" not "Edge/")
    if "Edg/" in ua:
        return "Edge"

    # Legacy pre-Chromium Edge (2015–2019)
    if "Edge/" in ua:
        return "Edge"

    # Opera / Opera GX (contains Chrome/ — must be before Chrome)
    if "OPR/" in ua or "OPT/" in ua:
        return "Opera"
    if "Opera" in ua:
        return "Opera"

    # Vivaldi (contains Chrome/ — must be before Chrome)
    if "Vivaldi/" in ua:
        return "Vivaldi"

    # UC Browser (contains Chrome/ — must be before Chrome)
    if "UCBrowser/" in ua:
        return "UC Browser"

    # Firefox (Gecko-based, no Chrome/ token)
    if "Firefox/" in ua:
        return "Firefox"

    # Firefox on iOS (WKWebView wrapper)
    if "FxiOS/" in ua:
        return "Firefox"

    # Chrome on iOS (WKWebView wrapper)
    if "CriOS/" in ua:
        return "Chrome"

    # Chrome (generic — after all Chromium-derived browsers)
    if "Chrome/" in ua:
        return "Chrome"

    # Safari — must check AFTER Chrome since Chrome contains "Safari/537.36"
    # Real Safari has "Version/X.Y" and uses "Safari/605.x" (not 537.36)
    if "Safari/" in ua and "Version/" in ua and "Chrome/" not in ua:
        return "Safari"

    return ""


def _detect_os(ua: str) -> str:
    """Detect OS name from UA string."""
    # iOS — check before macOS (iPad/iPhone contain "like Mac OS X")
    if "iPhone" in ua or "iPod" in ua:
        return "iOS"
    if "iPad" in ua:
        return "iOS"
    if "CriOS/" in ua or "FxiOS/" in ua or "EdgiOS/" in ua:
        # iOS browsers using WKWebView — may not have explicit iPhone/iPad token
        return "iOS"

    # Android — check before Linux (Android contains "Linux")
    if "Android" in ua:
        return "Android"

    # Windows
    if "Windows" in ua:
        return "Windows"

    # ChromeOS — check before Linux (ChromeOS contains "Linux")
    if "CrOS" in ua:
        return "ChromeOS"

    # macOS
    if "Macintosh" in ua or "Mac OS X" in ua:
        return "macOS"

    # Linux
    if "Linux" in ua or "X11" in ua:
        return "Linux"

    return ""


def _detect_device_type(ua: str) -> str:
    """Detect device type: mobile / tablet / tv / bot / desktop."""
    if _BOT_RE.search(ua):
        return "bot"

    if _TV_RE.search(ua):
        return "tv"

    if _TABLET_RE.search(ua):
        return "tablet"

    if _MOBILE_RE.search(ua):
        return "mobile"

    return "desktop"


def parse_user_agent(ua: str) -> tuple[str, str, str]:
    """
    Parse user agent string into (browser, os, device_type).

    Returns empty strings for unknown values — never raises.

    Known limitations:
    - Brave, Arc, Dia, Comet cannot be distinguished from Chrome via UA alone
    - Windows 10 and 11 are identical in UA strings
    - macOS 11–15 all report as 10.15.7 (frozen)
    - iPads in Desktop Mode appear as macOS desktop
    """
    if not ua:
        return "", "", ""

    browser = _detect_browser(ua)
    os_name = _detect_os(ua)
    device_type = _detect_device_type(ua)

    return browser, os_name, device_type
