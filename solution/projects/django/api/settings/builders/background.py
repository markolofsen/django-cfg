"""Background work: RQ queues and the periodic schedule.

Split out of ``api/settings/config.py``.
"""

from __future__ import annotations

from typing import Optional

from django_cfg import DjangoRQConfig, RQQueueConfig, RQScheduleConfig


def build_rq_config() -> Optional[DjangoRQConfig]:
    """Queues, admin link and the periodic schedule."""
    return DjangoRQConfig(
        enabled=True,
        redis_db=9,  # djangocfg - see deployment/REDIS.md
        queues=[
            RQQueueConfig(queue="default", default_timeout=360, default_result_ttl=500),
            RQQueueConfig(queue="high", default_timeout=180, default_result_ttl=300),
            RQQueueConfig(queue="low", default_timeout=600, default_result_ttl=800),
            RQQueueConfig(queue="knowledge", default_timeout=600, default_result_ttl=3600),
        ],
        show_admin_link=True,
        prometheus_enabled=True,
        schedules=[
            # RQScheduleConfig(func="apps.crypto.tasks.update_coin_prices", interval=300, queue="default", limit=50, verbosity=0, description="Update coin prices (frequent)"),
        ],
    )
