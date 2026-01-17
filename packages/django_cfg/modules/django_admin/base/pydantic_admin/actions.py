"""
Action registration for admin.

Registers bulk actions and changelist actions with Unfold decorator support.
"""

import logging
from typing import TYPE_CHECKING

from unfold.decorators import action as unfold_action

if TYPE_CHECKING:
    from ...config import AdminConfig

logger = logging.getLogger(__name__)


def register_actions(cls, config: 'AdminConfig'):
    """
    Register actions from ActionConfig with Unfold decorator support.

    Supports two types of actions:
    - bulk: Traditional bulk actions (require selected items)
    - changelist: Buttons above the listing (no selection required)

    Args:
        cls: The admin class to add actions to
        config: AdminConfig instance
    """
    bulk_action_functions = []
    changelist_action_functions = []

    for action_config in config.actions:
        # Get handler function
        handler = action_config.get_handler_function()

        # Build decorator kwargs
        decorator_kwargs = {
            'description': action_config.description,
        }

        # Add URL path for changelist actions
        if action_config.action_type == 'changelist':
            url_path = action_config.url_path or action_config.name.replace('_', '-')
            decorator_kwargs['url_path'] = url_path

        # Add variant (Unfold uses ActionVariant enum, but we accept strings)
        if action_config.variant and action_config.variant != 'default':
            decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
            decorator_kwargs['attrs']['class'] = f'button-{action_config.variant}'

        # Add icon if specified
        if action_config.icon:
            decorator_kwargs['icon'] = action_config.icon

        # Add confirmation if enabled
        if action_config.confirmation:
            decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
            decorator_kwargs['attrs']['data-confirm'] = 'Are you sure you want to perform this action?'

        # Add permissions if specified
        if action_config.permissions:
            decorator_kwargs['permissions'] = action_config.permissions

        # Apply Unfold decorator
        decorated_handler = unfold_action(**decorator_kwargs)(handler)

        # Store for later registration
        action_name = action_config.name
        setattr(cls, action_name, decorated_handler)

        # Add to appropriate list
        if action_config.action_type == 'changelist':
            changelist_action_functions.append(action_name)
        else:  # bulk
            bulk_action_functions.append(action_name)

    # Set bulk actions list
    if bulk_action_functions:
        if hasattr(cls, 'actions') and cls.actions:
            cls.actions = list(cls.actions) + bulk_action_functions
        else:
            cls.actions = bulk_action_functions

    # Set changelist actions list (Unfold's actions_list)
    if changelist_action_functions:
        if hasattr(cls, 'actions_list') and cls.actions_list:
            cls.actions_list = list(cls.actions_list) + changelist_action_functions
        else:
            cls.actions_list = changelist_action_functions
