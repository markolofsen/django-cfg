"""Thin output abstraction.

Wraps Django's ``stdout`` / ``style`` from a management command, plus
a stdlib logger. Same surface for tests (pass ``None`` everywhere and
inspect the captured messages).

Why not just use logging:
    Management commands need both: structured logs for log aggregators
    AND user-facing stdout with colors. Combining them in one tiny
    helper keeps every other module logger-agnostic.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator, Protocol


class _StyleProto(Protocol):
    """Subset of Django's ``BaseCommand.style`` we use."""

    def SUCCESS(self, msg: str) -> str: ...
    def WARNING(self, msg: str) -> str: ...
    def ERROR(self, msg: str) -> str: ...
    def NOTICE(self, msg: str) -> str: ...


class _StdoutProto(Protocol):
    def write(self, msg: str, style_func: Any = None, ending: str = "\n") -> None: ...


class MigratorLogger:
    """Output adapter — same shape as the old MigrationLogger but typed."""

    def __init__(
        self,
        stdout: _StdoutProto | None = None,
        style: _StyleProto | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.stdout = stdout
        self.style = style
        self.logger = logger or logging.getLogger("django_cfg.migrator")
        self._indent = 0

    # --- Public log methods ---

    def info(self, message: str) -> None:
        self._write(message)
        self.logger.info(message)

    def success(self, message: str) -> None:
        self._write(message, kind="SUCCESS")
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self._write(message, kind="WARNING")
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self._write(message, kind="ERROR")
        self.logger.error(message)

    def notice(self, message: str) -> None:
        self._write(message, kind="NOTICE")
        self.logger.info(message)

    # --- Sections (indented blocks) ---

    @contextmanager
    def section(self, title: str) -> Iterator[None]:
        """Group log lines under a titled section.

        Lines emitted inside the ``with`` block get one indent level.
        """
        self.info(f"━━━ {title} ━━━")
        self._indent += 1
        try:
            yield
        finally:
            self._indent -= 1

    # --- Internal ---

    def _write(self, message: str, *, kind: str | None = None) -> None:
        prefix = "  " * self._indent
        full = f"{prefix}{message}"
        if self.stdout is None:
            return
        styler = None
        if self.style is not None and kind is not None:
            styler = getattr(self.style, kind, None)
        if styler:
            self.stdout.write(styler(full))
        else:
            self.stdout.write(full)
