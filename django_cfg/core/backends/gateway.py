"""
HTTP email-gateway backend for Django CFG.

Sends Django ``EmailMessage`` objects as JSON to a trusted email-gateway
endpoint (one ``POST`` per message, ``Authorization: Bearer <secret>``). The
gateway owns the provider integration (which ESP, which sender identities,
rate limits) — Django never holds provider credentials and never knows which
provider is behind the gateway.

Selected via ``EmailConfig(backend="gateway", ...)``, which emits::

    EMAIL_BACKEND = "django_cfg.core.backends.gateway.GatewayEmailBackend"
    EMAIL_GATEWAY_URL = "https://email-api.example.com/send"
    EMAIL_GATEWAY_SECRET = "..."

Wire contract (gateway payload v1) — deliberately mirrors the Cloudflare
Email Sending REST shape so a thin Worker can forward it to a provider
binding without re-modelling:

* ``to``/``cc``/``bcc`` — lists of address strings;
* ``from``/``reply_to`` — string or ``{address, name}``;
* ``text``/``html`` — at least one present;
* ``attachments`` — ``{content(base64), filename, type, disposition[, content_id]}``;
* ``headers`` — passthrough of extra headers.

Expected response envelope::

    {"success": bool, "errors": [...],
     "result": {"delivered": [...], "permanent_bounces": [...], "queued": [...]}}
"""

import base64
import logging
import time
from email.mime.base import MIMEBase
from email.utils import parseaddr

import httpx
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

#: Only transient statuses are retried; 4xx validation/auth errors are permanent.
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.0  # seconds; doubles per attempt


class GatewayEmailError(Exception):
    """A send was rejected by the email gateway."""


def _address_object(value: str) -> "str | dict":
    """Convert ``"Name <a@b>"`` to the ``{address, name}`` object form."""
    name, address = parseaddr(value)
    if name:
        return {"address": address, "name": name}
    return address or value


