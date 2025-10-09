import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedAdminPaymentListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<AdminPaymentList>;
}

/**
 * Serializer for creating payments in admin interface. Uses UniversalPayment
 * only for data creation.
 * 
 * Request model (no read-only fields).
 */
export interface AdminPaymentCreateRequest {
  user: number;
  amount_usd: number;
  /** Provider currency code (e.g., BTC, ZROERC20) */
  currency_code: string;
  provider: string;
  description?: string;
  callback_url?: string;
  cancel_url?: string;
}

/**
 * Serializer for creating payments in admin interface. Uses UniversalPayment
 * only for data creation.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminPaymentCreate {
  user: number;
  amount_usd: number;
  provider: string;
  description?: string;
  callback_url?: string;
  cancel_url?: string;
}

/**
 * Detailed serializer for individual payment in admin interface. Uses
 * UniversalPayment only for data extraction.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminPaymentDetail {
  id: string;
  user: Record<string, any>;
  internal_payment_id: string;
  amount_usd: number;
  actual_amount_usd: number;
  fee_amount_usd: number;
  currency_code: string;
  currency_name: string;
  provider: string;
  provider_display: string;
  status: string;
  status_display: string;
  pay_amount: string;
  pay_address: string;
  payment_url: string;
  transaction_hash: string;
  confirmations_count: number;
  security_nonce: string;
  expires_at: string;
  completed_at: string;
  status_changed_at: string;
  description: string;
  callback_url: string;
  cancel_url: string;
  provider_data: string;
  webhook_data: string;
  created_at: string;
  updated_at: string;
  age: string;
}

/**
 * Serializer for updating payments in admin interface.
 * 
 * Request model (no read-only fields).
 */
export interface AdminPaymentUpdateRequest {
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.AdminPaymentUpdateRequestStatus;
  /** Payment description */
  description?: string;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Provider-specific data (validated by Pydantic) */
  provider_data?: string;
  /** Webhook data (validated by Pydantic) */
  webhook_data?: string;
}

/**
 * Serializer for updating payments in admin interface.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminPaymentUpdate {
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.AdminPaymentUpdateStatus;
  /** Payment description */
  description?: string;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Provider-specific data (validated by Pydantic) */
  provider_data?: string;
  /** Webhook data (validated by Pydantic) */
  webhook_data?: string;
}

/**
 * Serializer for updating payments in admin interface.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedAdminPaymentUpdateRequest {
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.PatchedAdminPaymentUpdateRequestStatus;
  /** Payment description */
  description?: string;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Provider-specific data (validated by Pydantic) */
  provider_data?: string;
  /** Webhook data (validated by Pydantic) */
  webhook_data?: string;
}

/**
 * Serializer for payment statistics in admin interface.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminPaymentStats {
  total_payments: number;
  total_amount_usd: number;
  successful_payments: number;
  failed_payments: number;
  pending_payments: number;
  success_rate: number;
  /** Statistics by provider */
  by_provider: Record<string, any>;
  /** Statistics by currency */
  by_currency: Record<string, any>;
  /** Payments in last 24 hours */
  last_24h: Record<string, any>;
  /** Payments in last 7 days */
  last_7d: Record<string, any>;
  /** Payments in last 30 days */
  last_30d: Record<string, any>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedAdminPaymentStatsList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<AdminPaymentStats>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedAdminUserList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<AdminUser>;
}

/**
 * Simplified user serializer for admin interface.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminUser {
  id: number;
  /** Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. */
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  /** Designates whether this user should be treated as active. Unselect this instead of deleting accounts. */
  is_active: boolean;
}

/**
 * Serializer for comprehensive webhook statistics.
 * 
 * Request model (no read-only fields).
 */
export interface WebhookStatsRequest {
  total: number;
  successful: number;
  failed: number;
  pending: number;
  success_rate: number;
  /** Statistics by provider */
  providers: Record<string, any>;
  /** Events in last 24 hours */
  last_24h: Record<string, any>;
  avg_response_time: number;
  max_response_time: number;
}

