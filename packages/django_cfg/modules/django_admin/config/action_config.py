"""
Action configuration for declarative admin.
"""

from typing import Callable, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionConfig(BaseModel):
    """
    Admin action configuration.

    Defines custom actions for admin list view.
    Handler can be either:
    - String: Python path to action handler function (e.g., "myapp.actions.my_action")
    - Callable: Direct reference to action function (e.g., my_action)
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid", arbitrary_types_allowed=True)

    name: str = Field(..., description="Action function name")
    description: str = Field(..., description="Action description shown in UI")
    variant: str = Field("default", description="Button variant: default, success, warning, danger, primary")
    icon: Optional[str] = Field(None, description="Material icon name")
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
