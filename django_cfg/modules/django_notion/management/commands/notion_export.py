"""Move rows of a Django model into a Notion data source (one way: Django to Notion).

    python manage.py notion_export auth.User --to <data source id or target name>             # dry run (default)
    python manage.py notion_export auth.User --to <ds> --samples 3                            # + masked shapes
    python manage.py notion_export auth.User --to <ds> --apply --limit 3                      # a tiny real batch
    python manage.py notion_export auth.User --to <ds> --apply --manifest /tmp/m.tsv   # written row by row

Safe to re-run: a row whose key is already in Notion is skipped; nothing is updated or deleted. Reports carry counts
and masked shapes only. The mapping comes from ``register_export``; the user model has a minimal built-in preset.
"""

from __future__ import annotations

from datetime import date

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_notion import client as client_mod
from django_cfg.modules.django_notion import conf
from django_cfg.modules.django_notion.exceptions import NotionError
from django_cfg.modules.django_notion.export import Throttle, build_plan, execute, get_export, mask
from django_cfg.modules.django_notion.export.mapping import build_properties


class Command(BaseCommand):
    help = "Export a model's rows into a Notion data source. Dry run unless --apply."

    def add_arguments(self, parser):
        parser.add_argument("model", help="app_label.ModelName")
        parser.add_argument("--to", required=True, help="Notion data source id, or the name of a NotionConfig target")
        parser.add_argument("--apply", action="store_true", help="Write to Notion. Without it nothing is written.")
        parser.add_argument("--limit", type=int, default=None, help="At most N new rows this run.")
        parser.add_argument("--batch", default="", help="Import batch id stamped on every row (default: <model>-<date>).")
        parser.add_argument("--manifest", default="", help="With --apply: append 'pk<TAB>page id' lines here (no PII).")
        parser.add_argument("--samples", type=int, default=0, help="Print N masked sample rows.")
        parser.add_argument("--interval", type=float, default=0.35, help="Seconds between Notion requests (3/s).")
        parser.add_argument("--no-notion", action="store_true", help="Plan from the database only; do not read Notion (not with --apply).")

    def handle(self, *args, **o):
        if o["apply"] and o["no_notion"]:
            raise CommandError("--apply needs to read Notion; --no-notion is for planning only")
        try:
            model = apps.get_model(o["model"])
        except (LookupError, ValueError) as exc:
            raise CommandError(f"unknown model {o['model']!r}: use app_label.ModelName") from exc
        try:
            mapping = get_export(model._meta.label_lower)
            client, data_source = (None, o["to"]) if o["no_notion"] else self._destination(o["to"])
        except NotionError as exc:
            raise CommandError(str(exc)) from exc
        batch = o["batch"] or f"{model._meta.label_lower}-{date.today():%Y-%m-%d}"

        w = self.stdout.write
        w(f"mode: {'APPLY' if o['apply'] else 'dry-run'}   model: {model._meta.label}   batch: {batch}")
        plan = build_plan(mapping, model)
        rep = execute(plan, client, data_source, apply=o["apply"], batch=batch, limit=o["limit"],
                      throttle=Throttle(o["interval"]), read_notion=not o["no_notion"],
                      manifest_path=o["manifest"] if o["apply"] and o["manifest"] else None)
        for line in rep.lines(apply=o["apply"], limit=o["limit"]):
            w(line)
        for rec in plan.records[: o["samples"]]:
            cols = sorted(build_properties(mapping, rec.obj, rec.key, batch))
            w(f"  sample: pk {rec.pk} | {mask(rec.key)} | columns {cols}")
        if o["apply"] and (rep.blockers or rep.errors):
            raise CommandError("finished with blockers or errors; re-run after fixing (idempotent)")

    def _destination(self, to: str):
        cfg = conf.get_notion_config()
        target = cfg.targets.get(to)
        client = client_mod.get_client(target)
        if target is not None:
            return client, client_mod.resolve_data_source(client, target)
        return client, to