/**
 * Serializer for comprehensive webhook statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookStats {
  total: number;
  successful: number;
  failed: number;
  pending: number;
  success_rate: number;
  /** Statistics by provider */
  providers: Record<string, any>;
  /** Events in last 24 hours */
  last_24h: Record<string, any>;
  avg_response_time: number;
  max_response_time: number;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedWebhookStatsList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<WebhookStats>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedWebhookEventListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<WebhookEventList>;
}

/**
 * Serializer for paginated webhook events list.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookEventList {
  events: Array<WebhookEvent>;
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

/**
 * Serializer for paginated webhook events list.
 * 
 * Request model (no read-only fields).
 */
export interface WebhookEventListRequest {
  events: Array<WebhookEventRequest>;
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedAPIKeyListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<APIKeyList>;
}

/**
 * API key creation serializer with service integration. Creates new API keys
 * and returns the full key value (only once).
 * 
 * Request model (no read-only fields).
 */
export interface APIKeyCreateRequest {
  /** Descriptive name for the API key */
  name: string;
  /** Expiration in days (optional, null for no expiration) */
  expires_in_days?: number;
}

/**
 * API key creation serializer with service integration. Creates new API keys
 * and returns the full key value (only once).
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeyCreate {
  /** Descriptive name for the API key */
  name: string;
  /** Expiration in days (optional, null for no expiration) */
  expires_in_days?: number;
}

/**
 * Complete API key serializer with full details. Used for API key detail views
 * (no key value for security).
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeyDetail {
  /** Unique identifier for this record */
  id: string;
  user: string;
  /** Human-readable name for this API key */
  name: string;
  key_preview: string;
  /** Whether this API key is active */
  is_active: boolean;
  is_expired: boolean;
  is_valid: boolean;
  days_until_expiry: number;
  /** Total number of requests made with this key */
  total_requests: number;
  /** When this API key was last used */
  last_used_at?: string;
  /** When this API key expires (null = never expires) */
  expires_at?: string;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * API key update serializer for modifying API key properties. Allows updating
 * name and active status only.
 * 
 * Request model (no read-only fields).
 */
export interface APIKeyUpdateRequest {
  /** Human-readable name for this API key */
  name: string;
  /** Whether this API key is active */
  is_active?: boolean;
}

/**
 * API key update serializer for modifying API key properties. Allows updating
 * name and active status only.
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeyUpdate {
  /** Human-readable name for this API key */
  name: string;
  /** Whether this API key is active */
  is_active?: boolean;
}

/**
 * API key update serializer for modifying API key properties. Allows updating
 * name and active status only.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedAPIKeyUpdateRequest {
  /** Human-readable name for this API key */
  name?: string;
  /** Whether this API key is active */
  is_active?: boolean;
}

/**
 * API key validation serializer. Validates API key and returns key
 * information.
 * 
 * Request model (no read-only fields).
 */
export interface APIKeyValidationRequest {
  /** API key to validate */
  key: string;
}

/**
 * API key validation response serializer. Defines the structure of API key
 * validation response for OpenAPI schema.
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeyValidationResponse {
  /** Whether the validation was successful */
  success: boolean;
  /** Whether the API key is valid */
  valid: boolean;
  api_key: Record<string, any>;
  /** Validation message */
  message: string;
  /** Error message if validation failed */
  error?: string;
  /** Error code if validation failed */
  error_code?: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedUserBalanceList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<UserBalance>;
}

/**
 * User balance serializer with computed fields. Provides balance information
 * with display helpers.
 * 
 * Response model (includes read-only fields).
 */
export interface UserBalance {
  user: string;
  /** Current balance in USD (float for performance) */
  balance_usd: number;
  /** Formatted balance display. */
  balance_display: string;
  /** Check if balance is zero. */
  is_empty: boolean;
  /** Check if user has any transactions. */
  has_transactions: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedCurrencyListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<CurrencyList>;
}

