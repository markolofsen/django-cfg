"""
:class:`QueueHealthMonitor` — orchestrates one RQ queue-health check cycle.

A single :meth:`QueueHealthMonitor.run` call:

1. Resolves the :class:`RQHealthConfig` (from the active DjangoConfig, or an
   explicit override).
2. Iterates the monitored queues, collecting :class:`QueueMetrics` and
   evaluating them into :class:`QueueStatus`.
3. Emits one structured INFO summary, plus WARNING/ERROR log lines per queue.
4. Applies per-(queue, severity) Redis cooldown and sends Telegram alerts /
   recovery messages.
5. Optionally prunes orphaned queue IDs when ``auto_prune_orphan_ids`` is set.

:meth:`run` never raises — it is designed to be the body of a scheduled RQ job.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from django_cfg.models.django.rq_health import RQHealthConfig
from django_cfg.utils import get_logger

from .alerting import send_queue_alert, send_queue_recovery
from .cooldown import is_alerting, mark_alerted, mark_recovered, should_alert
from .evaluator import QueueStatus, Severity, evaluate
from .metrics import collect_queue_metrics

logger = get_logger("rq.health")


class QueueHealthMonitor:
    """
    Runs queue-health checks for all monitored RQ queues.

    Args:
        config: Optional :class:`RQHealthConfig` override. When omitted, the
            config is resolved from the active DjangoConfig (``django_rq.health``).
        dry_run: When True, evaluate and log but never send Telegram alerts and
            never prune orphan IDs.
    """

    def __init__(self, config: Optional[RQHealthConfig] = None, dry_run: bool = False):
        self._config = config
        self.dry_run = dry_run

    # ------------------------------------------------------------------ config

    def resolve_config(self) -> RQHealthConfig:
        """Return the :class:`RQHealthConfig` (explicit override or from DjangoConfig)."""
        if self._config is not None:
            return self._config

        try:
            from django_cfg.modules.django_rq.services.config_helper import get_rq_config

            rq_config = get_rq_config()
            if rq_config is not None and getattr(rq_config, "health", None) is not None:
                return rq_config.health
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"could not resolve RQHealthConfig from DjangoConfig: {exc}")

        # Fall back to defaults so the monitor still functions.
        return RQHealthConfig()

    def resolve_queues(self, config: RQHealthConfig) -> List[str]:
        """Return the list of queue names to monitor."""
        if config.monitored_queues:
            return list(config.monitored_queues)

        try:
            from django_cfg.modules.django_rq.services.config_helper import get_rq_config

            rq_config = get_rq_config()
            if rq_config is not None:
                return rq_config.get_queue_names()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"could not resolve queue list: {exc}")

        return ["default"]

    # -------------------------------------------------------------------- run

    def run(self) -> Dict[str, object]:
        """
        Execute one health-check cycle.

        Returns:
            A summary dict — safe to use as an RQ job return value. Never raises.
        """
        summary: Dict[str, object] = {
            "checked": 0,
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "alerts_sent": 0,
            "recoveries_sent": 0,
            "orphans_pruned": 0,
            "dry_run": self.dry_run,
            "queues": {},
            "error": None,
        }

        try:
            config = self.resolve_config()
            if not config.enabled:
                logger.info("RQ queue-health monitor is disabled — skipping cycle")
                summary["error"] = "disabled"
                return summary

            queue_names = self.resolve_queues(config)
            redis_conn = self._get_redis(queue_names)

            statuses: List[QueueStatus] = []
            for queue_name in queue_names:
                status = self._check_queue(queue_name, config)
                statuses.append(status)
                summary["checked"] = int(summary["checked"]) + 1
                summary[status.label] = int(summary[status.label]) + 1
                summary["queues"][queue_name] = {  # type: ignore[index]
                    "status": status.label,
                    "overflow": status.overflow,
                    "stuck": status.stuck,
                    "breaches": [b.metric for b in status.breaches],
                }

            # Structured per-cycle INFO summary.
            logger.info(
                "RQ queue-health cycle: "
                f"{summary['checked']} checked, {summary['healthy']} healthy, "
                f"{summary['warning']} warning, {summary['critical']} critical",
                extra={
                    "metric": "cycle",
                    "value": summary["checked"],
                    "status": "critical" if summary["critical"] else (
                        "warning" if summary["warning"] else "healthy"
                    ),
                },
            )

            # Alerting + recovery + orphan pruning.
            if redis_conn is not None:
                for status in statuses:
                    self._handle_status(status, config, redis_conn, summary)

        except Exception as exc:  # monitor must never raise out of the task
            summary["error"] = str(exc)
            logger.error(
                f"RQ queue-health monitor failed: {exc}",
                exc_info=True,
                extra={"metric": "monitor", "status": "critical"},
            )

        return summary

    # ----------------------------------------------------------------- helpers

    def _get_redis(self, queue_names: List[str]):
        """Return a Redis connection from the first available queue, or None."""
        try:
            import django_rq

            queue = django_rq.get_queue(queue_names[0] if queue_names else "default")
            return queue.connection
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"could not obtain Redis connection: {exc}")
            return None

    def _check_queue(self, queue_name: str, config: RQHealthConfig) -> QueueStatus:
        """Collect + evaluate a single queue and emit per-queue log lines."""
        metrics = collect_queue_metrics(queue_name, orphan_sample_size=config.orphan_sample_size)
        thresholds = config.thresholds_for(queue_name)
        status = evaluate(metrics, thresholds)

        # Log every breach with consistent structured extra.
        for breach in status.breaches:
            log = logger.error if breach.severity >= Severity.CRITICAL else logger.warning
            log(
                f"queue '{queue_name}' {breach.metric}={breach.value} "
                f"breached {breach.severity.label} threshold {breach.threshold}",
                extra={
                    "queue": queue_name,
                    "metric": breach.metric,
                    "value": breach.value,
                    "threshold": breach.threshold,
                    "status": breach.severity.label,
                },
            )

        if status.is_healthy:
            logger.debug(f"queue '{queue_name}' healthy", extra={"queue": queue_name, "status": "healthy"})

        return status

    def _handle_status(
        self,
        status: QueueStatus,
        config: RQHealthConfig,
        redis_conn,
        summary: Dict[str, object],
    ) -> None:
        """Apply cooldown, send alerts/recovery, and optionally prune orphans."""
        queue = status.queue

        if status.is_healthy:
            # Recovery: only for queues that were actually alerting.
            if is_alerting(redis_conn, queue):
                if not self.dry_run and config.telegram_alerts_enabled and config.send_recovery_alerts:
                    if send_queue_recovery(queue, alert_chat_id=config.alert_chat_id):
                        summary["recoveries_sent"] = int(summary["recoveries_sent"]) + 1
                        logger.info(f"queue '{queue}' recovered — recovery alert sent")
                mark_recovered(redis_conn, queue)
            return

        # Degraded — decide whether to alert (cooldown + escalation).
        if not config.telegram_alerts_enabled:
            mark_alerted(redis_conn, queue)
        elif self.dry_run:
            logger.info(f"[dry-run] would alert for queue '{queue}' ({status.label})")
        else:
            allowed = should_alert(redis_conn, queue, status.severity, config.alert_cooldown_sec)
            if allowed:
                if send_queue_alert(status, alert_chat_id=config.alert_chat_id):
                    summary["alerts_sent"] = int(summary["alerts_sent"]) + 1
            else:
                logger.warning(
                    f"queue '{queue}' is {status.label} but alert suppressed by cooldown",
                    extra={"queue": queue, "metric": "alert", "status": status.label},
                )
            mark_alerted(redis_conn, queue)

        # Optional orphan-id self-heal (opt-in).
        if config.auto_prune_orphan_ids and not self.dry_run:
            metrics = status.metrics
            if metrics is not None and metrics.orphan_missing > 0:
                pruned = self._prune_orphans(queue)
                summary["orphans_pruned"] = int(summary["orphans_pruned"]) + pruned

    def _prune_orphans(self, queue_name: str) -> int:
        """Prune orphaned queue IDs for a queue; returns the count removed."""
        try:
            from django_cfg.modules.django_rq.tasks.maintenance import prune_orphaned_queue_ids

            result = prune_orphaned_queue_ids(queue_name=queue_name, dry_run=False)
            return int(result.get("pruned", 0))
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"orphan pruning failed for '{queue_name}': {exc}", exc_info=True)
            return 0


__all__ = [
    "QueueHealthMonitor",
]
