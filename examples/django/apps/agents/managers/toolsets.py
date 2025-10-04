"""
Custom managers for toolset models.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any, List


class ToolExecutionQuerySet(models.QuerySet):
    """Custom queryset for ToolExecution."""
    
    def for_user(self, user):
        """Filter tool executions for specific user."""
        return self.filter(user=user)
    
    def by_status(self, status: str):
        """Filter by execution status."""
        return self.filter(status=status)
    
    def by_tool(self, tool_name: str):
        """Filter by tool name."""
        return self.filter(tool_name=tool_name)
    
    def by_toolset(self, toolset_name: str):
        """Filter by toolset name."""
        return self.filter(toolset_name=toolset_name)
    
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
    
    def with_retries(self):
        """Get executions that had retries."""
        return self.filter(retry_count__gt=0)
    
    def expensive(self, min_time: float = 1.0):
        """Get time-expensive executions."""
        return self.filter(execution_time__gte=min_time)


class ToolExecutionManager(models.Manager):
    """Custom manager for ToolExecution."""
    
    def get_queryset(self):
        return ToolExecutionQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get executions for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get executions by status."""
        return self.get_queryset().by_status(status)
    
    def by_tool(self, tool_name: str):
        """Get executions by tool."""
        return self.get_queryset().by_tool(tool_name)
    
    def by_toolset(self, toolset_name: str):
        """Get executions by toolset."""
        return self.get_queryset().by_toolset(toolset_name)
    
    def successful(self):
        """Get successful executions."""
        return self.get_queryset().successful()
    
    def failed(self):
        """Get failed executions."""
        return self.get_queryset().failed()
    
    def recent(self, days: int = 7):
        """Get recent executions."""
        return self.get_queryset().recent(days)
    
    def with_retries(self):
        """Get executions with retries."""
        return self.get_queryset().with_retries()
    
    def expensive(self, min_time: float = 1.0):
        """Get expensive executions."""
        return self.get_queryset().expensive(min_time)
    
    def create_execution(
        self,
        tool_name: str,
        toolset_name: str,
        user,
        arguments: Dict,
        agent_execution=None,
        **kwargs
    ):
        """Create a new tool execution."""
        return self.create(
            tool_name=tool_name,
            toolset_name=toolset_name,
            user=user,
            arguments=arguments,
            agent_execution=agent_execution,
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get tool execution statistics for user."""
        executions = self.for_user(user)
        
        return {
            'total': executions.count(),
            'successful': executions.successful().count(),
            'failed': executions.failed().count(),
            'recent': executions.recent().count(),
            'with_retries': executions.with_retries().count(),
            'avg_execution_time': executions.aggregate(
                avg=models.Avg('execution_time')
            )['avg'],
            'total_retries': executions.aggregate(
                total=models.Sum('retry_count')
            )['total'] or 0,
        }
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get overall tool statistics."""
        return {
            'unique_tools': self.values('tool_name').distinct().count(),
            'unique_toolsets': self.values('toolset_name').distinct().count(),
            'total_executions': self.count(),
            'success_rate': self.successful().count() / max(self.count(), 1) * 100,
            'avg_execution_time': self.aggregate(
                avg=models.Avg('execution_time')
            )['avg'],
        }


class ApprovalLogQuerySet(models.QuerySet):
    """Custom queryset for ApprovalLog."""
    
    def for_user(self, user):
        """Filter approvals for specific user."""
        return self.filter(user=user)
    
    def by_status(self, status: str):
        """Filter by approval status."""
        return self.filter(status=status)
    
    def by_tool(self, tool_name: str):
        """Filter by tool name."""
        return self.filter(tool_name=tool_name)
    
    def pending(self):
        """Get pending approvals."""
        return self.filter(status='pending')
    
    def approved(self):
        """Get approved requests."""
        return self.filter(status='approved')
    
    def rejected(self):
        """Get rejected requests."""
        return self.filter(status='rejected')
    
    def expired(self):
        """Get expired requests."""
        return self.filter(status='expired')
    
    def recent(self, days: int = 7):
        """Get recent requests."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(requested_at__gte=cutoff)
    
    def decided_by(self, user):
        """Get requests decided by specific user."""
        return self.filter(
            models.Q(approved_by=user) | models.Q(rejected_by=user)
        )
    
    def fast_decisions(self, max_seconds: int = 60):
        """Get quickly decided requests."""
        return self.filter(time_to_decision__lte=max_seconds)


class ApprovalLogManager(models.Manager):
    """Custom manager for ApprovalLog."""
    
    def get_queryset(self):
        return ApprovalLogQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get approvals for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_status(self, status: str):
        """Get approvals by status."""
        return self.get_queryset().by_status(status)
    
    def by_tool(self, tool_name: str):
        """Get approvals by tool."""
        return self.get_queryset().by_tool(tool_name)
    
    def pending(self):
        """Get pending approvals."""
        return self.get_queryset().pending()
    
    def approved(self):
        """Get approved requests."""
        return self.get_queryset().approved()
    
    def rejected(self):
        """Get rejected requests."""
        return self.get_queryset().rejected()
    
    def expired(self):
        """Get expired requests."""
        return self.get_queryset().expired()
    
    def recent(self, days: int = 7):
        """Get recent requests."""
        return self.get_queryset().recent(days)
    
    def decided_by(self, user):
        """Get requests decided by user."""
        return self.get_queryset().decided_by(user)
    
    def fast_decisions(self, max_seconds: int = 60):
        """Get fast decisions."""
        return self.get_queryset().fast_decisions(max_seconds)
    
    def create_approval_request(
        self,
        approval_id: str,
        tool_name: str,
        user,
        tool_args: Dict,
        justification: str = "",
        expires_at=None,
        **kwargs
    ):
        """Create a new approval request."""
        if expires_at is None:
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(hours=24)
        
        return self.create(
            approval_id=approval_id,
            tool_name=tool_name,
            user=user,
            tool_args=tool_args,
            justification=justification,
            expires_at=expires_at,
            **kwargs
        )
    
    def get_stats_for_user(self, user) -> Dict[str, Any]:
        """Get approval statistics for user."""
        requests = self.for_user(user)
        
        return {
            'total': requests.count(),
            'pending': requests.pending().count(),
            'approved': requests.approved().count(),
            'rejected': requests.rejected().count(),
            'expired': requests.expired().count(),
            'recent': requests.recent().count(),
            'approval_rate': requests.approved().count() / max(requests.count(), 1) * 100,
            'avg_decision_time': requests.exclude(
                time_to_decision__isnull=True
            ).aggregate(
                avg=models.Avg('time_to_decision')
            )['avg'],
        }


class ToolsetConfigurationQuerySet(models.QuerySet):
    """Custom queryset for ToolsetConfiguration."""
    
    def active(self):
        """Get active toolset configurations."""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Get toolsets available for specific user."""
        return self.filter(
            models.Q(allowed_users=user) |
            models.Q(allowed_groups__in=user.groups.all()) |
            models.Q(created_by=user)
        ).distinct()
    
    def by_creator(self, user):
        """Get toolsets created by specific user."""
        return self.filter(created_by=user)
    
    def by_class(self, toolset_class: str):
        """Filter by toolset class."""
        return self.filter(toolset_class=toolset_class)
    
    def recent(self, days: int = 7):
        """Get recently created toolsets."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def search(self, query: str):
        """Search toolsets by name or description."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(toolset_class__icontains=query)
        )