/**
 * Complete currency serializer with full details. Used for currency
 * information and management.
 * 
 * Response model (includes read-only fields).
 */
export interface Currency {
  id: number;
  /** Currency code (e.g., BTC, USD, ETH) */
  code: string;
  /** Full currency name (e.g., Bitcoin, US Dollar) */
  name: string;
  /** Currency symbol (e.g., $, ₿, Ξ) */
  symbol: string;
  /** Type of currency

  * `fiat` - Fiat Currency
  * `crypto` - Cryptocurrency */
  currency_type: Enums.CurrencyCurrencyType;
  type_display: string;
  /** Number of decimal places for this currency */
  decimal_places: number;
  /** Whether this currency is available for payments */
  is_active: boolean;
  /** Check if this is a cryptocurrency. */
  is_crypto: boolean;
  /** Check if this is a fiat currency. */
  is_fiat: boolean;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedEndpointGroupList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<EndpointGroup>;
}

/**
 * Endpoint group serializer for API access management. Used for subscription
 * endpoint group configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface EndpointGroup {
  id: number;
  /** Endpoint group name (e.g., 'Payment API', 'Balance API') */
  name: string;
  /** Description of what this endpoint group provides */
  description: string;
  /** Whether this endpoint group is available */
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Complete payment serializer with full details. Used for detail views and
 * updates.
 * 
 * Response model (includes read-only fields).
 */
export interface Payment {
  /** Unique identifier for this record */
  id: string;
  user: string;
  /** Payment amount in USD (float for performance) */
  amount_usd: number;
  /** Payment currency */
  currency: number;
  /** Blockchain network (for crypto payments) */
  network?: number;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider?: Enums.PaymentProvider;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.PaymentStatus;
  status_display: string;
  /** Get formatted amount display. */
  amount_display: string;
  /** Provider's payment ID */
  provider_payment_id?: string;
  /** Payment page URL */
  payment_url?: string;
  /** Cryptocurrency payment address */
  pay_address?: string;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Payment description */
  description?: string;
  /** Blockchain transaction hash */
  transaction_hash?: string;
  /** Number of blockchain confirmations */
  confirmations_count: number;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
  /** When this payment expires */
  expires_at?: string;
  /** When this payment was completed */
  completed_at?: string;
  /** Check if payment is pending. */
  is_pending: boolean;
  /** Check if payment is completed. */
  is_completed: boolean;
  /** Check if payment is failed. */
  is_failed: boolean;
  /** Check if payment is expired. */
  is_expired: boolean;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedNetworkList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<Network>;
}

/**
 * Network serializer for blockchain networks. Used for network information and
 * selection.
 * 
 * Response model (includes read-only fields).
 */
export interface Network {
  id: number;
  currency: Record<string, any>;
  /** Network name (e.g., Ethereum, Bitcoin, Polygon) */
  name: string;
  /** Network code (e.g., ETH, BTC, MATIC) */
  code: string;
  /** Whether this network is available for payments */
  is_active: boolean;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * API keys overview metrics
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeysOverview {
  /** Total number of API keys */
  total_keys: number;
  /** Number of active API keys */
  active_keys: number;
  /** Number of expired API keys */
  expired_keys: number;
  /** Total requests across all keys */
  total_requests: number;
  /** When any key was last used */
  last_used_at?: string;
  /** Name of most used API key */
  most_used_key_name?: string;
  /** Requests count for most used key */
  most_used_key_requests: number;
  /** Number of keys expiring within 7 days */
  expiring_soon_count: number;
}

/**
 * User balance overview metrics
 * 
 * Response model (includes read-only fields).
 */
export interface BalanceOverview {
  /** Current balance in USD */
  current_balance: number;
  /** Formatted balance display */
  balance_display: string;
  /** Total amount deposited (lifetime) */
  total_deposited: number;
  /** Total amount spent (lifetime) */
  total_spent: number;
  /** Last transaction timestamp */
  last_transaction_at?: string;
  /** Whether user has any transactions */
  has_transactions: boolean;
  /** Whether balance is zero */
  is_empty: boolean;
}

/**
 * Complete chart response for payments analytics
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentsChartResponse {
  /** Chart series data */
  series: Array<ChartSeries>;
  /** Time period */
  period: string;
  /** Total amount for period */
  total_amount: number;
  /** Total payments for period */
  total_payments: number;
  /** Success rate for period */
  success_rate: number;
}

