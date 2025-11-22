"""Status badges field configuration for multiple conditional badges."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .base import FieldConfig


class BadgeRule(BaseModel):
    """Single badge rendering rule.

    Badge is shown if condition_field evaluates to condition_value.
    """

    condition_field: str = Field(
        ...,
        description="Model field name to check (e.g., 'is_bot', 'is_verified')"
    )
    condition_value: Any = Field(
        True,
        description="Value that triggers badge display (default: True for boolean fields)"
    )
    label: str = Field(
        ...,
        description="Badge text to display"
    )
    variant: Literal["primary", "secondary", "success", "danger", "warning", "info"] = Field(
        ...,
        description="Badge color variant"
    )
    icon: Optional[str] = Field(
        None,
        description="Material icon name (from Icons class)"
    )


class StatusBadgesField(FieldConfig):
    """
    Display multiple conditional badges based on model field values.

    Perfect for status flags like is_bot, is_verified, is_premium, etc.
    Each badge is shown only if its condition field matches the expected value.

    Examples:
        # User status badges
        StatusBadgesField(
            name="status_badges",
            title="Status",
            badge_rules=[
                BadgeRule(
                    condition_field="is_bot",
                    condition_value=True,
                    label="Bot",
                    variant="info",
                    icon=Icons.SMART_TOY
                ),
                BadgeRule(
                    condition_field="is_verified",
                    condition_value=True,
                    label="Verified",
                    variant="success",
                    icon=Icons.VERIFIED
                ),
                BadgeRule(
                    condition_field="is_premium",
                    condition_value=True,
                    label="Premium",
                    variant="warning",
                    icon=Icons.STAR
                ),
                BadgeRule(
                    condition_field="is_scam",
                    condition_value=True,
                    label="Scam",
                    variant="danger",
                    icon=Icons.WARNING
                ),
            ],
            empty_text="Regular",  # Shown when no badges match
            empty_variant="secondary"
        )

        # Payment method badges
        StatusBadgesField(
            name="payment_methods",
            title="Accepted",
            badge_rules=[
                BadgeRule(
                    condition_field="accepts_credit_card",
                    condition_value=True,
                    label="Credit Card",
                    variant="success",
                    icon=Icons.CREDIT_CARD
                ),
                BadgeRule(
                    condition_field="accepts_paypal",
                    condition_value=True,
                    label="PayPal",
                    variant="primary"
                ),
            ]
        )
    """

    ui_widget: Literal["status_badges"] = "status_badges"

    badge_rules: List[BadgeRule] = Field(
        ...,
        description="List of badge rules - each rule defines a conditional badge"
    )

    # Empty state configuration
    empty_text: Optional[str] = Field(
        None,
        description="Text to show when no badges match (e.g., 'Regular', 'None')"
    )
    empty_variant: str = Field(
        "secondary",
        description="Badge variant for empty state"
    )

    # Layout options
    separator: str = Field(
        " ",
        description="Separator between badges (default: single space)"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract status badges widget configuration."""
        config = super().get_widget_config()

        # Convert Pydantic models to dicts
        config['badge_rules'] = [
            {
                'condition_field': rule.condition_field,
                'condition_value': rule.condition_value,
                'label': rule.label,
                'variant': rule.variant,
                'icon': rule.icon,
            }
            for rule in self.badge_rules
        ]

        config['separator'] = self.separator

        if self.empty_text is not None:
            config['empty_text'] = self.empty_text
            config['empty_variant'] = self.empty_variant

        return config
