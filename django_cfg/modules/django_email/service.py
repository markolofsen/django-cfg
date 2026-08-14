"""
Auto-configuring Email Service for django_cfg.

This email service automatically configures itself based on the DjangoConfig instance
without requiring manual parameter passing.
"""

import re
import socket
import threading
from html import unescape
from smtplib import SMTPAuthenticationError, SMTPDataError, SMTPException, SMTPRecipientsRefused, SMTPSenderRefused
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..base import BaseCfgModule
from ..django_logging import get_logger

logger = get_logger("django_cfg.email")

# The locale whose file doubles as the fallback for every untranslated locale.
# Kept next to the resolver rather than imported from the accounts app: this
# module is the generic email transport and must not depend on it.
DEFAULT_TEMPLATE_LOCALE = "en"

def subject_from_html(html: str) -> Optional[str]:
    """The rendered ``<title>`` of an email template, or None.

    A localized letter has to carry its own Subject: a caller that builds the
    subject itself can only write it in one language, and the inbox then shows an
    English subject over translated prose. The ``<title>`` is where the template
    already states it, so it doubles as the envelope subject.
    """
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if not match:
        return None
    subject = unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return subject or None


def html_to_text(html: str) -> str:
    """The plain-text body of an HTML letter.

    ``strip_tags`` alone is not enough. The template engine escapes as it
    renders, so an apostrophe reaches the HTML as ``&#x27;`` — correct there,
    and correct still after ``strip_tags``, which removes tags and leaves
    entities untouched. Nothing decodes them in a ``text/plain`` part, so the
    reader is shown the raw entity:

        I&#x27;d genuinely like to know what you make of it

    Reported from a real welcome letter on 2026-08-14. ``subject_from_html``
    already unescapes for the same reason; this is the body's half of it.
    """
    return unescape(strip_tags(html))


def text_direction(locale: Optional[str]) -> str:
    """``rtl`` or ``ltr`` for a locale tag.

    Thin re-export of ``mailer.locales.text_direction``: the locale policy lives
    in the mailer app, but this module is imported by callers that predate it.
    Imported lazily because this module is the generic transport and must not
    require the mailer app to be installed.
    """
    from django_cfg.apps.system.mailer.locales import text_direction as _impl

    return _impl(locale)


def _record_send(
    key: str,
    recipients: List[str],
    subject: str,
    locale: str,
    status: str,
    error: str,
) -> None:
    """Write one ``EmailLog`` row per recipient.

    Best-effort by design: the log is diagnostic, and losing a row must never
    lose the mail. It also runs in the sending thread, so a database error here
    would otherwise surface as an unrelated "background email task failed".

    Nothing is written when the mailer app is absent — a project can install
    django-cfg without it, and a send should not depend on the log's existence.
    """
    try:
        from django_cfg.apps.system.mailer.models import EmailLog

        EmailLog.objects.bulk_create(
            [
                EmailLog(
                    key=key or "",
                    recipient=address,
                    subject=(subject or "")[:255],
                    locale=locale or "",
                    status=status,
                    error=error or "",
                )
                for address in recipients or []
            ]
        )
    except Exception as e:
        logger.debug(f"Email log skipped: {e}")


def _notify_telegram_on_email_error(error_msg: str, context: dict = None):
    """Send telegram notification about email sending error."""
    try:
        from ..django_telegram import DjangoTelegram
        DjangoTelegram.send_error(
            error=f"Email Sending Error\n\n{error_msg}",
            context=context
        )
    except Exception as e:
        logger.debug(f"Could not send telegram notification: {e}")


# Live sending threads, so a caller that is about to exit can wait for them.
_SEND_THREADS: List[threading.Thread] = []
_SEND_THREADS_LOCK = threading.Lock()


def wait_for_sends(timeout: float = 30.0) -> bool:
    """Block until queued sends finish. True if all completed.

    Sending happens on daemon threads, which Python kills at interpreter exit —
    fine for a web process that keeps running, fatal for a management command
    that returns immediately. Anything short-lived must call this, or it reports
    success for a letter that never left.
    """
    with _SEND_THREADS_LOCK:
        threads = [t for t in _SEND_THREADS if t.is_alive()]
    deadline = None
    for thread in threads:
        if deadline is None:
            import time as _time

            deadline = _time.monotonic() + timeout
        import time as _time

        remaining = deadline - _time.monotonic()
        if remaining <= 0:
            break
        thread.join(remaining)
    with _SEND_THREADS_LOCK:
        _SEND_THREADS[:] = [t for t in _SEND_THREADS if t.is_alive()]
        return not _SEND_THREADS


