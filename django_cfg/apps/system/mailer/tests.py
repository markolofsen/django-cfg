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


class DurableIntentTests(TestCase):
    """The row exists *before* the transport is touched.

    For the life of this model `queued` was declared, made the field default, and
    written by nothing — measured on cmdop production: 112 rows, `queued` = 0.
    Every row was created after the transport had already returned, so a process
    that died mid-send left no evidence the letter had ever been attempted. These
    tests pin the pre-write and the transition, not the happy path — the happy
    path was already green while the defect was present.
    """

    def test_the_intent_row_exists_before_the_transport_runs(self):
        """The whole point. Observed from inside the send, not after it."""
        from django_cfg.modules.django_email.service import DjangoEmailService

        seen = {}

        def _observe(_fn):
            # Called instead of sending: at this moment the transport has not run.
            row = EmailLog.objects.get()
            seen["status"] = row.status
            seen["sent_at"] = row.sent_at
            return 1

        service = DjangoEmailService()
        with patch.object(service, "_handle_email_sending", side_effect=_observe), patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            service.send_html(
                subject="S",
                html_message="<p>hi</p>",
                recipient_list=["a@x.test"],
                log_key="welcome",
                log_locale="en",
            )

        self.assertEqual(seen["status"], "queued")
        self.assertIsNone(seen["sent_at"])
        # ...and it was transitioned, not duplicated.
        self.assertEqual(EmailLog.objects.count(), 1)
        self.assertEqual(EmailLog.objects.get().status, "sent")

    def test_a_send_that_never_resolves_leaves_a_queued_row(self):
        """The crash case: the thread is handed off and dies before reporting.

        `_send_in_background` is patched to a no-op, which is exactly what a
        killed daemon thread looks like from the caller's side — the letter's row
        must still be there, and it must be findable as unresolved.
        """
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch.object(service, "_send_in_background", side_effect=lambda fn: None):
            service.send_html(
                subject="S",
                html_message="<p>hi</p>",
                recipient_list=["a@x.test"],
                log_key="welcome",
                log_locale="en",
            )

        row = EmailLog.objects.get()
        self.assertEqual(row.status, "queued")
        self.assertIsNone(row.sent_at)
        self.assertTrue(row.is_abandoned)

    def test_sent_at_is_stamped_only_on_success(self):
        """The field must answer 'did the transport accept it', not 'when did we
        last touch the row' — otherwise a failed row looks delivered."""
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
        self.assertIsNone(row.sent_at)
        self.assertFalse(row.is_abandoned)

    def test_a_queued_row_that_was_sent_is_not_abandoned(self):
        """`sent_at` is load-bearing here, and only this case proves it.

        The other `is_abandoned` assertions use rows whose *status* already
        decides the answer, so a version of the property that ignored `sent_at`
        passed both. This is the ambiguous row the field exists for: the transport
        accepted it and the status update was what got lost, which is a reconciled
        send, not an abandoned one — resending it would double-mail someone.
        """
        from django.utils import timezone

        row = EmailLog.objects.create(
            recipient="a@x.test", status="queued", sent_at=timezone.now()
        )
        self.assertFalse(row.is_abandoned)

    def test_send_simple_records_a_row_at_all(self):
        """This path wrote nothing whatsoever.

        Measured on production: all 112 rows carry a key, i.e. every one came
        through `send_html`. Mail sent from here was recorded nowhere.
        """
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch.object(service, "_handle_email_sending", return_value=1), patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            service.send_simple(
                subject="S",
                message="hi",
                recipient_list=["a@x.test"],
                log_key="alert",
                log_locale="en",
            )

        row = EmailLog.objects.get()
        self.assertEqual((row.status, row.key), ("sent", "alert"))

    def test_send_simple_records_a_refused_send_as_failed(self):
        """`_handle_email_sending` returns 0 without raising, so a status keyed
        off exceptions alone would file a refused send as delivered."""
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch.object(service, "_handle_email_sending", return_value=0), patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            service.send_simple(
                subject="S", message="hi", recipient_list=["a@x.test"], log_key="alert"
            )

        self.assertEqual(EmailLog.objects.get().status, "failed")

    def test_multipart_records_a_row_and_notices_a_zero_result(self):
        """The head of the attachments family — four entry points route through
        it, and it discarded `send()`'s return value entirely."""
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with patch(
            "django_cfg.modules.django_email.service.EmailMultiAlternatives"
        ) as msg, patch.object(
            service, "_send_in_background", side_effect=lambda fn: fn()
        ):
            msg.return_value.send.return_value = 0
            service.send_multipart(
                subject="S",
                recipient_list=["a@x.test"],
                text_content="hi",
                log_key="report",
            )

        row = EmailLog.objects.get()
        self.assertEqual((row.status, row.key), ("failed", "report"))
        self.assertIsNone(row.sent_at)

    def test_bad_multipart_arguments_leave_no_queued_row(self):
        """The intent must not outlive a letter that was never going to be built."""
        from django_cfg.modules.django_email.service import DjangoEmailService

        service = DjangoEmailService()
        with self.assertRaises(ValueError):
            service.send_multipart(subject="S", recipient_list=["a@x.test"])
        self.assertEqual(EmailLog.objects.count(), 0)


