"""
Embed chat messages in chunks (optional vectorisation, decision D6). Also the backfill: repeat until it reports 0 threads.

Usage:
    python manage.py chat_vectorise --chunk-model cfg_chat.ThreadChunk             # one batch of 200 threads
    python manage.py chat_vectorise --chunk-model assistant.ThreadChunk --all      # until nothing is pending
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_llm.agent.chat.vectors import service
from django_cfg.modules.django_llm.agent.chat.vectors.embedder import DEFAULT_MODEL, llm_embedder
from django_cfg.modules.django_llm.agent.chat.vectors.models import AbstractChatChunk


class Command(BaseCommand):
    help = "Embed unindexed chat messages in chunks of 10-20 (never one vector per message)"

    def add_arguments(self, parser):
        parser.add_argument("--chunk-model", required=True, help="app_label.ChunkModel (a subclass of AbstractChatChunk)")
        parser.add_argument("--limit", type=int, default=200, help="threads per batch")
        parser.add_argument("--all", action="store_true", help="repeat until no thread is pending (the backfill)")
        parser.add_argument("--embedding-model", default=DEFAULT_MODEL)

    def handle(self, *args, **options):
        try:
            chunk_model = apps.get_model(options["chunk_model"])
        except (LookupError, ValueError) as err:
            raise CommandError(f"no model {options['chunk_model']!r}") from err
        if not issubclass(chunk_model, AbstractChatChunk):
            raise CommandError(f"{options['chunk_model']} is not a subclass of AbstractChatChunk")
        embed = llm_embedder(options["embedding_model"])
        total = service.SyncResult()
        while True:
            done = service.sync_pending(chunk_model, embed, limit=options["limit"], model=options["embedding_model"])
            for name, value in vars(done).items():
                setattr(total, name, getattr(total, name) + value)
            if not options["all"] or done.threads == 0 or done.created + done.reembedded == 0:
                break
        self.stdout.write(f"{chunk_model._meta.label}: {vars(total)}")
