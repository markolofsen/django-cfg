"""
Django models for agent registry and configuration.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import json


class AgentDefinition(models.Model):
    """Registry of available agents with their configurations."""
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    instructions = models.TextField(help_text="System prompt for the agent")
    
    # Type information
    deps_type = models.CharField(max_length=100, help_text="Python class name for dependencies")
    output_type = models.CharField(max_length=100, help_text="Python class name for output")
    
    # Model configuration
    model = models.CharField(max_length=100, default='openai:gpt-4o-mini')
    timeout = models.PositiveIntegerField(default=300, help_text="Timeout in seconds")
    max_retries = models.PositiveIntegerField(default=3)
    enable_caching = models.BooleanField(default=True)
    
    # Tools configuration
    tools_config = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Configuration for agent tools"
    )
    
    # Permissions and access control
    is_active = models.BooleanField(default=True, db_index=True)
    is_public = models.BooleanField(default=False, help_text="Available to all users")
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        blank=True, 
        related_name='allowed_agents',
        help_text="Users allowed to use this agent"
    )
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='allowed_agents',
        help_text="Groups allowed to use this agent"
    )
    
    # Metadata
    category = models.CharField(max_length=50, blank=True, db_index=True)
    tags = models.JSONField(default=list, blank=True, help_text="List of tags")
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Audit fields
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_agents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    from ..managers.registry import AgentDefinitionManager
    objects = AgentDefinitionManager()
    
    class Meta:
        db_table = 'orchestrator_agent_definitions'
        indexes = [
            models.Index(fields=['is_active', 'category']),
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['-usage_count']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"AgentDefinition({self.name})"
    
    def clean(self):
        """Validate agent definition."""
        super().clean()
        
        # Validate tools_config is valid JSON
        if self.tools_config:
            try:
                if isinstance(self.tools_config, str):
                    json.loads(self.tools_config)
            except json.JSONDecodeError:
                raise ValidationError({'tools_config': 'Invalid JSON format'})
        
        # Validate tags is a list
        if self.tags and not isinstance(self.tags, list):
            raise ValidationError({'tags': 'Tags must be a list'})
        
        # Validate timeout range
        if self.timeout < 1 or self.timeout > 3600:
            raise ValidationError({'timeout': 'Timeout must be between 1 and 3600 seconds'})
        
        # Validate max_retries range
        if self.max_retries < 0 or self.max_retries > 10:
            raise ValidationError({'max_retries': 'Max retries must be between 0 and 10'})
    
    def save(self, *args, **kwargs):
        # Set display_name if not provided
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
        
        # Clean and validate
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def can_be_used_by(self, user) -> bool:
        """Check if user can use this agent."""
        if not self.is_active:
            return False
        
        if self.is_public:
            return True
        
        if user == self.created_by:
            return True
        
        if self.allowed_users.filter(id=user.id).exists():
            return True
        
        if self.allowed_groups.filter(user__id=user.id).exists():
            return True
        
        return False
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'instructions': self.instructions,
            'deps_type': self.deps_type,
            'output_type': self.output_type,
            'model': self.model,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'enable_caching': self.enable_caching,
            'tools_config': self.tools_config,
            'is_active': self.is_active,
            'category': self.category,
            'tags': self.tags,
            'version': self.version,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    


class AgentTemplate(models.Model):
    """Templates for creating new agents."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Template configuration
    template_config = models.JSONField(help_text="Template configuration")
    default_instructions = models.TextField()
    recommended_model = models.CharField(max_length=100, default='openai:gpt-4o-mini')
    
    # Categorization
    category = models.CharField(max_length=50, db_index=True)
    use_cases = models.JSONField(default=list, help_text="List of use cases")
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Custom managers
    from ..managers.registry import AgentTemplateManager
    objects = AgentTemplateManager()
    
    class Meta:
        db_table = 'orchestrator_agent_templates'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"AgentTemplate({self.name})"
    
    def create_agent_definition(
        self, 
        name: str, 
        user, 
        custom_instructions: str = None
    ) -> AgentDefinition:
        """Create agent definition from template."""
        config = self.template_config.copy()
        
        return AgentDefinition.objects.create(
            name=name,
            description=self.description,
            instructions=custom_instructions or self.default_instructions,
            deps_type=config.get('deps_type', 'DjangoDeps'),
            output_type=config.get('output_type', 'ProcessResult'),
            model=config.get('model', self.recommended_model),
            timeout=config.get('timeout', 300),
            max_retries=config.get('max_retries', 3),
            tools_config=config.get('tools_config', {}),
            category=self.category,
            created_by=user
        )
