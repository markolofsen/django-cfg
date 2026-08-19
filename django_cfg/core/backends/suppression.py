"""The pre-send gate: one place that decides whether an address may be mailed.

Why this is a **backend** and not a hook on ``DjangoEmailService``
------------------------------------------------------------------
The obvious place to ask "may we send this?" is the service that sends it, and
that place does not hold. ``DjangoEmailService`` exposes eight public send
methods over a near-choke-point, ``_handle_email_sending`` — and one of them
walks around it: ``send_multipart`` calls ``email.send(...)`` directly, so a gate
on the wrapper is bypassed by **every attachment-bearing send**. That is not a
bug to fix in place; it is evidence about where the real choke point is. A hook
one refactor away from being skipped is decorative, and it passes its own test
suite the entire time it is skipped.

``django.core.mail`` has exactly one narrow waist: **every** way to send —
``send_mail``, ``EmailMessage.send()``, ``EmailMultiAlternatives.send()``, a
direct ``get_connection()``, ``mail_admins`` — ends at a backend's
``send_messages()``. Gating there makes the bypass *unexpressible* rather than
merely detectable: there is no send path in Django that reaches a transport
without passing through a backend, so a future method added to the service, or a
caller that ignores the service entirely, is gated by construction and without
anyone remembering to gate it.

This wraps another backend rather than replacing one, so the gate composes with
whatever transport a project already selected (SMTP, gateway, console, locmem).

Streams are DECLARED, never inferred
------------------------------------
Transactional mail — OTP, login and security alerts, dunning — must **not** be
stoppable by a marketing opt-out. Somebody who unsubscribed from a newsletter
still has to be able to log in.

The tempting shortcut is to infer the stream from context: the method that was
called, the template name, whether a campaign id is set. Every one of those is a
guess that fails silently in the dangerous direction — a renamed template or a
new send method would quietly reclassify OTP as marketing and lock users out of
their own accounts. So the stream is a property **declared on the message**, it
has exactly one name (:data:`STREAM_HEADER`), and its default is
``transactional``.

That default is the fail-safe direction *for this decision specifically*: an
unlabelled letter is treated as mail a person cannot opt out of, so the failure
mode of forgetting to label a marketing blast is that an unsubscribe is not
honoured — visible, reportable, fixable — rather than sign-in mail silently
disappearing. Marketing senders label their mail; that is a much smaller set of
call sites than "everything that might be transactional", and it is the set that
already knows it is marketing.

Who owns the suppression list
-----------------------------
Not django-cfg. The framework has deliberately never grown a suppression table —
see ``apps/system/mailer/signals.py``: a project that keeps a consent ledger
already has the schema, the vocabulary and the admin for it (in cmdop:
``crm_email_suppressions`` plus the newsletter plane's D1 rows, behind
``filter_suppressed``), and a second copy in the framework would make two owners
of one fact and go stale silently.

So this module supplies the **choke point and the vocabulary**, and asks the
project a single question through :data:`EMAIL_SUPPRESSION_RESOLVER`. Configured
with no resolver, the gate is a pass-through — correct for a library, and it
means installing this backend cannot by itself start dropping anybody's mail.
"""

from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)

#: The header a caller sets to declare a message's stream.
#:
#: A header rather than an attribute on purpose: it survives every way Django
#: builds a message (``EmailMessage``, ``EmailMultiAlternatives``, anything a
#: project subclasses), it is set through the ordinary ``headers=`` argument that
#: already exists on all of them, and it needs no cooperation from the message
#: class. An attribute would be invisible to any caller that constructs its own
#: message type — which ``send_multipart`` effectively does.
STREAM_HEADER = "X-Cfg-Email-Stream"

#: Mail a recipient cannot opt out of: OTP, login/security alerts, dunning,
#: and anything else whose loss locks someone out or hides a charge.
STREAM_TRANSACTIONAL = "transactional"

#: Mail a recipient may opt out of: newsletters, digests, campaigns, product
#: announcements.
STREAM_MARKETING = "marketing"

#: The stream assumed when a message declares none. See the module docstring:
#: unlabelled mail is treated as un-opt-out-able, so forgetting to label a
#: marketing blast produces a reportable policy miss rather than silently
#: swallowing somebody's sign-in code.
DEFAULT_STREAM = STREAM_TRANSACTIONAL

VALID_STREAMS = frozenset({STREAM_TRANSACTIONAL, STREAM_MARKETING})


def stream_of(message) -> str:
    """The stream a message declares, or :data:`DEFAULT_STREAM`.

    An unrecognised value is treated as the default and reported, rather than
    raising or being passed through to the resolver. A typo (``"marketting"``)
    must not become a third stream with no rules attached, and it must not fail
    a send either — but it does have to be visible, because the letter is being
    treated as un-opt-out-able and the sender clearly meant something else.
    """
    headers = getattr(message, "extra_headers", None) or {}
    declared = headers.get(STREAM_HEADER)
    if declared is None:
        return DEFAULT_STREAM
    value = str(declared).strip().lower()
    if value not in VALID_STREAMS:
        logger.warning(
            "Unknown email stream %r on message (subject=%r); treating as %r. "
            "Valid streams: %s",
            declared,
            getattr(message, "subject", ""),
            DEFAULT_STREAM,
            ", ".join(sorted(VALID_STREAMS)),
        )
        return DEFAULT_STREAM
    return value


def mark_stream(message, stream: str):
    """Declare ``stream`` on ``message``. Returns the message, for chaining."""
    if stream not in VALID_STREAMS:
        raise ValueError(
            f"Unknown email stream {stream!r}; expected one of "
            f"{', '.join(sorted(VALID_STREAMS))}"
        )
    if message.extra_headers is None:  # pragma: no cover - Django always sets {}
        message.extra_headers = {}
    message.extra_headers[STREAM_HEADER] = stream
    return message


