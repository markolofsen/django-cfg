"""
Django-CFG wrapper for django-rq rqworker-pool command.

Runs multiple RQ workers in a pool for better performance.

Example:
    python manage.py rqworker_pool default --num-workers 4
    python manage.py rqworker_pool high default --num-workers 8
"""

import importlib

from django_cfg.modules.django_rq.fork_safety import fix_macos_fork_safety, prepare_forking_worker

# Before any import that might initialise ObjC.
fix_macos_fork_safety()

# django-rq ships this command as `rqworker-pool.py`; the hyphen means no
# `from ... import` can name it, and the import this file used to have failed
# on every run with ModuleNotFoundError.
DjangoRQWorkerPoolCommand = importlib.import_module(
    "django_rq.management.commands.rqworker-pool"
).Command


class Command(DjangoRQWorkerPoolCommand):
    """
    Runs a pool of RQ workers for improved throughput.

    Inherits all functionality from django-rq's rqworker-pool command.
    Creates multiple worker processes to handle jobs in parallel.

    Common options:
        --num-workers N      Number of worker processes (default: CPU count)
        --burst              Run in burst mode
        --name NAME          Worker name prefix

    Workers are forked, so the same database preparation as ``rqworker``
    applies — see ``django_cfg.modules.django_rq.fork_safety``.
    """

    help = 'Runs a pool of RQ workers for django-cfg (wrapper for django-rq rqworker-pool)'

    def handle(self, *args, **options):
        prepare_forking_worker()
        return super().handle(*args, **options)
