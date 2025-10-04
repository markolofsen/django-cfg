"""
Management command to show orchestrator status.
"""

import asyncio
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from django_cfg.modules.django_orchestrator.integration.registry import get_registry
from django_cfg.modules.django_orchestrator.models.execution import AgentExecution, WorkflowExecution
from django_cfg.modules.django_orchestrator.models.registry import AgentDefinition


class Command(BaseCommand):
    """Show Django Orchestrator status and statistics."""
    
    help = 'Display Django Orchestrator status and statistics'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics'
        )
        parser.add_argument(
            '--agents',
            action='store_true',
            help='Show agent-specific statistics'
        )
        parser.add_argument(
            '--recent',
            type=int,
            default=24,
            help='Show statistics for recent hours (default: 24)'
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        self.stdout.write(
            self.style.SUCCESS('🤖 Django Orchestrator Status')
        )
        self.stdout.write('=' * 50)
        
        # Run async operations
        asyncio.run(self._show_status(options))
    
    async def _show_status(self, options):
        """Show orchestrator status."""
        # Registry status
        await self._show_registry_status()
        
        # Database statistics
        await self._show_database_stats(options['recent'])
        
        if options['detailed']:
            await self._show_detailed_stats(options['recent'])
        
        if options['agents']:
            await self._show_agent_stats(options['recent'])
    
    async def _show_registry_status(self):
        """Show registry status."""
        self.stdout.write('\n📋 Registry Status:')
        
        registry = get_registry()
        metrics = registry.get_agent_metrics()
        
        self.stdout.write(f"  Runtime Agents: {metrics['runtime_agents_count']}")
        self.stdout.write(f"  Available Patterns: {len(metrics['orchestrator_metrics']['available_patterns'])}")
        
        if metrics['agent_names']:
            self.stdout.write(f"  Loaded Agents: {', '.join(metrics['agent_names'])}")
        else:
            self.stdout.write("  No agents currently loaded")
    
    async def _show_database_stats(self, recent_hours):
        """Show database statistics."""
        self.stdout.write('\n📊 Database Statistics:')
        
        # Total counts
        total_definitions = await AgentDefinition.objects.acount()
        active_definitions = await AgentDefinition.objects.filter(is_active=True).acount()
        
        self.stdout.write(f"  Agent Definitions: {total_definitions} ({active_definitions} active)")
        
        # Recent activity
        since = timezone.now() - timedelta(hours=recent_hours)
        
        recent_executions = await AgentExecution.objects.filter(created_at__gte=since).acount()
        recent_workflows = await WorkflowExecution.objects.filter(created_at__gte=since).acount()
        
        self.stdout.write(f"  Recent Executions ({recent_hours}h): {recent_executions} agents, {recent_workflows} workflows")
        
        # Success rates
        total_executions = await AgentExecution.objects.acount()
        successful_executions = await AgentExecution.objects.filter(status='completed').acount()
        
        if total_executions > 0:
            success_rate = (successful_executions / total_executions) * 100
            self.stdout.write(f"  Overall Success Rate: {success_rate:.1f}%")
    
    async def _show_detailed_stats(self, recent_hours):
        """Show detailed statistics."""
        self.stdout.write('\n📈 Detailed Statistics:')
        
        since = timezone.now() - timedelta(hours=recent_hours)
        
        # Execution status breakdown
        statuses = {}
        async for execution in AgentExecution.objects.filter(created_at__gte=since):
            statuses[execution.status] = statuses.get(execution.status, 0) + 1
        
        if statuses:
            self.stdout.write(f"  Execution Status (last {recent_hours}h):")
            for status, count in statuses.items():
                self.stdout.write(f"    {status.title()}: {count}")
        
        # Average execution time
        from django.db.models import Avg
        avg_time = await AgentExecution.objects.filter(
            created_at__gte=since,
            execution_time__isnull=False
        ).aaggregate(avg_time=Avg('execution_time'))
        
        if avg_time['avg_time']:
            self.stdout.write(f"  Average Execution Time: {avg_time['avg_time']:.2f}s")
        
        # Token usage
        from django.db.models import Sum
        token_stats = await AgentExecution.objects.filter(
            created_at__gte=since
        ).aaggregate(
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        )
        
        if token_stats['total_tokens']:
            self.stdout.write(f"  Total Tokens Used: {token_stats['total_tokens']:,}")
        
        if token_stats['total_cost']:
            self.stdout.write(f"  Total Cost: ${token_stats['total_cost']:.4f}")
    
    async def _show_agent_stats(self, recent_hours):
        """Show agent-specific statistics."""
        self.stdout.write('\n🤖 Agent Statistics:')
        
        since = timezone.now() - timedelta(hours=recent_hours)
        
        # Most used agents
        from django.db.models import Count
        agent_usage = []
        
        async for item in AgentExecution.objects.filter(
            created_at__gte=since
        ).values('agent_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]:
            agent_usage.append((item['agent_name'], item['count']))
        
        if agent_usage:
            self.stdout.write(f"  Most Used Agents (last {recent_hours}h):")
            for agent_name, count in agent_usage:
                self.stdout.write(f"    {agent_name}: {count} executions")
        
        # Agent definitions by category
        categories = {}
        async for agent_def in AgentDefinition.objects.filter(is_active=True):
            category = agent_def.category or 'uncategorized'
            categories[category] = categories.get(category, 0) + 1
        
        if categories:
            self.stdout.write("  Agents by Category:")
            for category, count in sorted(categories.items()):
                self.stdout.write(f"    {category.title()}: {count}")
        
        # Registry runtime status
        registry = get_registry()
        runtime_agents = registry.get_runtime_agents()
        
        if runtime_agents:
            self.stdout.write("  Runtime Agent Metrics:")
            for agent_name, agent in runtime_agents.items():
                metrics = agent.get_metrics()
                self.stdout.write(
                    f"    {agent_name}: "
                    f"{metrics['execution_count']} runs, "
                    f"{metrics['success_rate']:.1%} success, "
                    f"{metrics['cache_hit_rate']:.1%} cache hit"
                )
