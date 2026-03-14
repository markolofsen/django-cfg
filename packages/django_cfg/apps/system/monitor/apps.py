"""
Frontend Monitor Application Configuration.
"""

import logging

from django.apps import AppConfig

_logger = logging.getLogger(__name__)


class FrontendMonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.apps.system.monitor"
    label = "django_cfg_monitor"
    verbose_name = "Frontend Monitor"

    def ready(self) -> None:
        # 1. Existing: match AnonymousSession to user on login
        import django_cfg.apps.system.monitor.signals  # noqa: F401

        # 2. Server-side capture (conditional on config)
        try:
            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            cfg = get_settings()
            enabled = cfg.server_capture_enabled
        except Exception:
            enabled = True  # default to enabled if config unavailable

        if not enabled:
            return

        self._connect_request_exception_signal()
        self._install_logging_handler()
        self._install_slow_query_detection()
        self._register_rq_handler()

    def _connect_request_exception_signal(self) -> None:
        """
        Connect capture_request_exception to got_request_exception.

        Uses dispatch_uid to guarantee idempotency — safe if ready() is called
        more than once (e.g. in test suites that reset the app registry).
        """
        try:
            from django.core.signals import got_request_exception
            from django_cfg.apps.system.monitor.signals import capture_request_exception

            got_request_exception.connect(
                capture_request_exception,
                dispatch_uid="django_cfg_monitor.capture_request_exception",
            )
        except Exception:
            _logger.exception("ServerMonitor: failed to connect got_request_exception signal")

    def _install_logging_handler(self) -> None:
        """
        Add MonitorHandler to the root logger at ERROR level.

        Idempotent: checks for an existing MonitorHandler before adding one.
        """
        try:
            from django_cfg.apps.system.monitor.capture.handlers import MonitorHandler

            root_logger = logging.getLogger()
            already_installed = any(
                isinstance(h, MonitorHandler) for h in root_logger.handlers
            )
            if not already_installed:
                handler = MonitorHandler(level=logging.ERROR)
                root_logger.addHandler(handler)
        except Exception:
            _logger.exception("ServerMonitor: failed to install logging handler")

    def _install_slow_query_detection(self) -> None:
        """
        Install slow query wrapper on every new DB connection via connection_created signal.
        Threshold of 0 disables detection entirely.
        """
        try:
            from django_cfg.apps.system.monitor.__cfg__ import get_settings
            cfg = get_settings()
            threshold = cfg.slow_query_threshold_ms
            if threshold <= 0:
                return
            db_alias = cfg.monitor_db_alias or "monitor"

            from django.db.backends.signals import connection_created
            from django_cfg.apps.system.monitor.capture.slow_query import make_slow_query_wrapper

            wrapper = make_slow_query_wrapper(threshold_ms=threshold, db_alias=db_alias)
            _WRAPPER_ATTR = "_django_cfg_monitor_slow_query"

            def on_connection_created(sender, connection, **kwargs):
                # Idempotent: mark the connection so we never add the wrapper twice
                # (ready() may be called more than once in test suites)
                if getattr(connection, _WRAPPER_ATTR, False):
                    return
                setattr(connection, _WRAPPER_ATTR, True)
                connection.execute_wrappers.append(wrapper)

            connection_created.connect(
                on_connection_created,
                dispatch_uid="django_cfg_monitor.slow_query_wrapper",
            )
        except Exception:
            _logger.exception("ServerMonitor: failed to install slow query detection")

    def _register_rq_handler(self) -> None:
        """
        Register monitor_rq_exception_handler in RQ_EXCEPTION_HANDLERS Django setting.

        Only runs if django-rq is available. Uses safe mutation of the setting
        (list append) to coexist with user-defined handlers.
        """
        try:
            import django_rq  # noqa: F401 — check availability
        except ImportError:
            return

        try:
            from django.conf import settings as django_settings
            from django_cfg.apps.system.monitor.capture.rq import monitor_rq_exception_handler

            handler_path = "django_cfg.apps.system.monitor.capture.rq.monitor_rq_exception_handler"
            existing = getattr(django_settings, "RQ_EXCEPTION_HANDLERS", [])

            if handler_path not in existing:
                # Settings may be a frozen tuple in some configurations — convert to list
                if not isinstance(existing, list):
                    existing = list(existing)
                existing.append(handler_path)
                django_settings.RQ_EXCEPTION_HANDLERS = existing
        except Exception:
            _logger.exception("ServerMonitor: failed to register RQ exception handler")