class DedupKeyTests(TestCase):
    """`@rules/communications-and-notifications.md:88-95`: deduplicate by logical
    event + channel + recipient + template version."""

    def test_the_same_letter_to_the_same_person_shares_a_key(self):
        from django_cfg.modules.django_email.service import dedup_key_for

        self.assertEqual(
            dedup_key_for("welcome", "a@x.test", "en"),
            dedup_key_for("welcome", "a@x.test", "en"),
        )

    def test_address_case_does_not_create_a_second_identity(self):
        """`A@x.test` and `a@x.test` are one inbox; two keys would let the same
        letter through twice."""
        from django_cfg.modules.django_email.service import dedup_key_for

        self.assertEqual(
            dedup_key_for("welcome", "A@X.test", "en"),
            dedup_key_for("welcome", "a@x.test", "en"),
        )

    def test_a_different_locale_is_a_different_letter(self):
        """Locale stands in for template version: the same event re-rendered in
        another language is not a duplicate of the first."""
        from django_cfg.modules.django_email.service import dedup_key_for

        self.assertNotEqual(
            dedup_key_for("welcome", "a@x.test", "en"),
            dedup_key_for("welcome", "a@x.test", "ru"),
        )

    def test_different_recipients_never_share_a_key(self):
        from django_cfg.modules.django_email.service import dedup_key_for

        self.assertNotEqual(
            dedup_key_for("welcome", "a@x.test", "en"),
            dedup_key_for("welcome", "b@x.test", "en"),
        )

    def test_the_key_fits_the_column(self):
        """A silently truncated key collides with its own neighbours."""
        from django_cfg.modules.django_email.service import dedup_key_for

        key = dedup_key_for("k" * 300, "a" * 300 + "@x.test", "en")
        self.assertLessEqual(len(key), 200)

    def test_rows_written_by_either_path_carry_a_key(self):
        """A row with a blank key is invisible to any duplicate check — worse than
        a duplicate, because it reads as a letter nobody sent."""
        _record_send("welcome", ["a@x.test"], "S", "en", "sent", "")
        self.assertTrue(EmailLog.objects.get().dedup_key)


class LogWriteIsolationTests(TestCase):
    """A diagnostic write must not be able to break the caller's transaction.

    This is not hypothetical: running before the migration was applied, the
    failing INSERT poisoned the surrounding transaction, the `except` returned
    normally as designed, and then every later query raised
    `TransactionManagementError`. The send died anyway — a `try` around a write
    inside someone else's `atomic` protects the logger, not the caller.
    """

    def test_a_failing_intent_write_leaves_the_transaction_usable(self):
        """The failure must come from the DATABASE, not from Python.

        Three earlier versions of this test proved nothing, and the third is the
        instructive one:

        1. `side_effect=RuntimeError` — a Python error, never reaches the database,
           so there was nothing to recover from.
        2. calling `bulk_create` from inside its own patch — `RecursionError`,
           a Python error again.
        3. raw SQL, to dodge that recursion — the `IntegrityError` fired, and the
           test *still* passed with the savepoint removed.

        Isolating that last one gave the actual mechanism: **the ORM marks the
        transaction as needing rollback; a raw cursor does not.** Measured, at the
        outermost `atomic`, failing INSERT / caller survives:

            ORM bulk_create, no savepoint : BROKEN (TransactionManagementError)
            ORM bulk_create, savepoint    : survives
            raw cursor,      no savepoint : survives

        So the failure must come through the ORM, and the recursion is avoided by
        failing a *different* ORM write instead of re-entering the patched one.
        """
        from django.db import transaction

        from django_cfg.modules.django_email.service import _open_send

        def _bad_insert(rows):
            # A real, failing ORM write: NOT NULL fed a NULL. `create` rather than
            # `bulk_create`, so this cannot recurse into the patch it stands in for.
            EmailLog.objects.create(recipient=None, status=None)

        with transaction.atomic():
            with patch.object(EmailLog.objects, "bulk_create", side_effect=_bad_insert):
                self.assertEqual(_open_send("welcome", ["a@x.test"], "S", "en"), [])
            # The caller's work must still be possible.
            EmailContent.objects.create(key="probe", locale="en", subject="S")

        self.assertTrue(EmailContent.objects.filter(key="probe").exists())

    def test_a_failing_outcome_write_leaves_the_transaction_usable(self):
        from django.db import transaction

        from django_cfg.modules.django_email.service import _close_send

        def _bad_update(*a, **kw):
            # Through the ORM, for the reason spelled out in the intent test above:
            # a raw cursor's IntegrityError does not mark the transaction broken,
            # so it cannot detect a missing savepoint.
            EmailLog.objects.create(recipient=None, status=None)

        row = EmailLog.objects.create(recipient="a@x.test", status="queued")
        with transaction.atomic():
            with patch(
                "django.db.models.QuerySet.update", side_effect=_bad_update
            ):
                _close_send([row.pk], "sent", "")  # must not raise
            EmailContent.objects.create(key="probe", locale="en", subject="S")

        self.assertTrue(EmailContent.objects.filter(key="probe").exists())

    def test_no_intent_means_no_invented_outcome_row(self):
        """`_open_send` returning [] means the intent was never recorded; writing
        an outcome anyway would report a send with no intent behind it."""
        from django_cfg.modules.django_email.service import _close_send

        _close_send([], "sent", "")
        self.assertEqual(EmailLog.objects.count(), 0)