/**
 * Complete payments dashboard metrics
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentsMetrics {
  balance: Record<string, any>;
  subscription: Record<string, any>;
  api_keys: Record<string, any>;
  payments: Record<string, any>;
}

/**
 * Complete payments dashboard overview response
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentsDashboardOverview {
  metrics: Record<string, any>;
  /** Recent payments */
  recent_payments: Array<RecentPayment>;
  /** Recent transactions */
  recent_transactions: Array<RecentTransaction>;
  chart_data: Record<string, any>;
}

/**
 * Payment analytics response with currency and provider breakdown
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentAnalyticsResponse {
  /** Analytics by currency */
  currency_analytics: Array<CurrencyAnalyticsItem>;
  /** Analytics by provider */
  provider_analytics: Array<ProviderAnalyticsItem>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedRecentPaymentList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<RecentPayment>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedRecentTransactionList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<RecentTransaction>;
}

/**
 * Current subscription overview
 * 
 * Response model (includes read-only fields).
 */
export interface SubscriptionOverview {
  /** Subscription tier */
  tier: string;
  /** Human-readable tier name */
  tier_display: string;
  /** Subscription status */
  status: string;
  /** Human-readable status */
  status_display: string;
  /** Color for status display */
  status_color: string;
  /** Whether subscription is active */
  is_active: boolean;
  /** Whether subscription is expired */
  is_expired: boolean;
  /** Days until expiration */
  days_remaining: number;
  /** Hourly request limit */
  requests_per_hour: number;
  /** Daily request limit */
  requests_per_day: number;
  /** Total requests made */
  total_requests: number;
  /** Usage percentage for current period */
  usage_percentage: number;
  /** Monthly cost in USD */
  monthly_cost_usd: number;
  /** Formatted cost display */
  cost_display: string;
  /** Subscription start date */
  starts_at: string;
  /** Subscription expiration date */
  expires_at: string;
  /** Last API request timestamp */
  last_request_at?: string;
  /** Number of accessible endpoint groups */
  endpoint_groups_count: number;
  /** List of accessible endpoint group names */
  endpoint_groups: Array<string>;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPaymentListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<PaymentList>;
}

/**
 * Payment creation serializer with Pydantic integration. Validates input and
 * delegates to PaymentService.
 * 
 * Request model (no read-only fields).
 */
export interface PaymentCreateRequest {
  /** Amount in USD (1.00 - 50,000.00) */
  amount_usd: number;
  /** Cryptocurrency to receive

  * `BTC` - Bitcoin
  * `ETH` - Ethereum
  * `LTC` - Litecoin
  * `XMR` - Monero
  * `USDT` - Tether
  * `USDC` - USD Coin
  * `ADA` - Cardano
  * `DOT` - Polkadot */
  currency_code: Enums.PaymentCreateRequestCurrencyCode;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider?: Enums.PaymentCreateRequestProvider;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Payment description */
  description?: string;
  /** Additional metadata */
  metadata?: string;
}

/**
 * Payment creation serializer with Pydantic integration. Validates input and
 * delegates to PaymentService.
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentCreate {
  /** Amount in USD (1.00 - 50,000.00) */
  amount_usd: number;
  /** Cryptocurrency to receive

  * `BTC` - Bitcoin
  * `ETH` - Ethereum
  * `LTC` - Litecoin
  * `XMR` - Monero
  * `USDT` - Tether
  * `USDC` - USD Coin
  * `ADA` - Cardano
  * `DOT` - Polkadot */
  currency_code: Enums.PaymentCreateCurrencyCode;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider?: Enums.PaymentCreateProvider;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Payment description */
  description?: string;
  /** Additional metadata */
  metadata?: string;
}

