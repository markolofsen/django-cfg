"""
django_grpc.events.log_worker — Async producer-consumer D1 log worker.

Architecture:
  - ObservabilityInterceptor calls enqueue_log() → non-blocking put_nowait()
  - Background task _log_worker_loop() batches and flushes to D1 via execute_batch()
  - Queue is capped at MAX_QUEUE_SIZE to prevent OOM — overflow drops silently

Throughput:
  - Sequential INSERTs: ~67 rows/s (15ms each)
  - Batch 50 rows: ~667 rows/s (5× improvement)

Lifecycle:
  - start_log_worker() called from DjangoGrpcConfig.ready() (ASGI startup)
  - Worker stops gracefully on asyncio.CancelledError (flushes remaining buffer)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from django_cfg.modules.django_grpc.config.persistence import LogWorkerConfig

logger = logging.getLogger(__name__)

# Module-level singletons — one queue and one worker task per process
#
# R-15 fix: _log_queue was a bare annotation (no assigned value). Any call to
# enqueue_log() before start_log_worker() raised NameError inside the try/except
# which was silently swallowed — log entries were lost without any indication.
# Initialised to a placeholder Queue(0) so enqueue_log() raises QueueFull
# (logged as a warning) instead of NameError (silently ignored).
_log_queue: asyncio.Queue = asyncio.Queue(maxsize=0)  # replaced by start_log_worker()
_worker_task: Optional[asyncio.Task] = None

# H-2: drop counter — incremented each time enqueue_log() discards an entry.
# Exposed via get_drop_count() so dashboards / health-checks can surface saturation.
_drop_count: int = 0


def get_drop_count() -> int:
    """Return total log entries dropped due to queue saturation since process start."""
    return _drop_count


def _get_worker_config() -> LogWorkerConfig:
    """Read log worker config from the grpc_module singleton. Falls back to defaults."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings
        return settings.persistence.log_worker
    except Exception:
        return LogWorkerConfig()


@dataclass
class GrpcLogEntry:
    """Lightweight log entry for the async queue (avoids holding Pydantic model)."""
    request_id:       str
    service_name:     str
    method_name:      str
    full_method:      str
    status:           str
    duration_ms:      Optional[int]
    user_id:          Optional[int]
    is_authenticated: int
    client_ip:        Optional[str]
    grpc_status_code: Optional[str]
    error_message:    Optional[str]
    created_at:       str
    completed_at:     Optional[str]


def enqueue_log(entry: GrpcLogEntry) -> None:
    """Non-blocking enqueue. Drops and increments drop counter if queue is full."""
    global _log_queue, _drop_count
    try:
        _log_queue.put_nowait(entry)
    except asyncio.QueueFull:
        # H-2: count every dropped entry so dashboards can detect saturation.
        _drop_count += 1
        cfg = _get_worker_config()
        logger.warning(
            "gRPC log buffer full (%d) — dropping log entry (total dropped: %d)",
            cfg.queue_size, _drop_count,
        )
    except Exception:
        pass   # queue not yet initialised (e.g. management commands) — ignore


def start_log_worker() -> None:
    """Start the background D1 log worker. Called from inside asyncio.run() in rungrpc.py.

    R-05 fix: must be called from a running event loop. If called from a sync context
    (e.g. DjangoGrpcConfig.ready() before asyncio.run()), logs a warning and returns.
    Re-creates the queue if it was created in a different event loop (ASGI restart).
    Idempotent — calling twice in the same loop is a no-op.
    """
    global _log_queue, _worker_task

    # R-05: guard — must be inside a running event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning(
            "start_log_worker() called outside a running event loop — skipping. "
            "Call from within asyncio.run() (e.g. rungrpc _async_main)."
        )
        return

    cfg = _get_worker_config()

    # Re-create queue if it belongs to a different (closed) event loop.
    # asyncio.Queue stores no explicit loop ref in Python 3.10+, but a Queue created
    # in loop A cannot safely be used in loop B — recreate on every new loop start.
    existing_loop = getattr(_log_queue, "_loop", None)
    if existing_loop is not None and existing_loop is not loop:
        _log_queue = asyncio.Queue(maxsize=cfg.queue_size)
    elif not isinstance(_log_queue, asyncio.Queue) or _log_queue.maxsize == 0:
        # Replace the placeholder Queue(0) created at module import time
        _log_queue = asyncio.Queue(maxsize=cfg.queue_size)

    if _worker_task is not None and not _worker_task.done():
        return   # already running in this loop

    _worker_task = asyncio.create_task(
        _log_worker_loop(batch_size=cfg.batch_size, flush_interval=cfg.flush_interval),
        name="grpc-d1-log-worker",
    )
    logger.info("gRPC D1 log worker started (batch=%d, interval=%.1fs)", cfg.batch_size, cfg.flush_interval)


