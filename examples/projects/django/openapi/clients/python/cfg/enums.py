from enum import IntEnum, Enum

# Python 3.10 compatibility: StrEnum was added in Python 3.11
# Use str + Enum instead for backward compatibility
class StrEnum(str, Enum):
    """String Enum for Python 3.10+ compatibility"""
    pass


class ArchiveItemContentType(StrEnum):
    """
    Content classification
    * `document` - Document
    * `code` - Code
    * `image` - Image
    * `data` - Data
    * `archive` - Archive
    * `unknown` - Unknown
    """

    DOCUMENT = "document"
    CODE = "code"
    IMAGE = "image"
    DATA = "data"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"



class ArchiveItemChunkChunkType(StrEnum):
    """
    Type of content in chunk
    * `text` - Text
    * `code` - Code
    * `heading` - Heading
    * `metadata` - Metadata
    * `table` - Table
    * `list` - List
    """

    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    METADATA = "metadata"
    TABLE = "table"
    LIST = "list"



class ArchiveItemChunkDetailChunkType(StrEnum):
    """
    Type of content in chunk
    * `text` - Text
    * `code` - Code
    * `heading` - Heading
    * `metadata` - Metadata
    * `table` - Table
    * `list` - List
    """

    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    METADATA = "metadata"
    TABLE = "table"
    LIST = "list"



class ArchiveItemChunkRequestChunkType(StrEnum):
    """
    Type of content in chunk
    * `text` - Text
    * `code` - Code
    * `heading` - Heading
    * `metadata` - Metadata
    * `table` - Table
    * `list` - List
    """

    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    METADATA = "metadata"
    TABLE = "table"
    LIST = "list"



class ArchiveItemDetailContentType(StrEnum):
    """
    Content classification
    * `document` - Document
    * `code` - Code
    * `image` - Image
    * `data` - Data
    * `archive` - Archive
    * `unknown` - Unknown
    """

    DOCUMENT = "document"
    CODE = "code"
    IMAGE = "image"
    DATA = "data"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"



class ArchiveSearchRequestRequestContentTypesItems(StrEnum):
    """
    * `document` - Document
    * `code` - Code
    * `image` - Image
    * `data` - Data
    * `archive` - Archive
    * `unknown` - Unknown
    """

    DOCUMENT = "document"
    CODE = "code"
    IMAGE = "image"
    DATA = "data"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"



class ArchiveSearchRequestRequestChunkTypesItems(StrEnum):
    """
    * `text` - Text
    * `code` - Code
    * `heading` - Heading
    * `metadata` - Metadata
    * `table` - Table
    * `list` - List
    """

    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    METADATA = "metadata"
    TABLE = "table"
    LIST = "list"



class ChatMessageRole(StrEnum):
    """
    Message sender role
    * `user` - User
    * `assistant` - Assistant
    * `system` - System
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"



class DocumentArchiveArchiveType(StrEnum):
    """
    Archive format
    * `zip` - ZIP
    * `tar` - TAR
    * `tar.gz` - TAR GZ
    * `tar.bz2` - TAR BZ2
    """

    ZIP = "zip"
    TAR = "tar"
    TAR.GZ = "tar.gz"
    TAR.BZ2 = "tar.bz2"



class DocumentArchiveProcessingStatus(StrEnum):
    """
    * `pending` - Pending
    * `processing` - Processing
    * `completed` - Completed
    * `failed` - Failed
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"



class DocumentArchiveDetailArchiveType(StrEnum):
    """
    Archive format
    * `zip` - ZIP
    * `tar` - TAR
    * `tar.gz` - TAR GZ
    * `tar.bz2` - TAR BZ2
    """

    ZIP = "zip"
    TAR = "tar"
    TAR.GZ = "tar.gz"
    TAR.BZ2 = "tar.bz2"



class DocumentArchiveDetailProcessingStatus(StrEnum):
    """
    * `pending` - Pending
    * `processing` - Processing
    * `completed` - Completed
    * `failed` - Failed
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"



class DocumentArchiveListArchiveType(StrEnum):
    """
    Archive format
    * `zip` - ZIP
    * `tar` - TAR
    * `tar.gz` - TAR GZ
    * `tar.bz2` - TAR BZ2
    """

    ZIP = "zip"
    TAR = "tar"
    TAR.GZ = "tar.gz"
    TAR.BZ2 = "tar.bz2"



class DocumentArchiveListProcessingStatus(StrEnum):
    """
    * `pending` - Pending
    * `processing` - Processing
    * `completed` - Completed
    * `failed` - Failed
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"



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



class PatchedArchiveItemChunkRequestChunkType(StrEnum):
    """
    Type of content in chunk
    * `text` - Text
    * `code` - Code
    * `heading` - Heading
    * `metadata` - Metadata
    * `table` - Table
    * `list` - List
    """

    TEXT = "text"
    CODE = "code"
    HEADING = "heading"
    METADATA = "metadata"
    TABLE = "table"
    LIST = "list"



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



class PaymentDetailStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `partially_paid` - Partially Paid
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    PARTIALLY_PAID = "partially_paid"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"



class PaymentListStatus(StrEnum):
    """
    Current payment status
    * `pending` - Pending
    * `confirming` - Confirming
    * `confirmed` - Confirmed
    * `completed` - Completed
    * `partially_paid` - Partially Paid
    * `failed` - Failed
    * `expired` - Expired
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    PARTIALLY_PAID = "partially_paid"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"



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



class QuickActionColor(StrEnum):
    """
    Button color theme
    * `primary` - primary
    * `success` - success
    * `warning` - warning
    * `danger` - danger
    * `secondary` - secondary
    """

    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    SECONDARY = "secondary"



class StatCardChangeType(StrEnum):
    """
    Change type
    * `positive` - positive
    * `negative` - negative
    * `neutral` - neutral
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"



class SystemHealthOverallStatus(StrEnum):
    """
    Overall system health status
    * `healthy` - healthy
    * `warning` - warning
    * `error` - error
    * `unknown` - unknown
    """

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"



class SystemHealthItemStatus(StrEnum):
    """
    Health status
    * `healthy` - healthy
    * `warning` - warning
    * `error` - error
    * `unknown` - unknown
    """

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"



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