class ToolsetConfigurationManager(models.Manager):
    """Custom manager for ToolsetConfiguration."""
    
    def get_queryset(self):
        return ToolsetConfigurationQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active toolsets."""
        return self.get_queryset().active()
    
    def for_user(self, user):
        """Get toolsets for user."""
        return self.get_queryset().for_user(user)
    
    def by_creator(self, user):
        """Get toolsets by creator."""
        return self.get_queryset().by_creator(user)
    
    def by_class(self, toolset_class: str):
        """Get toolsets by class."""
        return self.get_queryset().by_class(toolset_class)
    
    def recent(self, days: int = 7):
        """Get recent toolsets."""
        return self.get_queryset().recent(days)
    
    def search(self, query: str):
        """Search toolsets."""
        return self.get_queryset().search(query)
    
    def create_toolset(
        self,
        name: str,
        toolset_class: str,
        created_by,
        description: str = "",
        config: Optional[Dict] = None,
        **kwargs
    ):
        """Create a new toolset configuration."""
        return self.create(
            name=name,
            toolset_class=toolset_class,
            description=description,
            config=config or {},
            created_by=created_by,
            **kwargs
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get toolset statistics."""
        queryset = self.get_queryset()
        
        return {
            'total': queryset.count(),
            'active': queryset.active().count(),
            'unique_classes': queryset.values('toolset_class').distinct().count(),
            'recent': queryset.recent().count(),
        }


