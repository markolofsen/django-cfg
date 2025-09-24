"""
Django signals for orchestrator integration.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from ..models.registry import AgentDefinition
from .registry import get_registry

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AgentDefinition)
async def agent_definition_saved(sender, instance: AgentDefinition, created, **kwargs):
    """Handle agent definition save."""
    registry = get_registry()
    
    if created:
        logger.info(f"New agent definition created: {instance.name}")
    else:
        logger.info(f"Agent definition updated: {instance.name}")
        
        # Reload agent if it exists in runtime
        if instance.name in registry.get_runtime_agents():
            try:
                await registry.reload_agent(instance.name)
                logger.info(f"Reloaded runtime agent: {instance.name}")
            except Exception as e:
                logger.error(f"Failed to reload agent '{instance.name}': {e}")


@receiver(post_delete, sender=AgentDefinition)
def agent_definition_deleted(sender, instance: AgentDefinition, **kwargs):
    """Handle agent definition deletion."""
    registry = get_registry()
    
    # Remove from runtime if exists
    if instance.name in registry.get_runtime_agents():
        del registry._runtime_agents[instance.name]
        registry.orchestrator.unregister_agent(instance.name)
        logger.info(f"Removed runtime agent: {instance.name}")


def setup_signals():
    """Setup signal handlers."""
    # Signals are automatically connected via decorators
    logger.info("Django Orchestrator signals configured")
