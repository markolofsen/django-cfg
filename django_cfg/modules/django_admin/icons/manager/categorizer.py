"""Categorize Material Icons by name and metadata."""
from __future__ import annotations

import logging

from .models import IconCategories, IconCodepoints, IconMetaMap  # noqa: F401

logger = logging.getLogger(__name__)

# Keyword → category mapping used as fallback when metadata has no category
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "navigation":    ["dashboard", "menu", "home", "apps", "navigate", "arrow", "chevron", "expand", "more"],
    "users":         ["people", "person", "group", "account", "face", "user", "profile"],
    "documents":     ["description", "text", "article", "note", "folder", "file", "document", "page"],
    "communication": ["chat", "message", "email", "mail", "forum", "comment", "call", "phone"],
    "ai_automation": ["smart", "auto", "sync", "refresh", "repeat", "psychology", "memory", "robot"],
    "actions":       ["play", "pause", "stop", "add", "remove", "edit", "delete", "save", "cancel", "done"],
    "status":        ["check", "error", "warning", "info", "pending", "success", "failed"],
    "media":         ["video", "audio", "music", "photo", "image", "camera", "mic", "volume"],
    "settings":      ["settings", "tune", "build", "construction", "gear", "config"],
    "commerce":      ["shopping", "cart", "store", "payment", "money", "price", "sell"],
    "travel":        ["flight", "hotel", "car", "train", "directions", "map", "location"],
    "social":        ["share", "favorite", "like", "star", "bookmark", "follow"],
    "device":        ["phone", "tablet", "laptop", "desktop", "watch", "tv", "speaker"],
    "editor":        ["format", "text", "font", "color", "align", "indent", "bold", "italic"],
    "maps":          ["map", "location", "place", "pin", "navigation", "gps"],
    "notification":  ["notification", "alert", "bell", "announce"],
    "content":       ["content", "copy", "paste", "cut", "select", "clipboard"],
    "hardware":      ["memory", "storage", "battery", "wifi", "bluetooth", "usb"],
    "image":         ["image", "photo", "picture", "crop", "filter", "camera"],
    "av":            ["play", "pause", "stop", "volume", "music", "video", "audio"],
    "places":        ["home", "work", "school", "hospital", "restaurant", "hotel"],
    "file":          ["folder", "file", "upload", "download", "attach", "archive"],
    "toggle":        ["toggle", "switch", "radio", "checkbox", "on", "off"],
}

def categorize_icons(
    icons_data: IconCodepoints,
    metadata: IconMetaMap,
) -> IconCategories:
    """Return a dict of category → sorted icon names.

    Priority:
    1. metadata['categories'] from Google Fonts
    2. keyword matching against CATEGORY_KEYWORDS
    3. fallback 'other' bucket
    """
    categories: dict[str, list[str]] = {k: [] for k in CATEGORY_KEYWORDS}

    for icon_name in icons_data:
        meta = metadata.get(icon_name)

        # 1. Use metadata categories when available
        placed = False
        for cat in (meta.categories if meta else []):
            cat_key = cat.lower().replace(" ", "_")
            if cat_key in categories:
                categories[cat_key].append(icon_name)
                placed = True
                break

        if placed:
            continue

        # 2. Keyword fallback
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in icon_name.lower() for kw in keywords):
                categories[category].append(icon_name)
                placed = True
                break

        # 3. Other
        if not placed:
            categories.setdefault("other", []).append(icon_name)

    result = {k: sorted(v) for k, v in categories.items() if v}
    logger.info("📂 Categorized icons into %d categories", len(result))
    return result
