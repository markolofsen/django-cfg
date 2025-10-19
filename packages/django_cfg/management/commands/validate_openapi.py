"""
Alias for validate_openapi command.

This is an alias that delegates to the actual implementation in
django_cfg.modules.django_client.management.commands.validate_openapi

For backward compatibility and discoverability.
"""

from django_cfg.modules.django_client.management.commands.validate_openapi import (
    Command,  # noqa: F401
)
