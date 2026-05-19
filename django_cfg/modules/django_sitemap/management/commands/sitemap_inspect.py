"""`python manage.py sitemap_inspect` — list registered sources + counts.

Useful for verifying a quality filter didn't accidentally exclude
everything.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from django_cfg.modules.django_sitemap import all_sources, resolve_field


class Command(BaseCommand):
    help = "List registered sitemap sources with row counts and sample URLs."

    def handle(self, *args, **options) -> None:
        sources = all_sources()
        if not sources:
            self.stdout.write(self.style.WARNING("No sitemap sources registered."))
            return

        rows: list[tuple[str, str, str, str]] = []
        for source in sources:
            qs = source.queryset_factory()
            total = qs.count()
            order_args = [c.strip() for c in source.order.split(",") if c.strip()]
            sample = qs.order_by(*order_args).first()
            if sample is None:
                sample_url = "(no rows)"
            else:
                url_kwargs = {
                    alias: resolve_field(sample, path)
                    for alias, path in source.fields.items()
                }
                sample_url = source.url_template.format(**url_kwargs)
            chunks = max(1, (total + source.page_size - 1) // source.page_size)
            rows.append((source.name, f"{total:,}", str(chunks), sample_url))

        widths = [max(len(r[i]) for r in rows + [("Source", "Total", "Chunks", "Sample URL")]) for i in range(4)]
        fmt = "  ".join(f"{{:<{w}}}" for w in widths)
        self.stdout.write(fmt.format("Source", "Total", "Chunks", "Sample URL"))
        self.stdout.write(fmt.format("-" * widths[0], "-" * widths[1], "-" * widths[2], "-" * widths[3]))
        for r in rows:
            self.stdout.write(fmt.format(*r))
