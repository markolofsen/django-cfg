"""
Example: STOP Command Implementation

Demonstrates stopping a client with graceful shutdown and status updates.

Key patterns:
- Status transition (RUNNING → STOPPING → STOPPED)
- Optional reason tracking
- Error recovery

Usage:
    from your_app.grpc.commands.stop import stop_client

    success = await stop_client(client, model=instance, reason="Maintenance")
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def stop_client(
    client,  # ExampleCommandClient
    model,   # HasStatus protocol
    reason: Optional[str] = None,
    graceful: bool = True,
) -> bool:
    """
    Send STOP command to client.

    Args:
        client: Command client instance
        model: Django model with status field
        reason: Optional reason for stopping
        graceful: If True, allow client to finish current work

    Returns:
        True if command sent successfully, False otherwise

    Example:
        # Graceful stop
        success = await stop_client(client, model, reason="Scheduled maintenance", graceful=True)

        # Force stop
        success = await stop_client(client, model, reason="Emergency", graceful=False)
    """
    try:
        # Update model status
        current_status = model.status
        model.status = "STOPPING"
        await model.asave(update_fields=['status'])
        logger.info(f"Updated {client.client_id} status to STOPPING")

        # Create protobuf command
        # Example:
        # command = pb2.Command(
        #     stop=pb2.StopCommand(
        #         reason=reason or "Manual stop",
        #         graceful=graceful,
        #         timestamp=int(datetime.now().timestamp())
        #     )
        # )

        logger.warning(
            f"Example implementation: Create your STOP command protobuf message here."
        )

        # Send command
        # success = await client._send_command(command)

        # For this example:
        # if success:
        #     logger.info(f"✅ STOP command sent to {client.client_id}")
        #     model.status = "STOPPED"
        #     await model.asave(update_fields=['status'])
        # else:
        #     logger.warning(f"⚠️  Client {client.client_id} not connected")
        #     # Revert to previous status
        #     model.status = current_status
        #     await model.asave(update_fields=['status'])

        # return success

        return False  # Placeholder

    except Exception as e:
        logger.error(
            f"❌ Error sending STOP command to {client.client_id}: {e}",
            exc_info=True
        )
        # Handle error
        try:
            model.status = "ERROR"
            await model.asave(update_fields=['status'])
        except Exception:
            pass
        return False


__all__ = ['stop_client']
