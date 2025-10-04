"""
Django Agents - Universal AI agent system for Django applications.

Built on Pydantic AI with KISS principles and proper decomposition.
"""

__version__ = "0.1.0"
__author__ = "Django-CFG Team"

# Set default app config
default_app_config = 'django_cfg.apps.agents.apps.AgentsConfig'

__all__ = [
    # Core classes
    "DjangoAgent",
    "SimpleOrchestrator",
    "DjangoDeps",
    "RunContext",
    
    # Models
    "ExecutionResult",
    "WorkflowConfig",
    "ProcessResult",
    "AnalysisResult",
    
    # Exceptions
    "AgentError",
    "AgentNotFoundError", 
    "ExecutionError",
]

def __getattr__(name):
    """Lazy import for agents components."""
    if name == "DjangoAgent":
        from .core.agent import DjangoAgent
        return DjangoAgent
    elif name == "SimpleOrchestrator":
        from .core.orchestrator import SimpleOrchestrator
        return SimpleOrchestrator
    elif name == "DjangoDeps":
        from .core.dependencies import DjangoDeps
        return DjangoDeps
    elif name == "RunContext":
        from .core.dependencies import RunContext
        return RunContext
    elif name == "ExecutionResult":
        from .core.models import ExecutionResult
        return ExecutionResult
    elif name == "WorkflowConfig":
        from .core.models import WorkflowConfig
        return WorkflowConfig
    elif name == "ProcessResult":
        from .core.models import ProcessResult
        return ProcessResult
    elif name == "AnalysisResult":
        from .core.models import AnalysisResult
        return AnalysisResult
    elif name == "AgentError":
        from .core.exceptions import AgentError
        return AgentError
    elif name == "AgentNotFoundError":
        from .core.exceptions import AgentNotFoundError
        return AgentNotFoundError
    elif name == "ExecutionError":
        from .core.exceptions import ExecutionError
        return ExecutionError
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
