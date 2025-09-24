"""
Simple Orchestrator - Main coordination class for multi-agent workflows.
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from .agent import DjangoAgent
from .models import ExecutionResult, WorkflowConfig
from .exceptions import AgentNotFoundError, ExecutionError, ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class ExecutionPattern:
    """Base class for execution patterns."""
    
    name: str
    description: str
    
    async def execute(
        self,
        agents: List[DjangoAgent],
        prompt: str,
        deps: Any,
        **kwargs
    ) -> List[ExecutionResult]:
        """Execute agents according to pattern."""
        raise NotImplementedError


class SequentialPattern(ExecutionPattern):
    """Sequential execution pattern - agents run one after another."""
    
    def __init__(self):
        super().__init__(
            name="sequential",
            description="Execute agents one after another, passing results forward"
        )
    
    async def execute(
        self,
        agents: List[DjangoAgent],
        prompt: str,
        deps: Any,
        **kwargs
    ) -> List[ExecutionResult]:
        """Execute agents sequentially."""
        results = []
        current_prompt = prompt
        
        for i, agent in enumerate(agents):
            logger.debug(f"Executing agent {i+1}/{len(agents)}: {agent.name}")
            
            try:
                result = await agent.run(current_prompt, deps)
                results.append(result)
                
                # Pass result to next agent (if not the last one)
                if i < len(agents) - 1:
                    current_prompt = f"Previous result: {result.output}\nNew task: {prompt}"
                
            except Exception as e:
                logger.error(f"Sequential execution failed at agent '{agent.name}': {e}")
                # Add failed result
                results.append(ExecutionResult(
                    agent_name=agent.name,
                    output=None,
                    execution_time=0.0,
                    error=str(e)
                ))
                break  # Stop execution on error
        
        return results


class ParallelPattern(ExecutionPattern):
    """Parallel execution pattern - agents run concurrently."""
    
    def __init__(self):
        super().__init__(
            name="parallel",
            description="Execute agents concurrently with optional concurrency limits"
        )
    
    async def execute(
        self,
        agents: List[DjangoAgent],
        prompt: str,
        deps: Any,
        **kwargs
    ) -> List[ExecutionResult]:
        """Execute agents in parallel."""
        max_concurrent = kwargs.get('max_concurrent', 5)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_agent_with_semaphore(agent: DjangoAgent) -> ExecutionResult:
            async with semaphore:
                try:
                    return await agent.run(prompt, deps)
                except Exception as e:
                    logger.error(f"Parallel execution failed for agent '{agent.name}': {e}")
                    return ExecutionResult(
                        agent_name=agent.name,
                        output=None,
                        execution_time=0.0,
                        error=str(e)
                    )
        
        logger.debug(f"Executing {len(agents)} agents in parallel (max_concurrent={max_concurrent})")
        
        # Execute all agents concurrently
        tasks = [run_agent_with_semaphore(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that weren't caught
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ExecutionResult(
                    agent_name=agents[i].name,
                    output=None,
                    execution_time=0.0,
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results


class ConditionalPattern(ExecutionPattern):
    """Conditional execution pattern - execute agents based on conditions."""
    
    def __init__(self):
        super().__init__(
            name="conditional",
            description="Execute agents based on condition evaluation"
        )
    
    async def execute(
        self,
        agents: List[DjangoAgent],
        prompt: str,
        deps: Any,
        **kwargs
    ) -> List[ExecutionResult]:
        """Execute agents conditionally."""
        if len(agents) < 2:
            raise ConfigurationError("Conditional pattern requires at least 2 agents")
        
        # First agent determines condition
        condition_agent = agents[0]
        execution_agents = agents[1:]
        
        logger.debug(f"Using '{condition_agent.name}' as condition agent")
        
        # Get condition
        condition_result = await condition_agent.run(prompt, deps)
        results = [condition_result]
        
        # Check if we should proceed
        should_proceed = self._evaluate_condition(condition_result.output)
        
        if should_proceed:
            logger.debug(f"Condition met, executing {len(execution_agents)} agents")
            
            # Execute remaining agents sequentially
            sequential = SequentialPattern()
            execution_results = await sequential.execute(execution_agents, prompt, deps, **kwargs)
            results.extend(execution_results)
        else:
            logger.debug("Condition not met, skipping execution agents")
        
        return results
    
    def _evaluate_condition(self, output: Any) -> bool:
        """Evaluate condition from agent output."""
        # Simple condition evaluation
        if isinstance(output, dict):
            return output.get('proceed', False) or output.get('success', False)
        elif isinstance(output, bool):
            return output
        elif hasattr(output, 'success'):
            return output.success
        else:
            # Default to True if we can't determine condition
            return True


class SimpleOrchestrator:
    """
    Main orchestrator for agent coordination.
    
    Provides simple, clean interface for multi-agent workflows
    following KISS principles.
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.agents: Dict[str, DjangoAgent] = {}
        self.patterns: Dict[str, ExecutionPattern] = {
            'sequential': SequentialPattern(),
            'parallel': ParallelPattern(),
            'conditional': ConditionalPattern()
        }
        
        # Metrics
        self._total_executions = 0
        self._total_execution_time = 0.0
        self._pattern_usage = {}
        
        logger.info("Initialized SimpleOrchestrator")
    
    def register_agent(self, agent: DjangoAgent):
        """
        Register agent with orchestrator.
        
        Args:
            agent: DjangoAgent instance to register
            
        Raises:
            ConfigurationError: If agent name already exists
        """
        if agent.name in self.agents:
            raise ConfigurationError(f"Agent '{agent.name}' already registered")
        
        self.agents[agent.name] = agent
        logger.info(f"Registered agent '{agent.name}'")
    
    def unregister_agent(self, agent_name: str):
        """
        Unregister agent from orchestrator.
        
        Args:
            agent_name: Name of agent to unregister
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent '{agent_name}'")
    
    def get_agent(self, name: str) -> DjangoAgent:
        """
        Get registered agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            DjangoAgent instance
            
        Raises:
            AgentNotFoundError: If agent not found
        """
        if name not in self.agents:
            raise AgentNotFoundError(name)
        
        return self.agents[name]
    
    def list_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.agents.keys())
    
    def add_pattern(self, pattern: ExecutionPattern):
        """
        Add custom execution pattern.
        
        Args:
            pattern: ExecutionPattern instance
        """
        self.patterns[pattern.name] = pattern
        logger.info(f"Added execution pattern '{pattern.name}'")
    
    async def execute(
        self,
        pattern: str,
        agents: List[str],
        prompt: str,
        deps: Any,
        config: Optional[WorkflowConfig] = None,
        **kwargs
    ) -> List[ExecutionResult]:
        """
        Execute agents using specified pattern.
        
        Args:
            pattern: Execution pattern name
            agents: List of agent names to execute
            prompt: Input prompt for agents
            deps: Dependencies for execution
            config: Optional workflow configuration
            **kwargs: Pattern-specific options
            
        Returns:
            List of execution results
            
        Raises:
            AgentNotFoundError: If any agent not found
            ConfigurationError: If pattern not found
            ExecutionError: If execution fails
        """
        # Validate pattern
        if pattern not in self.patterns:
            available_patterns = list(self.patterns.keys())
            raise ConfigurationError(
                f"Unknown pattern '{pattern}'. Available patterns: {available_patterns}"
            )
        
        # Validate agents
        agent_instances = []
        for agent_name in agents:
            if agent_name not in self.agents:
                raise AgentNotFoundError(agent_name)
            agent_instances.append(self.agents[agent_name])
        
        # Apply configuration
        if config:
            kwargs.setdefault('max_concurrent', config.max_concurrent)
            kwargs.setdefault('timeout', config.timeout)
        
        # Execute pattern
        start_time = time.time()
        execution_id = f"exec_{int(time.time() * 1000)}"
        
        logger.info(
            f"Starting execution {execution_id}: pattern='{pattern}', "
            f"agents={agents}, prompt='{prompt[:50]}...'"
        )
        
        try:
            pattern_executor = self.patterns[pattern]
            results = await pattern_executor.execute(agent_instances, prompt, deps, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Update metrics
            self._total_executions += 1
            self._total_execution_time += execution_time
            self._pattern_usage[pattern] = self._pattern_usage.get(pattern, 0) + 1
            
            # Log results
            successful_agents = sum(1 for r in results if r.success)
            failed_agents = len(results) - successful_agents
            
            logger.info(
                f"Completed execution {execution_id} in {execution_time:.2f}s: "
                f"{successful_agents} successful, {failed_agents} failed"
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Execution {execution_id} failed after {execution_time:.2f}s: {e}")
            
            raise ExecutionError(
                f"Execution failed: {str(e)}",
                original_error=e
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        return {
            'total_executions': self._total_executions,
            'total_execution_time': self._total_execution_time,
            'average_execution_time': (
                self._total_execution_time / self._total_executions
                if self._total_executions > 0 else 0
            ),
            'pattern_usage': self._pattern_usage.copy(),
            'registered_agents': len(self.agents),
            'available_patterns': list(self.patterns.keys())
        }
    
    def reset_metrics(self):
        """Reset orchestrator metrics."""
        self._total_executions = 0
        self._total_execution_time = 0.0
        self._pattern_usage = {}
    
    @property
    def registered_agents(self) -> Dict[str, DjangoAgent]:
        """Get copy of registered agents."""
        return self.agents.copy()
    
    def __repr__(self) -> str:
        return f"SimpleOrchestrator(agents={len(self.agents)}, patterns={len(self.patterns)})"
