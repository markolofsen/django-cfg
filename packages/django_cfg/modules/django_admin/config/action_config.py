"""
Action configuration for declarative admin.
"""

from typing import Callable, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionConfig(BaseModel):
    """
    Admin action configuration.

    Defines custom actions for admin list view.

    Action Types:
    - bulk: Traditional bulk actions (require selected items in queryset)
    - changelist: Buttons above the listing (no selection required)

    Handler can be either:
    - String: Python path to action handler function (e.g., "myapp.actions.my_action")
    - Callable: Direct reference to action function (e.g., my_action)

    Handler Signatures:
    - Bulk actions: handler(modeladmin, request, queryset)
    - Changelist actions: handler(modeladmin, request)
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid", arbitrary_types_allowed=True)

    name: str = Field(..., description="Action function name")
    description: str = Field(..., description="Action description shown in UI")
    action_type: Literal["bulk", "changelist"] = Field(
        "bulk",
        description="Type of action: 'bulk' (requires selection) or 'changelist' (button above listing)"
    )
    variant: str = Field("default", description="Button variant: default, success, warning, danger, primary, info")
    icon: Optional[str] = Field(None, description="Material icon name")
    url_path: Optional[str] = Field(None, description="Custom URL path for changelist actions (auto-generated if not provided)")
    confirmation: bool = Field(False, description="Require confirmation before execution")
    handler: Union[str, Callable] = Field(..., description="Python path to action handler function or callable")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")

    def get_handler_function(self):
        """Import and return the handler function."""
        # If handler is already a callable, return it directly
        if callable(self.handler):
            return self.handler

        # Otherwise import from string path
        import importlib
        module_path, function_name = self.handler.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, function_name)
