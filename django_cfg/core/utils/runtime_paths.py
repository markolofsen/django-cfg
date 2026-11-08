"""
Runtime paths: where django-cfg writes logs and caches.

One resolver for every writer. Nothing here touches the disk except the
explicit ``ensure_dir`` helper, and nothing runs at import time.

Precedence per setting: explicit argument, then ``DjangoConfig`` (the typed
``logging`` block: ``dir``, ``level``, ``rotate_mb``, ``backups``, ``retain_days``),
then the ``DJANGO_CFG_LOG_*`` env var, then the built-in default.

=========  =======================  ====================  =======================
Dir        Env                      Config                Default
=========  =======================  ====================  =======================
logs       ``DJANGO_CFG_LOG_DIR``   ``logging.dir``       general logs: stdout
                                                          only; the monitor-event
                                                          file: ``/var/log/<app>``
                                                          if writable, else the
                                                          per-user state dir, else
                                                          no file (one warning)
cache      ``DJANGO_CFG_CACHE_DIR`` ``cache_dir``         ``user_cache_dir(project)``
=========  =======================  ====================  =======================

No default is ever inside the project tree, and there is no ``./logs`` or ``./.cache``
fallback and no alias.

Every file django-cfg opens is bounded: size-based rotation (``rotate_mb`` x ``backups``)
and a startup prune (``retain_days``, ``DJANGO_CFG_LOG_DIR_MAX_BYTES``), see
``modules/django_logging/maintenance.py``.
"""
from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

ENV_LOG_DIR = "DJANGO_CFG_LOG_DIR"
ENV_LOG_FORMAT = "DJANGO_CFG_LOG_FORMAT"
ENV_LOG_LEVEL = "DJANGO_CFG_LOG_LEVEL"
ENV_CACHE_DIR = "DJANGO_CFG_CACHE_DIR"
ENV_LOG_ROTATE_MB = "DJANGO_CFG_LOG_ROTATE_MB"
ENV_LOG_BACKUPS = "DJANGO_CFG_LOG_BACKUPS"
ENV_LOG_RETAIN_DAYS = "DJANGO_CFG_LOG_RETAIN_DAYS"
ENV_LOG_DIR_MAX_BYTES = "DJANGO_CFG_LOG_DIR_MAX_BYTES"
ENV_LOG_PRUNE = "DJANGO_CFG_LOG_PRUNE"

DEFAULT_LOG_ROTATE_MB = 10
DEFAULT_LOG_BACKUPS = 5
DEFAULT_LOG_RETAIN_DAYS = 14
DEFAULT_LOG_DIR_MAX_BYTES = 500 * 1024 * 1024

#: Deprecated aliases (recognised, warn once).
LEGACY_ENV_LOG_TO_TMP = "DJANGO_LOG_TO_TMP"
LEGACY_ENV_LLM_CACHE_DIR = "CMDOP_LLM_CACHE_DIR"

#: Where a daemon-style app logs on Linux; a module attribute so tests can point it elsewhere.
SYSTEM_LOG_ROOT = Path("/var/log")

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


def _config_logging(name: str):
    """A field of ``DjangoConfig.logging``, or None when unset / no config yet."""
    cfg = _current_config()
    logging_cfg = getattr(cfg, "logging", None) if cfg is not None else None
    return getattr(logging_cfg, name, None) if logging_cfg is not None else None


def _config_log_dir() -> Optional[str]:
    value = _config_logging("dir")
    return str(value) if value else None


def _config_cache_dir() -> Optional[str]:
    cfg = _current_config()
    value = getattr(cfg, "cache_dir", None) if cfg is not None else None
    return str(value) if value else None


def user_state_log_dir() -> Path:
    """Per-user log directory: ``~/.local/state/<app>/log`` (Linux), ``~/Library/Logs/<app>`` (macOS)."""
    from platformdirs import user_log_dir

    return Path(user_log_dir(project_name()))


default_log_dir = user_state_log_dir


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
    return None