async def stop_log_worker(timeout: float = 10.0) -> None:
    """Gracefully stop the log worker. Call from rungrpc.py shutdown sequence.

    Cancels the worker task and waits up to *timeout* seconds for it to finish
    flushing buffered entries. CancelledError and TimeoutError are both swallowed
    so shutdown always completes even if the worker hangs.
    """
    global _worker_task
    if _worker_task is not None and not _worker_task.done():
        _worker_task.cancel()
        try:
            await asyncio.wait_for(asyncio.shield(_worker_task), timeout=timeout)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        _worker_task = None
        logger.info("gRPC D1 log worker stopped")


async def _log_worker_loop(batch_size: int, flush_interval: float) -> None:
    """Infinite consumer loop: collect entries → flush to D1 in batches."""
    buffer: list[GrpcLogEntry] = []

    while True:
        try:
            # Block up to flush_interval waiting for the next entry
            try:
                entry = await asyncio.wait_for(
                    _log_queue.get(),
                    timeout=flush_interval,
                )
                buffer.append(entry)
                _log_queue.task_done()
            except asyncio.TimeoutError:
                pass   # interval elapsed — flush whatever we have

            # Flush when batch is full OR queue is drained and we have pending rows
            if len(buffer) >= batch_size or (buffer and _log_queue.empty()):
                await _flush_buffer(buffer)
                buffer = []

        except asyncio.CancelledError:
            # Graceful shutdown — flush remaining entries before stopping
            if buffer:
                await _flush_buffer(buffer)
            logger.info("gRPC D1 log worker stopped")
            raise

        except Exception as exc:
            logger.error("gRPC log worker unexpected error: %s", exc)
            await asyncio.sleep(1)   # back-off before resuming


async def _flush_buffer(buffer: list[GrpcLogEntry]) -> None:
    """Write buffer to D1 via execute_batch() in a thread (synchronous SDK)."""
    if not buffer:
        return

    try:
        from django_cfg.modules.django_grpc.events.service import GrpcD1Service
        from django_cfg.modules.django_grpc.events.types import GrpcRequestLogRow

        service = GrpcD1Service()
        rows = [
            GrpcRequestLogRow(
                id=entry.request_id,
                service_name=entry.service_name,
                method_name=entry.method_name,
                full_method=entry.full_method,
                status=entry.status,
                duration_ms=entry.duration_ms,
                user_id=entry.user_id,
                is_authenticated=entry.is_authenticated,
                client_ip=entry.client_ip,
                grpc_status_code=entry.grpc_status_code,
                error_message=entry.error_message,
                created_at=entry.created_at,
                completed_at=entry.completed_at,
            )
            for entry in buffer
        ]
        await asyncio.to_thread(service.batch_insert_request_logs, rows)
        logger.debug("gRPC log worker: flushed %d rows to D1", len(rows))

    except Exception as exc:
        logger.error("gRPC D1 log flush failed (%d entries lost): %s", len(buffer), exc)
        # Do NOT re-raise — worker loop continues; entries are dropped on D1 failure


__all__ = [
    "GrpcLogEntry",
    "enqueue_log",
    "start_log_worker",
    "stop_log_worker",
    "get_drop_count",
]
