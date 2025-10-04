"""
Django models for tracking agent and workflow executions.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class AgentExecution(models.Model):
    """Track individual agent executions."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100, db_index=True)
    agent_definition = models.ForeignKey(
        'django_cfg_agents.AgentDefinition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions',
        help_text="Agent definition used for this execution"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    # Execution data
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True
    )
    input_prompt = models.TextField()
    output_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metrics
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    cached = models.BooleanField(default=False)
    
    # Workflow context
    workflow_execution = models.ForeignKey(
        'WorkflowExecution', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='agent_executions'
    )
    execution_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    from ..managers.execution import AgentExecutionManager
    objects = AgentExecutionManager()
    
    class Meta:
        db_table = 'orchestrator_agent_executions'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['agent_name', 'user']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['workflow_execution', 'execution_order']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AgentExecution({self.agent_name}, {self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set timestamps based on status
        if self.status == self.Status.RUNNING and not self.started_at:
            self.started_at = timezone.now()
        elif self.status in [self.Status.COMPLETED, self.Status.FAILED] and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_successful(self):
        """Check if execution was successful."""
        return self.status == self.Status.COMPLETED and not self.error_message


class WorkflowExecution(models.Model):
    """Track multi-agent workflow executions."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
        PAUSED = 'paused', 'Paused'
    
    class Pattern(models.TextChoices):
        SEQUENTIAL = 'sequential', 'Sequential'
        PARALLEL = 'parallel', 'Parallel'
        CONDITIONAL = 'conditional', 'Conditional'
        CUSTOM = 'custom', 'Custom'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    # Workflow configuration
    pattern = models.CharField(max_length=20, choices=Pattern.choices, default=Pattern.SEQUENTIAL)
    agent_names = models.JSONField(help_text="List of agent names in execution order")
    input_prompt = models.TextField()
    
    # Execution state
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True
    )
    current_step = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True, help_text="Workflow configuration")
    
    # Results
    final_output = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metrics
    total_execution_time = models.FloatField(null=True, blank=True)
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    from ..managers.execution import WorkflowExecutionManager
    objects = WorkflowExecutionManager()
    
    class Meta:
        db_table = 'orchestrator_workflow_executions'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['pattern', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"WorkflowExecution({self.name or self.id}, {self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set total_steps from agent_names
        if self.agent_names:
            self.total_steps = len(self.agent_names)
        
        # Auto-set timestamps based on status
        if self.status == self.Status.RUNNING and not self.started_at:
            self.started_at = timezone.now()
        elif self.status in [self.Status.COMPLETED, self.Status.FAILED] and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Calculate workflow duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_steps == 0:
            return 0
        return (self.current_step / self.total_steps) * 100
    
    @property
    def is_successful(self):
        """Check if workflow was successful."""
        return self.status == self.Status.COMPLETED and not self.error_message
    
    def get_agent_executions(self):
        """Get related agent executions in order."""
        return self.agent_executions.order_by('execution_order')
    
    def get_successful_executions(self):
        """Get successful agent executions."""
        return self.agent_executions.filter(status=AgentExecution.Status.COMPLETED)
    
    def get_failed_executions(self):
        """Get failed agent executions."""
        return self.agent_executions.filter(status=AgentExecution.Status.FAILED)
