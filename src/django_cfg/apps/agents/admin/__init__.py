"""
Django admin interfaces for Django Orchestrator.
"""

from .registry_admin import AgentDefinitionAdmin, AgentTemplateAdmin
from .execution_admin import AgentExecutionAdmin, WorkflowExecutionAdmin
from .toolsets_admin import ToolExecutionAdmin, ApprovalLogAdmin, ToolsetConfigurationAdmin

__all__ = [
    'AgentDefinitionAdmin',
    'AgentTemplateAdmin', 
    'AgentExecutionAdmin',
    'WorkflowExecutionAdmin',
    'ToolExecutionAdmin',
    'ApprovalLogAdmin',
    'ToolsetConfigurationAdmin',
]
