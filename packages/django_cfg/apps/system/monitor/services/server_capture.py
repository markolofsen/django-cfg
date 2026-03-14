"""
Server-side exception capture service.

Responsible for:
- Extracting the innermost frame from a traceback
- Computing fingerprints
- Calling ServerEvent.record() with the correct db_alias
"""

import hashlib
import logging
import traceback as tb_module
from types import TracebackType
from typing import Any, Optional

logger = logging.getLogger(__name__)


def extract_innermost_frame(tb: Optional[TracebackType]) -> tuple[str, str, int]:
    """
    Walk the traceback to its innermost frame.
    Returns (module_name, func_name, lineno).

    The innermost frame is where the exception actually occurred —
    the most relevant frame for grouping.
    """
    if tb is None:
        return "", "", 0
    frame = None
    lineno = 0
    while tb is not None:
        frame = tb.tb_frame
        lineno = tb.tb_lineno
        tb = tb.tb_next
    if frame is None:
        return "", "", 0
    module = frame.f_globals.get("__name__", "")
    func_name = frame.f_code.co_name
    return module, func_name, lineno


def build_fingerprint(
    exception_type: str,
    module: str,
    func_name: str,
) -> str:
    """
    Build a stable 16-character fingerprint.

    sha256("{exception_type}::{module}::{func_name}")[:16]

    Line numbers are intentionally excluded: they change with every refactor
    and would generate spurious new fingerprints for unchanged bugs.
    """
    raw = f"{exception_type}::{module}::{func_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class ServerCaptureService:
    """
    Converts raw exception data into a ServerEvent upsert.
    All methods fail silently — must never break calling code.
    """

    def capture_exception(
        self,
        exc_type: type,
        exc_value: BaseException,
        tb: Optional[TracebackType],
        *,
        event_type: str,
        db_alias: str = "monitor",
        url: str = "",
        http_method: str = "",
        http_status: Optional[int] = None,
        logger_name: str = "",
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        try:
            from django_cfg.apps.system.monitor.models.server_event import ServerEvent

            exception_type_str = f"{exc_type.__module__}.{exc_type.__qualname__}"
            module, func_name, lineno = extract_innermost_frame(tb)
            stack_trace = "".join(
                tb_module.format_exception(exc_type, exc_value, tb)
            ) if tb else ""

            ServerEvent.record(
                exception_type=exception_type_str,
                module=module,
                func_name=func_name,
                event_type=event_type,
                message=str(exc_value)[:2000],
                db_alias=db_alias,
                stack_trace=stack_trace[:10000] if stack_trace else None,
                logger_name=logger_name,
                url=url,
                http_method=http_method,
                http_status=http_status,
                lineno=lineno or None,
                extra=extra or {},
            )
        except Exception:
            logger.exception("ServerCaptureService: failed to capture exception")

    def capture_log_record(
        self,
        record: logging.LogRecord,
        db_alias: str = "monitor",
    ) -> None:
        try:
            from django_cfg.apps.system.monitor.models.server_event import ServerEvent

            exc_type, exc_value, tb = record.exc_info if record.exc_info else (None, None, None)

            if exc_type is not None:
                self.capture_exception(
                    exc_type=exc_type,
                    exc_value=exc_value,
                    tb=tb,
                    event_type=ServerEvent.EventType.UNHANDLED_EXCEPTION,
                    db_alias=db_alias,
                    logger_name=record.name,
                )
            else:
                # Plain ERROR log without exception — fingerprint on logger + message prefix
                # to differentiate distinct errors at the same location
                exception_type_str = f"LOG::{record.levelname}"
                module = record.module or ""
                func_name = record.funcName or ""
                raw = f"{exception_type_str}::{module}::{func_name}::{record.getMessage()[:80]}"
                _ = hashlib.sha256(raw.encode()).hexdigest()[:16]  # computed in record()

                ServerEvent.record(
                    exception_type=exception_type_str,
                    module=module,
                    func_name=func_name,
                    event_type=ServerEvent.EventType.LOG_ERROR,
                    message=record.getMessage()[:2000],
                    db_alias=db_alias,
                    logger_name=record.name,
                    lineno=record.lineno or None,
                )
        except Exception:
            logger.exception("ServerCaptureService: failed to capture log record")
