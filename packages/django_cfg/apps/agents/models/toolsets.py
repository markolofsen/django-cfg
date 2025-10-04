"""
Django models for toolset management and tool execution tracking.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ToolExecution(models.Model):
    """Track tool executions within agent runs."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent_execution = models.ForeignKey(
        'AgentExecution', 
        on_delete=models.CASCADE,
        related_name='tool_executions'
    )
    
    # Tool information
    tool_name = models.CharField(max_length=100, db_index=True)
    toolset_name = models.CharField(max_length=100, blank=True)
    
    # Execution data
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    arguments = models.JSONField(help_text="Tool arguments")
    result = models.JSONField(null=True, blank=True, help_text="Tool execution result")
    error_message = models.TextField(blank=True)
    
    # Metrics
    execution_time = models.FloatField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    from ..managers.toolsets import ToolExecutionManager
    objects = ToolExecutionManager()
    
    class Meta:
        db_table = 'orchestrator_tool_executions'
        indexes = [
            models.Index(fields=['tool_name', 'status']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['agent_execution', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"ToolExecution({self.tool_name}, {self.status})"
    
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


class ApprovalLog(models.Model):
    """Log approval decisions for tool executions."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        EXPIRED = 'expired', 'Expired'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Request context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_requests')
    tool_name = models.CharField(max_length=100)
    tool_args = models.JSONField()
    justification = models.TextField(blank=True)
    
    # Approval decision
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approvals_given'
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='rejections_given'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    from ..managers.toolsets import ApprovalLogManager
    objects = ApprovalLogManager()
    
    class Meta:
        db_table = 'orchestrator_approval_logs'
        indexes = [
            models.Index(fields=['status', 'requested_at']),
            models.Index(fields=['user', '-requested_at']),
            models.Index(fields=['approved_by', '-decided_at']),
        ]
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"ApprovalLog({self.approval_id}, {self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set decided_at timestamp
        if self.status in [self.Status.APPROVED, self.Status.REJECTED] and not self.decided_at:
            self.decided_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if approval request has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def time_to_decision(self):
        """Calculate time from request to decision."""
        if self.decided_at:
            return (self.decided_at - self.requested_at).total_seconds()
        return None
    
    def approve(self, approver):
        """Approve the request."""
        self.status = self.Status.APPROVED
        self.approved_by = approver
        self.decided_at = timezone.now()
        self.save()
    
    def reject(self, rejector, reason: str = ""):
        """Reject the request."""
        self.status = self.Status.REJECTED
        self.rejected_by = rejector
        self.rejection_reason = reason
        self.decided_at = timezone.now()
        self.save()


class ToolsetConfiguration(models.Model):
    """Configuration for toolsets."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Configuration
    toolset_class = models.CharField(max_length=200, help_text="Python class path")
    config = models.JSONField(default=dict, help_text="Toolset configuration")
    
    # Access control
    is_active = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='allowed_toolsets')
    allowed_groups = models.ManyToManyField('auth.Group', blank=True, related_name='allowed_toolsets')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom managers
    from ..managers.toolsets import ToolsetConfigurationManager
    objects = ToolsetConfigurationManager()
    
    class Meta:
        db_table = 'orchestrator_toolset_configurations'
        ordering = ['name']
    
    def __str__(self):
        return f"ToolsetConfiguration({self.name})"
    
    def can_be_used_by(self, user) -> bool:
        """Check if user can use this toolset."""
        if not self.is_active:
            return False
        
        if user == self.created_by:
            return True
        
        if self.allowed_users.filter(id=user.id).exists():
            return True
        
        if self.allowed_groups.filter(user__id=user.id).exists():
            return True
        
        return False


class ToolPermission(models.Model):
    """Permissions for specific tools."""
    
    class Permission(models.TextChoices):
        ALLOW = 'allow', 'Allow'
        DENY = 'deny', 'Deny'
        REQUIRE_APPROVAL = 'require_approval', 'Require Approval'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool_name = models.CharField(max_length=100, db_index=True)
    permission = models.CharField(
        max_length=20,
        choices=Permission.choices,
        default=Permission.ALLOW
    )
    
    # Optional conditions
    conditions = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Conditions for permission (e.g., argument limits)"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tool_permissions_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Custom managers
    from ..managers.toolsets import ToolPermissionManager
    objects = ToolPermissionManager()
    
    class Meta:
        db_table = 'orchestrator_tool_permissions'
        unique_together = ['user', 'tool_name']
        indexes = [
            models.Index(fields=['user', 'tool_name']),
            models.Index(fields=['tool_name', 'permission']),
        ]
    
    def __str__(self):
        return f"ToolPermission({self.user.username}, {self.tool_name}, {self.permission})"
    
    def check_conditions(self, tool_args: dict) -> bool:
        """Check if tool arguments meet permission conditions."""
        if not self.conditions:
            return True
        
        # Implement condition checking logic
        # This is a simple example - extend as needed
        for condition_key, condition_value in self.conditions.items():
            if condition_key in tool_args:
                arg_value = tool_args[condition_key]
                
                # Simple equality check
                if isinstance(condition_value, dict):
                    if 'max' in condition_value and arg_value > condition_value['max']:
                        return False
                    if 'min' in condition_value and arg_value < condition_value['min']:
                        return False
                elif arg_value != condition_value:
                    return False
        
        return True
