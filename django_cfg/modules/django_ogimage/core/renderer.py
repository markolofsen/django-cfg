"""OG image renderer using PicTex (Flexbox/HarfBuzz).

Each visual zone is built in its own function — background, accent bar,
branding overlay, and content block — then composed on a Canvas.

Requires pictex to be installed (included with django-cfg[full]).
"""
from __future__ import annotations

import io
import logging
import os
import tempfile
from typing import Any

from .fonts import FontSpec, get_all_fallback_fonts, get_font_spec
from .layout import DEFAULT, OGLayoutPreset, corner_to_fixed_pos
from .params import OGImageParams

logger = logging.getLogger(__name__)


# ── Color helpers ─────────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_light_color(hex_color: str) -> bool:
    """ITU-R BT.709 luminance > 128 → light background."""
    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b > 128


# ── Pre-resolved color palette ────────────────────────────────────────────────

class _Colors:
    """Colors derived from params.style + params color fields."""

    def __init__(self, params: OGImageParams) -> None:
        effective_bg = "#ffffff" if params.style == "light" else params.bg_color
        light = _is_light_color(effective_bg)
        self.title: str = "#111827" if light else params.text_color
        self.description: str = "#6b7280" if light else "#94a3b8"
        self.site_name: str = "#374151" if light else "#e2e8f0"


# ── Public entry point ────────────────────────────────────────────────────────

def render(
    params: OGImageParams,
    logo_bytes: bytes | None = None,
    site_name: str = "",
    layout: OGLayoutPreset = DEFAULT,
) -> bytes:
    """Render OG card using PicTex. Returns PNG bytes."""
    font_spec = get_font_spec(params.locale)
    fallbacks = get_all_fallback_fonts(font_spec.bold)
    colors = _Colors(params)

    tmp_logo_path: str | None = None
    try:
        background = _build_background(params, layout)
        accent_bar = _build_accent_bar(params, layout)
        brand_el, tmp_logo_path = _build_brand_overlay(logo_bytes, site_name, layout, colors, font_spec)
        content_el = _build_content(params, layout, colors, font_spec)

        overlays: list[Any] = [e for e in [background, accent_bar, brand_el, content_el] if e is not None]

        from pictex import Canvas  # type: ignore[import-untyped]
        canvas: Any = Canvas().font_family(font_spec.bold)
        if fallbacks:
            canvas.font_fallbacks(*fallbacks)

        buf = io.BytesIO()
        canvas.render(*overlays).to_pillow().save(buf, format="PNG")
        return buf.getvalue()

    finally:
        if tmp_logo_path and os.path.exists(tmp_logo_path):
            os.unlink(tmp_logo_path)


# ── Element builders ──────────────────────────────────────────────────────────

def _build_background(params: OGImageParams, layout: OGLayoutPreset) -> Any:
    from pictex import Column, LinearGradient  # type: ignore[import-untyped]

    base: Any = Column().size(params.width, params.height).padding(layout.padding_y, layout.padding_x)

    if params.style == "light":
        return base.background_color("white").border(1, "#e5e7eb")

    return base.background_color(
        LinearGradient(
            colors=[params.bg_color, params.bg_color2],
            start_point=(0.5, 0.0),
            end_point=(0.5, 1.0),
        )
    )


def _build_accent_bar(params: OGImageParams, layout: OGLayoutPreset) -> Any:
    if layout.accent_position == "none":
        return None

    from pictex import Row  # type: ignore[import-untyped]

    edge: dict[str, int] = {"top": 0} if layout.accent_position == "top" else {"bottom": 0}
    return Row().size("100%", 4).background_color(params.accent_color).fixed_position(left=0, **edge)


def _build_brand_overlay(
    logo_bytes: bytes | None,
    site_name: str,
    layout: OGLayoutPreset,
    colors: _Colors,
    font_spec: FontSpec,
) -> tuple[Any, str | None]:
    """Returns (brand_element | None, tmp_logo_path | None)."""
    if layout.brand_position == "none" or (not logo_bytes and not site_name):
        return None, None

    from pictex import Image, Row, Text  # type: ignore[import-untyped]

    tmp_logo_path: str | None = None
    children: list[Any] = []

    if logo_bytes:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(logo_bytes)
        tmp.close()
        tmp_logo_path = tmp.name
        children.append(
            Image(tmp_logo_path).size(layout.logo_size, layout.logo_size).border_radius(6)
        )

    if site_name:
        children.append(
            Text(site_name[:60])
            .font_size(layout.site_name_font_size)
            .font_weight(600)
            .color(colors.site_name)
        )

    pos = corner_to_fixed_pos(layout.brand_position, layout.padding_x, layout.padding_y)
    brand_el: Any = Row(*children).align_items("center").gap(12).fixed_position(**pos)

    if font_spec.is_rtl:
        brand_el = brand_el.direction("rtl")

    return brand_el, tmp_logo_path


def _build_content(
    params: OGImageParams,
    layout: OGLayoutPreset,
    colors: _Colors,
    font_spec: FontSpec,
) -> Any:
    from pictex import Column, Text  # type: ignore[import-untyped]

    px, py = layout.padding_x, layout.padding_y

    title_el: Any = (
        Text(params.title[:200])
        .font_size(layout.title_font_size)
        .font_weight(700)
        .color(colors.title)
        .text_wrap("normal")
        .line_height(1.2)
    )
    if font_spec.is_rtl:
        title_el = title_el.text_align("right").direction("rtl")

    children: list[Any] = [title_el]

    if params.description:
        desc_el: Any = (
            Text(params.description[:150])
            .font_size(layout.description_font_size)
            .color(colors.description)
            .text_wrap("normal")
            .line_height(1.4)
            .margin(24, 0, 0, 0)
        )
        if font_spec.is_rtl:
            desc_el = desc_el.text_align("right").direction("rtl")
        children.append(desc_el)

    content: Any = (
        Column(*children)
        .size(params.width - px * 2, params.height - py * 2)
        .justify_content(layout.content_align)
        .gap(0)
        .fixed_position(top=py, left=px)
    )
    if font_spec.is_rtl:
        content = content.direction("rtl").align_items("end")

    return content
