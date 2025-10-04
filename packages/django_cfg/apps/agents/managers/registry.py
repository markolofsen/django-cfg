"""
Custom managers for agent registry models.
"""

from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any, List


class AgentDefinitionQuerySet(models.QuerySet):
    """Custom queryset for AgentDefinition."""
    
    def active(self):
        """Get active agent definitions."""
        return self.filter(is_active=True)
    
    def public(self):
        """Get public agent definitions."""
        return self.filter(is_public=True)
    
    def for_user(self, user):
        """Get agent definitions available for specific user."""
        return self.filter(
            models.Q(is_public=True) |
            models.Q(created_by=user) |
            models.Q(allowed_users=user) |
            models.Q(allowed_groups__in=user.groups.all())
        ).distinct()
    
    def by_category(self, category: str):
        """Filter by category."""
        return self.filter(category=category)
    
    def by_creator(self, user):
        """Get agents created by specific user."""
        return self.filter(created_by=user)
    
    def popular(self, min_usage: int = 10):
        """Get popular agents."""
        return self.filter(usage_count__gte=min_usage)
    
    def recent(self, days: int = 7):
        """Get recently created agents."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def with_executions(self):
        """Include execution statistics."""
        return self.prefetch_related('executions')
    
    def search(self, query: str):
        """Search agents by name, description, or instructions."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(display_name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(instructions__icontains=query)
        )


class AgentDefinitionManager(models.Manager):
    """Custom manager for AgentDefinition."""
    
    def get_queryset(self):
        return AgentDefinitionQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active agents."""
        return self.get_queryset().active()
    
    def public(self):
        """Get public agents."""
        return self.get_queryset().public()
    
    def for_user(self, user):
        """Get agents available for user."""
        return self.get_queryset().for_user(user)
    
    def by_category(self, category: str):
        """Get agents by category."""
        return self.get_queryset().by_category(category)
    
    def by_creator(self, user):
        """Get agents by creator."""
        return self.get_queryset().by_creator(user)
    
    def popular(self, min_usage: int = 10):
        """Get popular agents."""
        return self.get_queryset().popular(min_usage)
    
    def recent(self, days: int = 7):
        """Get recent agents."""
        return self.get_queryset().recent(days)
    
    def with_executions(self):
        """Get agents with executions."""
        return self.get_queryset().with_executions()
    
    def search(self, query: str):
        """Search agents."""
        return self.get_queryset().search(query)
    
    def create_agent(
        self,
        name: str,
        display_name: str,
        instructions: str,
        created_by,
        description: str = "",
        category: str = "",
        is_public: bool = False,
        **kwargs
    ):
        """Create a new agent definition."""
        return self.create(
            name=name,
            display_name=display_name,
            instructions=instructions,
            description=description,
            category=category,
            is_public=is_public,
            created_by=created_by,
            **kwargs
        )
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return list(
            self.active()
            .values_list('category', flat=True)
            .distinct()
            .exclude(category='')
            .order_by('category')
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall agent statistics."""
        queryset = self.get_queryset()
        
        return {
            'total': queryset.count(),
            'active': queryset.active().count(),
            'public': queryset.public().count(),
            'categories': len(self.get_categories()),
            'total_usage': queryset.aggregate(
                total=models.Sum('usage_count')
            )['total'] or 0,
            'avg_usage': queryset.aggregate(
                avg=models.Avg('usage_count')
            )['avg'] or 0,
        }


class AgentTemplateQuerySet(models.QuerySet):
    """Custom queryset for AgentTemplate."""
    
    def active(self):
        """Get active templates."""
        return self.filter(is_active=True)
    
    def by_category(self, category: str):
        """Filter by category."""
        return self.filter(category=category)
    
    def by_creator(self, user):
        """Get templates created by specific user."""
        return self.filter(created_by=user)
    
    def recent(self, days: int = 7):
        """Get recently created templates."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def search(self, query: str):
        """Search templates by name or description."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query)
        )


class AgentTemplateManager(models.Manager):
    """Custom manager for AgentTemplate."""
    
    def get_queryset(self):
        return AgentTemplateQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get active templates."""
        return self.get_queryset().active()
    
    def by_category(self, category: str):
        """Get templates by category."""
        return self.get_queryset().by_category(category)
    
    def by_creator(self, user):
        """Get templates by creator."""
        return self.get_queryset().by_creator(user)
    
    def recent(self, days: int = 7):
        """Get recent templates."""
        return self.get_queryset().recent(days)
    
    def search(self, query: str):
        """Search templates."""
        return self.get_queryset().search(query)
    
    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        template_config: Dict,
        created_by,
        default_instructions: str = "",
        recommended_model: str = "",
        use_cases: Optional[List] = None,
        **kwargs
    ):
        """Create a new agent template."""
        return self.create(
            name=name,
            description=description,
            category=category,
            template_config=template_config,
            default_instructions=default_instructions,
            recommended_model=recommended_model,
            use_cases=use_cases or [],
            created_by=created_by,
            **kwargs
        )
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return list(
            self.active()
            .values_list('category', flat=True)
            .distinct()
            .exclude(category='')
            .order_by('category')
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get template statistics."""
        queryset = self.get_queryset()
        
        return {
            'total': queryset.count(),
            'active': queryset.active().count(),
            'categories': len(self.get_categories()),
            'recent': queryset.recent().count(),
        }
