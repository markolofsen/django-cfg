"""Terminal output, in one place so the agent modules do not each grow a copy.

Writes through a Django command's ``stdout``/``stderr`` when given one, so
output is captured in tests and styled consistently with every other command.
"""

from __future__ import annotations

import sys
from typing import Any, Optional

BOLD, GREEN, GREY, RED, YELLOW, RESET = (
    "\033[1m",
    "\033[32m",
    "\033[90m",
    "\033[31m",
    "\033[33m",
    "\033[0m",
)


class Console:
    """Output sink. ``command`` is a Django ``BaseCommand`` when there is one."""

    def __init__(self, command: Optional[Any] = None) -> None:
        self._command = command

    def _write(self, text: str, *, error: bool = False) -> None:
        if self._command is not None:
            stream = self._command.stderr if error else self._command.stdout
            stream.write(text)
            return
        print(text, file=sys.stderr if error else sys.stdout)

    def plain(self, msg: str = "") -> None:
        self._write(msg)

    def bold(self, msg: str) -> None:
        self._write(f"{BOLD}{msg}{RESET}")

    def ok(self, msg: str) -> None:
        self._write(f"  {GREEN}✓{RESET} {msg}")

    def warn(self, msg: str) -> None:
        self._write(f"  {YELLOW}!{RESET} {msg}")

    def err(self, msg: str) -> None:
        self._write(f"  {RED}✗{RESET} {msg}", error=True)

    def skip(self, msg: str) -> None:
        self._write(f"  {GREY}–{RESET} {msg}")


def mask(secret: Optional[str]) -> str:
    """Show enough of a key to recognise it, never enough to use it.

    Printed so an operator can confirm *which* key was picked up — the whole
    point of resolving it automatically is that nobody typed it, so nobody has
    seen it. Short values are hidden entirely rather than mostly revealed.
    """
    if not secret:
        return "(none)"
    return f"{secret[:4]}…{secret[-4:]}" if len(secret) > 12 else "…"
