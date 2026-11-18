"""One reading of "which mailer is configured", for Django 5.2 and 6.1+.

Django 6.1 replaced ``EMAIL_BACKEND`` and the other ``EMAIL_*`` connection
settings with ``MAILERS`` and ``django.core.mail.mailers``; the old names are
removed in Django 2028. When ``MAILERS`` is defined, reading any of the old
settings raises ``AttributeError``, and ``getattr(settings, "EMAIL_BACKEND", "")``
quietly answers ``""``. Code that asks "is this locmem?" or "which host?" that way
gets a wrong answer without an error, so it asks here instead.

``EmailConfig`` emits ``MAILERS`` on 6.1+ and ``EMAIL_*`` on 5.2
(``models/services/email.py``). A project that writes its own email settings
may still use ``EMAIL_*`` on 6.1; that is read too, with Django's own warning.
"""

from __future__ import annotations

from typing import Any, Dict

import django
from django.conf import settings

#: The documented test for mailers support ("Migrating email to mailers").
from ...models.services.email import HAS_MAILERS

DEFAULT_ALIAS = "default"
DEFAULT_SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Deprecated EMAIL_* setting -> its MAILERS OPTIONS name (Django 6.1 docs,
# howto/mailers-migration "The complete list of deprecated EMAIL_* settings").
_LEGACY_OPTIONS = {
    "EMAIL_HOST": "host",
    "EMAIL_PORT": "port",
    "EMAIL_HOST_USER": "username",
    "EMAIL_HOST_PASSWORD": "password",
    "EMAIL_USE_TLS": "use_tls",
    "EMAIL_USE_SSL": "use_ssl",
    "EMAIL_TIMEOUT": "timeout",
    "EMAIL_FILE_PATH": "file_path",
}


def mailers_configured() -> bool:
    """True when the running settings use ``MAILERS`` (Django 6.1+ only)."""
    return HAS_MAILERS and hasattr(settings, "MAILERS")


def default_mailer_config() -> Dict[str, Any]:
    """The default mailer as ``{"BACKEND": path, "OPTIONS": {...}}``.

    The same shape on both Django lines, so callers read one structure. Under
    ``MAILERS`` it is the ``default`` entry (``BACKEND`` filled with Django's own
    default when omitted); under ``EMAIL_*`` it is built from those settings.
    """
    if mailers_configured():
        entry = settings.MAILERS.get(DEFAULT_ALIAS) or {}
        return {
            "BACKEND": entry.get("BACKEND", DEFAULT_SMTP_BACKEND),
            "OPTIONS": dict(entry.get("OPTIONS") or {}),
        }

    options = {
        option: getattr(settings, name)
        for name, option in _LEGACY_OPTIONS.items()
        if hasattr(settings, name)
    }
    return {
        "BACKEND": getattr(settings, "EMAIL_BACKEND", DEFAULT_SMTP_BACKEND),
        "OPTIONS": options,
    }


def default_backend_path() -> str:
    """Dotted path of the default mailer's backend class."""
    return default_mailer_config()["BACKEND"]


def default_connection():
    """An instance of the default mailer: ``mail.mailers.default`` on 6.1+.

    ``get_connection()`` is deprecated in 6.1 and is used only on 5.2, where
    ``mailers`` does not exist.
    """
    from django.core import mail

    if HAS_MAILERS:
        return mail.mailers.default
    return mail.get_connection()


__all__ = [
    "HAS_MAILERS",
    "DEFAULT_ALIAS",
    "DEFAULT_SMTP_BACKEND",
    "mailers_configured",
    "default_mailer_config",
    "default_backend_path",
    "default_connection",
]
