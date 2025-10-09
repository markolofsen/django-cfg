from enum import IntEnum, StrEnum


class AdminPaymentUpdateStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class AdminPaymentUpdateRequestStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class CurrencyCurrencyType(StrEnum):
    """
    Type of currency
    * `fiat` - Fiat Currency
    * `crypto` - Cryptocurrency
    """

    FIAT = "fiat"
    CRYPTO = "crypto"



class CurrencyListCurrencyType(StrEnum):
    """
    Type of currency
    * `fiat` - Fiat Currency
    * `crypto` - Cryptocurrency
    """

    FIAT = "fiat"
    CRYPTO = "crypto"



class EmailLogStatus(StrEnum):
    """
    * `pending` - Pending
    * `sent` - Sent
    * `failed` - Failed
    """

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"



class LeadSubmissionContactType(StrEnum):
    """
    * `email` - Email
    * `whatsapp` - WhatsApp
    * `telegram` - Telegram
    * `phone` - Phone
    * `other` - Other
    """

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class LeadSubmissionRequestContactType(StrEnum):
    """
    * `email` - Email
    * `whatsapp` - WhatsApp
    * `telegram` - Telegram
    * `phone` - Phone
    * `other` - Other
    """

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class NewsletterCampaignStatus(StrEnum):
    """
    * `draft` - Draft
    * `sending` - Sending
    * `sent` - Sent
    * `failed` - Failed
    """

    DRAFT = "draft"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"



class OTPRequestRequestChannel(StrEnum):
    """
    Delivery channel: 'email' or 'phone'. Auto-detected if not provided.
    * `email` - Email
    * `phone` - Phone
    """

    EMAIL = "email"
    PHONE = "phone"



class OTPVerifyRequestChannel(StrEnum):
    """
    Delivery channel: 'email' or 'phone'. Auto-detected if not provided.
    * `email` - Email
    * `phone` - Phone
    """

    EMAIL = "email"
    PHONE = "phone"



class PatchedAdminPaymentUpdateRequestStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PatchedLeadSubmissionRequestContactType(StrEnum):
    """
    * `email` - Email
    * `whatsapp` - WhatsApp
    * `telegram` - Telegram
    * `phone` - Phone
    * `other` - Other
    """

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class PatchedPaymentRequestProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PatchedPaymentRequestStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PatchedSubscriptionRequestStatus(StrEnum):
    """
    Subscription status
    * `active` - Active
    * `inactive` - Inactive
    * `suspended` - Suspended
    * `cancelled` - Cancelled
    * `expired` - Expired
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class PatchedSubscriptionRequestTier(StrEnum):
    """
    Subscription tier
    * `free` - Free Tier
    * `basic` - Basic Tier
    * `pro` - Pro Tier
    * `enterprise` - Enterprise Tier
    """

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class PatchedTicketRequestStatus(StrEnum):
    """
    * `open` - Open
    * `waiting_for_user` - Waiting for User
    * `waiting_for_admin` - Waiting for Admin
    * `resolved` - Resolved
    * `closed` - Closed
    """

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class PaymentProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PaymentStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PaymentCreateCurrencyCode(StrEnum):
    """
    Cryptocurrency to receive
    * `BTC` - Bitcoin
    * `ETH` - Ethereum
    * `LTC` - Litecoin
    * `XMR` - Monero
    * `USDT` - Tether
    * `USDC` - USD Coin
    * `ADA` - Cardano
    * `DOT` - Polkadot
    """

    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    XMR = "XMR"
    USDT = "USDT"
    USDC = "USDC"
    ADA = "ADA"
    DOT = "DOT"



class PaymentCreateProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PaymentCreateRequestCurrencyCode(StrEnum):
    """
    Cryptocurrency to receive
    * `BTC` - Bitcoin
    * `ETH` - Ethereum
    * `LTC` - Litecoin
    * `XMR` - Monero
    * `USDT` - Tether
    * `USDC` - USD Coin
    * `ADA` - Cardano
    * `DOT` - Polkadot
    """

    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    XMR = "XMR"
    USDT = "USDT"
    USDC = "USDC"
    ADA = "ADA"
    DOT = "DOT"



class PaymentCreateRequestProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PaymentListProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PaymentListStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PaymentRequestProvider(StrEnum):
    """
    Payment provider
    * `nowpayments` - NowPayments
    """

    NOWPAYMENTS = "nowpayments"



class PaymentRequestStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class QueueActionAction(StrEnum):
    """
    Action to perform on queues
    * `clear` - clear
    * `clear_all` - clear_all
    * `purge` - purge
    * `purge_failed` - purge_failed
    * `flush` - flush
    """

    CLEAR = "clear"
    CLEAR_ALL = "clear_all"
    PURGE = "purge"
    PURGE_FAILED = "purge_failed"
    FLUSH = "flush"



class QueueActionRequestAction(StrEnum):
    """
    Action to perform on queues
    * `clear` - clear
    * `clear_all` - clear_all
    * `purge` - purge
    * `purge_failed` - purge_failed
    * `flush` - flush
    """

    CLEAR = "clear"
    CLEAR_ALL = "clear_all"
    PURGE = "purge"
    PURGE_FAILED = "purge_failed"
    FLUSH = "flush"



class SubscriptionStatus(StrEnum):
    """
    Subscription status
    * `active` - Active
    * `inactive` - Inactive
    * `suspended` - Suspended
    * `cancelled` - Cancelled
    * `expired` - Expired
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class SubscriptionTier(StrEnum):
    """
    Subscription tier
    * `free` - Free Tier
    * `basic` - Basic Tier
    * `pro` - Pro Tier
    * `enterprise` - Enterprise Tier
    """

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class SubscriptionListStatus(StrEnum):
    """
    Subscription status
    * `active` - Active
    * `inactive` - Inactive
    * `suspended` - Suspended
    * `cancelled` - Cancelled
    * `expired` - Expired
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class SubscriptionRequestStatus(StrEnum):
    """
    Subscription status
    * `active` - Active
    * `inactive` - Inactive
    * `suspended` - Suspended
    * `cancelled` - Cancelled
    * `expired` - Expired
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class SubscriptionRequestTier(StrEnum):
    """
    Subscription tier
    * `free` - Free Tier
    * `basic` - Basic Tier
    * `pro` - Pro Tier
    * `enterprise` - Enterprise Tier
    """

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class TicketStatus(StrEnum):
    """
    * `open` - Open
    * `waiting_for_user` - Waiting for User
    * `waiting_for_admin` - Waiting for Admin
    * `resolved` - Resolved
    * `closed` - Closed
    """

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class TicketRequestStatus(StrEnum):
    """
    * `open` - Open
    * `waiting_for_user` - Waiting for User
    * `waiting_for_admin` - Waiting for Admin
    * `resolved` - Resolved
    * `closed` - Closed
    """

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class TransactionTransactionType(StrEnum):
    """
    Type of transaction
    * `deposit` - Deposit
    * `withdrawal` - Withdrawal
    * `payment` - Payment
    * `refund` - Refund
    * `fee` - Fee
    * `bonus` - Bonus
    * `adjustment` - Adjustment
    """

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    BONUS = "bonus"
    ADJUSTMENT = "adjustment"



class WebhookEventStatus(StrEnum):
    """
    * `success` - Success
    * `failed` - Failed
    * `pending` - Pending
    * `retry` - Retry
    """

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RETRY = "retry"



class WebhookEventRequestStatus(StrEnum):
    """
    * `success` - Success
    * `failed` - Failed
    * `pending` - Pending
    * `retry` - Retry
    """

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RETRY = "retry"



class WorkerActionAction(StrEnum):
    """
    Action to perform on workers
    * `start` - start
    * `stop` - stop
    * `restart` - restart
    """

    START = "start"
    STOP = "stop"
    RESTART = "restart"



class WorkerActionRequestAction(StrEnum):
    """
    Action to perform on workers
    * `start` - start
    * `stop` - stop
    * `restart` - restart
    """

    START = "start"
    STOP = "stop"
    RESTART = "restart"



