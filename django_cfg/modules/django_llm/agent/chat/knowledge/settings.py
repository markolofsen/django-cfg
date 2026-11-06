"""Where the knowledge folder is, and the one cache of disk bases per worker.

* `CHAT__KNOWLEDGE_DIR` (Django setting, then environment variable): the folder. Relative values are taken from `BASE_DIR`.
  Unset: `<BASE_DIR>/knowledge`. A missing folder is "off", never an error.
* `CHAT__KNOWLEDGE_LANGUAGE`: the language the files are written in (default English); the prompt tells the model.
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

from django_cfg.modules.django_llm.agent.chat.knowledge.base import DiskKnowledgeBase

log = logging.getLogger(__name__)
DIR_SETTING = "CHAT__KNOWLEDGE_DIR"
LANGUAGE_SETTING = "CHAT__KNOWLEDGE_LANGUAGE"
_bases: dict[str, DiskKnowledgeBase] = {}
_lock = threading.Lock()
_warned: set[str] = set()


def _setting(name: str) -> Any:
    from django.conf import settings

    value = getattr(settings, name, None)
    return value if value not in (None, "") else (os.environ.get(name) or None)


def configured_dir() -> Path | None:
    """Where the knowledge folder is meant to be (it may not exist), or `None` when nothing says."""
    from django.conf import settings

    base = getattr(settings, "BASE_DIR", None)
    configured = _setting(DIR_SETTING)
    path = Path(str(configured)) if configured else (Path(str(base)) / "knowledge" if base else None)
    if path is not None and not path.is_absolute() and base:
        path = Path(str(base)) / path
    return path


def knowledge_dir() -> Path | None:
    """The configured knowledge folder, or `None` when there is none on disk."""
    path = configured_dir()
    return path if path is not None and path.is_dir() else None


def warn_once(message: str) -> None:
    """A WARNING once per worker per message (a kind asks on every request)."""
    with _lock:
        if message in _warned:
            return
        _warned.add(message)
    log.warning(message)


def warn_missing() -> None:
    where = configured_dir()
    warn_once(
        f"chat knowledge: a kind has knowledge on but the folder {where or '<BASE_DIR>/knowledge'} does not exist; "
        f"the kind answers without a knowledge base (is the folder copied into the image? override with {DIR_SETTING})"
    )


def knowledge_language() -> str:
    return str(_setting(LANGUAGE_SETTING) or "English")


def disk_base(root: str | Path) -> DiskKnowledgeBase:
    """The shared base for a folder: one index per worker, however many requests ask."""
    key = str(Path(root).resolve())
    with _lock:
        if key not in _bases:
            _bases[key] = DiskKnowledgeBase(key)
            log.info("chat knowledge: using folder %s", key)
        return _bases[key]


def forget_bases() -> None:
    with _lock:
        _bases.clear()
        _warned.clear()