class DjangoEmailService(BaseCfgModule):
    """
    Auto-configuring email service that gets settings from DjangoConfig.

    Usage:
        from django_cfg.modules import DjangoEmailService

        email = DjangoEmailService()
        email.send_simple("Test", "Hello World!", ["user@example.com"])
    """

    def __init__(self):
        """Initialize email service with auto-discovered config."""
        self.config = self.get_config()
        self.email_config = getattr(self.config, 'email', None)

    @staticmethod
    def _is_running_under_tests() -> bool:
        """True when Django's test runner has swapped in the locmem backend.

        Keyed off the backend rather than ``sys.argv`` or a settings flag: the
        runner sets it for every test process however it was started (manage.py,
        pytest, parallel workers), and it is exactly the condition under which
        sending must not outlive the test.
        """
        return "locmem" in getattr(settings, "EMAIL_BACKEND", "")

    def _send_in_background(self, func, *args, **kwargs):
        """
        Execute a function in a background thread to avoid blocking.

        Runs **inline** under a test runner. A thread that outlives the test
        writing to the database races the runner's transaction rollback, which
        surfaces as an unrelated `database table is locked` in whichever test
        happens to run next — a failure that reproduces about one run in three
        and points at the wrong code. Tests that want to observe threading patch
        this method directly.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        if self._is_running_under_tests():
            func(*args, **kwargs)
            return

        def _wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                # _handle_email_sending already notifies telegram for SMTP errors;
                # this catches anything that escapes it (e.g. template rendering).
                error_msg = f"Background email task failed: {e}"
                logger.error(error_msg)
                _notify_telegram_on_email_error(error_msg, {
                    'error_type': type(e).__name__,
                    'function': func.__name__ if hasattr(func, '__name__') else 'unknown',
                })

        thread = threading.Thread(target=_wrapper, daemon=True, name="django-cfg-email")
        thread.start()
        # Tracked so a caller can wait for delivery. These are daemon threads, so
        # a short-lived process (a management command, a script) exits out from
        # under them and the mail is never sent — see `wait_for_sends`.
        with _SEND_THREADS_LOCK:
            _SEND_THREADS.append(thread)

    def _handle_email_sending(self, email_func, *args, **kwargs):
        """
        Wrapper for email sending with proper timeout/exception handling.

        Args:
            email_func: Email sending function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of email_func or 0 on timeout/error
        """
        try:
            result = email_func(*args, **kwargs)
            logger.debug(f"Email sent successfully: {email_func.__name__}")
            return result
        except (socket.timeout, TimeoutError) as e:
            msg = f"SMTP timeout: {e}"
            logger.warning(msg)
            _notify_telegram_on_email_error(msg, {
                "type": "timeout",
                "host": getattr(self.email_config, "host", "?"),
            })
            return 0
        except SMTPAuthenticationError as e:
            msg = f"SMTP authentication failed: {e}"
            logger.error(msg)
            _notify_telegram_on_email_error(msg, {
                "type": "auth_error",
                "host": getattr(self.email_config, "host", "?"),
                "username": getattr(self.email_config, "username", "?"),
            })
            return 0
        except SMTPDataError as e:
            msg = f"SMTP data error (quota/limit/policy): {e}"
            logger.error(msg)
            _notify_telegram_on_email_error(msg, {
                "type": "data_error",
                "code": e.smtp_code,
                "host": getattr(self.email_config, "host", "?"),
            })
            return 0
        except SMTPRecipientsRefused as e:
            msg = f"SMTP recipients refused: {e.recipients}"
            logger.error(msg)
            _notify_telegram_on_email_error(msg, {
                "type": "recipients_refused",
                "recipients": str(e.recipients),
            })
            return 0
        except SMTPSenderRefused as e:
            msg = f"SMTP sender refused: {e.sender}"
            logger.error(msg)
            _notify_telegram_on_email_error(msg, {
                "type": "sender_refused",
                "sender": e.sender,
                "code": e.smtp_code,
            })
            return 0
        except SMTPException as e:
            msg = f"SMTP error: {e}"
            logger.warning(msg)
            _notify_telegram_on_email_error(msg, {
                "type": type(e).__name__,
                "host": getattr(self.email_config, "host", "?"),
            })
            return 0
        except Exception as e:
            msg = f"Unexpected email error: {e}"
            logger.error(msg)
            _notify_telegram_on_email_error(msg, {
                "type": type(e).__name__,
            })
            if not kwargs.get('fail_silently', False):
                raise
            return 0

    def send_simple(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send a simple text email in background thread (non-blocking).

        Args:
            subject: Email subject
            message: Email message (plain text)
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        def _do_send():
            self._handle_email_sending(
                send_mail,
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
            )

        # Always send in background thread to avoid blocking
        self._send_in_background(_do_send)
        return True

    def send_html(
        self,
        subject: str,
        html_message: str,
        recipient_list: List[str],
        text_message: Optional[str] = None,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
        log_key: str = "",
        log_locale: str = "",
        text_only: bool = False,
    ) -> bool:
        """
        Send an HTML email with optional plain text alternative in background thread (non-blocking).

        Args:
            subject: Email subject
            html_message: HTML email content
            recipient_list: List of recipient email addresses
            text_message: Plain text alternative (auto-generated if not provided)
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors
            text_only: Send as text/plain with NO HTML part. A letter written in
                the first person reads better this way — the client renders it in
                its own font, so it looks like a message a person typed instead of
                a page imitating one, and no client can break the layout.

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)
        reply_to = self._get_reply_to()

        if text_message is None:
            text_message = html_to_text(html_message)

        # EmailMultiAlternatives rather than send_mail: send_mail has no
        # reply_to parameter, so a configured Reply-To would be dropped and every
        # reply to a first-person letter would reach the unattended sender
        # instead of a mailbox someone reads.
        def _send():
            message = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=from_email,
                to=recipient_list,
                reply_to=reply_to,
            )
            if not text_only:
                message.attach_alternative(html_message, "text/html")
            return message.send(fail_silently=fail_silently)

        def _do_send():
            # Logged around the actual attempt, inside the thread: sending is
            # threaded and the transport is HTTP, so a failure otherwise surfaces
            # nowhere a human looks.
            #
            # The RESULT is what decides the status, not just an exception:
            # `_handle_email_sending` swallows every SMTP error and returns 0, so
            # keying off exceptions alone would file a failed send as "sent".
            try:
                sent = self._handle_email_sending(_send)
            except Exception as exc:
                _record_send(
                    log_key, recipient_list, subject, log_locale, "failed", str(exc)
                )
                raise
            if sent:
                _record_send(log_key, recipient_list, subject, log_locale, "sent", "")
            else:
                _record_send(
                    log_key,
                    recipient_list,
                    subject,
                    log_locale,
                    "failed",
                    "transport reported 0 messages sent; see the log for the provider error",
                )

        # Always send in background thread to avoid blocking
        self._send_in_background(_do_send)
        return True

    @staticmethod
    def _template_candidates(
        template_name: str, extension: str, locale: Optional[str] = None
    ) -> List[str]:
        """Template names to try, most specific first.

        ``render_to_string`` accepts a list and uses the first that exists, so
        this gives per-file fallback: a locale may ship only some of the
        templates a product has, and each missing one degrades to the base
        rather than failing the send.

        Two layouts are accepted, and a **directory** is preferred:

        ==========================  ==============================
        directory (preferred)       ``emails/welcome/fr.html``
        sibling suffix (legacy)     ``emails/welcome.fr.html``
        ==========================  ==============================

        The directory form is what a translated letter should use: at 17 locales
        the suffix form buries a single letter under 34 sibling files, and the
        shared shell has no obvious home among them. The suffix form stays
        supported because it is the shape existing products already ship, and
        one-locale templates read fine that way.

        For a region-carrying locale the base language is tried too, so
        ``pt-BR`` also reaches a ``pt`` template if a product ships one.
        """
        candidates: List[str] = []
        if locale:
            tags = [locale]
            base = locale.split("-")[0]
            if base != locale:
                tags.append(base)
            for tag in tags:
                candidates.append(f"{template_name}/{tag}.{extension}")
                candidates.append(f"{template_name}.{tag}.{extension}")
        # Unsuffixed last: it is the fallback every untranslated locale lands on.
        candidates.append(f"{template_name}/{DEFAULT_TEMPLATE_LOCALE}.{extension}")
        candidates.append(f"{template_name}.{extension}")
        return candidates

    def send_template(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
        locale: Optional[str] = None,
        text_only: bool = False,
    ) -> bool:
        """
        Send an email using a Django template in background thread (non-blocking).

        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors
            locale: Render the locale-specific variant when one exists —
                ``<template_name>.<locale>.html``, falling back to
                ``<template_name>.html``. Also exposed to the template as
                ``locale`` so the base shell can set ``<html lang>``.

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        # Prepare context with auto-added values
        context = self._prepare_template_context(context)
        if locale:
            context.setdefault("locale", locale)

        # Render HTML template
        html_message = render_to_string(
            self._template_candidates(template_name, "html", locale), context
        )

        # Try to render plain text template. The locale-specific .txt is
        # optional even when a locale-specific .html exists — a translator who
        # only supplied HTML must not silently break the send.
        try:
            text_message = render_to_string(
                self._template_candidates(template_name, "txt", locale), context
            )
        except Exception:
            text_message = html_to_text(html_message)

        # A localized template states its own subject in <title>, and that wins:
        # the caller can only hard-code one language, which is how an English
        # "Welcome to X" ends up over a Russian letter.
        template_subject = subject_from_html(html_message)
        if template_subject:
            subject = template_subject

        return self.send_html(
            subject=subject,
            html_message=html_message,
            recipient_list=recipient_list,
            text_message=text_message,
            from_email=from_email,
            fail_silently=fail_silently,
            # The template's own directory names the letter in the log, so a row
            # says "welcome" rather than just an address and a subject.
            log_key=(template_name or "").rstrip("/").split("/")[-1],
            log_locale=locale or "",
            text_only=text_only,
        )

    def send_multipart(
        self,
        subject: str,
        recipient_list: List[str],
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        attachments: Optional[List[tuple]] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send a multipart email with attachments.

        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            html_content: HTML email content
            text_content: Plain text email content
            from_email: Sender email (auto-detected if not provided)
            attachments: List of (filename, content, mimetype) tuples
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email was sent successfully, False otherwise
        """
        from_email = self._get_formatted_from_email(from_email)

        if not html_content and not text_content:
            raise ValueError("Either html_content or text_content must be provided")

        def _send_multipart_email():
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content or html_to_text(html_content or ''),
                    from_email=from_email,
                    to=recipient_list,
                )

                if html_content:
                    email.attach_alternative(html_content, "text/html")

                if attachments:
                    for filename, content, mimetype in attachments:
                        email.attach(filename, content, mimetype)

                email.send(fail_silently=fail_silently)
                logger.info(f"Multipart email sent successfully to {recipient_list}")
            except Exception as e:
                error_msg = f"Failed to send multipart email: {e}"
                logger.error(error_msg)

                # Notify telegram about error
                context = {
                    'error_type': type(e).__name__,
                    'subject': subject,
                    'recipients': recipient_list,
                    'from': from_email,
                    'attachments_count': len(attachments) if attachments else 0,
                }
                _notify_telegram_on_email_error(str(e), context)

                if not fail_silently:
                    raise

        # Always send in background thread to avoid blocking
        self._send_in_background(_send_multipart_email)
        return True

    def send_with_attachments(
        self,
        subject: str,
        recipient_list: List[str],
        attachments: List[tuple],
        message: Optional[str] = None,
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Universal method to send emails with attachments.

        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            attachments: List of (filename, content, mimetype) tuples
            message: Plain text message (for simple emails)
            html_message: HTML message (for HTML emails)
            template_name: Template name without .html extension (for template emails)
            context: Template context variables (required if template_name provided)
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email was sent successfully, False otherwise
        """
        html_content = None
        text_content = None

        if template_name:
            # Template-based email
            if not context:
                context = {}

            # Prepare context with auto-added values
            context = self._prepare_template_context(context)

            # Render templates
            html_content = render_to_string(f"{template_name}.html", context)
            try:
                text_content = render_to_string(f"{template_name}.txt", context)
            except:
                text_content = html_to_text(html_content)

        elif html_message:
            # HTML email
            html_content = html_message
            text_content = message or html_to_text(html_message)

        elif message:
            # Simple text email
            text_content = message

        else:
            raise ValueError("Must provide either message, html_message, or template_name")

        return self.send_multipart(
            subject=subject,
            recipient_list=recipient_list,
            html_content=html_content,
            text_content=text_content,
            from_email=from_email,
            attachments=attachments,
            fail_silently=fail_silently,
        )

    def _prepare_template_context(self, context: Dict[str, Any], email_log_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare template context with auto-added values from config.

        Args:
            context: Original context dictionary
            email_log_id: Optional email log ID for tracking

        Returns:
            Updated context with auto-added values
        """
        # Create a copy to avoid modifying the original
        updated_context = context.copy()

        # Auto-add project_name from config if not provided
        if 'project_name' not in updated_context:
            updated_context['project_name'] = self.config.project_name

        # Auto-add logo_url from config if not provided
        if 'logo_url' not in updated_context and self.config.project_logo:
            updated_context['logo_url'] = self.config.project_logo

        # Auto-add site_url from config if not provided
        if 'site_url' not in updated_context:
            updated_context['site_url'] = self.config.site_url

        # Auto-add subscribe_url (P.S. footer) — absent unless configured
        if 'subscribe_url' not in updated_context:
            subscribe_url = getattr(self.email_config, 'subscribe_url', None) \
                or getattr(settings, 'EMAIL_SUBSCRIBE_URL', None)
            if subscribe_url:
                updated_context['subscribe_url'] = subscribe_url

        # Add tracking URLs if email_log_id is provided
        if email_log_id:
            base_url = self.config.api_url.rstrip('/')
            updated_context['tracking_pixel_url'] = f"{base_url}/cfg/newsletter/track/open/{email_log_id}/"
            updated_context['tracking_click_url'] = f"{base_url}/cfg/newsletter/track/click/{email_log_id}"

        return updated_context

    def _get_default_from_email(self) -> str:
        """Get the default from email address."""
        if self.email_config and self.email_config.default_from:
            return self.email_config.default_from

        # Fallback to Django settings
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

    def _get_formatted_from_email(self, from_email: Optional[str] = None) -> str:
        """
        Get formatted from email with project name.

        Args:
            from_email: Optional custom from email

        Returns:
            Formatted email in format: "Project Name <email@example.com>"
        """
        if from_email is None:
            from_email = self._get_default_from_email()

        # If email already contains name (has < and >), return as is
        if '<' in from_email and '>' in from_email:
            return from_email

        # An explicit display name wins over the project name: a letter written
        # in the first person should arrive from a person, and the name is what
        # the reader sees before deciding whether to open it at all.
        name = None
        if self.email_config:
            name = getattr(self.email_config, 'default_from_name', None)
        name = name or self.config.project_name
        return f'"{name}" <{from_email}>'

    def _get_reply_to(self) -> Optional[List[str]]:
        """Configured Reply-To, as the list Django's message classes expect.

        Separate from the sender because the two answer different questions: the
        `From` is an identity the gateway pins, while replies have to reach a
        mailbox someone reads. A letter that invites a reply from an unattended
        address discards it silently.
        """
        reply_to = getattr(self.email_config, 'reply_to', None) if self.email_config else None
        return [reply_to] if reply_to else None

    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return self.email_config is not None and bool(self.email_config.host)

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current email backend."""
        backend = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

        info = {
            'backend': backend,
            'configured': self.is_configured(),
            'host': getattr(settings, 'EMAIL_HOST', None),
            'port': getattr(settings, 'EMAIL_PORT', None),
            'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
            'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
        }

        if self.email_config:
            info.update({
                'default_from_email': self.email_config.default_from,
                'default_from_name': getattr(self.email_config, 'default_from_name', None),
            })

        return info

    # Backward compatibility aliases
    def send_html_with_attachments(self, subject: str, html_message: str, recipient_list: List[str],
                                 attachments: List[tuple], text_message: Optional[str] = None,
                                 from_email: Optional[str] = None, fail_silently: bool = False) -> bool:
        """Alias for send_with_attachments with HTML message."""
        return self.send_with_attachments(
            subject=subject, recipient_list=recipient_list, attachments=attachments,
            html_message=html_message, message=text_message, from_email=from_email, fail_silently=fail_silently
        )

    def send_template_with_attachments(self, subject: str, template_name: str, context: Dict[str, Any],
                                     recipient_list: List[str], attachments: List[tuple],
                                     from_email: Optional[str] = None, fail_silently: bool = False) -> bool:
        """Alias for send_with_attachments with template."""
        return self.send_with_attachments(
            subject=subject, recipient_list=recipient_list, attachments=attachments,
            template_name=template_name, context=context, from_email=from_email, fail_silently=fail_silently
        )

    def send_template_with_tracking(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        email_log_id: str,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send an email using a Django template with tracking support in background thread (non-blocking).

        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            email_log_id: Email log ID for tracking
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        # Prepare context with auto-added values and tracking
        context = self._prepare_template_context(context, email_log_id)

        # Render HTML template
        html_message = render_to_string(f"{template_name}.html", context)

        # Try to render plain text template
        try:
            text_message = render_to_string(f"{template_name}.txt", context)
        except:
            text_message = html_to_text(html_message)

        return self.send_html(
            subject=subject,
            html_message=html_message,
            recipient_list=recipient_list,
            text_message=text_message,
            from_email=from_email,
            fail_silently=fail_silently,
        )


__all__ = ["DjangoEmailService"]
