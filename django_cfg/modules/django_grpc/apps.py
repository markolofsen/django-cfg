"""
django_grpc — Django AppConfig.

Starts the async D1 log worker when Django is launched under ASGI (grpc.aio context).
Dependency check is lazy — skipped for migrate, shell, test, etc.
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("django_cfg.django_grpc")


class DjangoGrpcConfig(AppConfig):
    name = "django_cfg.modules.django_grpc"
    label = "django_grpc"
    verbose_name = "gRPC (D1)"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        self._check_deps_if_needed()
        self._start_log_worker()

    # ------------------------------------------------------------------

    def _check_deps_if_needed(self) -> None:
        import sys

        if len(sys.argv) < 2:
            return

        skip = {
            "makemigrations", "migrate", "shell", "shell_plus",
            "check", "help", "test", "collectstatic",
            "createsuperuser", "showmigrations", "sqlmigrate",
        }

        command = sys.argv[1]
        if command in skip:
            return
        if "pytest" in sys.argv[0]:
            return

        if command == "rungrpc":
            try:
                from ._deps import DependencyChecker
                DependencyChecker.check_all(raise_on_missing=True)
            except SystemExit:
                raise
            except Exception as exc:
                import sys as _sys
                print(str(exc))
                _sys.exit(1)

    def _start_log_worker(self) -> None:
        """Start D1 log worker when running under ASGI (event loop present).

        J-5 fix: replaced asyncio.get_event_loop() (DeprecationWarning in Python 3.10+
        outside async context) with asyncio.get_running_loop() which raises RuntimeError
        when no loop is running — cleaner, no deprecation noise.
        """
        try:
            import asyncio
            asyncio.get_running_loop()  # raises RuntimeError if no loop is running
            from .events.log_worker import start_log_worker
            start_log_worker()
        except RuntimeError:
            pass  # not in async context (manage.py migrate, shell, etc.) — skip
        except Exception:
            pass  # any other error — skip silently
