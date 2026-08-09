"""Editable, per-locale copy for system letters.

**Only the words live here.** The layout stays a Django template in the product's
own tree, and it renders these fields. That split is the whole design:

- *In the database* — subject, greeting, paragraphs. What a translator or the
  founder rewrites, per language, without a deploy.
- *In the template* — tables, inline styles, the shell command block, `dir`,
  the signature line. Editing that once must not mean editing it 17 times, and a
  visual change belongs in a diff someone can review.

Storing whole rendered letters instead would move markup into 17 text columns:
template inheritance stops working, the plain-text part can no longer be derived
from the HTML, and a broken table becomes invisible until it reaches an inbox.

The fallback chain is resolved in ``EmailContent.resolve``, not by the caller,
because "no Danish row yet" must degrade to English rather than raise.
"""

from __future__ import annotations

from typing import Optional

from django.db import models


class EmailContent(models.Model):
    """One letter's copy, in one language.

    Keyed by ``(key, locale)``: ``key`` names the letter (``welcome``), ``locale``
    the language. A missing locale is normal — see ``resolve``.
    """

    key = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Which letter this is, e.g. 'welcome'. Matches the template directory name.",
    )
    locale = models.CharField(
        max_length=16,
        help_text="BCP-47 tag, e.g. 'ru' or 'pt-BR'. Region subtags are kept as-is.",
    )

    subject = models.CharField(
        max_length=255,
        help_text="Envelope Subject: header. Translated — an English subject over "
                  "a translated letter is the most visible way to get this wrong.",
    )

    # The letter's prose, one field per block the template exposes. Blank is
    # allowed throughout: a block a locale leaves empty simply renders nothing,
    # so a partial translation degrades gracefully instead of failing to send.
    greeting = models.CharField(max_length=128, blank=True, help_text="'Hi —'")
    lede = models.TextField(blank=True, help_text="Opening paragraphs. One per line.")
    run_intro = models.CharField(
        max_length=255, blank=True, help_text="Line introducing the command block."
    )
    run_after = models.TextField(
        blank=True, help_text="Paragraphs after the command block. One per line."
    )
    points = models.TextField(
        blank=True, help_text="The middle paragraphs. One per line."
    )
    outro = models.TextField(blank=True, help_text="Closing paragraph(s). One per line.")
    signoff = models.TextField(
        blank=True, help_text="The ask before the signature, e.g. inviting a reply."
    )
    role = models.CharField(
        max_length=128,
        blank=True,
        help_text="What follows the sender's name in the signature, e.g. 'founder of Cmdop'.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Unchecking falls this locale back to the default one, without deleting the text.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "django_cfg_mailer"
        verbose_name = "Email content"
        verbose_name_plural = "Email content"
        constraints = [
            models.UniqueConstraint(
                fields=["key", "locale"], name="emailcontent_unique_key_locale"
            )
        ]
        ordering = ("key", "locale")

    def __str__(self) -> str:
        return f"{self.key} [{self.locale}]"

    # --- resolution -----------------------------------------------------

    @classmethod
    def resolve(
        cls, key: str, locale: str, default_locale: str = "en"
    ) -> Optional["EmailContent"]:
        """Best available copy for ``key`` in ``locale``, or None.

        Order: the exact tag, then its base language (so ``pt-BR`` reaches a
        ``pt`` row), then ``default_locale``. Inactive rows are skipped at every
        step, which is what makes ``is_active`` a usable switch rather than a
        flag that silently blanks a letter.

        Returns None when the key has no usable row at all — the caller then
        renders the template's own built-in defaults, so a project that never
        loads fixtures still sends a correct letter.
        """
        tags = [locale]
        base = (locale or "").split("-")[0]
        if base and base != locale:
            tags.append(base)
        if default_locale not in tags:
            tags.append(default_locale)

        rows = {
            row.locale: row
            for row in cls.objects.filter(key=key, locale__in=tags, is_active=True)
        }
        for tag in tags:
            if tag in rows:
                return rows[tag]
        return None

    def as_context(self) -> dict:
        """The fields as template context, with multi-line blocks split.

        Paragraph blocks are stored one-per-line and handed over as lists, so the
        template controls the markup — the database never holds a ``<p>`` tag.
        """

        def paragraphs(value: str) -> list[str]:
            return [line.strip() for line in (value or "").splitlines() if line.strip()]

        return {
            "subject": self.subject,
            "greeting": self.greeting,
            "lede": paragraphs(self.lede),
            "run_intro": self.run_intro,
            "run_after": paragraphs(self.run_after),
            "points": paragraphs(self.points),
            "outro": paragraphs(self.outro),
            "signoff": paragraphs(self.signoff),
            "role": self.role,
        }
