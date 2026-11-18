"""
Registration of ``AdminConfig.actions`` on a ``PydanticAdmin`` class.

The decorator itself lives in ``django_cfg.modules.django_admin.actions``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...actions import DEFAULT_CONFIRMATION, action

if TYPE_CHECKING:
    from ...config import AdminConfig

logger = logging.getLogger(__name__)


def register_actions(cls, config: 'AdminConfig'):
    """
    Register actions from ``AdminConfig.actions`` on the admin class.

    ``action_type="bulk"`` goes to ``cls.actions``; ``"changelist"`` to
    ``cls.actions_list`` (a button above the list).
    """
    bulk_action_functions = []
    changelist_action_functions = []

    for action_config in config.actions:
        handler = action_config.get_handler_function()

        url_path = None
        if action_config.action_type == 'changelist':
            url_path = action_config.url_path or action_config.name.replace('_', '-')

        decorated_handler = action(
            description=action_config.description,
            permissions=action_config.permissions or None,
            url_path=url_path,
            icon=action_config.icon,
            variant=action_config.variant,
            confirm=DEFAULT_CONFIRMATION if action_config.confirmation else None,
            method=action_config.method,
        )(handler)

        action_name = action_config.name
        setattr(cls, action_name, decorated_handler)

        if action_config.action_type == 'changelist':
            changelist_action_functions.append(action_name)
        else:
            bulk_action_functions.append(action_name)

    if bulk_action_functions:
        existing = list(cls.actions or []) if getattr(cls, 'actions', None) else []
        cls.actions = existing + bulk_action_functions

    if changelist_action_functions:
        existing = list(getattr(cls, 'actions_list', None) or [])
        cls.actions_list = existing + changelist_action_functions