class ToolPermissionQuerySet(models.QuerySet):
    """Custom queryset for ToolPermission."""
    
    def for_user(self, user):
        """Filter permissions for specific user."""
        return self.filter(user=user)
    
    def by_tool(self, tool_name: str):
        """Filter by tool name."""
        return self.filter(tool_name=tool_name)
    
    def by_permission(self, permission: str):
        """Filter by permission type."""
        return self.filter(permission=permission)
    
    def allowed(self):
        """Get allowed permissions."""
        return self.filter(permission='allow')
    
    def denied(self):
        """Get denied permissions."""
        return self.filter(permission='deny')
    
    def requiring_approval(self):
        """Get permissions requiring approval."""
        return self.filter(permission='require_approval')
    
    def by_creator(self, user):
        """Get permissions created by specific user."""
        return self.filter(created_by=user)
    
    def recent(self, days: int = 7):
        """Get recently created permissions."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class ToolPermissionManager(models.Manager):
    """Custom manager for ToolPermission."""
    
    def get_queryset(self):
        return ToolPermissionQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        """Get permissions for specific user."""
        return self.get_queryset().for_user(user)
    
    def by_tool(self, tool_name: str):
        """Get permissions by tool."""
        return self.get_queryset().by_tool(tool_name)
    
    def by_permission(self, permission: str):
        """Get permissions by type."""
        return self.get_queryset().by_permission(permission)
    
    def allowed(self):
        """Get allowed permissions."""
        return self.get_queryset().allowed()
    
    def denied(self):
        """Get denied permissions."""
        return self.get_queryset().denied()
    
    def requiring_approval(self):
        """Get permissions requiring approval."""
        return self.get_queryset().requiring_approval()
    
    def by_creator(self, user):
        """Get permissions by creator."""
        return self.get_queryset().by_creator(user)
    
    def recent(self, days: int = 7):
        """Get recent permissions."""
        return self.get_queryset().recent(days)
    
    def create_permission(
        self,
        user,
        tool_name: str,
        permission: str,
        created_by,
        conditions: Optional[Dict] = None,
        **kwargs
    ):
        """Create a new tool permission."""
        return self.create(
            user=user,
            tool_name=tool_name,
            permission=permission,
            conditions=conditions or {},
            created_by=created_by,
            **kwargs
        )
    
    def get_user_permission(self, user, tool_name: str):
        """Get user's permission for specific tool."""
        try:
            return self.get(user=user, tool_name=tool_name)
        except self.model.DoesNotExist:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get permission statistics."""
        queryset = self.get_queryset()
        
        return {
            'total': queryset.count(),
            'allowed': queryset.allowed().count(),
            'denied': queryset.denied().count(),
            'requiring_approval': queryset.requiring_approval().count(),
            'unique_tools': queryset.values('tool_name').distinct().count(),
            'unique_users': queryset.values('user').distinct().count(),
            'recent': queryset.recent().count(),
        }