/**
 * Complete payment serializer with full details. Used for detail views and
 * updates.
 * 
 * Request model (no read-only fields).
 */
export interface PaymentRequest {
  /** Payment amount in USD (float for performance) */
  amount_usd: number;
  /** Payment currency */
  currency: number;
  /** Blockchain network (for crypto payments) */
  network?: number;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider?: Enums.PaymentRequestProvider;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.PaymentRequestStatus;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Payment description */
  description?: string;
  /** When this payment expires */
  expires_at?: string;
}

/**
 * Complete payment serializer with full details. Used for detail views and
 * updates.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedPaymentRequest {
  /** Payment amount in USD (float for performance) */
  amount_usd?: number;
  /** Payment currency */
  currency?: number;
  /** Blockchain network (for crypto payments) */
  network?: number;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider?: Enums.PatchedPaymentRequestProvider;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.PatchedPaymentRequestStatus;
  /** Success callback URL */
  callback_url?: string;
  /** Cancellation URL */
  cancel_url?: string;
  /** Payment description */
  description?: string;
  /** When this payment expires */
  expires_at?: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedProviderCurrencyList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<ProviderCurrency>;
}

/**
 * Provider currency serializer for provider-specific currency info. Used for
 * provider currency management and rates.
 * 
 * Response model (includes read-only fields).
 */
export interface ProviderCurrency {
  id: number;
  currency: Record<string, any>;
  network: Record<string, any>;
  /** Payment provider name (e.g., nowpayments) */
  provider: string;
  /** Currency code as used by the provider */
  provider_currency_code: string;
  /** Get minimum amount from provider configuration. */
  provider_min_amount_usd: number;
  /** Get maximum amount from provider configuration. */
  provider_max_amount_usd: number;
  /** Get fee percentage from provider configuration. */
  provider_fee_percentage: number;
  /** Get fixed fee from provider configuration. */
  provider_fixed_fee_usd: number;
  /** Whether this currency is enabled for this provider */
  is_enabled: boolean;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedSubscriptionListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<SubscriptionList>;
}

/**
 * Subscription creation serializer with service integration. Validates input
 * and delegates to SubscriptionService.
 * 
 * Request model (no read-only fields).
 */
export interface SubscriptionCreateRequest {
  /** Tariff ID for the subscription */
  tariff_id: number;
  /** Endpoint group ID (optional) */
  endpoint_group_id?: number;
  /** Subscription duration in days */
  duration_days?: number;
}

/**
 * Subscription creation serializer with service integration. Validates input
 * and delegates to SubscriptionService.
 * 
 * Response model (includes read-only fields).
 */
export interface SubscriptionCreate {
  /** Tariff ID for the subscription */
  tariff_id: number;
  /** Endpoint group ID (optional) */
  endpoint_group_id?: number;
  /** Subscription duration in days */
  duration_days?: number;
}

/**
 * Complete subscription serializer with full details. Used for subscription
 * detail views and updates.
 * 
 * Response model (includes read-only fields).
 */
