"""
Pydantic Configuration Models for Centrifugo Bridge.

Type-safe, validated configuration using Pydantic v2.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Callable, Any, Dict


class ChannelConfig(BaseModel):
    """
    Configuration for a single gRPC field → Centrifugo channel mapping.

    Example:
        ```python
        ChannelConfig(
            template='bot#{bot_id}#heartbeat',
            rate_limit=0.1,
            critical=False
        )
        ```

    Attributes:
        template: Channel name template with {variable} placeholders
        rate_limit: Minimum seconds between publishes (None = no limit)
        critical: Critical events bypass rate limiting
        enabled: Enable/disable this specific channel
        metadata: Additional metadata included in published data
    """

    template: str = Field(
        ...,
        description="Channel template with {variable} placeholders",
        examples=["bot#{bot_id}#heartbeat", "user#{user_id}#notifications"]
    )

    rate_limit: Optional[float] = Field(
        None,
        description="Minimum seconds between publishes (None = no limit)",
        ge=0.0,
        examples=[0.1, 1.0, None]
    )

    critical: bool = Field(
        False,
        description="Critical events bypass rate limiting"
    )

    enabled: bool = Field(
        True,
        description="Enable/disable this channel"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata to include in published data"
    )

    # Optional custom transform function (not serialized)
    transform: Optional[Callable[[str, Any], dict]] = Field(
        None,
        exclude=True,
        description="Custom transform function(field_name, field_value) -> dict"
    )

    @field_validator('template')
    @classmethod
    def validate_template(cls, v: str) -> str:
        """Ensure template contains at least one variable placeholder."""
        if '{' not in v or '}' not in v:
            raise ValueError(
                f"Channel template must contain variables like {{bot_id}}: {v}"
            )
        return v

    model_config = {
        'arbitrary_types_allowed': True,  # Allow Callable types
        'extra': 'forbid',  # Strict validation
    }


class CentrifugoChannels(BaseModel):
    """
    Base configuration model for Centrifugo channel mappings.

    Inherit from this class to define your channel mappings:

    Example:
        ```python
        class BotChannels(CentrifugoChannels):
            heartbeat: ChannelConfig = ChannelConfig(
                template='bot#{bot_id}#heartbeat',
                rate_limit=0.1
            )

            status: ChannelConfig = ChannelConfig(
                template='bot#{bot_id}#status',
                critical=True
            )

        class BotStreamingService(Servicer, CentrifugoBridgeMixin):
            centrifugo_channels = BotChannels()
        ```

    Attributes:
        enabled: Enable/disable entire Centrifugo bridge
        default_rate_limit: Default rate limit for all channels
        graceful_degradation: Continue if Centrifugo unavailable
    """

    enabled: bool = Field(
        True,
        description="Enable/disable entire Centrifugo bridge"
    )

    default_rate_limit: Optional[float] = Field(
        None,
        description="Default rate limit for all channels (can be overridden per channel)",
        ge=0.0
    )

    graceful_degradation: bool = Field(
        True,
        description="Continue service operation if Centrifugo is unavailable"
    )

    def get_channel_mappings(self) -> Dict[str, ChannelConfig]:
        """
        Extract all ChannelConfig fields as dictionary.

        Returns:
            Dict mapping field names to ChannelConfig instances

        Example:
            ```python
            channels = BotChannels()
            mappings = channels.get_channel_mappings()
            # {'heartbeat': ChannelConfig(...), 'status': ChannelConfig(...)}
            ```
        """
        mappings = {}

        for field_name, field_info in self.model_fields.items():
            # Skip base config fields
            if field_name in ('enabled', 'default_rate_limit', 'graceful_degradation'):
                continue

            # Get field value
            field_value = getattr(self, field_name, None)

            # Check if it's a ChannelConfig
            if isinstance(field_value, ChannelConfig):
                mappings[field_name] = field_value

        return mappings

    model_config = {
        'extra': 'allow',  # Allow additional ChannelConfig fields
        'arbitrary_types_allowed': True,
    }


__all__ = [
    "ChannelConfig",
    "CentrifugoChannels",
]
