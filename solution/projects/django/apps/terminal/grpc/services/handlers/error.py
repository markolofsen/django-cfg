"""
Handle error reports from Electron.
"""

import uuid
import logging
from django.utils import timezone

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)


async def handle_error_report(
    session_id: str,
    error,  # pb2.ErrorReport
) -> None:
    """
    Handle error report from Electron.

    Args:
        session_id: UUID of the terminal session
        error: ErrorReport protobuf message (error_code, message, stack_trace, is_fatal)
    """
    try:
        logger.error(
            f"Terminal error: session={session_id[:8]}... "
            f"code={error.error_code} message={error.message} "
            f"fatal={error.is_fatal}"
        )

        if error.stack_trace:
            logger.error(f"Stack trace:\n{error.stack_trace}")

        # If fatal, mark session as error
        if error.is_fatal:
            await TerminalSession.objects.filter(
                id=uuid.UUID(session_id)
            ).aupdate(
                status=TerminalSession.Status.ERROR,
                disconnected_at=timezone.now(),
            )

    except Exception as e:
        logger.error(f"Failed to handle error report: {e}", exc_info=True)
