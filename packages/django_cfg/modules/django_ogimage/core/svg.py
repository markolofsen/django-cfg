"""SVG rasterization utilities.

Converts SVG bytes to PNG using skia-python (SVGDOM).
Raises on failure — callers should catch and handle (e.g. skip logo).

# cairosvg fallback intentionally omitted — not a declared dependency.
# To add optional cairosvg support, declare it in pyproject.toml
# [project.optional-dependencies] and guard with try/except ImportError.
"""
from __future__ import annotations


def _is_svg(data: bytes) -> bool:
    head = data[:512].lstrip()
    return head.startswith(b"<?xml") or head.startswith(b"<svg") or b"<svg" in head[:512]


def _svg_to_png(svg_bytes: bytes, size: int = 256) -> bytes:
    """Rasterize SVG bytes to a square PNG of the given size using skia-python."""
    import skia  # type: ignore[import-untyped]

    svg_stream = skia.MemoryStream(svg_bytes)
    dom = skia.SVGDOM.MakeFromStream(svg_stream)
    if dom is None:
        raise ValueError("skia.SVGDOM could not parse SVG bytes")

    dom.setContainerSize(skia.Size(size, size))

    surface = skia.Surface(size, size)
    with surface as canvas:
        canvas.clear(skia.ColorTRANSPARENT)
        dom.render(canvas)

    return bytes(surface.makeImageSnapshot().encodeToData())
