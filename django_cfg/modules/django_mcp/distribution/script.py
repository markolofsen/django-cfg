"""``install.sh``: a fixed template with three substituted values.

The script is served to anyone, so the only things that go into it are what the
caller already knows (alias, name, URL) plus the auth mode. A value that does not
pass its check is refused outright: a half-sanitised script is worse than a 404.
"""

from __future__ import annotations

import re
from pathlib import Path

from django_cfg.modules.django_mcp.__cfg__ import ALIAS_PATTERN

_TEMPLATE = Path(__file__).with_name("install.sh.tmpl")

_ALIAS = re.compile(ALIAS_PATTERN)
#: An http(s) endpoint written with URL characters only. No quote, backslash,
#: backtick, space, ``$``, ``?`` or ``#``: the URL ends up inside shell single
#: quotes and a TOML string, and an endpoint has no query.
_URL = re.compile(r"^https?://[A-Za-z0-9._~:/%@\[\]-]+/$")
_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f  ]")

CONTENT_TYPE = "text/x-shellscript; charset=utf-8"


class UnsafeValue(ValueError):
    """A value that must not reach the script."""


def shell_quote(value: str) -> str:
    """``value`` as one POSIX single-quoted word."""
    return "'" + value.replace("'", "'\\''") + "'"


def clean_name(name: str, fallback: str) -> str:
    """A display name on one line, without control characters."""
    text = re.sub(r"\s+", " ", _CONTROL.sub(" ", name or "")).strip()[:80]
    return text or fallback


def render_install_script(*, alias: str, name: str, url: str, oauth: bool) -> str:
    if not _ALIAS.match(alias or ""):
        raise UnsafeValue(f"alias {alias!r} does not match {ALIAS_PATTERN}")
    if not _URL.match(url or ""):
        raise UnsafeValue(f"endpoint URL {url!r} is not a plain http(s) URL ending in '/'")
    values = {
        "@@URL_RAW@@": url,
        "@@ALIAS@@": shell_quote(alias),
        "@@NAME@@": shell_quote(clean_name(name, alias)),
        "@@URL@@": shell_quote(url),
        "@@AUTH@@": "oauth" if oauth else "key",
    }
    text = _TEMPLATE.read_text(encoding="utf-8")
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    return text
