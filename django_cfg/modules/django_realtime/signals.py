"""Kicks from account events: an open socket must not outlive the credential it was opened with.

Connected in `apps.py` while realtime is installed. Each one puts a kick on the bus after the commit; every process
closes the matching sockets with 4419 (the client refreshes over HTTP and reconnects, or stays out).

- session logout (`user_logged_out`)               -> that session's sockets
- `user_sessions_revoked` (accounts: `logout_all`, a changed `tokens_valid_after` on any save, refresh-token
  logout through the blacklist view)                -> the users' sockets, or every signed-in socket
- password set on an existing user, or a save with `is_active=False` -> the user's sockets

Revocations no signal reports (an API key deleted, a session expired in its store) are caught by the periodic
credential re-check (`RealtimeConfig.reauth_interval`).
"""

from __future__ import annotations

import logging

from django.db import transaction

from .publishing import kick

logger = logging.getLogger(__name__)


def _later(**kwargs) -> None:
    def send() -> None:
        try:
            kick(**kwargs)
        except Exception as exc:  # noqa: BLE001 - the account change stands; the re-check closes the socket later
            logger.warning("realtime: kick failed (%s); sockets close at the next credential re-check", exc)

    transaction.on_commit(send)


def on_logged_out(sender, request=None, user=None, **kwargs) -> None:
    session = getattr(request, "session", None)
    key = getattr(session, "session_key", None) if session is not None else None
    if key:
        _later(session_key=key)


def on_user_saved(sender, instance=None, created=False, **kwargs) -> None:
    if created or instance is None:
        return
    password_changed = getattr(instance, "_password", None) is not None
    if password_changed or not getattr(instance, "is_active", True):
        _later(user=instance.pk)


def on_sessions_revoked(sender, user_ids=None, **kwargs) -> None:
    if user_ids is None:
        _later(everyone=True)
        return
    for pk in user_ids:
        _later(user=pk)


def connect() -> None:
    from django.contrib.auth import get_user_model
    from django.contrib.auth.signals import user_logged_out
    from django.db.models.signals import post_save

    user_logged_out.connect(on_logged_out, dispatch_uid="django_cfg_realtime_logged_out")
    post_save.connect(on_user_saved, sender=get_user_model(), dispatch_uid="django_cfg_realtime_user_saved")
    try:
        from django_cfg.apps.system.accounts.signals import user_sessions_revoked
    except ImportError:  # a project with its own user app
        return
    user_sessions_revoked.connect(on_sessions_revoked, dispatch_uid="django_cfg_realtime_sessions_revoked")