export interface Subscription {
  /** Unique identifier for this record */
  id: string;
  user: string;
  tariff: Record<string, any>;
  endpoint_group: Record<string, any>;
  /** Subscription status

  * `active` - Active
  * `inactive` - Inactive
  * `suspended` - Suspended
  * `cancelled` - Cancelled
  * `expired` - Expired */
  status?: Enums.SubscriptionStatus;
  status_display: string;
  /** Get color for status display. */
  status_color: string;
  /** Subscription tier

  * `free` - Free Tier
  * `basic` - Basic Tier
  * `pro` - Pro Tier
  * `enterprise` - Enterprise Tier */
  tier?: Enums.SubscriptionTier;
  /** Total API requests made with this subscription */
  total_requests: number;
  /** Get usage percentage for current period. */
  usage_percentage: number;
  /** When the last API request was made */
  last_request_at?: string;
  /** When this subscription expires */
  expires_at: string;
  /** Check if subscription is active and not expired. */
  is_active: boolean;
  /** Check if subscription is expired. */
  is_expired: boolean;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * Complete subscription serializer with full details. Used for subscription
 * detail views and updates.
 * 
 * Request model (no read-only fields).
 */
export interface SubscriptionRequest {
  /** Subscription status

  * `active` - Active
  * `inactive` - Inactive
  * `suspended` - Suspended
  * `cancelled` - Cancelled
  * `expired` - Expired */
  status?: Enums.SubscriptionRequestStatus;
  /** Subscription tier

  * `free` - Free Tier
  * `basic` - Basic Tier
  * `pro` - Pro Tier
  * `enterprise` - Enterprise Tier */
  tier?: Enums.SubscriptionRequestTier;
  /** When this subscription expires */
  expires_at: string;
}

/**
 * Complete subscription serializer with full details. Used for subscription
 * detail views and updates.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedSubscriptionRequest {
  /** Subscription status

  * `active` - Active
  * `inactive` - Inactive
  * `suspended` - Suspended
  * `cancelled` - Cancelled
  * `expired` - Expired */
  status?: Enums.PatchedSubscriptionRequestStatus;
  /** Subscription tier

  * `free` - Free Tier
  * `basic` - Basic Tier
  * `pro` - Pro Tier
  * `enterprise` - Enterprise Tier */
  tier?: Enums.PatchedSubscriptionRequestTier;
  /** When this subscription expires */
  expires_at?: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedTariffList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<Tariff>;
}

/**
 * Tariff serializer for subscription pricing. Used for tariff information and
 * selection.
 * 
 * Response model (includes read-only fields).
 */
export interface Tariff {
  id: number;
  /** Tariff name (e.g., 'Free', 'Basic', 'Pro') */
  name: string;
  /** Detailed description of what this tariff includes */
  description: string;
  /** Monthly price in USD */
  monthly_price_usd: number;
  /** API requests allowed per month */
  requests_per_month: number;
  /** API requests allowed per hour */
  requests_per_hour: number;
  /** Whether this tariff is available for new subscriptions */
  is_active: boolean;
  endpoint_groups: Array<EndpointGroup>;
  endpoint_groups_count: number;
  /** When this record was created */
  created_at: string;
  /** When this record was last updated */
  updated_at: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedTransactionList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<Transaction>;
}

/**
 * Transaction serializer with full details. Used for transaction history and
 * details.
 * 
 * Response model (includes read-only fields).
 */
export interface Transaction {
  /** Unique identifier for this record */
  id: string;
  user: string;
  /** Transaction amount in USD (positive=credit, negative=debit) */
  amount_usd: number;
  amount_display: string;
  /** Type of transaction

  * `deposit` - Deposit
  * `withdrawal` - Withdrawal
  * `payment` - Payment
  * `refund` - Refund
  * `fee` - Fee
  * `bonus` - Bonus
  * `adjustment` - Adjustment */
  transaction_type: Enums.TransactionTransactionType;
  type_color: string;
  /** Transaction description */
  description: string;
  /** Related payment ID (if applicable) */
  payment_id?: string;
  /** Additional transaction metadata */
  metadata: string;
  is_credit: boolean;
  is_debit: boolean;
  /** When this record was created */
  created_at: string;
}

/**
 * Serializer for payment list in admin interface. Uses UniversalPayment only
 * for data extraction.
 * 
 * Response model (includes read-only fields).
 */
export interface AdminPaymentList {
  id: string;
  user: Record<string, any>;
  amount_usd: number;
  currency_code: string;
  currency_name: string;
  provider: string;
  provider_display: string;
  status: string;
  status_display: string;
  pay_amount: string;
  pay_address: string;
  transaction_hash: string;
  created_at: string;
  updated_at: string;
  description: string;
  age: string;
}

