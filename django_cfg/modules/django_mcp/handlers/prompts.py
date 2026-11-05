"""MCP prompts/list and prompts/get."""

from typing import Any, Dict

from django_cfg.modules.django_mcp.exceptions import MCPError
from django_cfg.modules.django_mcp.registries import prompt_registry
from django_cfg.modules.django_mcp.services.context import MCPContext


class PromptsHandler:
    @staticmethod
    def handle_prompts_list(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        profile = getattr(context, "profile", None)
        return {"prompts": [p.definition() for p in prompt_registry.visible(profile)]}

    @staticmethod
    def handle_prompts_get(params: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        name = params.get("name")
        prompt = prompt_registry.get(name, getattr(context, "profile", None)) if name else None
        if prompt is None:
            raise MCPError(f"Prompt '{name}' not found")
        arguments = params.get("arguments") or {}
        missing = [a["name"] for a in prompt.arguments if a.get("required") and a["name"] not in arguments]
        if missing:
            raise MCPError(f"Missing prompt argument(s): {', '.join(missing)}")
        text = prompt.render(context, arguments)
        return {
            "description": prompt.description,
            "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
        }
