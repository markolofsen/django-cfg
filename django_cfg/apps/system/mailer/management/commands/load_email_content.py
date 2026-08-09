"""Load per-locale letter copy from templates into ``EmailContent``.

    python manage.py load_email_content welcome
    python manage.py load_email_content welcome --locales ru de
    python manage.py load_email_content welcome --dry-run
    python manage.py load_email_content welcome --overwrite

This is the migration path off file-only templates, and the loader for the
fixtures shipped with django-cfg. It reads the prose out of
``emails/<key>/<locale>.html`` by rendering each block, and writes one row per
locale.

Why render rather than parse: the blocks contain ``{{ project_name }}`` and
entities, and a regex over template source gets both wrong. Rendering with a
sentinel project name and turning it back into the placeholder afterwards keeps
the copy reusable across projects.

Existing rows are left alone unless ``--overwrite`` is given: someone may have
edited the text in the admin, and reloading a fixture must not silently discard
that.
"""

from __future__ import annotations

import html as htmllib
import re

from django.core.management.base import BaseCommand, CommandError
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

# A project name that cannot occur in prose, so it can be swapped back for the
# placeholder without a false positive.
SENTINEL = "\x00PROJECT_NAME\x00"

# model field -> whether the block holds multiple paragraphs
BLOCKS = {
    "subject": False,
    "greeting": False,
    "lede": True,
    "run_intro": False,
    "run_after": True,
    "points": True,
    "outro": True,
    "signoff": True,
    "role": False,
}


def _render_block(template, name: str, context: dict) -> str:
    """Render one named block of an already-loaded template, or ''."""
    nodelist = template.template.nodelist
    from django.template.loader_tags import BlockNode, ExtendsNode

    def find(nodes):
        for node in nodes:
            if isinstance(node, BlockNode) and node.name == name:
                return node
            if isinstance(node, ExtendsNode):
                found = find(node.nodelist)
                if found is not None:
                    return found
        return None

    block = find(nodelist)
    if block is None:
        return ""

    from django.template import Context

    return block.render(Context(context))


PARAGRAPH_SPLIT = "\x00P\x00"


def _clean(raw: str, multiline: bool) -> str:
    """Markup and entities out; one line per *paragraph*.

    Only ``</p>`` ends a paragraph. Newlines in the template file are just
    wrapping and get collapsed — splitting on them instead would store one
    "paragraph" per line of markup, which turns a two-paragraph lede into five.
    """
    text = re.sub(r"</p\s*>", PARAGRAPH_SPLIT, raw, flags=re.I)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = htmllib.unescape(text).replace("\u00a0", " ")

    paragraphs = []
    for chunk in text.split(PARAGRAPH_SPLIT):
        collapsed = re.sub(r"\s+", " ", chunk).strip()
        if collapsed:
            paragraphs.append(collapsed)
    if not multiline:
        return " ".join(paragraphs)
    return "\n".join(paragraphs)


class Command(BaseCommand):
    help = "Load letter copy from emails/<key>/<locale>.html into EmailContent"

    def add_arguments(self, parser):
        parser.add_argument("key", help="Letter key, e.g. 'welcome'")
        parser.add_argument(
            "--locales",
            nargs="+",
            help="Locales to load (default: every supported locale that has a template)",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace rows that already exist (they may hold admin edits)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be written and change nothing",
        )
        parser.add_argument(
            "--defaults",
            action="store_true",
            help=(
                "Load django-cfg's built-in English copy instead of reading the "
                "project's templates — for a fresh install with nothing to import"
            ),
        )

    def handle(self, *args, **options):
        from django_cfg.apps.system.mailer.models import EmailContent
        from django_cfg.apps.system.accounts.services.welcome import SUPPORTED_LOCALES

        key = options["key"]
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]

        if options["defaults"]:
            return self._load_defaults(key, overwrite=overwrite, dry_run=dry_run)

        locales = options["locales"] or list(SUPPORTED_LOCALES)
        created = updated = skipped = missing = 0

        for locale in locales:
            name = f"emails/{key}/{locale}.html"
            try:
                template = get_template(name)
            except TemplateDoesNotExist:
                missing += 1
                self.stdout.write(f"  {locale}: no template ({name})")
                continue

            context = {"project_name": SENTINEL, "locale": locale, "user": None}
            fields = {}
            for field, multiline in BLOCKS.items():
                rendered = _render_block(template, field, context)
                fields[field] = _clean(rendered, multiline).replace(
                    SENTINEL, "{{ project_name }}"
                )

            if not fields["subject"]:
                raise CommandError(
                    f"{name} rendered an empty subject — does it define {{% block subject %}}?"
                )

            existing = EmailContent.objects.filter(key=key, locale=locale).first()
            if existing and not overwrite:
                skipped += 1
                self.stdout.write(f"  {locale}: exists, left alone (--overwrite to replace)")
                continue

            if dry_run:
                self.stdout.write(f"  {locale}: would {'update' if existing else 'create'} — {fields['subject']!r}")
                continue

            if existing:
                for field, value in fields.items():
                    setattr(existing, field, value)
                existing.is_active = True
                existing.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"  {locale}: updated"))
            else:
                EmailContent.objects.create(key=key, locale=locale, **fields)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  {locale}: created"))

        summary = f"{created} created, {updated} updated, {skipped} skipped"
        if missing:
            summary += f", {missing} without a template"
        self.stdout.write(("[dry-run] " if dry_run else "") + summary)

    def _load_defaults(self, key: str, *, overwrite: bool, dry_run: bool) -> None:
        """Write django-cfg's own English copy for ``key``."""
        from django_cfg.apps.system.mailer.fixtures.email_copy import (
            DEFAULT_EMAIL_COPY,
        )
        from django_cfg.apps.system.mailer.models import EmailContent
        from django_cfg.apps.system.accounts.services.welcome import DEFAULT_LOCALE

        fields = DEFAULT_EMAIL_COPY.get(key)
        if fields is None:
            raise CommandError(
                f"No built-in copy for {key!r} "
                f"(available: {', '.join(sorted(DEFAULT_EMAIL_COPY))})"
            )

        existing = EmailContent.objects.filter(key=key, locale=DEFAULT_LOCALE).first()
        if existing and not overwrite:
            self.stdout.write(
                f"  {DEFAULT_LOCALE}: exists, left alone (--overwrite to replace)"
            )
            return
        if dry_run:
            verb = "update" if existing else "create"
            self.stdout.write(f"[dry-run] would {verb} {key} [{DEFAULT_LOCALE}]")
            return

        EmailContent.objects.update_or_create(
            key=key, locale=DEFAULT_LOCALE, defaults={**fields, "is_active": True}
        )
        self.stdout.write(
            self.style.SUCCESS(f"  {DEFAULT_LOCALE}: built-in copy loaded for {key!r}")
        )
