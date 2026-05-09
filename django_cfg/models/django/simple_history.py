"""Simple history configuration model."""

from pydantic import BaseModel, Field


class SimpleHistoryConfig(BaseModel):
    """
    django-simple-history audit log configuration.

    Automatically tracks field-level diffs for any model that adds
    ``history = HistoricalRecords()``. Shows a full diff timeline in
    Django admin via SimpleHistoryAdmin.

    Example:
        ```python
        from django_cfg import DjangoConfig, SimpleHistoryConfig

        class MyConfig(DjangoConfig):
            simple_history: SimpleHistoryConfig = SimpleHistoryConfig()
        ```
    """

    enabled: bool = Field(default=True, description="Enable django-simple-history audit log")

    assert_unicode_username: bool = Field(
        default=False,
        description="Set SIMPLE_HISTORY_ASSERT_UNICODE_USERNAME — raise if history_user has non-unicode name",
    )

    revert_disabled: bool = Field(
        default=False,
        description="Set SIMPLE_HISTORY_REVERT_DISABLED — hide revert button in admin",
    )

    history_change_reason_max_length: int = Field(
        default=100,
        description="Max length of history_change_reason field",
    )


__all__ = ["SimpleHistoryConfig"]
