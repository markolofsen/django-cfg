"""
Pydantic models for LLM balance monitoring.

Type-safe response models for balance checking.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    """
    Standard balance response model.

    All providers return this consistent format.
    """

    balance: Optional[float] = Field(
        default=None,
        description="Current balance in USD (None if not available)"
    )

    currency: str = Field(
        default="usd",
        description="Currency code (always 'usd')"
    )

    usage: Optional[float] = Field(
        default=None,
        description="Total usage in USD (if available)"
    )

    limit: Optional[float] = Field(
        default=None,
        description="Credit limit in USD (if set)"
    )

    status: Optional[Literal["valid", "invalid", "error", "unavailable"]] = Field(
        default=None,
        description="API key validation status (for providers without balance API)"
    )

    note: Optional[str] = Field(
        default=None,
        description="Additional information about the balance"
    )

    error: Optional[str] = Field(
        default=None,
        description="Error message if request failed"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "balance": 15.50,
                "currency": "usd",
                "usage": 134.50,
                "limit": 150.00,
                "status": "valid",
                "note": "Remaining credit balance"
            }
        }
