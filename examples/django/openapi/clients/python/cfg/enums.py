from enum import IntEnum, StrEnum


class Currency.currency_type(StrEnum):
    """Type of currency * `fiat` - Fiat Currency * `crypto` - Cryptocurrency"""

    FIAT = "fiat"
    CRYPTO = "crypto"



class CurrencyList.currency_type(StrEnum):
    """Type of currency * `fiat` - Fiat Currency * `crypto` - Cryptocurrency"""

    FIAT = "fiat"
    CRYPTO = "crypto"



class EmailLog.status(StrEnum):
    """* `pending` - Pending * `sent` - Sent * `failed` - Failed"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"



class LeadSubmission.contact_type(StrEnum):
    """* `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
- Phone * `other` - Other"""

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class LeadSubmissionRequest.contact_type(StrEnum):
    """* `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
- Phone * `other` - Other"""

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class NewsletterCampaign.status(StrEnum):
    """* `draft` - Draft * `sending` - Sending * `sent` - Sent * `failed` - Failed"""

    DRAFT = "draft"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"



class OTPRequestRequest.channel(StrEnum):
    """Delivery channel: 'email' or 'phone'. Auto-detected if not provided. *
`email` - Email * `phone` - Phone"""

    EMAIL = "email"
    PHONE = "phone"



class OTPVerifyRequest.channel(StrEnum):
    """Delivery channel: 'email' or 'phone'. Auto-detected if not provided. *
`email` - Email * `phone` - Phone"""

    EMAIL = "email"
    PHONE = "phone"



class PatchedLeadSubmissionRequest.contact_type(StrEnum):
    """* `email` - Email * `whatsapp` - WhatsApp * `telegram` - Telegram * `phone`
- Phone * `other` - Other"""

    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"



class PatchedPaymentRequest.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class PatchedPaymentRequest.status(StrEnum):
    """Current payment status * `pending` - Pending * `confirming` - Confirming *
`confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
`expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PatchedSubscriptionRequest.status(StrEnum):
    """Subscription status * `active` - Active * `inactive` - Inactive *
`suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class PatchedSubscriptionRequest.tier(StrEnum):
    """Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
Tier * `enterprise` - Enterprise Tier"""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class PatchedTicketRequest.status(StrEnum):
    """* `open` - Open * `waiting_for_user` - Waiting for User *
`waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
Closed"""

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class Payment.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class Payment.status(StrEnum):
    """Current payment status * `pending` - Pending * `confirming` - Confirming *
`confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
`expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PaymentCreate.currency_code(StrEnum):
    """Cryptocurrency to receive * `BTC` - Bitcoin * `ETH` - Ethereum * `LTC` -
Litecoin * `XMR` - Monero * `USDT` - Tether * `USDC` - USD Coin * `ADA` -
Cardano * `DOT` - Polkadot"""

    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    XMR = "XMR"
    USDT = "USDT"
    USDC = "USDC"
    ADA = "ADA"
    DOT = "DOT"



class PaymentCreate.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class PaymentCreateRequest.currency_code(StrEnum):
    """Cryptocurrency to receive * `BTC` - Bitcoin * `ETH` - Ethereum * `LTC` -
Litecoin * `XMR` - Monero * `USDT` - Tether * `USDC` - USD Coin * `ADA` -
Cardano * `DOT` - Polkadot"""

    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    XMR = "XMR"
    USDT = "USDT"
    USDC = "USDC"
    ADA = "ADA"
    DOT = "DOT"



class PaymentCreateRequest.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class PaymentList.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class PaymentList.status(StrEnum):
    """Current payment status * `pending` - Pending * `confirming` - Confirming *
`confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
`expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PaymentRequest.provider(StrEnum):
    """Payment provider * `nowpayments` - NowPayments"""

    NOWPAYMENTS = "nowpayments"



class PaymentRequest.status(StrEnum):
    """Current payment status * `pending` - Pending * `confirming` - Confirming *
`confirmed` - Confirmed * `completed` - Completed * `failed` - Failed *
`expired` - Expired * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class QueueAction.action(StrEnum):
    """Action to perform on queues * `clear` - clear * `clear_all` - clear_all *
`purge` - purge * `purge_failed` - purge_failed * `flush` - flush"""

    CLEAR = "clear"
    CLEAR_ALL = "clear_all"
    PURGE = "purge"
    PURGE_FAILED = "purge_failed"
    FLUSH = "flush"



class QueueActionRequest.action(StrEnum):
    """Action to perform on queues * `clear` - clear * `clear_all` - clear_all *
`purge` - purge * `purge_failed` - purge_failed * `flush` - flush"""

    CLEAR = "clear"
    CLEAR_ALL = "clear_all"
    PURGE = "purge"
    PURGE_FAILED = "purge_failed"
    FLUSH = "flush"



class Subscription.status(StrEnum):
    """Subscription status * `active` - Active * `inactive` - Inactive *
`suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class Subscription.tier(StrEnum):
    """Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
Tier * `enterprise` - Enterprise Tier"""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class SubscriptionList.status(StrEnum):
    """Subscription status * `active` - Active * `inactive` - Inactive *
`suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class SubscriptionRequest.status(StrEnum):
    """Subscription status * `active` - Active * `inactive` - Inactive *
`suspended` - Suspended * `cancelled` - Cancelled * `expired` - Expired"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"



class SubscriptionRequest.tier(StrEnum):
    """Subscription tier * `free` - Free Tier * `basic` - Basic Tier * `pro` - Pro
Tier * `enterprise` - Enterprise Tier"""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"



class Ticket.status(StrEnum):
    """* `open` - Open * `waiting_for_user` - Waiting for User *
`waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
Closed"""

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class TicketRequest.status(StrEnum):
    """* `open` - Open * `waiting_for_user` - Waiting for User *
`waiting_for_admin` - Waiting for Admin * `resolved` - Resolved * `closed` -
Closed"""

    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"



class Transaction.transaction_type(StrEnum):
    """Type of transaction * `deposit` - Deposit * `withdrawal` - Withdrawal *
`payment` - Payment * `refund` - Refund * `fee` - Fee * `bonus` - Bonus *
`adjustment` - Adjustment"""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    BONUS = "bonus"
    ADJUSTMENT = "adjustment"



class WorkerAction.action(StrEnum):
    """Action to perform on workers * `start` - start * `stop` - stop * `restart` -
restart"""

    START = "start"
    STOP = "stop"
    RESTART = "restart"



class WorkerActionRequest.action(StrEnum):
    """Action to perform on workers * `start` - start * `stop` - stop * `restart` -
restart"""

    START = "start"
    STOP = "stop"
    RESTART = "restart"



