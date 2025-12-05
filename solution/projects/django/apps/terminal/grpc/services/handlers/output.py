"""
Handle terminal output from Electron.
"""

import logging
from django.db.models import F

from apps.terminal.models import TerminalSession
from apps.terminal.consumers import get_terminal_publisher

logger = logging.getLogger(__name__)


async def handle_terminal_output(
    session_id: str,
    output,  # pb2.TerminalOutput
    centrifugo_publisher=None,  # Optional, uses singleton if not provided
) -> None:
    """
    Handle terminal output from Electron.

    Forward to browser via Centrifugo pub/sub.

    Args:
        session_id: UUID of the terminal session
        output: TerminalOutput protobuf message (data, is_stderr, sequence)
        centrifugo_publisher: Optional publisher, uses singleton if not provided
    """
    try:
        data_len = len(output.data)
        is_stderr = output.is_stderr
        sequence = output.sequence

        logger.debug(
            f"Terminal output: session={session_id[:8]}... "
            f"bytes={data_len} stderr={is_stderr}"
        )

        # Forward to Centrifugo for browser clients
        publisher = centrifugo_publisher or get_terminal_publisher()
        await publisher.publish_output(
            session_id=session_id,
            data=output.data,
            is_stderr=is_stderr,
            sequence=sequence,
        )

        # Update session stats
        await TerminalSession.objects.filter(
            id=session_id
        ).aupdate(
            bytes_received=F('bytes_received') + data_len
        )

    except Exception as e:
        logger.error(f"Failed to handle terminal output: {e}", exc_info=True)
