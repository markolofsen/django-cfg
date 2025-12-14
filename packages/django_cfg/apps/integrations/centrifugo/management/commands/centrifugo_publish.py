"""Django management command to publish messages to Centrifugo channels.

Usage:
    # Publish simple message
    python manage.py centrifugo_publish --channel "ai_chat:workspace:UUID" --message "Hello!"

    # Publish JSON data
    python manage.py centrifugo_publish -c "notifications" -d '{"type": "alert", "text": "Test"}'

    # Publish to AI chat with proper format
    python manage.py centrifugo_publish -c "ai_chat:workspace:UUID" -m "Test message"

    # Publish custom JSON
    python manage.py centrifugo_publish -c "my:channel" -d '{"foo": "bar"}'
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from django.core.management.base import CommandError
from django.utils.termcolors import colorize

from django_cfg.management.utils import AdminCommand
from django_cfg.apps.integrations.centrifugo.services.publisher import CentrifugoPublisher
from django_cfg.apps.integrations.centrifugo.services.client import get_direct_centrifugo_client

logger = logging.getLogger(__name__)


class Command(AdminCommand):
    """Publish messages to Centrifugo channels."""

    command_name = 'centrifugo_publish'
    help = "Publish messages to Centrifugo channels for testing and debugging"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Channel specification (required)
        parser.add_argument(
            "--channel",
            "-c",
            type=str,
            required=True,
            help="Centrifugo channel name (e.g., 'ai_chat:workspace:UUID')",
        )

        # Message content (choose one: --message or --data)
        parser.add_argument(
            "--message",
            "-m",
            type=str,
            help="Simple text message to publish",
        )

        parser.add_argument(
            "--data",
            "-d",
            type=str,
            help="JSON data to publish (e.g., '{\"type\": \"test\", \"text\": \"Hello\"}')",
        )

        # Options
        parser.add_argument(
            "--direct",
            action="store_true",
            default=True,
            help="Use direct Centrifugo client (bypass wrapper, default: True)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Run async publish
            result = asyncio.run(self._publish(options))

            if result:
                # Handle different response types
                if hasattr(result, 'offset'):
                    # CentrifugoClient response
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Message published successfully!\n"
                        f"   Offset: {result.offset}\n"
                        f"   Epoch: {result.epoch}"
                    ))
                else:
                    # DirectCentrifugoClient response
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Message published successfully!\n"
                        f"   Message ID: {result.message_id}\n"
                        f"   Published: {result.published}"
                    ))
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to publish message"))

        except Exception as e:
            raise CommandError(f"Error publishing message: {e}")

    async def _publish(self, options: Dict[str, Any]):
        """Publish message asynchronously."""
        # Initialize publisher
        publisher = CentrifugoPublisher(use_direct=options['direct'])

        # Get channel
        channel = options['channel']

        self.stdout.write(f"📡 Publishing to channel: {colorize(channel, fg='cyan')}")

        # Determine data to publish
        data = self._get_data(options)

        self.stdout.write(f"📦 Data: {colorize(json.dumps(data, indent=2, ensure_ascii=False), fg='yellow')}")

        # Publish
        result = await publisher.client.publish(
            channel=channel,
            data=data,
        )

        return result

    def _get_data(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Construct data payload from options."""
        # If explicit JSON data provided
        if options.get('data'):
            try:
                return json.loads(options['data'])
            except json.JSONDecodeError as e:
                raise CommandError(f"Invalid JSON in --data: {e}")

        # If simple message provided
        if options.get('message'):
            return {
                "type": "message",
                "text": options['message'],
                "timestamp": self._get_timestamp(),
            }

        # Default: require either --message or --data
        raise CommandError("Either --message or --data is required")

    @staticmethod
    def _get_timestamp() -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
