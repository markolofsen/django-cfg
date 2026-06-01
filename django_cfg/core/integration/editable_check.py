"""
Editable-install diagnostics for django-cfg.

Dev-only safety net for a common gotcha: a developer installs django-cfg in
editable mode via ``scripts/install_local_djangocfg.sh`` (which removes
``site-packages/django_cfg`` so the ``.pth`` editable link wins), but then a
plain ``uv sync`` / ``uv run`` silently reinstalls the PyPI copy on top. The
import then resolves to ``site-packages`` instead of the local source, so
``project_apps`` are no longer injected and apps "disappear" with no warning.

This module detects that mismatch heuristically and only ever emits a warning —
it never raises and never alters behaviour. It is meant to be called from the
dev/DEBUG startup banner and from the ``check_editable`` management command.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Env marker that install_local_djangocfg.sh may write so we know editable was
# intended even if the ~/djangocfg symlink is absent. Purely optional.
EDITABLE_MARKER_ENV = "DJANGO_CFG_EDITABLE_EXPECTED"


@dataclass
class EditableStatus:
    """Result of the editable-vs-PyPI heuristic."""

    loaded_path: Optional[str]
    """Absolute path to the loaded django_cfg package dir (django_cfg.__file__ parent)."""

    is_site_packages: bool
    """True if django_cfg was loaded from a site-packages / dist-packages tree."""

    editable_expected: bool
    """True if there is a signal the developer intended an editable install."""

    expected_source: Optional[str]
    """Resolved local editable source path, if one was detected (~/djangocfg)."""

    @property
    def mismatch(self) -> bool:
        """True when editable was expected but the PyPI copy is loaded instead."""
        return self.editable_expected and self.is_site_packages


def _loaded_django_cfg_dir() -> Optional[str]:
    """Return the directory django_cfg was actually imported from, or None."""
    try:
        import django_cfg

        file = getattr(django_cfg, "__file__", None)
        if not file:
            return None
        return str(Path(file).resolve().parent)
    except Exception:
        return None


def _is_site_packages(path: Optional[str]) -> bool:
    """Heuristic: does this path live inside an installed-packages tree?"""
    if not path:
        return False
    normalized = path.replace("\\", "/")
    return "/site-packages/" in normalized or "/dist-packages/" in normalized


def _detect_editable_source() -> Optional[str]:
    """
    Find the local editable django-cfg source the developer likely intended.

    Mirrors the candidate logic in install_local_djangocfg.sh: the ~/djangocfg
    symlink (or directory) is the canonical signal that this machine develops
    django-cfg locally. Returns the resolved source path if it looks like a
    django-cfg checkout, else None.
    """
    home = Path.home()
    candidates = [
        home / "djangocfg",
        home / "djangocfg" / "projects" / "django-cfg",
    ]
    for candidate in candidates:
        try:
            pyproject = candidate / "pyproject.toml"
            if pyproject.is_file():
                text = pyproject.read_text(encoding="utf-8", errors="ignore")
                if "django-cfg" in text or "django_cfg" in text:
                    return str(candidate.resolve())
        except Exception:
            continue
    return None


def get_editable_status() -> EditableStatus:
    """
    Compute the editable-vs-PyPI status using only filesystem/env heuristics.

    Never raises. "Editable expected" is true if EITHER the opt-in env marker is
    set OR a local ~/djangocfg source checkout is present on this machine.
    """
    loaded_path = _loaded_django_cfg_dir()
    is_sp = _is_site_packages(loaded_path)

    env_marker = os.getenv(EDITABLE_MARKER_ENV, "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    source = _detect_editable_source()

    editable_expected = bool(env_marker or source)

    return EditableStatus(
        loaded_path=loaded_path,
        is_site_packages=is_sp,
        editable_expected=editable_expected,
        expected_source=source,
    )
