class NotionError(Exception):
    """Base class of django_notion errors."""


class NotionConfigError(NotionError):
    """Missing or wrong configuration (token, target, data source). Messages never contain the token."""
