"""
Global RQ exception handler for server-side monitoring.

Registered via RQ_EXCEPTION_HANDLERS in AppConfig.ready() when
server_capture_enabled=True and the RQ integration is available.

Also provides MonitoringWorker — a Worker subclass that captures
OOM / SIGKILL events via work_horse_killed_handler.
"""

import logging
import traceback as tb_module

logger = logging.getLogger(__name__)


def monitor_rq_exception_handler(job, exc_type, exc_value, tb):
    """
    Global RQ exception handler — captures job failures into ServerEvent.

    Returns True to allow the default RQ handler chain to continue
    (e.g. moving the job to the FailedJobRegistry).

    Fingerprint: rq::{queue_name}::{func_name}::{exc_type}
    No line numbers — same failure deduplicates across deploys.
    """
    try:
        from django.apps import apps
        if not apps.ready:
            return True

        from django_cfg.apps.system.monitor.__cfg__ import get_settings
        cfg = get_settings()
        if not cfg.server_capture_enabled:
            return True
        db_alias = cfg.monitor_db_alias or "monitor"

        from django_cfg.apps.system.monitor.models.server_event import ServerEvent

        queue_name = getattr(job, "origin", "") or ""
        func_name = getattr(job, "func_name", "") or ""
        exc_type_name = exc_type.__name__ if exc_type else "UnknownError"

        stack_trace = ""
        if exc_type and exc_value and tb:
            stack_trace = "".join(
                tb_module.format_exception(exc_type, exc_value, tb)
            )[:10000]

        message = str(exc_value)[:2000] if exc_value else exc_type_name

        extra = {
            "job_id": getattr(job, "id", ""),
            "queue": queue_name,
            "func_name": func_name,
            "args": repr(getattr(job, "args", ()))[:500],
            "kwargs": repr(getattr(job, "kwargs", {}))[:500],
        }

        ServerEvent.record(
            exception_type=f"{exc_type.__module__}.{exc_type.__qualname__}" if exc_type else "UnknownError",
            module=func_name.rsplit(".", 1)[0] if "." in func_name else func_name,
            func_name=func_name.rsplit(".", 1)[-1] if "." in func_name else func_name,
            event_type=ServerEvent.EventType.RQ_FAILURE,
            message=message,
            db_alias=db_alias,
            stack_trace=stack_trace or None,
            extra=extra,
        )

    except Exception:
        logger.exception("monitor_rq_exception_handler: failed to capture RQ failure")

    return True  # Continue to next handler in chain


def _capture_oom_kill(job_id: str, queue_name: str, worker_name: str) -> None:
    """
    Called by MonitoringWorker when a work-horse is killed (OOM / SIGKILL).
    Writes an OOM_KILL ServerEvent.
    """
    try:
        from django.apps import apps
        if not apps.ready:
            return

        from django_cfg.apps.system.monitor.__cfg__ import get_settings
        cfg = get_settings()
        if not cfg.server_capture_enabled:
            return
        db_alias = cfg.monitor_db_alias or "monitor"

        from django_cfg.apps.system.monitor.models.server_event import ServerEvent

        ServerEvent.record(
            exception_type="OOM_KILL",
            module=queue_name,
            func_name=worker_name,
            event_type=ServerEvent.EventType.OOM_KILL,
            message=f"Worker process killed (OOM/SIGKILL): job {job_id}",
            db_alias=db_alias,
            level=ServerEvent.Level.ERROR,
            extra={
                "job_id": job_id,
                "queue": queue_name,
                "worker": worker_name,
            },
        )
    except Exception:
        logger.exception("_capture_oom_kill: failed to record OOM event")


def get_monitoring_worker_class():
    """
    Returns MonitoringWorker if django-rq is available, else None.

    MonitoringWorker extends the default Worker with OOM/SIGKILL capture.
    Use via DjangoRQConfig.worker_class or --worker-class CLI flag.
    """
    try:
        from rq import Worker

        class MonitoringWorker(Worker):
            """
            RQ Worker subclass that captures OOM/SIGKILL into ServerEvent.

            The work_horse_killed_handler fires on the *parent* worker process
            when the child work-horse dies unexpectedly (exit code != 0).
            """

            def work_horse_killed_handler(self, job, retpid, ret_val, rusage):
                try:
                    job_id = job.id if job else "unknown"
                    queue_name = self.queue_names()[0] if self.queue_names() else "unknown"
                    _capture_oom_kill(
                        job_id=job_id,
                        queue_name=queue_name,
                        worker_name=self.name,
                    )
                except Exception:
                    logger.exception("MonitoringWorker.work_horse_killed_handler: error")
                finally:
                    super().work_horse_killed_handler(job, retpid, ret_val, rusage)

        return MonitoringWorker

    except ImportError:
        return None
