"""Type aliases for common patterns."""

from typing import Literal

# Environment types
EnvironmentString = Literal["development", "production", "test"]

# Django types
DatabaseAlias = str
AppLabel = str
MiddlewareLabel = str

# URL types
UrlPath = str
UrlPattern = str
