"""
Agent registry for Django integration.
"""

import logging
from typing import Dict, List, Optional, Type, Any
from django.contrib.auth.models import User

from ..core.agent import DjangoAgent
from ..core.orchestrator import SimpleOrchestrator
from ..core.dependencies import DjangoDeps
from ..models.registry import AgentDefinition

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry for managing agents in Django application.
    
    Provides:
    - Agent registration and discovery
    - Database-backed agent definitions
    - Runtime agent creation
    - Permission checking
    """
    
    def __init__(self):
        """Initialize agent registry."""
        self._runtime_agents: Dict[str, DjangoAgent] = {}
        self._orchestrator = SimpleOrchestrator()
        
        logger.info("Initialized AgentRegistry")
    
    @property
    def orchestrator(self) -> SimpleOrchestrator:
        """Get orchestrator instance."""
        return self._orchestrator
    
    async def register_agent_definition(
        self,
        name: str,
        instructions: str,
        deps_type: str,
        output_type: str,
        user: User,
        **kwargs
    ) -> AgentDefinition:
        """
        Register new agent definition in database.
        
        Args:
            name: Agent identifier
            instructions: System prompt
            deps_type: Dependencies type name
            output_type: Output type name
            user: User creating the agent
            **kwargs: Additional agent configuration
            
        Returns:
            Created AgentDefinition instance
        """
        # Check if agent already exists
        if await AgentDefinition.objects.filter(name=name).aexists():
            raise ValueError(f"Agent '{name}' already exists")
        
        # Create agent definition
        agent_def = await AgentDefinition.objects.acreate(
            name=name,
            instructions=instructions,
            deps_type=deps_type,
            output_type=output_type,
            created_by=user,
            **kwargs
        )
        
        logger.info(f"Registered agent definition: {name}")
        return agent_def
    
    async def get_agent_definition(self, name: str) -> Optional[AgentDefinition]:
        """Get agent definition by name."""
        try:
            return await AgentDefinition.objects.aget(name=name, is_active=True)
        except AgentDefinition.DoesNotExist:
            return None
    
    async def list_agent_definitions(
        self, 
        user: Optional[User] = None,
        category: Optional[str] = None
    ) -> List[AgentDefinition]:
        """List available agent definitions."""
        queryset = AgentDefinition.objects.filter(is_active=True)
        
        if user:
            queryset = AgentDefinition.get_available_for_user(user)
        
        if category:
            queryset = queryset.filter(category=category)
        
        return [agent_def async for agent_def in queryset.order_by('name')]
    
    async def create_runtime_agent(
        self, 
        agent_def: AgentDefinition,
        llm_client: Optional[Any] = None
    ) -> DjangoAgent:
        """
        Create runtime agent from definition.
        
        Args:
            agent_def: Agent definition from database
            llm_client: Optional LLM client override
            
        Returns:
            DjangoAgent instance
        """
        # Import dependency and output types
        deps_type = self._import_type(agent_def.deps_type)
        output_type = self._import_type(agent_def.output_type)
        
        # Create agent
        agent = DjangoAgent(
            name=agent_def.name,
            deps_type=deps_type,
            output_type=output_type,
            instructions=agent_def.instructions,
            model=agent_def.model,
            llm_client=llm_client,
            timeout=agent_def.timeout,
            max_retries=agent_def.max_retries,
            enable_caching=agent_def.enable_caching
        )
        
        # Apply tools configuration if available
        if agent_def.tools_config:
            await self._apply_tools_config(agent, agent_def.tools_config)
        
        # Cache runtime agent
        self._runtime_agents[agent_def.name] = agent
        
        # Register with orchestrator
        self._orchestrator.register_agent(agent)
        
        logger.info(f"Created runtime agent: {agent_def.name}")
        return agent
    
    async def get_or_create_agent(
        self, 
        name: str,
        user: Optional[User] = None,
        llm_client: Optional[Any] = None
    ) -> Optional[DjangoAgent]:
        """
        Get existing runtime agent or create from definition.
        
        Args:
            name: Agent name
            user: User requesting agent (for permission check)
            llm_client: Optional LLM client override
            
        Returns:
            DjangoAgent instance or None if not found/not allowed
        """
        # Check if already in runtime cache
        if name in self._runtime_agents:
            agent = self._runtime_agents[name]
            
            # Verify agent is still valid
            agent_def = await self.get_agent_definition(name)
            if agent_def and (not user or agent_def.can_be_used_by(user)):
                return agent
            else:
                # Remove invalid agent
                del self._runtime_agents[name]
                self._orchestrator.unregister_agent(name)
        
        # Get agent definition
        agent_def = await self.get_agent_definition(name)
        if not agent_def:
            return None
        
        # Check permissions
        if user and not agent_def.can_be_used_by(user):
            logger.warning(f"User {user.username} denied access to agent '{name}'")
            return None
        
        # Create runtime agent
        return await self.create_runtime_agent(agent_def, llm_client)
    
    async def execute_agent(
        self,
        agent_name: str,
        prompt: str,
        deps: DjangoDeps,
        user: Optional[User] = None,
        **kwargs
    ):
        """
        Execute agent by name.
        
        Args:
            agent_name: Name of agent to execute
            prompt: Input prompt
            deps: Dependencies
            user: User executing agent
            **kwargs: Additional execution parameters
            
        Returns:
            Execution result
        """
        # Get agent
        agent = await self.get_or_create_agent(agent_name, user)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found or not accessible")
        
        # Update usage statistics
        agent_def = await self.get_agent_definition(agent_name)
        if agent_def:
            agent_def.increment_usage()
        
        # Execute agent
        return await agent.run(prompt, deps, **kwargs)
    
    async def reload_agent(self, name: str) -> bool:
        """
        Reload agent from database definition.
        
        Args:
            name: Agent name to reload
            
        Returns:
            True if reloaded successfully
        """
        # Remove from runtime cache
        if name in self._runtime_agents:
            del self._runtime_agents[name]
            self._orchestrator.unregister_agent(name)
        
        # Recreate from definition
        agent_def = await self.get_agent_definition(name)
        if agent_def:
            await self.create_runtime_agent(agent_def)
            return True
        
        return False
    
    async def reload_all_agents(self) -> int:
        """
        Reload all agents from database.
        
        Returns:
            Number of agents reloaded
        """
        # Clear runtime cache
        self._runtime_agents.clear()
        
        # Clear orchestrator
        for agent_name in list(self._orchestrator.agents.keys()):
            self._orchestrator.unregister_agent(agent_name)
        
        # Reload all active agents
        agent_defs = await self.list_agent_definitions()
        count = 0
        
        for agent_def in agent_defs:
            try:
                await self.create_runtime_agent(agent_def)
                count += 1
            except Exception as e:
                logger.error(f"Failed to reload agent '{agent_def.name}': {e}")
        
        logger.info(f"Reloaded {count} agents")
        return count
    
    def _import_type(self, type_name: str) -> Type:
        """Import type by name."""
        # Handle built-in types
        if type_name in ['DjangoDeps', 'ContentDeps', 'DataProcessingDeps', 'BusinessLogicDeps']:
            from ..core.dependencies import DjangoDeps, ContentDeps, DataProcessingDeps, BusinessLogicDeps
            return locals()[type_name]
        
        if type_name in ['ProcessResult', 'AnalysisResult', 'ValidationResult']:
            from ..core.models import ProcessResult, AnalysisResult, ValidationResult
            return locals()[type_name]
        
        # Handle custom types
        try:
            module_name, class_name = type_name.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        except (ValueError, ImportError, AttributeError) as e:
            logger.error(f"Failed to import type '{type_name}': {e}")
            # Fallback to basic types
            from ..core.dependencies import DjangoDeps
            from ..core.models import ProcessResult
            
            if 'Deps' in type_name:
                return DjangoDeps
            else:
                return ProcessResult
    
    async def _apply_tools_config(self, agent: DjangoAgent, tools_config: Dict[str, Any]):
        """Apply tools configuration to agent."""
        # This would be extended to support dynamic tool loading
        # For now, just log the configuration
        logger.debug(f"Tools config for agent '{agent.name}': {tools_config}")
    
    def get_runtime_agents(self) -> Dict[str, DjangoAgent]:
        """Get all runtime agents."""
        return self._runtime_agents.copy()
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get registry metrics."""
        return {
            'runtime_agents_count': len(self._runtime_agents),
            'orchestrator_metrics': self._orchestrator.get_metrics(),
            'agent_names': list(self._runtime_agents.keys()),
        }


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


async def initialize_registry() -> AgentRegistry:
    """Initialize registry and load agents from database."""
    registry = get_registry()
    
    try:
        # Load all active agents
        count = await registry.reload_all_agents()
        logger.info(f"Initialized registry with {count} agents")
    except Exception as e:
        logger.error(f"Failed to initialize registry: {e}")
    
    return registry
