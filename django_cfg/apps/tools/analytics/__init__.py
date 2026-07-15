"""
First-party, self-hosted analytics for django-cfg.

Pageviews, cookieless sessions, and — the part hosted analytics structurally
cannot do — attribution to your *authenticated users*.

Design constraint (non-negotiable): **zero extra runtime processes.** Ingest is a
synchronous INSERT in the request thread. No Celery, no RQ worker, no consumer
daemon, no sidecar container, no cron. It works out of the box from `pip install`.

That is not a shortcut — it is the production baseline. Umami (MIT) writes
synchronously with no worker at all, and Shynet ships CELERY_TASK_ALWAYS_EAGER
by default. Measured on real durable storage, the write costs ~0.1 ms with
`SET LOCAL synchronous_commit = off`, while merely opening a DB connection costs
2.8 ms. Queueing it would optimize the wrong term.

Configuration:
    ```python
    from django_cfg import DjangoConfig, AnalyticsConfig

    class MyConfig(DjangoConfig):
        analytics = AnalyticsConfig()
    ```

See @dev/active/analytics/PLAN.md for the measurements and the rejected designs.
"""

default_app_config = "django_cfg.apps.tools.analytics.apps.AnalyticsAppConfig"