def _load_resolver():
    """The project's "may I mail this address?" function, or None.

    Resolved per call rather than cached on the instance: ``override_settings``
    in a test, and a project that swaps the resolver at runtime, must both take
    effect. This runs once per ``send_messages`` batch, not per recipient, so the
    import-string lookup is not on a hot path.
    """
    path = getattr(settings, "EMAIL_SUPPRESSION_RESOLVER", None)
    if not path:
        return None
    if callable(path):
        return path
    try:
        return import_string(path)
    except ImportError:
        logger.exception(
            "EMAIL_SUPPRESSION_RESOLVER=%r could not be imported; "
            "the suppression gate is INACTIVE for this send",
            path,
        )
        return None


class SuppressionGateBackend(BaseEmailBackend):
    """Wraps another email backend and drops suppressed recipients first.

    Selected with::

        EMAIL_BACKEND = "django_cfg.core.backends.suppression.SuppressionGateBackend"
        EMAIL_GATE_INNER_BACKEND = "django_cfg.core.backends.gateway.GatewayEmailBackend"
        EMAIL_SUPPRESSION_RESOLVER = "myproject.email.gate.allowed_recipients"

    The resolver is called once per message::

        allowed_recipients(addresses: list[str], *, stream: str) -> list[str]

    and returns the subset that may be mailed. It is the project's single
    answerer — the same function the project's own stacks call — so there is one
    place that decides, not one copy per stack.

    A message all of whose recipients are refused is **not handed to the
    transport at all** and is not counted as sent. That number is what
    ``DjangoEmailService`` keys ``EmailLog.status`` off, so a suppressed letter is
    recorded as not-sent, which is exactly what happened.
    """

    def __init__(self, fail_silently=False, inner_backend=None, resolver=None, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self._resolver = resolver
        self._inner_kwargs = kwargs
        self._explicit_inner = inner_backend
        self._inner = None

    def _get_inner(self):
        """The wrapped transport.

        Built lazily so that constructing the gate never constructs a transport
        that a fully-suppressed batch would not have used — and, more practically,
        so ``EMAIL_GATE_INNER_BACKEND`` can be swapped by ``override_settings``
        between sends in a test.
        """
        if self._inner is not None:
            return self._inner
        if self._explicit_inner is not None:
            # A backend instance passed in directly (tests, or a project wiring
            # its own); use it as-is rather than re-constructing from a path.
            if isinstance(self._explicit_inner, BaseEmailBackend):
                self._inner = self._explicit_inner
                return self._inner
            path = self._explicit_inner
        else:
            path = getattr(
                settings,
                "EMAIL_GATE_INNER_BACKEND",
                "django.core.mail.backends.smtp.EmailBackend",
            )
        self._inner = get_connection(
            backend=path, fail_silently=self.fail_silently, **self._inner_kwargs
        )
        return self._inner

    def open(self):
        return self._get_inner().open()

    def close(self):
        if self._inner is not None:
            self._inner.close()

    def send_messages(self, email_messages):
        """Filter every message's recipients, then hand the survivors on.

        Returns the inner backend's count, which excludes messages dropped here:
        a letter nobody was allowed to receive was not sent, and reporting it as
        sent is the failure this gate exists to prevent.
        """
        if not email_messages:
            return 0

        resolver = self._resolver or _load_resolver()
        if resolver is None:
            # No project answerer configured. A library must not invent a policy;
            # pass through untouched.
            return self._get_inner().send_messages(email_messages)

        allowed_messages = []
        for message in email_messages:
            kept = self._filter_message(message, resolver)
            if kept:
                allowed_messages.append(message)

        if not allowed_messages:
            return 0

        return self._get_inner().send_messages(allowed_messages)

    def _filter_message(self, message, resolver) -> bool:
        """Narrow ``message`` to its permitted recipients. True if any remain.

        Mutates the message in place: Django's own backends read ``to``/``cc``/
        ``bcc`` when they build the envelope, so narrowing the lists here is what
        makes the drop real rather than advisory.

        A resolver that raises does **not** silently pass the mail through. This
        is the one place where failing open would defeat the point — an outage in
        the consent ledger would resume mailing every address that ever opted
        out, which is precisely the state that is not allowed to recur. The
        exception propagates unless the caller asked for ``fail_silently``.
        """
        stream = stream_of(message)
        original = list(message.recipients())
        if not original:
            return False

        allowed = resolver(original, stream=stream)
        allowed_set = {str(a).strip().lower() for a in (allowed or [])}

        if len(allowed_set) == len(original):
            return True

        def _keep(addresses: Optional[Iterable[str]]) -> List[str]:
            return [a for a in (addresses or []) if str(a).strip().lower() in allowed_set]

        dropped = [a for a in original if str(a).strip().lower() not in allowed_set]
        message.to = _keep(getattr(message, "to", None))
        message.cc = _keep(getattr(message, "cc", None))
        message.bcc = _keep(getattr(message, "bcc", None))

        remaining = message.recipients()
        logger.info(
            "Suppression gate dropped %d of %d recipients (stream=%s, subject=%r); "
            "dropped=%s",
            len(dropped),
            len(original),
            stream,
            getattr(message, "subject", ""),
            dropped,
        )
        return bool(remaining)


__all__ = [
    "SuppressionGateBackend",
    "STREAM_HEADER",
    "STREAM_TRANSACTIONAL",
    "STREAM_MARKETING",
    "DEFAULT_STREAM",
    "mark_stream",
    "stream_of",
]
