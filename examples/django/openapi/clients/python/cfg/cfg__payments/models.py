from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import Currency.currency_type, PatchedPaymentRequest.provider, PatchedPaymentRequest.status, PatchedSubscriptionRequest.status, PatchedSubscriptionRequest.tier, Payment.provider, Payment.status, PaymentCreate.currency_code, PaymentCreate.provider, PaymentCreateRequest.currency_code, PaymentCreateRequest.provider, PaymentRequest.provider, PaymentRequest.status, Subscription.status, Subscription.tier, SubscriptionRequest.status, SubscriptionRequest.tier, Transaction.transaction_type


class PaginatedAPIKeyListList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class APIKeyCreateRequest(BaseModel):
    """API key creation serializer with service integration. Creates new API keys
and returns the full key value (only once).

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(description='Descriptive name for the API key', min_length=1, max_length=100)
    expires_in_days: int | None = Field(None, description='Expiration in days (optional, null for no expiration)', ge=1.0, le=365.0)



class APIKeyCreate(BaseModel):
    """API key creation serializer with service integration. Creates new API keys
and returns the full key value (only once).

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(description='Descriptive name for the API key', max_length=100)
    expires_in_days: int | None = Field(None, description='Expiration in days (optional, null for no expiration)', ge=1.0, le=365.0)



class APIKeyDetail(BaseModel):
    """Complete API key serializer with full details. Used for API key detail views
(no key value for security).

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = Field(description='Unique identifier for this record')
    user: str = ...
    name: str = Field(description='Human-readable name for this API key')
    key_preview: str = ...
    is_active: bool = Field(description='Whether this API key is active')
    is_expired: bool = ...
    is_valid: bool = ...
    days_until_expiry: int = ...
    total_requests: int = Field(description='Total number of requests made with this key')
    last_used_at: str | None = Field(description='When this API key was last used')
    expires_at: str | None = Field(description='When this API key expires (null = never expires)')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class APIKeyUpdateRequest(BaseModel):
    """API key update serializer for modifying API key properties. Allows updating
name and active status only.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(description='Human-readable name for this API key', min_length=1, max_length=100)
    is_active: bool = Field(None, description='Whether this API key is active')



class APIKeyUpdate(BaseModel):
    """API key update serializer for modifying API key properties. Allows updating
name and active status only.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(description='Human-readable name for this API key', max_length=100)
    is_active: bool = Field(None, description='Whether this API key is active')



class PatchedAPIKeyUpdateRequest(BaseModel):
    """API key update serializer for modifying API key properties. Allows updating
name and active status only.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    name: str = Field(None, description='Human-readable name for this API key', min_length=1, max_length=100)
    is_active: bool = Field(None, description='Whether this API key is active')



class APIKeyValidationRequest(BaseModel):
    """API key validation serializer. Validates API key and returns key
information.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    key: str = Field(description='API key to validate', min_length=32, max_length=64)



class APIKeyValidationResponse(BaseModel):
    """API key validation response serializer. Defines the structure of API key
validation response for OpenAPI schema.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Whether the validation was successful')
    valid: bool = Field(description='Whether the API key is valid')
    api_key: dict[str, Any] = ...
    message: str = Field(description='Validation message')
    error: str = Field(None, description='Error message if validation failed')
    error_code: str = Field(None, description='Error code if validation failed')



class PaginatedUserBalanceList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class UserBalance(BaseModel):
    """User balance serializer with computed fields. Provides balance information
with display helpers.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    user: str = ...
    balance_usd: float = Field(description='Current balance in USD (float for performance)')
    balance_display: str = Field(description='Formatted balance display.')
    is_empty: bool = Field(description='Check if balance is zero.')
    has_transactions: bool = Field(description='Check if user has any transactions.')
    created_at: str = ...
    updated_at: str = ...



class PaginatedCurrencyListList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Currency(BaseModel):
    """Complete currency serializer with full details. Used for currency
information and management.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    code: str = Field(description='Currency code (e.g., BTC, USD, ETH)')
    name: str = Field(description='Full currency name (e.g., Bitcoin, US Dollar)')
    symbol: str = Field(description='Currency symbol (e.g., $, ₿, Ξ)')
    currency_type: Currency.currency_type = Field(description='Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency')
    type_display: str = ...
    decimal_places: int = Field(description='Number of decimal places for this currency')
    is_active: bool = Field(description='Whether this currency is available for payments')
    is_crypto: bool = Field(description='Check if this is a cryptocurrency.')
    is_fiat: bool = Field(description='Check if this is a fiat currency.')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class PaginatedEndpointGroupList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class EndpointGroup(BaseModel):
    """Endpoint group serializer for API access management. Used for subscription
endpoint group configuration.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    name: str = Field(description="Endpoint group name (e.g., 'Payment API', 'Balance API')")
    description: str = Field(description='Description of what this endpoint group provides')
    is_enabled: bool = Field(description='Whether this endpoint group is available')
    created_at: str = ...
    updated_at: str = ...



class Payment(BaseModel):
    """Complete payment serializer with full details. Used for detail views and
