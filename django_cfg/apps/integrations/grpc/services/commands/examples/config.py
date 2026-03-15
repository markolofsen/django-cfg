"""
Example: CONFIG UPDATE Command Implementation

Demonstrates pushing configuration updates to connected clients.

Key patterns:
- JSONField updates (Django models)
- Partial vs full config updates
- Signal-triggered automatic config sync

Usage:
    from your_app.grpc.commands.config import update_config

    # Full config update
    success = await update_config(client, model=instance)

    # Partial update
    success = await update_config(client, model=instance, fields=['timeout', 'max_retries'])
"""

import logging
from typing import Any, Optional, List

logger = logging.getLogger(__name__)


async def update_config(
    client,  # ExampleCommandClient
    model,   # HasConfig protocol
    fields: Optional[List[str]] = None,
) -> bool:
    """
    Send CONFIG_UPDATE command to client.

    Pushes configuration from Django model to connected client.
    Useful for:
    - User updates config in admin/API
    - Django signal automatically pushes to client
    - Batch config updates across multiple clients

    Args:
        client: Command client instance
        model: Django model with config JSONField
        fields: If specified, only send these config fields (partial update)

    Returns:
        True if command sent successfully, False otherwise

    Example:
        # Auto-push on model save (using Django signals)
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from asgiref.sync import async_to_sync

        @receiver(post_save, sender=YourModel)
        def on_config_changed(sender, instance, **kwargs):
            from your_app.grpc.commands.config import update_config
            from your_app.grpc.commands.base_client import YourCommandClient

            client = YourCommandClient(
                client_id=str(instance.id),
                model=instance,
                grpc_port=50051
            )
            async_to_sync(update_config)(client, model=instance)

        # Manual update from API
        async def update_config_view(request, pk):
            instance = await YourModel.objects.aget(pk=pk)
            # ... update instance.config ...
            await instance.asave(update_fields=['config'])

            client = YourCommandClient(client_id=str(pk), model=instance, grpc_port=50051)
            success = await update_config(client, model=instance)
            return JsonResponse({"success": success})
    """
    try:
        # Get config from model
        config = model.config

        # If fields specified, create partial config
        if fields:
            config = {k: v for k, v in config.items() if k in fields}
            logger.debug(f"Sending partial config update to {client.client_id}: {list(config.keys())}")
        else:
            logger.debug(f"Sending full config update to {client.client_id}")

        # Create protobuf command
        # Example:
        # command = pb2.Command(
        #     config_update=pb2.ConfigUpdateCommand(
        #         config=json.dumps(config),
        #         partial=fields is not None,
        #         fields=fields or [],
        #         timestamp=int(datetime.now().timestamp())
        #     )
        # )

        logger.warning(
            f"Example implementation: Create your CONFIG_UPDATE command protobuf message here."
        )

        # Send command
        # success = await client._send_command(command)

        # For this example:
        # if success:
        #     logger.info(f"✅ CONFIG_UPDATE sent to {client.client_id}")
        # else:
        #     logger.warning(f"⚠️  Client {client.client_id} not connected, config will sync on reconnect")

        # return success

        return False  # Placeholder

    except Exception as e:
        logger.error(
            f"❌ Error sending CONFIG_UPDATE to {client.client_id}: {e}",
            exc_info=True
        )
        return False


async def batch_update_config(
    clients: List[Any],  # List[ExampleCommandClient]
    model: Any,  # HasConfig
    fields: Optional[List[str]] = None,
) -> dict:
    """
    Send config update to multiple clients.

    Useful for:
    - Updating config across all connected clients of same type
    - Rolling out global config changes

    Args:
        clients: List of command client instances
        model: Django model with config
        fields: Optional list of fields for partial update

    Returns:
        Dict with 'success': count, 'failed': count

    Example:
        from your_app.grpc.services.commands.registry import get_streaming_service

        # Get all connected clients
        service = get_streaming_service("your_service")
        client_ids = list(service.get_active_connections().keys())

        # Create clients
        clients = [
            YourCommandClient(client_id=cid, streaming_service=service)
            for cid in client_ids
        ]

        # Batch update
        results = await batch_update_config(clients, global_config_model, fields=['timeout'])
        print(f"Updated {results['success']} clients, {results['failed']} failed")
    """
    results = {'success': 0, 'failed': 0}

    for client in clients:
        success = await update_config(client, model, fields)
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1

    logger.info(
        f"Batch config update complete: {results['success']} succeeded, {results['failed']} failed"
    )

    return results


__all__ = ['update_config', 'batch_update_config']
