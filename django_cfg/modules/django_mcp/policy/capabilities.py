"""Restricted profiles admit reviewed implementations, not lookalike tool names."""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.modules.django_mcp.services.context import MCPContext

def reviewed_read_tool(tool: object) -> bool:
    from django_cfg.modules.django_mcp.tools.model_tools import QueryModelTool, GetObjectTool
    from django_cfg.modules.django_mcp.tools.introspection import ListAppsTool, GetModelSchemaTool
    from django_cfg.modules.django_mcp.agent.tools import QueryModelTool as ExtendedQueryModelTool
    return type(tool) in {QueryModelTool, GetObjectTool, ListAppsTool, GetModelSchemaTool, ExtendedQueryModelTool}


def unhandled_projection(context: "MCPContext", app_label: str, model_name: str) -> bool:
    if getattr(getattr(context, "profile", None), "restricted_reads", False):
        return True
    grant = context.config.get_model_config(app_label, model_name)
    return grant is not None and grant.read_policy is not None