updates.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = Field(description='Unique identifier for this record')
    user: str = ...
    amount_usd: float = Field(description='Payment amount in USD (float for performance)', ge=1.0, le=50000.0)
    currency: int = Field(description='Payment currency')
    network: int | None = Field(None, description='Blockchain network (for crypto payments)')
    provider: Payment.provider = Field(None, description='Payment provider\n\n* `nowpayments` - NowPayments')
    status: Payment.status = Field(None, description='Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded')
    status_display: str = ...
    amount_display: str = Field(description='Get formatted amount display.')
    provider_payment_id: str | None = Field(description="Provider's payment ID")
    payment_url: str | None = Field(description='Payment page URL')
    pay_address: str | None = Field(description='Cryptocurrency payment address')
    callback_url: str | None = Field(None, description='Success callback URL', max_length=200)
    cancel_url: str | None = Field(None, description='Cancellation URL', max_length=200)
    description: str = Field(None, description='Payment description')
    transaction_hash: str | None = Field(description='Blockchain transaction hash')
    confirmations_count: int = Field(description='Number of blockchain confirmations')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')
    expires_at: str | None = Field(None, description='When this payment expires')
    completed_at: str | None = Field(description='When this payment was completed')
    is_pending: bool = Field(description='Check if payment is pending.')
    is_completed: bool = Field(description='Check if payment is completed.')
    is_failed: bool = Field(description='Check if payment is failed.')
    is_expired: bool = Field(description='Check if payment is expired.')



class PaginatedNetworkList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Network(BaseModel):
    """Network serializer for blockchain networks. Used for network information and
selection.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    currency: dict[str, Any] = ...
    name: str = Field(description='Network name (e.g., Ethereum, Bitcoin, Polygon)')
    code: str = Field(description='Network code (e.g., ETH, BTC, MATIC)')
    is_active: bool = Field(description='Whether this network is available for payments')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class APIKeysOverview(BaseModel):
    """API keys overview metrics

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    total_keys: int = Field(description='Total number of API keys')
    active_keys: int = Field(description='Number of active API keys')
    expired_keys: int = Field(description='Number of expired API keys')
    total_requests: int = Field(description='Total requests across all keys')
    last_used_at: str | None = Field(description='When any key was last used')
    most_used_key_name: str | None = Field(description='Name of most used API key')
    most_used_key_requests: int = Field(description='Requests count for most used key')
    expiring_soon_count: int = Field(description='Number of keys expiring within 7 days')



class BalanceOverview(BaseModel):
    """User balance overview metrics

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    current_balance: float = Field(description='Current balance in USD')
    balance_display: str = Field(description='Formatted balance display')
    total_deposited: float = Field(description='Total amount deposited (lifetime)')
    total_spent: float = Field(description='Total amount spent (lifetime)')
    last_transaction_at: str | None = Field(description='Last transaction timestamp')
    has_transactions: bool = Field(description='Whether user has any transactions')
    is_empty: bool = Field(description='Whether balance is zero')



class PaymentsChartResponse(BaseModel):
    """Complete chart response for payments analytics

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    series: list[dict[str, Any]] = Field(description='Chart series data')
    period: str = Field(description='Time period')
    total_amount: float = Field(description='Total amount for period')
    total_payments: int = Field(description='Total payments for period')
    success_rate: float = Field(description='Success rate for period')



class PaymentsMetrics(BaseModel):
    """Complete payments dashboard metrics

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    balance: dict[str, Any] = ...
    subscription: dict[str, Any] = ...
    api_keys: dict[str, Any] = ...
    payments: dict[str, Any] = ...



class PaymentsDashboardOverview(BaseModel):
    """Complete payments dashboard overview response

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    metrics: dict[str, Any] = ...
    recent_payments: list[dict[str, Any]] = Field(description='Recent payments')
    recent_transactions: list[dict[str, Any]] = Field(description='Recent transactions')
    chart_data: dict[str, Any] = ...



