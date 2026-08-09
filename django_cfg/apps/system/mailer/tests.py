"""The mailer app: locale resolution, stored copy, and the send log."""

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from django_cfg.apps.system.mailer.models import EmailContent, EmailLog
from django_cfg.modules.django_email.service import _record_send


class ResolveTests(TestCase):
    """Fallback is the model's job, not the caller's."""

    def setUp(self):
        EmailContent.objects.create(key="welcome", locale="en", subject="English")
        EmailContent.objects.create(key="welcome", locale="ru", subject="Русский")
        EmailContent.objects.create(key="welcome", locale="pt-BR", subject="Português")

    def test_exact_locale_wins(self):
        self.assertEqual(EmailContent.resolve("welcome", "ru").subject, "Русский")

    def test_region_tag_matches_its_own_row(self):
        self.assertEqual(EmailContent.resolve("welcome", "pt-BR").subject, "Português")

    def test_base_language_falls_back_to_english_when_no_bare_row(self):
        """`pt` has no row of its own; only `pt-BR` does. English is next."""
        self.assertEqual(EmailContent.resolve("welcome", "pt").subject, "English")

    def test_region_tag_reaches_a_base_language_row(self):
        EmailContent.objects.create(key="welcome", locale="de", subject="Deutsch")
        self.assertEqual(EmailContent.resolve("welcome", "de-AT").subject, "Deutsch")

    def test_unknown_locale_falls_back_to_english(self):
        self.assertEqual(EmailContent.resolve("welcome", "xx").subject, "English")

    def test_inactive_row_is_skipped_not_returned_blank(self):
        EmailContent.objects.filter(locale="ru").update(is_active=False)
        self.assertEqual(EmailContent.resolve("welcome", "ru").subject, "English")

    def test_unknown_key_is_none_rather_than_an_error(self):
        """None means 'use the template's own wording', so it must not raise."""
        self.assertIsNone(EmailContent.resolve("nosuch", "en"))

    def test_no_english_row_either_is_none(self):
        EmailContent.objects.all().delete()
        self.assertIsNone(EmailContent.resolve("welcome", "ru"))


class AsContextTests(TestCase):
    def test_multiline_fields_become_paragraph_lists(self):
        row = EmailContent.objects.create(
            key="welcome",
            locale="en",
            subject="S",
            lede="First.\nSecond.",
            greeting="Hi",
        )
        context = row.as_context()
        self.assertEqual(context["lede"], ["First.", "Second."])
        self.assertEqual(context["greeting"], "Hi")

    def test_blank_lines_are_dropped(self):
        row = EmailContent.objects.create(
            key="welcome", locale="en", subject="S", points="One.\n\n\nTwo."
        )
        self.assertEqual(row.as_context()["points"], ["One.", "Two."])

    def test_empty_block_is_an_empty_list(self):
        row = EmailContent.objects.create(key="welcome", locale="en", subject="S")
        self.assertEqual(row.as_context()["outro"], [])


class SendLogTests(TestCase):
    def test_one_row_per_recipient(self):
        _record_send("welcome", ["a@x.test", "b@x.test"], "Subj", "ru", "sent", "")
        self.assertEqual(EmailLog.objects.count(), 2)
        self.assertEqual(
            set(EmailLog.objects.values_list("recipient", flat=True)),
            {"a@x.test", "b@x.test"},
        )

    def test_the_locale_is_recorded(self):
        """The field that answers 'why did this arrive in English'."""
        _record_send("welcome", ["a@x.test"], "Subj", "de", "sent", "")
        self.assertEqual(EmailLog.objects.get().locale, "de")

    def test_failure_keeps_the_transport_error_verbatim(self):
        _record_send("welcome", ["a@x.test"], "S", "en", "failed", "550 rejected")
        row = EmailLog.objects.get()
        self.assertEqual(row.status, "failed")
        self.assertIn("550 rejected", row.error)

    def test_an_overlong_subject_does_not_break_the_send(self):
        _record_send("welcome", ["a@x.test"], "x" * 400, "en", "sent", "")
        self.assertEqual(len(EmailLog.objects.get().subject), 255)

    def test_a_logging_failure_is_swallowed(self):
        """Losing a diagnostic row must never lose the mail."""
        with patch.object(
            EmailLog.objects, "bulk_create", side_effect=RuntimeError("db gone")
        ):
            _record_send("welcome", ["a@x.test"], "S", "en", "sent", "")  # must not raise
        self.assertEqual(EmailLog.objects.count(), 0)

    def test_no_recipients_writes_nothing(self):
        _record_send("welcome", [], "S", "en", "sent", "")
        self.assertEqual(EmailLog.objects.count(), 0)


class SendStatusTests(TestCase):
    """A swallowed SMTP error must not be filed as a success.

    ``_handle_email_sending`` catches every SMTP exception and returns 0, so a
    log driven by exceptions alone would record a failed send as ``sent``.
    """

    def test_zero_sent_is_recorded_as_failed(self):
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch.object(service, "_handle_email_sending", return_value=0), patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            service.send_html(
                subject="S",
                html_message="<p>hi</p>",
                recipient_list=["a@x.test"],
                log_key="welcome",
                log_locale="en",
            )
        row = EmailLog.objects.get()
        self.assertEqual(row.status, "failed")

    def test_a_successful_send_is_recorded_as_sent(self):
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch.object(service, "_handle_email_sending", return_value=1), patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            service.send_html(
                subject="S",
                html_message="<p>hi</p>",
                recipient_list=["a@x.test"],
                log_key="welcome",
                log_locale="ru",
            )
        row = EmailLog.objects.get()
        self.assertEqual((row.status, row.locale, row.key), ("sent", "ru", "welcome"))
