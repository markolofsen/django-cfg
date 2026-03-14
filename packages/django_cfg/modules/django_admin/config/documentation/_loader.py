"""Path resolution and markdown file scanning utilities."""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import List, Optional, Union


def resolve_path(path: Union[str, Path], app_path: Optional[Path] = None) -> Optional[Path]:
    """
    Resolve file or directory path with support for:
    - Relative to app: "docs"
    - Relative to project: "apps/myapp/docs"
    - Absolute: "/full/path/to/docs"
    """
    if not path:
        return None

    path_obj = Path(path)

    if path_obj.is_absolute():
        return path_obj if path_obj.exists() else None

    from django.conf import settings
    base_dir = Path(settings.BASE_DIR)

    project_path = base_dir / path_obj
    if project_path.exists():
        return project_path

    if app_path:
        app_resolved = app_path / path_obj
        if app_resolved.exists():
            return app_resolved

    if hasattr(settings, "INSTALLED_APPS"):
        for app in settings.INSTALLED_APPS:
            try:
                app_module = importlib.import_module(app.split(".")[0])
                if hasattr(app_module, "__path__"):
                    app_dir = Path(app_module.__path__[0])
                    app_file = app_dir / path_obj
                    if app_file.exists():
                        return app_file
            except (ImportError, AttributeError, IndexError):
                continue

    return None


def scan_markdown_files(directory: Path) -> List[Path]:
    """Recursively scan directory for markdown files."""
    if not directory.is_dir():
        return []
    return [f for f in directory.rglob("*.md") if f.is_file()]


def get_section_title(file_path: Path, base_dir: Path) -> str:
    """
    Generate section title from file path.

    Priority: H1 from content → README → directory name → filename.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass

    relative_path = file_path.relative_to(base_dir)

    if file_path.stem.lower() == "readme":
        if relative_path.parent != Path("."):
            return str(relative_path.parent).replace("/", " / ").replace("_", " ").title()
        return "Overview"

    parts = []
    if relative_path.parent != Path("."):
        parts.append(str(relative_path.parent).replace("/", " / ").replace("_", " ").title())
    parts.append(file_path.stem.replace("_", " ").replace("-", " ").title())
    return " / ".join(parts)
