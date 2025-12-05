"""
Handle status updates from Electron.
"""

import uuid
import logging
from django.utils import timezone

from apps.terminal.models import TerminalSession

logger = logging.getLogger(__name__)

# Map protobuf status to Django model status
STATUS_MAP = {
    0: TerminalSession.Status.PENDING,      # UNSPECIFIED
    1: TerminalSession.Status.PENDING,      # PENDING
    2: TerminalSession.Status.CONNECTED,    # CONNECTED
    3: TerminalSession.Status.DISCONNECTED, # DISCONNECTED
    4: TerminalSession.Status.ERROR,        # ERROR
}


async def handle_status_update(
    session_id: str,
    status_update,  # pb2.StatusUpdate
) -> None:
    """
    Handle status update from Electron.

    Args:
        session_id: UUID of the terminal session
        status_update: StatusUpdate protobuf message
    """
    try:
        new_status = STATUS_MAP.get(
            status_update.new_status,
            TerminalSession.Status.PENDING
        )

        logger.info(
            f"Status update: session={session_id[:8]}... "
            f"old={status_update.old_status} new={status_update.new_status} "
            f"reason={status_update.reason}"
        )

        update_fields = ['status', 'updated_at']
        update_data = {'status': new_status}

        # Update working directory if provided
        if status_update.working_directory:
            update_data['working_directory'] = status_update.working_directory
            update_fields.append('working_directory')

        # Set disconnected_at if disconnected
        if new_status == TerminalSession.Status.DISCONNECTED:
            update_data['disconnected_at'] = timezone.now()
            update_fields.append('disconnected_at')

        await TerminalSession.objects.filter(
            id=uuid.UUID(session_id)
        ).aupdate(**update_data)

    except Exception as e:
        logger.error(f"Failed to handle status update: {e}", exc_info=True)
