"""
Auto-display methods for Django ImageField / FileField.

Shows clickable image thumbnails (with modal zoom) or download links
for non-image files.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Tuple

from django.utils.safestring import SafeString, mark_safe

if TYPE_CHECKING:
    from ....config import AdminConfig

logger = logging.getLogger(__name__)

_IMAGE_EXTS = frozenset(("jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "avif", "ico"))


def create_imagefield_display_methods(
    cls: Any,
    readonly_fields: list[str],
    config: AdminConfig,
) -> Tuple[list[str], Dict[str, str], bool]:
    """
    Auto-create display methods for readonly ImageField / FileField.

    Returns:
        (updated_readonly_fields, {field_name: method_name}, has_image_preview)
    """
    model = config.model
    if not model:
        return list(readonly_fields), {}, False

    updated = list(readonly_fields)
    replacements: Dict[str, str] = {}
    has_preview = False

    for field_name in readonly_fields:
        try:
            field = model._meta.get_field(field_name)  # type: ignore[union-attr]
            if field.__class__.__name__ not in ("ImageField", "FileField"):
                continue

            method_name = f"_auto_display_{field_name}"
            setattr(cls, method_name, _make_image_method(field_name, field))
            replacements[field_name] = method_name
            has_preview = True

            try:
                updated[updated.index(field_name)] = method_name
            except ValueError:
                pass

            logger.debug("Created image display method '%s' for '%s'", method_name, field_name)

        except Exception as exc:
            logger.debug("Skipped image display for '%s': %s", field_name, exc)

    return updated, replacements, has_preview


def _make_image_method(fname: str, field_obj: Any) -> Any:
    def image_display_method(self: Any, obj: Any) -> SafeString | str:
        """Display ImageField/FileField with preview card or download link."""
        from ....utils import ImagePreviewDisplay

        value = getattr(obj, fname, None)
        if not value:
            return "—"

        image_url: str = value.url if hasattr(value, "url") else str(value)
        if not image_url:
            return "—"

        is_image = field_obj.__class__.__name__ == "ImageField"
        ext = image_url.lower().split("?")[0].rsplit(".", 1)[-1]
        if not is_image:
            is_image = ext in _IMAGE_EXTS

        if is_image:
            file_size: str | None = None
            dimensions: str | None = None

            for size_field in ("file_size", "size", f"{fname}_size"):
                size_val = getattr(obj, size_field, None)
                if size_val:
                    if isinstance(size_val, (int, float)):
                        if size_val >= 1024 * 1024:
                            file_size = f"{size_val / (1024 * 1024):.1f} MB"
                        elif size_val >= 1024:
                            file_size = f"{size_val / 1024:.1f} KB"
                        else:
                            file_size = f"{size_val} B"
                    else:
                        file_size = str(size_val)
                    break

            width = getattr(obj, "width", None) or getattr(obj, f"{fname}_width", None)
            height = getattr(obj, "height", None) or getattr(obj, f"{fname}_height", None)
            if width and height:
                dimensions = f"{width}×{height}"

            return mark_safe(ImagePreviewDisplay.render_card(  # type: ignore[return-value]
                image_url,
                config={
                    "thumbnail_width": "120px",
                    "thumbnail_height": "120px",
                    "show_info": True,
                    "zoom_enabled": True,
                    "file_size": file_size,
                    "dimensions": dimensions,
                },
            ))

        filename = image_url.split("/")[-1].split("?")[0]
        return mark_safe(  # type: ignore[return-value]
            f'<a href="{image_url}" target="_blank" '
            f'class="inline-flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:underline">'
            f'<span class="material-symbols-outlined text-sm">attachment</span>'
            f"{filename}</a>"
        )

    image_display_method.short_description = (  # type: ignore[attr-defined]
        getattr(field_obj, "verbose_name", None) or fname.replace("_", " ").title()
    )
    return image_display_method
