"""
Django-CFG wrapper for django-rq rqworker-pool command.

Runs multiple RQ workers in a pool for better performance.

Example:
    python manage.py rqworker_pool default --num-workers 4
    python manage.py rqworker_pool high default --num-workers 8
"""

from django_rq.management.commands.rqworker_pool import Command as DjangoRQWorkerPoolCommand


class Command(DjangoRQWorkerPoolCommand):
    """
    Runs a pool of RQ workers for improved throughput.

    Inherits all functionality from django-rq's rqworker-pool command.
    Creates multiple worker processes to handle jobs in parallel.

    Common options:
        --num-workers N      Number of worker processes (default: CPU count)
        --burst              Run in burst mode
        --name NAME          Worker name prefix
    """

    help = 'Runs a pool of RQ workers for django-cfg (wrapper for django-rq rqworker-pool)'