def _encode_content(content) -> str:
    """Base64-encode attachment content (str or bytes)."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return base64.b64encode(content).decode("ascii")


def _attachment_payload(attachment) -> dict:
    """Map one Django attachment (tuple or MIMEBase) to a payload attachment."""
    if isinstance(attachment, MIMEBase):
        payload = {
            "content": _encode_content(attachment.get_payload(decode=True) or b""),
            "filename": attachment.get_filename() or "attachment",
            "type": attachment.get_content_type(),
            "disposition": "attachment",
        }
        content_id = attachment.get("Content-ID")
        disposition = attachment.get("Content-Disposition", "")
        if content_id or disposition.startswith("inline"):
            payload["disposition"] = "inline"
            if content_id:
                payload["content_id"] = content_id.strip("<>")
        return payload

    # Plain tuple (filename, content, mimetype) — also matches Django 5.2's
    # EmailAttachment namedtuple.
    filename, content, mimetype = attachment
    return {
        "content": _encode_content(content),
        "filename": filename or "attachment",
        "type": mimetype or "application/octet-stream",
        "disposition": "attachment",
    }


def build_payload(message) -> dict:
    """Map a Django ``EmailMessage``/``EmailMultiAlternatives`` to payload v1."""
    payload = {
        "to": list(message.to),
        "from": _address_object(message.from_email),
        "subject": message.subject,
    }

    if message.cc:
        payload["cc"] = list(message.cc)
    if message.bcc:
        payload["bcc"] = list(message.bcc)
    if message.reply_to:
        payload["reply_to"] = _address_object(message.reply_to[0])

    if message.content_subtype == "html":
        payload["html"] = message.body
    elif message.body:
        payload["text"] = message.body

    for alternative in getattr(message, "alternatives", ()) or ():
        content, mimetype = alternative
        if mimetype == "text/html" and "html" not in payload:
            payload["html"] = content
        elif mimetype == "text/plain" and "text" not in payload:
            payload["text"] = content

    if message.attachments:
        payload["attachments"] = [
            _attachment_payload(attachment) for attachment in message.attachments
        ]

    if message.extra_headers:
        payload["headers"] = dict(message.extra_headers)

    return payload


class GatewayEmailBackend(BaseEmailBackend):
    """
    Django email backend that POSTs messages to a trusted email gateway.

    Stateless HTTP transport: ``open()``/``close()`` manage a shared
    ``httpx.Client`` for connection reuse across one ``send_messages()``
    batch, but no session state exists beyond that.
    """

    def __init__(
        self,
        fail_silently=False,
        gateway_url=None,
        gateway_secret=None,
        timeout=None,
        transport=None,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently)
        self.gateway_url = gateway_url or getattr(settings, "EMAIL_GATEWAY_URL", None)
        self.gateway_secret = gateway_secret or getattr(
            settings, "EMAIL_GATEWAY_SECRET", None
        )
        self.timeout = timeout if timeout is not None else getattr(
            settings, "EMAIL_TIMEOUT", None
        ) or 30
        self._transport = transport  # test seam (httpx.MockTransport)
        self._client = None

        if not (self.gateway_url and self.gateway_secret):
            raise ImproperlyConfigured(
                "GatewayEmailBackend requires EMAIL_GATEWAY_URL and "
                "EMAIL_GATEWAY_SECRET settings (EmailConfig gateway_url / "
                "gateway_secret)."
            )

    def open(self):
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers={"Authorization": f"Bearer {self.gateway_secret}"},
                transport=self._transport,
            )

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        created_client = self._client is None
        self.open()
        num_sent = 0
        try:
            for message in email_messages:
                if not message.recipients():
                    continue
                try:
                    # A message every recipient of which the gateway refused is
                    # NOT a send. Counting it as one is what let a suppressed
                    # address be recorded as `sent` — see `_send`.
                    if self._send(message):
                        num_sent += 1
                except Exception:
                    if not self.fail_silently:
                        raise
        finally:
            if created_client:
                self.close()
        return num_sent

    def _send(self, message):
        """POST one message; return whether any recipient was actually accepted.

        **Why this returns a value instead of just logging.** The gateway reports
        provider-side suppression by answering ``success: true`` with the refused
        addresses in ``result.permanent_bounces`` — deliberately, so the caller
        **records** it instead of retrying an address that will never accept mail
        (the gateway's own wording; "logs" was the misreading that produced the
        defect below, and is answered by ``_report_bounces``). This
        method used to write a ``logger.warning`` and return ``None``, which
        ``send_messages`` read as a successful send. The consequence reached all
        the way to the audit trail: ``DjangoEmailService`` keys ``EmailLog.status``
        off the number this backend returns, so a recipient the provider had
        refused was filed as ``sent`` — "handed to the transport", which is the
        one thing that had not happened. Wrong in the direction that matters,
        because ``sent`` is what an operator reads as "we mailed them".

        A partial refusal is still a send: if two of three recipients are
        suppressed, the letter did reach the third, and reporting that message as
        unsent would understate delivery just as badly as the old behaviour
        overstated it. Hence "any", not "all".
        """
        payload = build_payload(message)
        response = self._post_with_retry(payload)

        body = response.json()
        if not body.get("success"):
            raise GatewayEmailError(
                f"Email gateway rejected the message: "
                f"{body.get('errors') or response.text}"
            )

        result = body.get("result") or {}
        bounces = result.get("permanent_bounces") or []
        if not bounces:
            return True

        # Accepted by the gateway but undeliverable recipients exist — they are
        # suppressed on the provider side.
        #
        # Compared case-insensitively against the message's own recipient list:
        # addresses are echoed back by the provider and may differ in case, and a
        # mismatch here would silently degrade to "nothing was suppressed" —
        # exactly the failure this block exists to report.
        refused = {address.strip().lower() for address in bounces if address}
        remaining = [
            address
            for address in message.recipients()
            if address.strip().lower() not in refused
        ]

        logger.warning(
            "Email gateway reported permanent bounces for %s (subject=%r); "
            "%d of %d recipients remain",
            bounces,
            message.subject,
            len(remaining),
            len(message.recipients()),
        )
        self._report_bounces(bounces, message.subject, remaining)
        return bool(remaining)

    @staticmethod
    def _report_bounces(bounces, subject, remaining):
        """Announce a permanent bounce so a project can record it.

        **Why this exists: the log line above is not a record.** The gateway's own
        source says it reports suppression in the envelope "so the caller records
        it instead of retrying" — and the caller wrote a warning and moved on, so
        the only trace of "this address will never accept mail" was a log line
        nobody queries. The next send to the same address tried again.
        ``EmailLog`` says the message was not sent, which is true and silent about
        why.

        django-cfg deliberately does **not** grow a suppression table to fix that.
        A project that keeps one already has the schema and the vocabulary (in
        cmdop: ``crm_email_suppressions``, with a ``hard_bounce`` reason meaning
        exactly this), and a framework copy would make two owners of one fact. So
        this reports; the project records. Nothing listening means nothing
        happens, which is correct for a library.

        Failures are swallowed on purpose. This runs on the send path inside the
        sending thread, so a receiver's database error must not turn a delivered
        letter into a raised exception — and the log line above has already told
        the operator what the gateway said.
        """
        try:
            from django_cfg.apps.system.mailer.signals import (
                email_permanently_bounced,
            )
        except ImportError:
            # The mailer app is optional; a project can install django-cfg
            # without it. No listener is reachable, so there is nothing to tell.
            return

        try:
            email_permanently_bounced.send(
                sender=GatewayEmailBackend,
                addresses=list(bounces),
                subject=subject,
                remaining=list(remaining),
            )
        except Exception:
            logger.exception(
                "A receiver of email_permanently_bounced raised; the bounce is "
                "recorded in the log above but may not have been persisted"
            )

    def _post_with_retry(self, payload):
        client = self._client
        url = self.gateway_url
        if client is None or not url:
            raise GatewayEmailError("Backend connection is not open.")

        last_response = None
        for attempt in range(MAX_ATTEMPTS):
            if attempt:
                time.sleep(RETRY_BASE_DELAY * (2 ** (attempt - 1)))
            try:
                response = client.post(url, json=payload)
            except httpx.HTTPError as exc:
                if attempt == MAX_ATTEMPTS - 1:
                    raise GatewayEmailError(
                        f"Email gateway request failed: {exc}"
                    ) from exc
                continue

            if response.status_code in RETRY_STATUSES:
                last_response = response
                continue
            return response

        raise GatewayEmailError(
            "Email gateway request failed after "
            f"{MAX_ATTEMPTS} attempts (last status "
            f"{last_response.status_code if last_response is not None else 'n/a'})."
        )
