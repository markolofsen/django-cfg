"""Which security emails this project has switched on.

The source is ``DjangoConfig.account_emails``; both switches default to off, and
off is also the answer when no config is registered yet.
"""

from __future__ import annotations

import contextlib
import contextvars
import logging
from typing import Iterator

logger = logging.getLogger(__name__)

# True while a sign-in or registration flow is running: whatever it writes to
# the user row (a name from the provider, a verified flag) is not a profile
# change the user needs a letter about.
_in_sign_in: contextvars.ContextVar[bool] = contextvars.ContextVar("accounts_in_sign_in", default=False)


def _switch(name: str) -> bool:
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        emails = getattr(config, "account_emails", None) if config else None
        return bool(getattr(emails, name, False))
    except Exception:
        logger.debug("account_emails.%s unreadable, treating as off", name, exc_info=True)
        return False


def profile_change_email_enabled() -> bool:
    return _switch("profile_change_email")


def new_sign_in_email_enabled() -> bool:
    return _switch("new_sign_in_email")


@contextlib.contextmanager
def sign_in_flow() -> Iterator[None]:
    """Mark the enclosed writes as part of signing in or registering."""
    token = _in_sign_in.set(True)
    try:
        yield
    finally:
        _in_sign_in.reset(token)


def in_sign_in_flow() -> bool:
    return _in_sign_in.get()