/**
 * Serializer for individual webhook event.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookEvent {
  id: number;
  provider: string;
  event_type: string;
  /** * `success` - Success
  * `failed` - Failed
  * `pending` - Pending
  * `retry` - Retry */
  status: Enums.WebhookEventStatus;
  timestamp: string;
  /** Size in bytes */
  payload_size: number;
  /** Response time in ms */
  response_time: number;
  retry_count?: number;
  error_message?: string;
  payload_preview?: string;
  response_status_code?: number;
  webhook_url?: string;
}

/**
 * Serializer for individual webhook event.
 * 
 * Request model (no read-only fields).
 */
export interface WebhookEventRequest {
  provider: string;
  event_type: string;
  /** * `success` - Success
  * `failed` - Failed
  * `pending` - Pending
  * `retry` - Retry */
  status: Enums.WebhookEventRequestStatus;
  timestamp: string;
  /** Size in bytes */
  payload_size: number;
  /** Response time in ms */
  response_time: number;
  retry_count?: number;
  error_message?: string;
  payload_preview?: string;
  response_status_code?: number;
  webhook_url?: string;
}

/**
 * Lightweight API key serializer for lists. Optimized for API key lists with
 * minimal data (no key value).
 * 
 * Response model (includes read-only fields).
 */
export interface APIKeyList {
  /** Unique identifier for this record */
  id: string;
  user: string;
  /** Human-readable name for this API key */
  name: string;
  /** Whether this API key is active */
  is_active: boolean;
  is_expired: boolean;
  is_valid: boolean;
  /** Total number of requests made with this key */
  total_requests: number;
  /** When this API key was last used */
  last_used_at?: string;
  /** When this API key expires (null = never expires) */
  expires_at?: string;
  /** When this record was created */
  created_at: string;
}

/**
 * Lightweight currency serializer for lists. Optimized for currency selection
 * and lists.
 * 
 * Response model (includes read-only fields).
 */
export interface CurrencyList {
  id: number;
  /** Currency code (e.g., BTC, USD, ETH) */
  code: string;
  /** Full currency name (e.g., Bitcoin, US Dollar) */
  name: string;
  /** Currency symbol (e.g., $, ₿, Ξ) */
  symbol: string;
  /** Type of currency

  * `fiat` - Fiat Currency
  * `crypto` - Cryptocurrency */
  currency_type: Enums.CurrencyListCurrencyType;
  type_display: string;
  /** Whether this currency is available for payments */
  is_active: boolean;
}

/**
 * Chart series data for payments visualization
 * 
 * Response model (includes read-only fields).
 */
export interface ChartSeries {
  /** Series name */
  name: string;
  /** Data points */
  data: Array<ChartDataPoint>;
  /** Series color */
  color: string;
}

/**
 * Payments overview metrics
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentOverview {
  /** Total number of payments */
  total_payments: number;
  /** Number of completed payments */
  completed_payments: number;
  /** Number of pending payments */
  pending_payments: number;
  /** Number of failed payments */
  failed_payments: number;
  /** Total payment amount in USD */
  total_amount_usd: number;
  /** Total completed amount in USD */
  completed_amount_usd: number;
  /** Average payment amount in USD */
  average_payment_usd: number;
  /** Payment success rate percentage */
  success_rate: number;
  /** Last payment timestamp */
  last_payment_at?: string;
  /** Number of payments this month */
  payments_this_month: number;
  /** Total amount this month */
  amount_this_month: number;
  /** Most used currency */
  top_currency?: string;
  /** Usage count for top currency */
  top_currency_count: number;
}

/**
 * Recent payment item
 * 
 * Response model (includes read-only fields).
 */
