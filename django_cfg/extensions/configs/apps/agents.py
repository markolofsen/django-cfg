"""
Base configuration for agents extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.agents import BaseAgentsSettings

    class AgentsSettings(BaseAgentsSettings):
        pass

    settings = AgentsSettings()
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseAgentsSettings(BaseExtensionSettings):
    """Base settings for agents extension."""

    # === Manifest defaults ===
    name: str = "agents"
    version: str = "1.0.0"
    description: str = "AI Agents orchestration system"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "agents"
    url_prefix: str = "agents"
    url_namespace: str = "agents"

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="AI Agents",
            icon=Icons.SMART_TOY,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Agent Definitions",
                    icon=Icons.SMART_TOY,
                    app="agents",
                    model="agentdefinition",
                ),
                NavigationItem(
                    title="Agent Templates",
                    icon=Icons.DESCRIPTION,
                    app="agents",
                    model="agenttemplate",
                ),
                NavigationItem(
                    title="Agent Executions",
                    icon=Icons.PLAY_ARROW,
                    app="agents",
                    model="agentexecution",
                ),
                NavigationItem(
                    title="Workflow Executions",
                    icon=Icons.AUTORENEW,
                    app="agents",
                    model="workflowexecution",
                ),
                NavigationItem(
                    title="Tool Executions",
                    icon=Icons.BUILD,
                    app="agents",
                    model="toolexecution",
                ),
                NavigationItem(
                    title="Toolset Configurations",
                    icon=Icons.SETTINGS,
                    app="agents",
                    model="toolsetconfiguration",
                ),
            ],
        ),
    )
