"""
Example: START Command Implementation

This demonstrates the command decomposition pattern where each command
is implemented as a standalone async function.

Key patterns:
- Type-safe model operations using Protocol
- Django async ORM (asave with update_fields)
- Protobuf command creation
- Error handling and logging

Usage:
    from your_app.grpc.commands.start import start_client
    from your_app.grpc.commands.base_client import YourCommandClient

    # Create client
    client = YourCommandClient(client_id="123", model=instance)

    # Call command function
    success = await start_client(client, model=instance, reason="User request")
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def start_client(
    client,  # ExampleCommandClient
    model,   # HasStatus protocol
    reason: Optional[str] = None,
) -> bool:
    """
    Send START command to client.

    This is a standalone command function that can be:
    1. Called directly from management commands
    2. Wrapped in a method on the client class
    3. Used in REST API views
    4. Triggered by Django signals

    Args:
        client: Command client instance
        model: Django model with status field (HasStatus protocol)
        reason: Optional reason for starting

    Returns:
        True if command sent successfully, False otherwise

    Example:
        # From REST API
        from your_app.grpc.commands.start import start_client
        from your_app.grpc.commands.base_client import YourCommandClient

        async def start_view(request, pk):
            instance = await YourModel.objects.aget(pk=pk)
            client = YourCommandClient(client_id=str(pk), model=instance, grpc_port=50051)
            success = await start_client(client, model=instance, reason="API request")
            return JsonResponse({"success": success})

        # From management command (same-process)
        from your_app.grpc.services.registry import get_streaming_service

        service = get_streaming_service("your_service")
        client = YourCommandClient(client_id=str(pk), model=instance, streaming_service=service)
        success = await start_client(client, model=instance)
    """
    try:
        # Update model status to STARTING
        model.status = "STARTING"
        await model.asave(update_fields=['status'])
        logger.info(f"Updated {client.client_id} status to STARTING")

        # Create protobuf command
        # IMPORTANT: Replace with your actual protobuf types
        # Example:
        # command = pb2.Command(
        #     start=pb2.StartCommand(
        #         reason=reason or "Manual start",
        #         timestamp=int(datetime.now().timestamp())
        #     )
        # )

        # For this example, we'll just log a warning
        logger.warning(
            f"Example implementation: Create your START command protobuf message here. "
            f"See trading_bots/grpc/services/commands/start.py for reference."
        )

        # Send command via client (auto-detects same-process vs cross-process)
        # success = await client._send_command(command)

        # For this example, return placeholder
        # if success:
        #     logger.info(f"✅ START command sent to {client.client_id}")
        #     # Optionally update status to RUNNING
        #     model.status = "RUNNING"
        #     await model.asave(update_fields=['status'])
        # else:
        #     logger.warning(f"⚠️  Client {client.client_id} not connected")
        #     # Revert status
        #     model.status = "STOPPED"
        #     await model.asave(update_fields=['status'])

        # return success

        return False  # Placeholder

    except Exception as e:
        logger.error(
            f"❌ Error sending START command to {client.client_id}: {e}",
            exc_info=True
        )
        # Revert model status on error
        try:
            model.status = "ERROR"
            await model.asave(update_fields=['status'])
        except Exception:
            pass
        return False


__all__ = ['start_client']
