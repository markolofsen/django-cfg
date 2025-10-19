"""
Custom AutoSchema for drf-spectacular with intelligent tagging.

Automatically determines tags based on URL paths for better API organization.
"""

import re

from drf_spectacular.openapi import AutoSchema


class PathBasedAutoSchema(AutoSchema):
    """
    AutoSchema that determines tags from URL paths instead of view names.
    
    For cfg group URLs like /cfg/accounts/..., /cfg/support/..., 
    extracts the app name from the second path segment to create precise tags.
    
    This provides better organization in generated API clients:
    - /cfg/accounts/otp/request/ → tag: "cfg__accounts"
    - /cfg/support/tickets/ → tag: "cfg__support"
    - /cfg/payments/webhooks/ → tag: "cfg__payments"
    
    The TypeScript generator will use these tags to create properly structured folders.
    """

    def get_tags(self):
        """
        Override tag determination to use path-based logic.
        
        Returns:
            List of tags for this operation
        """

        # Get the path
        path = self.path

        # For cfg URLs (/cfg/app_name/...), extract app_name as tag
        # The TypeScript generator will add the group prefix (cfg_) automatically
        cfg_pattern = re.compile(r"^/cfg/([^/]+)/")
        match = cfg_pattern.match(path)
        if match:
            app_name = match.group(1)
            # Return just the app_name (e.g., "support", "accounts", "payments")
            # Generator will create: cfg__support, cfg__accounts, etc.
            return [app_name]

        # For other URLs, use default behavior (usually based on view name)
        return super().get_tags()

