/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum AdminPaymentUpdateStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum AdminPaymentUpdateRequestStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Type of currency
 * * `fiat` - Fiat Currency
 * * `crypto` - Cryptocurrency
 */
export enum CurrencyCurrencyType {
  FIAT = "fiat",
  CRYPTO = "crypto",
}

/**
 * Type of currency
 * * `fiat` - Fiat Currency
 * * `crypto` - Cryptocurrency
 */
export enum CurrencyListCurrencyType {
  FIAT = "fiat",
  CRYPTO = "crypto",
}

/**
 * * `pending` - Pending
 * * `sent` - Sent
 * * `failed` - Failed
 */
export enum EmailLogStatus {
  PENDING = "pending",
  SENT = "sent",
  FAILED = "failed",
}

/**
 * * `email` - Email
 * * `whatsapp` - WhatsApp
 * * `telegram` - Telegram
 * * `phone` - Phone
 * * `other` - Other
 */
export enum LeadSubmissionContactType {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * * `email` - Email
 * * `whatsapp` - WhatsApp
 * * `telegram` - Telegram
 * * `phone` - Phone
 * * `other` - Other
 */
export enum LeadSubmissionRequestContactType {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * * `draft` - Draft
 * * `sending` - Sending
 * * `sent` - Sent
 * * `failed` - Failed
 */
export enum NewsletterCampaignStatus {
  DRAFT = "draft",
  SENDING = "sending",
  SENT = "sent",
  FAILED = "failed",
}

/**
 * Delivery channel: 'email' or 'phone'. Auto-detected if not provided.
 * * `email` - Email
 * * `phone` - Phone
 */
export enum OTPRequestRequestChannel {
  EMAIL = "email",
  PHONE = "phone",
}

/**
 * Delivery channel: 'email' or 'phone'. Auto-detected if not provided.
 * * `email` - Email
 * * `phone` - Phone
 */
export enum OTPVerifyRequestChannel {
  EMAIL = "email",
  PHONE = "phone",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum PatchedAdminPaymentUpdateRequestStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * * `email` - Email
 * * `whatsapp` - WhatsApp
 * * `telegram` - Telegram
 * * `phone` - Phone
 * * `other` - Other
 */
export enum PatchedLeadSubmissionRequestContactType {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PatchedPaymentRequestProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum PatchedPaymentRequestStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Subscription status
 * * `active` - Active
 * * `inactive` - Inactive
 * * `suspended` - Suspended
 * * `cancelled` - Cancelled
 * * `expired` - Expired
 */
export enum PatchedSubscriptionRequestStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier
 * * `free` - Free Tier
 * * `basic` - Basic Tier
 * * `pro` - Pro Tier
 * * `enterprise` - Enterprise Tier
 */
export enum PatchedSubscriptionRequestTier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * * `open` - Open
 * * `waiting_for_user` - Waiting for User
 * * `waiting_for_admin` - Waiting for Admin
 * * `resolved` - Resolved
 * * `closed` - Closed
 */
export enum PatchedTicketRequestStatus {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PaymentProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum PaymentStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Cryptocurrency to receive
 * * `BTC` - Bitcoin
 * * `ETH` - Ethereum
 * * `LTC` - Litecoin
 * * `XMR` - Monero
 * * `USDT` - Tether
 * * `USDC` - USD Coin
 * * `ADA` - Cardano
 * * `DOT` - Polkadot
 */
export enum PaymentCreateCurrencyCode {
  BTC = "BTC",
  ETH = "ETH",
  LTC = "LTC",
  XMR = "XMR",
  USDT = "USDT",
  USDC = "USDC",
  ADA = "ADA",
  DOT = "DOT",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PaymentCreateProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Cryptocurrency to receive
 * * `BTC` - Bitcoin
 * * `ETH` - Ethereum
 * * `LTC` - Litecoin
 * * `XMR` - Monero
 * * `USDT` - Tether
 * * `USDC` - USD Coin
 * * `ADA` - Cardano
 * * `DOT` - Polkadot
 */
export enum PaymentCreateRequestCurrencyCode {
  BTC = "BTC",
  ETH = "ETH",
  LTC = "LTC",
  XMR = "XMR",
  USDT = "USDT",
  USDC = "USDC",
  ADA = "ADA",
  DOT = "DOT",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PaymentCreateRequestProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PaymentListProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum PaymentListStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Payment provider
 * * `nowpayments` - NowPayments
 */
export enum PaymentRequestProvider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum PaymentRequestStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * Action to perform on queues
 * * `clear` - clear
 * * `clear_all` - clear_all
 * * `purge` - purge
 * * `purge_failed` - purge_failed
 * * `flush` - flush
 */
export enum QueueActionAction {
  CLEAR = "clear",
  CLEAR_ALL = "clear_all",
  PURGE = "purge",
  PURGE_FAILED = "purge_failed",
  FLUSH = "flush",
}

/**
 * Action to perform on queues
 * * `clear` - clear
 * * `clear_all` - clear_all
 * * `purge` - purge
 * * `purge_failed` - purge_failed
 * * `flush` - flush
 */
export enum QueueActionRequestAction {
  CLEAR = "clear",
  CLEAR_ALL = "clear_all",
  PURGE = "purge",
  PURGE_FAILED = "purge_failed",
  FLUSH = "flush",
}

/**
 * Subscription status
 * * `active` - Active
 * * `inactive` - Inactive
 * * `suspended` - Suspended
 * * `cancelled` - Cancelled
 * * `expired` - Expired
 */
export enum SubscriptionStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier
 * * `free` - Free Tier
 * * `basic` - Basic Tier
 * * `pro` - Pro Tier
 * * `enterprise` - Enterprise Tier
 */
export enum SubscriptionTier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * Subscription status
 * * `active` - Active
 * * `inactive` - Inactive
 * * `suspended` - Suspended
 * * `cancelled` - Cancelled
 * * `expired` - Expired
 */
export enum SubscriptionListStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription status
 * * `active` - Active
 * * `inactive` - Inactive
 * * `suspended` - Suspended
 * * `cancelled` - Cancelled
 * * `expired` - Expired
 */
export enum SubscriptionRequestStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier
 * * `free` - Free Tier
 * * `basic` - Basic Tier
 * * `pro` - Pro Tier
 * * `enterprise` - Enterprise Tier
 */
export enum SubscriptionRequestTier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * * `open` - Open
 * * `waiting_for_user` - Waiting for User
 * * `waiting_for_admin` - Waiting for Admin
 * * `resolved` - Resolved
 * * `closed` - Closed
 */
export enum TicketStatus {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * * `open` - Open
 * * `waiting_for_user` - Waiting for User
 * * `waiting_for_admin` - Waiting for Admin
 * * `resolved` - Resolved
 * * `closed` - Closed
 */
export enum TicketRequestStatus {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * Type of transaction
 * * `deposit` - Deposit
 * * `withdrawal` - Withdrawal
 * * `payment` - Payment
 * * `refund` - Refund
 * * `fee` - Fee
 * * `bonus` - Bonus
 * * `adjustment` - Adjustment
 */
export enum TransactionTransactionType {
  DEPOSIT = "deposit",
  WITHDRAWAL = "withdrawal",
  PAYMENT = "payment",
  REFUND = "refund",
  FEE = "fee",
  BONUS = "bonus",
  ADJUSTMENT = "adjustment",
}

/**
 * * `success` - Success
 * * `failed` - Failed
 * * `pending` - Pending
 * * `retry` - Retry
 */
export enum WebhookEventStatus {
  SUCCESS = "success",
  FAILED = "failed",
  PENDING = "pending",
  RETRY = "retry",
}

/**
 * * `success` - Success
 * * `failed` - Failed
 * * `pending` - Pending
 * * `retry` - Retry
 */
export enum WebhookEventRequestStatus {
  SUCCESS = "success",
  FAILED = "failed",
  PENDING = "pending",
  RETRY = "retry",
}

/**
 * Action to perform on workers
 * * `start` - start
 * * `stop` - stop
 * * `restart` - restart
 */
export enum WorkerActionAction {
  START = "start",
  STOP = "stop",
  RESTART = "restart",
}

/**
 * Action to perform on workers
 * * `start` - start
 * * `stop` - stop
 * * `restart` - restart
 */
export enum WorkerActionRequestAction {
  START = "start",
  STOP = "stop",
  RESTART = "restart",
}