export interface RecentPayment {
  /** Payment ID */
  id: string;
  /** Internal payment ID */
  internal_payment_id: string;
  /** Payment amount in USD */
  amount_usd: number;
  /** Formatted amount display */
  amount_display: string;
  /** Currency code */
  currency_code: string;
  /** Payment status */
  status: string;
  /** Human-readable status */
  status_display: string;
  /** Color for status display */
  status_color: string;
  /** Payment provider */
  provider: string;
  /** Payment creation timestamp */
  created_at: string;
  /** Payment completion timestamp */
  completed_at?: string;
  /** Whether payment is pending */
  is_pending: boolean;
  /** Whether payment is completed */
  is_completed: boolean;
  /** Whether payment failed */
  is_failed: boolean;
}

/**
 * Recent transaction item
 * 
 * Response model (includes read-only fields).
 */
export interface RecentTransaction {
  /** Transaction ID */
  id: string;
  /** Transaction type */
  transaction_type: string;
  /** Transaction amount in USD */
  amount_usd: number;
  /** Formatted amount display */
  amount_display: string;
  /** Balance after transaction */
  balance_after: number;
  /** Transaction description */
  description: string;
  /** Transaction timestamp */
  created_at: string;
  /** Related payment ID */
  payment_id?: string;
  /** Whether this is a credit transaction */
  is_credit: boolean;
  /** Whether this is a debit transaction */
  is_debit: boolean;
  /** Color for transaction type display */
  type_color: string;
}

/**
 * Analytics data for a single currency
 * 
 * Response model (includes read-only fields).
 */
export interface CurrencyAnalyticsItem {
  /** Currency code (e.g., BTC) */
  currency_code: string;
  /** Currency name (e.g., Bitcoin) */
  currency_name: string;
  /** Total number of payments */
  total_payments: number;
  /** Total amount in USD */
  total_amount: number;
  /** Number of completed payments */
  completed_payments: number;
  /** Average payment amount in USD */
  average_amount: number;
  /** Success rate percentage */
  success_rate: number;
}

/**
 * Analytics data for a single payment provider
 * 
 * Response model (includes read-only fields).
 */
export interface ProviderAnalyticsItem {
  /** Provider code */
  provider: string;
  /** Provider display name */
  provider_display: string;
  /** Total number of payments */
  total_payments: number;
  /** Total amount in USD */
  total_amount: number;
  /** Number of completed payments */
  completed_payments: number;
  /** Success rate percentage */
  success_rate: number;
}

/**
 * Lightweight serializer for payment lists. Optimized for list views with
 * minimal data.
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentList {
  /** Unique identifier for this record */
  id: string;
  /** Payment amount in USD (float for performance) */
  amount_usd: number;
  /** Payment currency */
  currency: number;
  /** Payment provider

  * `nowpayments` - NowPayments */
  provider: Enums.PaymentListProvider;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status: Enums.PaymentListStatus;
  status_display: string;
  /** Get formatted amount display. */
  amount_display: string;
  /** When this record was created */
  created_at: string;
  /** When this payment expires */
  expires_at?: string;
}

/**
 * Lightweight subscription serializer for lists. Optimized for subscription
 * lists with minimal data.
 * 
 * Response model (includes read-only fields).
 */
export interface SubscriptionList {
  /** Unique identifier for this record */
  id: string;
  user: string;
  tariff_name: string;
  /** Subscription status

  * `active` - Active
  * `inactive` - Inactive
  * `suspended` - Suspended
  * `cancelled` - Cancelled
  * `expired` - Expired */
  status: Enums.SubscriptionListStatus;
  status_display: string;
  /** Check if subscription is active and not expired. */
  is_active: boolean;
  /** Check if subscription is expired. */
  is_expired: boolean;
  /** When this subscription expires */
  expires_at: string;
  /** When this record was created */
  created_at: string;
}

/**
 * Chart data point for payments analytics
 * 
 * Response model (includes read-only fields).
 */
export interface ChartDataPoint {
  /** X-axis value (date) */
  x: string;
  /** Y-axis value (amount or count) */
  y: number;
}