class PaymentAnalyticsResponse(BaseModel):
    """Payment analytics response with currency and provider breakdown

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    currency_analytics: list[dict[str, Any]] = Field(description='Analytics by currency')
    provider_analytics: list[dict[str, Any]] = Field(description='Analytics by provider')



class PaginatedRecentPaymentList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class PaginatedRecentTransactionList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class SubscriptionOverview(BaseModel):
    """Current subscription overview

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    tier: str = Field(description='Subscription tier')
    tier_display: str = Field(description='Human-readable tier name')
    status: str = Field(description='Subscription status')
    status_display: str = Field(description='Human-readable status')
    status_color: str = Field(description='Color for status display')
    is_active: bool = Field(description='Whether subscription is active')
    is_expired: bool = Field(description='Whether subscription is expired')
    days_remaining: int = Field(description='Days until expiration')
    requests_per_hour: int = Field(description='Hourly request limit')
    requests_per_day: int = Field(description='Daily request limit')
    total_requests: int = Field(description='Total requests made')
    usage_percentage: float = Field(description='Usage percentage for current period')
    monthly_cost_usd: float = Field(description='Monthly cost in USD')
    cost_display: str = Field(description='Formatted cost display')
    starts_at: str = Field(description='Subscription start date')
    expires_at: str = Field(description='Subscription expiration date')
    last_request_at: str | None = Field(description='Last API request timestamp')
    endpoint_groups_count: int = Field(description='Number of accessible endpoint groups')
    endpoint_groups: list[str] = Field(description='List of accessible endpoint group names')



class PaginatedPaymentListList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class PaymentCreateRequest(BaseModel):
    """Payment creation serializer with Pydantic integration. Validates input and
delegates to PaymentService.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    amount_usd: float = Field(description='Amount in USD (1.00 - 50,000.00)', ge=1.0, le=50000.0)
    currency_code: PaymentCreateRequest.currency_code = Field(description='Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot')
    provider: PaymentCreateRequest.provider = Field(None, description='Payment provider\n\n* `nowpayments` - NowPayments')
    callback_url: str = Field(None, description='Success callback URL')
    cancel_url: str = Field(None, description='Cancellation URL')
    description: str = Field(None, description='Payment description', max_length=500)
    metadata: str = Field(None, description='Additional metadata')



class PaymentCreate(BaseModel):
    """Payment creation serializer with Pydantic integration. Validates input and
delegates to PaymentService.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    amount_usd: float = Field(description='Amount in USD (1.00 - 50,000.00)', ge=1.0, le=50000.0)
    currency_code: PaymentCreate.currency_code = Field(description='Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot')
    provider: PaymentCreate.provider = Field(None, description='Payment provider\n\n* `nowpayments` - NowPayments')
    callback_url: str = Field(None, description='Success callback URL')
    cancel_url: str = Field(None, description='Cancellation URL')
    description: str = Field(None, description='Payment description', max_length=500)
    metadata: str = Field(None, description='Additional metadata')



class PaymentRequest(BaseModel):
    """Complete payment serializer with full details. Used for detail views and
updates.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    amount_usd: float = Field(description='Payment amount in USD (float for performance)', ge=1.0, le=50000.0)
    currency: int = Field(description='Payment currency')
    network: int | None = Field(None, description='Blockchain network (for crypto payments)')
    provider: PaymentRequest.provider = Field(None, description='Payment provider\n\n* `nowpayments` - NowPayments')
    status: PaymentRequest.status = Field(None, description='Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded')
    callback_url: str | None = Field(None, description='Success callback URL', max_length=200)
    cancel_url: str | None = Field(None, description='Cancellation URL', max_length=200)
    description: str = Field(None, description='Payment description')
    expires_at: str | None = Field(None, description='When this payment expires')



class PatchedPaymentRequest(BaseModel):
    """Complete payment serializer with full details. Used for detail views and
updates.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    amount_usd: float = Field(None, description='Payment amount in USD (float for performance)', ge=1.0, le=50000.0)
    currency: int = Field(None, description='Payment currency')
    network: int | None = Field(None, description='Blockchain network (for crypto payments)')
    provider: PatchedPaymentRequest.provider = Field(None, description='Payment provider\n\n* `nowpayments` - NowPayments')
    status: PatchedPaymentRequest.status = Field(None, description='Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded')
    callback_url: str | None = Field(None, description='Success callback URL', max_length=200)
    cancel_url: str | None = Field(None, description='Cancellation URL', max_length=200)
    description: str = Field(None, description='Payment description')
    expires_at: str | None = Field(None, description='When this payment expires')



