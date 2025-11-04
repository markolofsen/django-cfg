"""
Management command to load pre-built agent templates.
"""

import asyncio

from django.contrib.auth.models import User
from django.core.management.base import CommandError

from django_cfg.management.utils import AdminCommand

from django_cfg.apps.business.agents.models.registry import AgentDefinition


class Command(AdminCommand):
    """Load agent definitions from templates."""

    command_name = 'load_agent_templates'
    help = 'Load pre-built agent templates'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available templates'
        )
        parser.add_argument(
            '--load',
            type=str,
            nargs='*',
            help='Load specific templates (space-separated names)'
        )
        parser.add_argument(
            '--load-all',
            action='store_true',
            help='Load all available templates'
        )
        parser.add_argument(
            '--creator',
            type=str,
            help='Username of agent creator (defaults to first superuser)'
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        if options['list']:
            self._list_templates()
        elif options['load'] or options['load_all']:
            asyncio.run(self._load_templates(options))
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --list, --load, or --load-all')
            )

    def _list_templates(self):
        """List available templates."""
        templates = self._get_available_templates()

        self.stdout.write(self.style.SUCCESS('📋 Available Agent Templates:'))
        self.stdout.write('=' * 40)

        for category, agents in templates.items():
            self.stdout.write(f"\n{category.upper()}:")
            for agent_name, agent_info in agents.items():
                self.stdout.write(f"  • {agent_name}: {agent_info['description']}")

    async def _load_templates(self, options):
        """Load templates."""
        creator = await self._get_creator_user(options.get('creator'))
        templates = self._get_available_templates()

        if options['load_all']:
            # Load all templates
            to_load = []
            for category_templates in templates.values():
                to_load.extend(category_templates.keys())
        else:
            to_load = options['load']

        loaded_count = 0

        for template_name in to_load:
            # Find template
            template_info = None
            for category_templates in templates.values():
                if template_name in category_templates:
                    template_info = category_templates[template_name]
                    break

            if not template_info:
                self.stdout.write(
                    self.style.WARNING(f"Template '{template_name}' not found")
                )
                continue

            # Check if agent already exists
            if await AgentDefinition.objects.filter(name=template_name).aexists():
                self.stdout.write(
                    self.style.WARNING(f"Agent '{template_name}' already exists, skipping")
                )
                continue

            # Create agent
            try:
                agent_data = template_info.copy()
                agent_data['name'] = template_name
                agent_data['created_by'] = creator

                await AgentDefinition.objects.acreate(**agent_data)

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Loaded template: {template_name}")
                )
                loaded_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to load template '{template_name}': {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Loaded {loaded_count} agent templates")
        )

    def _get_available_templates(self):
        """Get available agent templates."""
        return {
            'content': {
                'content_analyzer': {
                    'description': 'Analyze content sentiment, topics, and quality',
                    'instructions': 'Analyze content for sentiment, topics, keywords, and quality metrics.',
                    'deps_type': 'ContentDeps',
                    'output_type': 'AnalysisResult',
                    'category': 'content',
                    'model': 'openai:gpt-4o-mini',
                },
                'content_generator': {
                    'description': 'Generate high-quality content based on requirements',
                    'instructions': 'Generate engaging, well-structured content based on type, audience, and style requirements.',
                    'deps_type': 'ContentDeps',
                    'output_type': 'ProcessResult',
                    'category': 'content',
                    'model': 'openai:gpt-4o-mini',
                },
                'content_validator': {
                    'description': 'Validate content quality and compliance',
                    'instructions': 'Validate content for grammar, style, accuracy, and guideline compliance.',
                    'deps_type': 'ContentDeps',
                    'output_type': 'ValidationResult',
                    'category': 'content',
                    'model': 'openai:gpt-4o-mini',
                },
            },
            'data': {
                'data_processor': {
                    'description': 'Process and transform data',
                    'instructions': 'Process, clean, and transform data according to specifications.',
                    'deps_type': 'DataProcessingDeps',
                    'output_type': 'ProcessResult',
                    'category': 'data',
                    'model': 'openai:gpt-4o-mini',
                },
                'data_validator': {
                    'description': 'Validate data quality and integrity',
                    'instructions': 'Validate data quality, check for errors, and ensure integrity.',
                    'deps_type': 'DataProcessingDeps',
                    'output_type': 'ValidationResult',
                    'category': 'data',
                    'model': 'openai:gpt-4o-mini',
                },
            },
            'business': {
                'business_rules': {
                    'description': 'Apply business rules and logic',
                    'instructions': 'Apply business rules, validate decisions, and ensure compliance.',
                    'deps_type': 'BusinessLogicDeps',
                    'output_type': 'ProcessResult',
                    'category': 'business',
                    'model': 'openai:gpt-4o-mini',
                },
                'decision_maker': {
                    'description': 'Make decisions based on criteria',
                    'instructions': 'Analyze options and make informed decisions based on criteria and context.',
                    'deps_type': 'BusinessLogicDeps',
                    'output_type': 'ProcessResult',
                    'category': 'business',
                    'model': 'openai:gpt-4o-mini',
                },
            }
        }

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
