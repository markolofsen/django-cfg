"""
Terminal Centrifugo integration.

Uses Centrifugo for pub/sub communication between browser and Django.
gRPC handlers forward terminal output to Centrifugo channels.
"""

import base64
import logging
import time
from typing import Optional

from django.utils import timezone

from django_cfg.apps.integrations.centrifugo.services.client import get_direct_centrifugo_client
from django_cfg.apps.integrations.centrifugo.services.client.exceptions import (
    CentrifugoConnectionError,
    CentrifugoTimeoutError,
)

logger = logging.getLogger(__name__)


class TerminalCentrifugoPublisher:
    """
    Publisher for terminal events via Centrifugo.

    Channel format: terminal#session#{session_id}
    """

    ERROR_LOG_INTERVAL = 30  # seconds between error logs

    def __init__(self):
        self._client = None
        self._last_error_log = 0
        self._error_count = 0

    def _get_client(self):
        """Get or create Centrifugo client."""
        if self._client is None:
            self._client = get_direct_centrifugo_client()
        return self._client

    def _log_error(self, msg: str, error: Exception) -> None:
        """Log error with throttling."""
        self._error_count += 1
        now = time.time()
        if now - self._last_error_log > self.ERROR_LOG_INTERVAL:
            self._last_error_log = now
            logger.warning(f"{msg} ({self._error_count} errors): {error}")

    def _get_channel(self, session_id: str) -> str:
        """Get Centrifugo channel name for session."""
        return f"terminal#session#{session_id}"

    async def publish_output(
        self,
        session_id: str,
        data: bytes,
        is_stderr: bool = False,
        sequence: int = 0,
    ) -> bool:
        """Publish terminal output to Centrifugo."""
        try:
            client = self._get_client()
            data_b64 = base64.b64encode(data).decode('ascii')

            await client.publish(
                channel=self._get_channel(session_id),
                data={
                    "type": "output",
                    "data": data_b64,
                    "is_stderr": is_stderr,
                    "sequence": sequence,
                    "timestamp": timezone.now().isoformat(),
                }
            )

            if self._error_count > 0:
                logger.info("Centrifugo connection restored")
                self._error_count = 0

            return True

        except (CentrifugoConnectionError, CentrifugoTimeoutError) as e:
            self._log_error("Centrifugo unavailable", e)
            return False

    async def publish_status(
        self,
        session_id: str,
        status: str,
        reason: str = "",
        working_directory: str = "",
    ) -> bool:
        """Publish status update to Centrifugo."""
        try:
            client = self._get_client()

            await client.publish(
                channel=self._get_channel(session_id),
                data={
                    "type": "status",
                    "status": status,
                    "reason": reason,
                    "working_directory": working_directory,
                    "timestamp": timezone.now().isoformat(),
                }
            )
            return True

        except (CentrifugoConnectionError, CentrifugoTimeoutError) as e:
            self._log_error("Centrifugo unavailable", e)
            return False

    async def publish_error(
        self,
        session_id: str,
        error_code: str,
        message: str,
        is_fatal: bool = False,
    ) -> bool:
        """Publish error to Centrifugo."""
        try:
            client = self._get_client()

            await client.publish(
                channel=self._get_channel(session_id),
                data={
                    "type": "error",
                    "error_code": error_code,
                    "message": message,
                    "is_fatal": is_fatal,
                    "timestamp": timezone.now().isoformat(),
                }
            )
            return True

        except (CentrifugoConnectionError, CentrifugoTimeoutError) as e:
            self._log_error("Centrifugo unavailable", e)
            return False

    async def publish_command_complete(
        self,
        session_id: str,
        command_id: str,
        exit_code: int,
        duration_ms: int,
    ) -> bool:
        """Publish command completion to Centrifugo."""
        try:
            client = self._get_client()

            await client.publish(
                channel=self._get_channel(session_id),
                data={
                    "type": "command_complete",
                    "command_id": command_id,
                    "exit_code": exit_code,
                    "duration_ms": duration_ms,
                    "timestamp": timezone.now().isoformat(),
                }
            )
            return True

        except (CentrifugoConnectionError, CentrifugoTimeoutError) as e:
            self._log_error("Centrifugo unavailable", e)
            return False


# Singleton
_terminal_publisher: Optional[TerminalCentrifugoPublisher] = None


def get_terminal_publisher() -> TerminalCentrifugoPublisher:
    """Get or create singleton terminal publisher."""
    global _terminal_publisher
    if _terminal_publisher is None:
        _terminal_publisher = TerminalCentrifugoPublisher()
    return _terminal_publisher
