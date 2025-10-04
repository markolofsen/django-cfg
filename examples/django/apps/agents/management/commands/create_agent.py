"""
Management command to create agent definitions.
"""

import asyncio
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django_cfg.modules.django_orchestrator.models.registry import AgentDefinition


class Command(BaseCommand):
    """Create agent definition from command line."""
    
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


class Command(BaseCommand):
    """Load agent definitions from templates."""
    
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
