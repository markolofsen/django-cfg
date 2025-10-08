/**
 * Type of currency * `fiat` - Fiat Currency * `crypto` - Cryptocurrency
 */
export enum Currency.currency_type {
  FIAT = "fiat",
  CRYPTO = "crypto",
}

/**
 * Type of currency * `fiat` - Fiat Currency * `crypto` - Cryptocurrency
 */
export enum CurrencyList.currency_type {
  FIAT = "fiat",
  CRYPTO = "crypto",
}

/**
 * * `pending` - Pending * `sent` - Sent * `failed` - Failed
 */
export enum EmailLog.status {
  PENDING = "pending",
  SENT = "sent",
  FAILED = "failed",
}

/**
 * * `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
 * - Phone * `other` - Other
 */
export enum LeadSubmission.contact_type {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * * `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
 * - Phone * `other` - Other
 */
export enum LeadSubmissionRequest.contact_type {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * * `draft` - Draft * `sending` - Sending * `sent` - Sent * `failed` - Failed
 */
export enum NewsletterCampaign.status {
  DRAFT = "draft",
  SENDING = "sending",
  SENT = "sent",
  FAILED = "failed",
}

/**
 * Delivery channel: 'email' or 'phone'. Auto-detected if not provided. *
 * `email` - Email * `phone` - Phone
 */
export enum OTPRequestRequest.channel {
  EMAIL = "email",
  PHONE = "phone",
}

/**
 * Delivery channel: 'email' or 'phone'. Auto-detected if not provided. *
 * `email` - Email * `phone` - Phone
 */
export enum OTPVerifyRequest.channel {
  EMAIL = "email",
  PHONE = "phone",
}

/**
 * * `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
 * - Phone * `other` - Other
 */
export enum PatchedLeadSubmissionRequest.contact_type {
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  TELEGRAM = "telegram",
  PHONE = "phone",
  OTHER = "other",
}

/**
 * Payment provider * `nowpayments` - NowPayments
 */
export enum PatchedPaymentRequest.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status * `pending` - Pending * `confirming` - Confirming *
 * `confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
 * `expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum PatchedPaymentRequest.status {
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
 * Subscription status * `active` - Active * `inactive` - Inactive *
 * `suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired
 */
export enum PatchedSubscriptionRequest.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
 * Tier * `enterprise` - Enterprise Tier
 */
export enum PatchedSubscriptionRequest.tier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * * `open` - Open * `waiting_for_user` - Waiting for User *
 * `waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
 * Closed
 */
export enum PatchedTicketRequest.status {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * Payment provider * `nowpayments` - NowPayments
 */
export enum Payment.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status * `pending` - Pending * `confirming` - Confirming *
 * `confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
 * `expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum Payment.status {
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
 * Cryptocurrency to receive * `BTC` - Bitcoin * `ETH` - Ethereum * `LTC` -
 * Litecoin * `XMR` - Monero * `USDT` - Tether * `USDC` - USD Coin * `ADA` -
 * Cardano * `DOT` - Polkadot
 */
export enum PaymentCreate.currency_code {
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
 * Payment provider * `nowpayments` - NowPayments
 */
export enum PaymentCreate.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Cryptocurrency to receive * `BTC` - Bitcoin * `ETH` - Ethereum * `LTC` -
 * Litecoin * `XMR` - Monero * `USDT` - Tether * `USDC` - USD Coin * `ADA` -
 * Cardano * `DOT` - Polkadot
 */
export enum PaymentCreateRequest.currency_code {
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
 * Payment provider * `nowpayments` - NowPayments
 */
export enum PaymentCreateRequest.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Payment provider * `nowpayments` - NowPayments
 */
export enum PaymentList.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status * `pending` - Pending * `confirming` - Confirming *
 * `confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
 * `expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum PaymentList.status {
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
 * Payment provider * `nowpayments` - NowPayments
 */
export enum PaymentRequest.provider {
  NOWPAYMENTS = "nowpayments",
}

/**
 * Current payment status * `pending` - Pending * `confirming` - Confirming *
 * `confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
 * `expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum PaymentRequest.status {
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
 * Action to perform on queues * `clear` - clear * `clear_all` - clear_all *
 * `purge` - purge * `purge_failed` - purge_failed * `flush` - flush
 */
export enum QueueAction.action {
  CLEAR = "clear",
  CLEAR_ALL = "clear_all",
  PURGE = "purge",
  PURGE_FAILED = "purge_failed",
  FLUSH = "flush",
}

/**
 * Action to perform on queues * `clear` - clear * `clear_all` - clear_all *
 * `purge` - purge * `purge_failed` - purge_failed * `flush` - flush
 */
export enum QueueActionRequest.action {
  CLEAR = "clear",
  CLEAR_ALL = "clear_all",
  PURGE = "purge",
  PURGE_FAILED = "purge_failed",
  FLUSH = "flush",
}

/**
 * Subscription status * `active` - Active * `inactive` - Inactive *
 * `suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired
 */
export enum Subscription.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
 * Tier * `enterprise` - Enterprise Tier
 */
export enum Subscription.tier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * Subscription status * `active` - Active * `inactive` - Inactive *
 * `suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired
 */
export enum SubscriptionList.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription status * `active` - Active * `inactive` - Inactive *
 * `suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired
 */
export enum SubscriptionRequest.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
 * Tier * `enterprise` - Enterprise Tier
 */
export enum SubscriptionRequest.tier {
  FREE = "free",
  BASIC = "basic",
  PRO = "pro",
  ENTERPRISE = "enterprise",
}

/**
 * * `open` - Open * `waiting_for_user` - Waiting for User *
 * `waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
 * Closed
 */
export enum Ticket.status {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * * `open` - Open * `waiting_for_user` - Waiting for User *
 * `waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
 * Closed
 */
export enum TicketRequest.status {
  OPEN = "open",
  WAITING_FOR_USER = "waiting_for_user",
  WAITING_FOR_ADMIN = "waiting_for_admin",
  RESOLVED = "resolved",
  CLOSED = "closed",
}

/**
 * Type of transaction * `deposit` - Deposit * `withdrawal` - Withdrawal *
 * `payment` - Payment * `refund` - Refund * `fee` - Fee * `bonus` - Bonus *
 * `adjustment` - Adjustment
 */
export enum Transaction.transaction_type {
  DEPOSIT = "deposit",
  WITHDRAWAL = "withdrawal",
  PAYMENT = "payment",
  REFUND = "refund",
  FEE = "fee",
  BONUS = "bonus",
  ADJUSTMENT = "adjustment",
}

/**
 * Action to perform on workers * `start` - start * `stop` - stop * `restart` -
 * restart
 */
export enum WorkerAction.action {
  START = "start",
  STOP = "stop",
  RESTART = "restart",
}

/**
 * Action to perform on workers * `start` - start * `stop` - stop * `restart` -
 * restart
 */
export enum WorkerActionRequest.action {
  START = "start",
  STOP = "stop",
  RESTART = "restart",
}

