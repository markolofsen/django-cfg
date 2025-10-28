from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import PaymentDetailStatus, PaymentListStatus


class Balance(BaseModel):
    """
    User balance serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    balance_usd: Any = Field(description='Current balance in USD', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    balance_display: Any = ...
    total_deposited: Any = Field(description='Total amount deposited (lifetime)', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    total_withdrawn: Any = Field(description='Total amount withdrawn (lifetime)', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    last_transaction_at: Any | None = Field(description='When the last transaction occurred')



class PaginatedPaymentListList(BaseModel):
    """
    
    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    count: int = Field(description='Total number of items across all pages')
    page: int = Field(description='Current page number (1-based)')
    pages: int = Field(description='Total number of pages')
    page_size: int = Field(description='Number of items per page')
    has_next: bool = Field(description='Whether there is a next page')
    has_previous: bool = Field(description='Whether there is a previous page')
    next_page: int | None = Field(None, description='Next page number (null if no next page)')
    previous_page: int | None = Field(None, description='Previous page number (null if no previous page)')
    results: list[Any] = Field(description='Array of items for current page')



class PaymentDetail(BaseModel):
    """
    Detailed payment information.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: Any = Field(description='Unique identifier for this record')
    internal_payment_id: Any = Field(description='Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)')
    amount_usd: Any = Field(description='Payment amount in USD', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    currency_code: Any = ...
    currency_name: Any = ...
    currency_token: Any = ...
    currency_network: Any = ...
    pay_amount: Any | None = Field(description='Amount to pay in cryptocurrency', pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    actual_amount: Any | None = Field(description='Actual amount received in cryptocurrency', pattern='^-?\\d{0,12}(?:\\.\\d{0,8})?$')
    actual_amount_usd: Any | None = Field(description='Actual amount received in USD', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    status: PaymentDetailStatus = Field(description='Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled')
    status_display: Any = ...
    pay_address: Any | None = Field(description='Cryptocurrency payment address')
    qr_code_url: Any | None = Field(description='Get QR code URL.')
    payment_url: Any | None = Field(description='Payment page URL (if provided by provider)')
    transaction_hash: Any | None = Field(description='Blockchain transaction hash')
    explorer_link: Any | None = Field(description='Get blockchain explorer link.')
    confirmations_count: int = Field(description='Number of blockchain confirmations')
    expires_at: Any | None = Field(description='When this payment expires (typically 30 minutes)')
    completed_at: Any | None = Field(description='When this payment was completed')
    created_at: Any = Field(description='When this record was created')
    is_completed: bool = ...
    is_failed: bool = ...
    is_expired: bool = ...
    description: Any = Field(description='Payment description')



class PaymentList(BaseModel):
    """
    Payment list item (lighter than detail).

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    id: Any = Field(description='Unique identifier for this record')
    internal_payment_id: Any = Field(description='Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)')
    amount_usd: Any = Field(description='Payment amount in USD', pattern='^-?\\d{0,8}(?:\\.\\d{0,2})?$')
    currency_code: Any = ...
    currency_token: Any = ...
    status: PaymentListStatus = Field(description='Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled')
    status_display: Any = ...
    created_at: Any = Field(description='When this record was created')
    completed_at: Any | None = Field(description='When this payment was completed')