def env_int(name: str, default: int) -> int:
    """Non-negative integer from the environment; ``default`` when unset or invalid."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value >= 0 else default


def _setting_int(config_name: str, env_name: str, default: int) -> int:
    """config (``logging.<config_name>``), then env, then default."""
    value = _config_logging(config_name)
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return env_int(env_name, default)


def log_rotate_bytes() -> int:
    """Size at which a django-cfg log file rotates (``rotate_mb``; 0 = never, for logrotate)."""
    return _setting_int("rotate_mb", ENV_LOG_ROTATE_MB, DEFAULT_LOG_ROTATE_MB) * 1024 * 1024


def log_backups() -> int:
    return _setting_int("backups", ENV_LOG_BACKUPS, DEFAULT_LOG_BACKUPS)


def log_retain_days() -> int:
    return _setting_int("retain_days", ENV_LOG_RETAIN_DAYS, DEFAULT_LOG_RETAIN_DAYS)


def usable_dir(path: Path) -> bool:
    """Could files be written under ``path``? Looks, creates nothing."""
    try:
        probe = path
        while not probe.exists():
            if probe.parent == probe:
                return False
            probe = probe.parent
        return probe.is_dir() and os.access(probe, os.W_OK | os.X_OK)
    except OSError:
        return False


def _inside_project(path: Path) -> bool:
    try:
        path.resolve().relative_to(Path.cwd().resolve())
        return True
    except (ValueError, OSError):
        return False


def resolve_monitor_log_dir() -> Optional[Path]:
    """
    Directory of the monitor-event file (``djangocfg/monitor.log``), or ``None`` when no
    file can be written and events go to stdout only (one warning).

    Order: ``logging.dir`` / ``DJANGO_CFG_LOG_DIR``, then ``/var/log/<app>``, then the
    per-user state dir. The two defaults are skipped when they sit inside the project
    tree. Creates nothing.
    """
    configured = resolve_log_dir()
    if configured is not None:
        if usable_dir(configured):
            return configured
        warn_once(
            f"monitor-dir:{configured}",
            f"django-cfg cannot write to the configured log directory {configured}; trying the defaults.",
        )
    app = project_name()
    for candidate in (SYSTEM_LOG_ROOT / app, user_state_log_dir()):
        if not _inside_project(candidate) and usable_dir(candidate):
            return candidate
    warn_once(
        "monitor-dir-none",
        f"django-cfg found no writable directory for the monitor event log (tried {SYSTEM_LOG_ROOT / app} and "
        f"{user_state_log_dir()}); monitor events go to stdout only. Set {ENV_LOG_DIR} or logging.dir.",
    )
    return None


def _dir_size(path: Path) -> int:
    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except OSError:
                continue
    except OSError:
        pass
    return total


def resolve_cache_dir(*parts: str, explicit: Optional[str | os.PathLike] = None) -> Path:
    """
    ``<cache root>/<parts>``. Does not create anything.

    Root precedence: explicit argument, config ``cache_dir``, ``DJANGO_CFG_CACHE_DIR``,
    ``user_cache_dir(project)``.
    """
    root: Optional[Path] = None
    if explicit:
        root = Path(explicit)
    elif value := _config_cache_dir():
        root = Path(value)
    elif value := os.environ.get(ENV_CACHE_DIR, "").strip():
        root = Path(value)
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
    """``json`` or ``text``.

    Config ``logging.format``, then the env var; with neither, ``json`` when
    stderr is not a terminal (a container, systemd, a pipe) and ``text`` at a
    developer's terminal.
    """
    value = str(_config_logging("format") or "").lower()
    if value not in ("json", "text"):
        value = os.environ.get(ENV_LOG_FORMAT, "").strip().lower()
    if value in ("json", "text"):
        return value
    try:
        return "text" if sys.stderr.isatty() else "json"
    except Exception:
        return "json"


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
    "ENV_LOG_FORMAT",
    "ENV_LOG_LEVEL",
    "DEFAULT_LOG_BACKUPS",
    "DEFAULT_LOG_DIR_MAX_BYTES",
    "DEFAULT_LOG_RETAIN_DAYS",
    "DEFAULT_LOG_ROTATE_MB",
    "ENV_LOG_BACKUPS",
    "ENV_LOG_DIR_MAX_BYTES",
    "ENV_LOG_RETAIN_DAYS",
    "ENV_LOG_ROTATE_MB",
    "ENV_LOG_PRUNE",
    "LEGACY_ENV_LLM_CACHE_DIR",
    "LEGACY_ENV_LOG_TO_TMP",
    "default_cache_root",
    "default_log_dir",
    "ensure_dir",
    "env_flag",
    "env_int",
    "log_backups",
    "log_retain_days",
    "log_rotate_bytes",
    "resolve_monitor_log_dir",
    "usable_dir",
    "user_state_log_dir",
    "log_format",
    "project_name",
    "resolve_cache_dir",
    "resolve_log_dir",
    "warn_deprecated_env",
    "warn_once",
]
