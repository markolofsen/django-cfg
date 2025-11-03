"""
Agents admin interfaces using Django Admin Utilities.

Modern, clean admin interfaces with Material Icons and consistent styling.
"""

from django.contrib import admin

from .execution_admin import AgentExecutionAdmin, WorkflowExecutionAdmin
from .registry_admin import AgentDefinitionAdmin, AgentTemplateAdmin
from .toolsets_admin import ApprovalLogAdmin, ToolExecutionAdmin, ToolsetConfigurationAdmin

# All models are registered in their respective admin files using @admin.register
# This provides:
# - Clean separation of concerns
# - Material Icons integration
# - Type-safe configurations
# - Performance optimizations
# - Consistent styling with django_admin module

__all__ = [
    'AgentExecutionAdmin',
    'WorkflowExecutionAdmin',
    'AgentDefinitionAdmin',
    'AgentTemplateAdmin',
    'ToolExecutionAdmin',
    'ApprovalLogAdmin',
    'ToolsetConfigurationAdmin',
]
