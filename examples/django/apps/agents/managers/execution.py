"""
Custom managers for agent execution models.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any


class AgentExecutionQuerySet(models.QuerySet):
    """Custom queryset for AgentExecution."""
    
    def for_user(self, user):
        """Filter executions for specific user."""
        return self.filter(user=user)
    
    def by_status(self, status: str):
        """Filter by execution status."""
        return self.filter(status=status)
    
    def successful(self):
        """Get successful executions."""
        return self.filter(status='completed')
    
    def failed(self):
        """Get failed executions."""
        return self.filter(status='failed')
    
    def recent(self, days: int = 7):
        """Get recent executions."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def by_agent(self, agent_name: str):
        """Filter by agent name."""
        return self.filter(agent_name=agent_name)
    
    def with_metrics(self):
        """Include execution metrics in query."""
        return self.select_related('user', 'workflow_execution', 'agent_definition')
    
    def expensive(self, min_cost: float = 0.01):
        """Get expensive executions."""
        return self.filter(cost__gte=min_cost)


class AgentExecutionManager(models.Manager):
    """Custom manager for AgentExecution."""
    
    def get_queryset(self):
        return AgentExecutionQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get executions for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get executions by status."""
        return self.get_queryset().by_status(status)
    
    def successful(self):
        """Get successful executions."""
        return self.get_queryset().successful()
    
    def failed(self):
        """Get failed executions."""
        return self.get_queryset().failed()
    
    def recent(self, days: int = 7):
        """Get recent executions."""
        return self.get_queryset().recent(days)
    
    def by_agent(self, agent_name: str):
        """Get executions by agent name."""
        return self.get_queryset().by_agent(agent_name)
    
    def with_metrics(self):
        """Get executions with metrics."""
        return self.get_queryset().with_metrics()
    
    def expensive(self, min_cost: float = 0.01):
        """Get expensive executions."""
        return self.get_queryset().expensive(min_cost)
    
    def create_execution(
        self,
        agent_name: str,
        user,
        input_prompt: str,
        agent_definition=None,
        workflow_execution=None,
        **kwargs
    ):
        """Create a new agent execution."""
        return self.create(
            agent_name=agent_name,
            user=user,
            input_prompt=input_prompt,
            agent_definition=agent_definition,
            workflow_execution=workflow_execution,
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get execution statistics for user."""
        executions = self.for_user(user)
        
        return {
            'total': executions.count(),
            'successful': executions.successful().count(),
            'failed': executions.failed().count(),
            'recent': executions.recent().count(),
            'total_cost': float(executions.aggregate(
                total=models.Sum('cost')
            )['total'] or 0),
            'avg_execution_time': executions.aggregate(
                avg=models.Avg('execution_time')
            )['avg'],
        }


class WorkflowExecutionQuerySet(models.QuerySet):
    """Custom queryset for WorkflowExecution."""
    
    def for_user(self, user):
        """Filter workflows for specific user."""
        return self.filter(user=user)
    
    def by_status(self, status: str):
        """Filter by workflow status."""
        return self.filter(status=status)
    
    def by_pattern(self, pattern: str):
        """Filter by workflow pattern."""
        return self.filter(pattern=pattern)
    
    def successful(self):
        """Get successful workflows."""
        return self.filter(status='completed')
    
    def failed(self):
        """Get failed workflows."""
        return self.filter(status='failed')
    
    def running(self):
        """Get currently running workflows."""
        return self.filter(status='running')
    
    def recent(self, days: int = 7):
        """Get recent workflows."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def with_executions(self):
        """Include related agent executions."""
        return self.prefetch_related('agent_executions')


class WorkflowExecutionManager(models.Manager):
    """Custom manager for WorkflowExecution."""
    
    def get_queryset(self):
        return WorkflowExecutionQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get workflows for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get workflows by status."""
        return self.get_queryset().by_status(status)
    
    def by_pattern(self, pattern: str):
        """Get workflows by pattern."""
        return self.get_queryset().by_pattern(pattern)
    
    def successful(self):
        """Get successful workflows."""
        return self.get_queryset().successful()
    
    def failed(self):
        """Get failed workflows."""
        return self.get_queryset().failed()
    
    def running(self):
        """Get running workflows."""
        return self.get_queryset().running()
    
    def recent(self, days: int = 7):
        """Get recent workflows."""
        return self.get_queryset().recent(days)
    
    def with_executions(self):
        """Get workflows with executions."""
        return self.get_queryset().with_executions()
    
    def create_workflow(
        self,
        name: str,
        user,
        pattern: str,
        agent_names: list,
        input_prompt: str,
        config: Optional[Dict] = None,
        **kwargs
    ):
        """Create a new workflow execution."""
        return self.create(
            name=name,
            user=user,
            pattern=pattern,
            agent_names=agent_names,
            input_prompt=input_prompt,
            config=config or {},
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get workflow statistics for user."""
        workflows = self.for_user(user)
        
        return {
            'total': workflows.count(),
            'successful': workflows.successful().count(),
            'failed': workflows.failed().count(),
            'running': workflows.running().count(),
            'recent': workflows.recent().count(),
            'total_cost': float(workflows.aggregate(
                total=models.Sum('total_cost')
            )['total'] or 0),
            'avg_execution_time': workflows.aggregate(
                avg=models.Avg('total_execution_time')
            )['avg'],
        }
