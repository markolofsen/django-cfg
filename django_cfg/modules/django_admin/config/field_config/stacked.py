"""Stacked field configuration for composite columns."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .base import FieldConfig


class RowItem(BaseModel):
    """
    Single item in a stacked row.

    Allows any widget type with its configuration.
    """

    field: str = Field(..., description="Model field name to display")
    widget: str = Field("text", description="Widget type: text, badge, datetime_relative, etc.")

    # Common styling
    bold: bool = Field(False, description="Use bold text")
    muted: bool = Field(False, description="Use muted/secondary text color")
    monospace: bool = Field(False, description="Use monospace font")

    # Text options
    prefix: Optional[str] = Field(None, description="Text prefix (e.g., 'ID: ')")
    suffix: Optional[str] = Field(None, description="Text suffix (e.g., ' beds')")
    truncate: Optional[int] = Field(None, description="Truncate text to N chars")

    # Badge options
    label_map: Optional[Dict[Any, str]] = Field(
        None, description="Map values to badge variants"
    )
    variant: Optional[str] = Field(None, description="Badge variant")
    true_label: Optional[str] = Field(None, description="Label for True value (for boolean badges)")
    false_label: Optional[str] = Field(None, description="Label for False value (for boolean badges)")

    # DateTime options
    show_relative: bool = Field(False, description="Show relative time")

    # Decimal options
    decimal_places: int = Field(2, description="Decimal places for numbers")

    # Icon
    icon: Optional[str] = Field(None, description="Material icon name")

    # Conditional display
    hide_if_empty: bool = Field(True, description="Hide this item if value is empty")

    # Extra config
    config: Optional[Dict[str, Any]] = Field(
        None, description="Extra widget-specific config"
    )


# Row can be single item or list of items (inline)
RowDef = Union[RowItem, List[RowItem]]


class StackedField(FieldConfig):
    """
    Composite field that stacks multiple data points in one column.

    Perfect for compact admin layouts where you want to show related data
    together without adding more columns.

    Examples:
        # Simple stacked info
        StackedField(
            name="info",
            title="Info",
            rows=[
                RowItem(field="title", bold=True),
                RowItem(field="status", widget="badge", label_map={"active": "success"}),
            ]
        )

        # With inline items (horizontal)
        StackedField(
            name="specs",
            title="Specs",
            rows=[
                RowItem(field="brand", bold=True),
                [  # Inline row
                    RowItem(field="bedrooms", suffix=" beds"),
                    RowItem(field="bathrooms", suffix=" baths"),
                ],
                RowItem(field="created_at", widget="datetime_relative", muted=True),
            ]
        )

        # Property listing compact view
        StackedField(
            name="listing_info",
            title="Listing",
            rows=[
                RowItem(field="title", bold=True, truncate=40),
                [
                    RowItem(field="listing_type", widget="badge"),
                    RowItem(field="status", widget="badge"),
                ],
                RowItem(field="price", widget="money_field"),
            ]
        )
    """

    ui_widget: Literal["stacked"] = "stacked"

    rows: List[RowDef] = Field(
        ...,
        description="List of rows. Each row is a RowItem or list of RowItems for inline display."
    )

    # Layout options
    gap: str = Field("0.25rem", description="Gap between rows (CSS)")
    inline_gap: str = Field("0.5rem", description="Gap between inline items (CSS)")
    align: Literal["left", "center", "right"] = Field(
        "left", description="Text alignment"
    )

    # Container options
    min_width: Optional[str] = Field(None, description="Minimum width (CSS)")
    max_width: Optional[str] = Field("300px", description="Maximum width (CSS)")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract stacked widget configuration."""
        config = super().get_widget_config()

        # Convert rows to serializable format
        serialized_rows = []
        for row in self.rows:
            if isinstance(row, list):
                # Inline row
                serialized_rows.append([item.model_dump() for item in row])
            else:
                # Single item row
                serialized_rows.append(row.model_dump())

        config["rows"] = serialized_rows
        config["gap"] = self.gap
        config["inline_gap"] = self.inline_gap
        config["align"] = self.align
        if self.min_width:
            config["min_width"] = self.min_width
        if self.max_width:
            config["max_width"] = self.max_width

        return config
