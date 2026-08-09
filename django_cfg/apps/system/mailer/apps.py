"""The mailer app: what a project sends, in which language, and what happened.

Separate from ``accounts`` on purpose. Accounts owns *who* a user is and *when* a
letter is triggered; this app owns the correspondence itself — the editable copy
per locale, and the record of each delivery. Putting the copy in ``accounts``
(which is where it started) tied a mail concern to a user model and left no
obvious home for a send log or a second letter that has nothing to do with
signing up.
"""

from django.apps import AppConfig


class MailerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.system.mailer"
    label = "django_cfg_mailer"
    verbose_name = "Mailer"