class PaginatedProviderCurrencyList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class ProviderCurrency(BaseModel):
    """Provider currency serializer for provider-specific currency info. Used for
provider currency management and rates.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    currency: dict[str, Any] = ...
    network: dict[str, Any] = ...
    provider: str = Field(description='Payment provider name (e.g., nowpayments)')
    provider_currency_code: str = Field(description='Currency code as used by the provider')
    provider_min_amount_usd: float = Field(description='Get minimum amount from provider configuration.')
    provider_max_amount_usd: float = Field(description='Get maximum amount from provider configuration.')
    provider_fee_percentage: float = Field(description='Get fee percentage from provider configuration.')
    provider_fixed_fee_usd: float = Field(description='Get fixed fee from provider configuration.')
    is_enabled: bool = Field(description='Whether this currency is enabled for this provider')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class PaginatedSubscriptionListList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class SubscriptionCreateRequest(BaseModel):
    """Subscription creation serializer with service integration. Validates input
and delegates to SubscriptionService.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    tariff_id: int = Field(description='Tariff ID for the subscription', ge=1.0)
    endpoint_group_id: int | None = Field(None, description='Endpoint group ID (optional)', ge=1.0)
    duration_days: int = Field(None, description='Subscription duration in days', ge=1.0, le=365.0)



class SubscriptionCreate(BaseModel):
    """Subscription creation serializer with service integration. Validates input
and delegates to SubscriptionService.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    tariff_id: int = Field(description='Tariff ID for the subscription', ge=1.0)
    endpoint_group_id: int | None = Field(None, description='Endpoint group ID (optional)', ge=1.0)
    duration_days: int = Field(None, description='Subscription duration in days', ge=1.0, le=365.0)



class Subscription(BaseModel):
    """Complete subscription serializer with full details. Used for subscription
detail views and updates.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = Field(description='Unique identifier for this record')
    user: str = ...
    tariff: dict[str, Any] = ...
    endpoint_group: dict[str, Any] = ...
    status: Subscription.status = Field(None, description='Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired')
    status_display: str = ...
    status_color: str = Field(description='Get color for status display.')
    tier: Subscription.tier = Field(None, description='Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier')
    total_requests: int = Field(description='Total API requests made with this subscription')
    usage_percentage: float = Field(description='Get usage percentage for current period.')
    last_request_at: str | None = Field(description='When the last API request was made')
    expires_at: str = Field(description='When this subscription expires')
    is_active: bool = Field(description='Check if subscription is active and not expired.')
    is_expired: bool = Field(description='Check if subscription is expired.')
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class SubscriptionRequest(BaseModel):
    """Complete subscription serializer with full details. Used for subscription
detail views and updates.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    status: SubscriptionRequest.status = Field(None, description='Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired')
    tier: SubscriptionRequest.tier = Field(None, description='Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier')
    expires_at: str = Field(description='When this subscription expires')



class PatchedSubscriptionRequest(BaseModel):
    """Complete subscription serializer with full details. Used for subscription
detail views and updates.

Request model (no read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    status: PatchedSubscriptionRequest.status = Field(None, description='Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired')
    tier: PatchedSubscriptionRequest.tier = Field(None, description='Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier')
    expires_at: str = Field(None, description='When this subscription expires')



class PaginatedTariffList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Tariff(BaseModel):
    """Tariff serializer for subscription pricing. Used for tariff information and
selection.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: int = ...
    name: str = Field(description="Tariff name (e.g., 'Free', 'Basic', 'Pro')")
    description: str = Field(description='Detailed description of what this tariff includes')
    monthly_price_usd: float = Field(description='Monthly price in USD')
    requests_per_month: int = Field(description='API requests allowed per month')
    requests_per_hour: int = Field(description='API requests allowed per hour')
    is_active: bool = Field(description='Whether this tariff is available for new subscriptions')
    endpoint_groups: list[dict[str, Any]] = ...
    endpoint_groups_count: int = ...
    created_at: str = Field(description='When this record was created')
    updated_at: str = Field(description='When this record was last updated')



class PaginatedTransactionList(BaseModel):
    """
Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
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
    results: list[dict[str, Any]] = Field(description='Array of items for current page')



class Transaction(BaseModel):
    """Transaction serializer with full details. Used for transaction history and
details.

Response model (includes read-only fields)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    id: str = Field(description='Unique identifier for this record')
    user: str = ...
    amount_usd: float = Field(description='Transaction amount in USD (positive=credit, negative=debit)')
    amount_display: str = ...
    transaction_type: Transaction.transaction_type = Field(description='Type of transaction\n\n* `deposit` - Deposit\n* `withdrawal` - Withdrawal\n* `payment` - Payment\n* `refund` - Refund\n* `fee` - Fee\n* `bonus` - Bonus\n* `adjustment` - Adjustment')
    type_color: str = ...
    description: str = Field(description='Transaction description')
    payment_id: str | None = Field(description='Related payment ID (if applicable)')
    metadata: str = Field(description='Additional transaction metadata')
    is_credit: bool = ...
    is_debit: bool = ...
    created_at: str = Field(description='When this record was created')



