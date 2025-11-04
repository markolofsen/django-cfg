"""
Management command to create agent definitions.
"""

import asyncio

from django.contrib.auth.models import User
from django.core.management.base import CommandError

from django_cfg.management.utils import AdminCommand

from django_cfg.apps.business.agents.models.registry import AgentDefinition


class Command(AdminCommand):
    """Create agent definition from command line."""

    command_name = 'create_agent'
    help = 'Create a new agent definition'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument('name', type=str, help='Agent name (unique identifier)')
        parser.add_argument('instructions', type=str, help='Agent instructions/system prompt')

        parser.add_argument(
            '--deps-type',
            type=str,
            default='DjangoDeps',
            help='Dependencies type (default: DjangoDeps)'
        )
        parser.add_argument(
            '--output-type',
            type=str,
            default='ProcessResult',
            help='Output type (default: ProcessResult)'
        )
        parser.add_argument(
            '--model',
            type=str,
            default='openai:gpt-4o-mini',
            help='LLM model to use (default: openai:gpt-4o-mini)'
        )
        parser.add_argument(
            '--category',
            type=str,
            default='',
            help='Agent category'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Execution timeout in seconds (default: 300)'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum retry attempts (default: 3)'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='Make agent public (accessible to all users)'
        )
        parser.add_argument(
            '--no-cache',
            action='store_true',
            help='Disable caching for this agent'
        )
        parser.add_argument(
            '--creator',
            type=str,
            help='Username of agent creator (defaults to first superuser)'
        )
        parser.add_argument(
            '--description',
            type=str,
            default='',
            help='Agent description'
        )
        parser.add_argument(
            '--tags',
            type=str,
            nargs='*',
            help='Agent tags (space-separated)'
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        # Run async operations
        asyncio.run(self._create_agent(options))

    async def _create_agent(self, options):
        """Create agent definition."""
        name = options['name']
        instructions = options['instructions']

        # Validate name
        if await AgentDefinition.objects.filter(name=name).aexists():
            raise CommandError(f"Agent '{name}' already exists")

        # Get creator user
        creator = await self._get_creator_user(options.get('creator'))

        # Prepare agent data
        agent_data = {
            'name': name,
            'instructions': instructions,
            'deps_type': options['deps_type'],
            'output_type': options['output_type'],
            'model': options['model'],
            'category': options['category'],
            'timeout': options['timeout'],
            'max_retries': options['max_retries'],
            'is_public': options['public'],
            'enable_caching': not options['no_cache'],
            'created_by': creator,
            'description': options['description'],
        }

        # Add tags if provided
        if options['tags']:
            agent_data['tags'] = options['tags']

        # Create agent definition
        try:
            agent_def = await AgentDefinition.objects.acreate(**agent_data)

            self.stdout.write(
                self.style.SUCCESS(f"✅ Created agent definition: {agent_def.name}")
            )

            # Show agent details
            self.stdout.write("\nAgent Details:")
            self.stdout.write(f"  Name: {agent_def.name}")
            self.stdout.write(f"  Display Name: {agent_def.display_name}")
            self.stdout.write(f"  Category: {agent_def.category or 'None'}")
            self.stdout.write(f"  Model: {agent_def.model}")
            self.stdout.write(f"  Dependencies: {agent_def.deps_type}")
            self.stdout.write(f"  Output Type: {agent_def.output_type}")
            self.stdout.write(f"  Timeout: {agent_def.timeout}s")
            self.stdout.write(f"  Max Retries: {agent_def.max_retries}")
            self.stdout.write(f"  Public: {agent_def.is_public}")
            self.stdout.write(f"  Caching: {agent_def.enable_caching}")
            self.stdout.write(f"  Created by: {agent_def.created_by.username}")

            if agent_def.tags:
                self.stdout.write(f"  Tags: {', '.join(agent_def.tags)}")

            if agent_def.description:
                self.stdout.write(f"  Description: {agent_def.description}")

            # Instructions preview
            instructions_preview = agent_def.instructions[:200]
            if len(agent_def.instructions) > 200:
                instructions_preview += "..."

            self.stdout.write(f"  Instructions: {instructions_preview}")

        except Exception as e:
            raise CommandError(f"Failed to create agent: {e}")

    async def _get_creator_user(self, username):
        """Get creator user."""
        if username:
            try:
                return await User.objects.aget(username=username)
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found")
        else:
            # Use first superuser
            try:
                return await User.objects.filter(is_superuser=True).afirst()
            except User.DoesNotExist:
                raise CommandError("No superuser found. Please create a superuser first or specify --creator")
