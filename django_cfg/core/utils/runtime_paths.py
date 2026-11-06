"""
Runtime paths: where django-cfg writes logs and caches.

One resolver for every writer. Nothing here touches the disk except the
explicit ``ensure_dir`` helper, and nothing runs at import time.

Precedence per directory: explicit argument, then config, then env var,
then default.

=========  =======================  ====================  =======================
Dir        Env                      Config                Default
=========  =======================  ====================  =======================
logs       ``DJANGO_CFG_LOG_DIR``   ``logging.log_dir``   none (stdout/stderr);
                                                          file asked via
                                                          ``DJANGO_CFG_LOG_FILE=1``:
                                                          ``user_log_dir(project)``
cache      ``DJANGO_CFG_CACHE_DIR`` ``cache_dir``         ``user_cache_dir(project)``
=========  =======================  ====================  =======================

Migration (one release): with no override set, an existing ``./logs`` or
``./.cache`` in the working directory is still used, with one warning that
names the env var. The next release removes that fallback.
"""
from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

ENV_LOG_DIR = "DJANGO_CFG_LOG_DIR"
ENV_LOG_FILE = "DJANGO_CFG_LOG_FILE"
ENV_LOG_FORMAT = "DJANGO_CFG_LOG_FORMAT"
ENV_LOG_LEVEL = "DJANGO_CFG_LOG_LEVEL"
ENV_LOG_ROTATE = "DJANGO_CFG_LOG_ROTATE"
ENV_CACHE_DIR = "DJANGO_CFG_CACHE_DIR"

#: Deprecated aliases (recognised, warn once).
LEGACY_ENV_LOG_TO_TMP = "DJANGO_LOG_TO_TMP"
LEGACY_ENV_LLM_CACHE_DIR = "CMDOP_LLM_CACHE_DIR"

_TRUTHY = ("1", "true", "yes", "on")

_warned: set[str] = set()
_log = logging.getLogger("django_cfg.runtime_paths")


def warn_once(key: str, message: str) -> bool:
    """Log ``message`` at WARNING the first time ``key`` is seen. Returns True if it logged."""
    if key in _warned:
        return False
    _warned.add(key)
    _log.warning(message)
    return True


def _reset_warnings() -> None:
    """Forget which warnings were issued (tests)."""
    _warned.clear()


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def project_name() -> str:
    """Top package of ``DJANGO_SETTINGS_MODULE``, else the working directory name."""
    module = os.environ.get("DJANGO_SETTINGS_MODULE", "").strip()
    if module:
        return module.split(".")[0]
    return Path.cwd().name or "django_cfg"


def _current_config():
    try:
        from django_cfg.core.state import get_current_config

        return get_current_config()
    except Exception:
        return None


def _config_log_dir() -> Optional[str]:
    cfg = _current_config()
    logging_cfg = getattr(cfg, "logging", None) if cfg is not None else None
    value = getattr(logging_cfg, "log_dir", None) if logging_cfg is not None else None
    return str(value) if value else None


def _config_cache_dir() -> Optional[str]:
    cfg = _current_config()
    value = getattr(cfg, "cache_dir", None) if cfg is not None else None
    return str(value) if value else None


def default_log_dir() -> Path:
    """Per-user log directory for this project (only used when a file was asked for)."""
    from platformdirs import user_log_dir

    return Path(user_log_dir(project_name()))


def default_cache_root() -> Path:
    """Per-user cache directory for this project."""
    from platformdirs import user_cache_dir

    return Path(user_cache_dir(project_name()))


def resolve_log_dir(explicit: Optional[str | os.PathLike] = None) -> Optional[Path]:
    """
    Directory for log files, or ``None`` when logs go to stdout/stderr only.

    Does not create anything.
    """
    if explicit:
        return Path(explicit)
    if value := _config_log_dir():
        return Path(value)
    if value := os.environ.get(ENV_LOG_DIR, "").strip():
        return Path(value)
    if env_flag(ENV_LOG_FILE):
        return default_log_dir()
    legacy = Path.cwd() / "logs"
    if legacy.is_dir():
        warn_once(
            "legacy-logs",
            f"django-cfg is still writing logs to {legacy}. This fallback goes away in the next "
            f"release: set {ENV_LOG_DIR}={legacy} to keep it, or remove the logs/ folder to log to stdout.",
        )
        return legacy
    return None


def resolve_cache_dir(*parts: str, explicit: Optional[str | os.PathLike] = None) -> Path:
    """
    ``<cache root>/<parts>``. Does not create anything.

    Root precedence: explicit argument, config ``cache_dir``, ``DJANGO_CFG_CACHE_DIR``,
    legacy ``./.cache`` (warns once), ``user_cache_dir(project)``.
    """
    root: Optional[Path] = None
    if explicit:
        root = Path(explicit)
    elif value := _config_cache_dir():
        root = Path(value)
    elif value := os.environ.get(ENV_CACHE_DIR, "").strip():
        root = Path(value)
    else:
        legacy = Path.cwd() / ".cache"
        if legacy.is_dir():
            warn_once(
                "legacy-cache",
                f"django-cfg is still caching in {legacy}. This fallback goes away in the next "
                f"release: set {ENV_CACHE_DIR}={legacy} to keep it.",
            )
            root = legacy
        else:
            root = default_cache_root()
    return root.joinpath(*parts) if parts else root


def _writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    return os.access(path, os.W_OK)


def ensure_dir(path: Path) -> Path:
    """
    Create ``path`` (with parents) and return it. When it is not writable,
    return a directory of the same tail under the system temp dir and warn once.
    """
    if _writable(path):
        return path
    fallback = Path(tempfile.gettempdir()) / "django_cfg" / project_name() / path.name
    warn_once(f"unwritable:{path}", f"django-cfg cannot write to {path}; using {fallback} instead.")
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def log_format() -> str:
    """``text`` (default) or ``json``."""
    value = os.environ.get(ENV_LOG_FORMAT, "").strip().lower()
    if not value:
        cfg = _current_config()
        value = str(getattr(getattr(cfg, "logging", None), "format", "") or "").lower()
    return "json" if value == "json" else "text"


def warn_deprecated_env() -> None:
    """Warn once for each deprecated env var that is still set."""
    if os.environ.get(LEGACY_ENV_LOG_TO_TMP) is not None:
        warn_once(
            "env-log-to-tmp",
            f"{LEGACY_ENV_LOG_TO_TMP} is deprecated and ignored: the /tmp/djangocfg/debug.log "
            f"mirror was removed. Use {ENV_LOG_DIR} for a log file.",
        )
    if os.environ.get(LEGACY_ENV_LLM_CACHE_DIR) is not None:
        warn_once(
            "env-llm-cache-dir",
            f"{LEGACY_ENV_LLM_CACHE_DIR} is deprecated: use {ENV_CACHE_DIR} (the cache root).",
        )


__all__ = [
    "ENV_CACHE_DIR",
    "ENV_LOG_DIR",
    "ENV_LOG_FILE",
    "ENV_LOG_FORMAT",
    "ENV_LOG_LEVEL",
    "ENV_LOG_ROTATE",
    "LEGACY_ENV_LLM_CACHE_DIR",
    "LEGACY_ENV_LOG_TO_TMP",
    "default_cache_root",
    "default_log_dir",
    "ensure_dir",
    "env_flag",
    "log_format",
    "project_name",
    "resolve_cache_dir",
    "resolve_log_dir",
    "warn_deprecated_env",
    "warn_once",
]
