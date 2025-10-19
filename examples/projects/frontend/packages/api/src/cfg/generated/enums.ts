/**
 * Content classification
 * * `document` - Document
 * * `code` - Code
 * * `image` - Image
 * * `data` - Data
 * * `archive` - Archive
 * * `unknown` - Unknown
 */
export enum ArchiveItemContentType {
  DOCUMENT = "document",
  CODE = "code",
  IMAGE = "image",
  DATA = "data",
  ARCHIVE = "archive",
  UNKNOWN = "unknown",
}

/**
 * Type of content in chunk
 * * `text` - Text
 * * `code` - Code
 * * `heading` - Heading
 * * `metadata` - Metadata
 * * `table` - Table
 * * `list` - List
 */
export enum ArchiveItemChunkChunkType {
  TEXT = "text",
  CODE = "code",
  HEADING = "heading",
  METADATA = "metadata",
  TABLE = "table",
  LIST = "list",
}

/**
 * Type of content in chunk
 * * `text` - Text
 * * `code` - Code
 * * `heading` - Heading
 * * `metadata` - Metadata
 * * `table` - Table
 * * `list` - List
 */
export enum ArchiveItemChunkDetailChunkType {
  TEXT = "text",
  CODE = "code",
  HEADING = "heading",
  METADATA = "metadata",
  TABLE = "table",
  LIST = "list",
}

/**
 * Type of content in chunk
 * * `text` - Text
 * * `code` - Code
 * * `heading` - Heading
 * * `metadata` - Metadata
 * * `table` - Table
 * * `list` - List
 */
export enum ArchiveItemChunkRequestChunkType {
  TEXT = "text",
  CODE = "code",
  HEADING = "heading",
  METADATA = "metadata",
  TABLE = "table",
  LIST = "list",
}

/**
 * Content classification
 * * `document` - Document
 * * `code` - Code
 * * `image` - Image
 * * `data` - Data
 * * `archive` - Archive
 * * `unknown` - Unknown
 */
export enum ArchiveItemDetailContentType {
  DOCUMENT = "document",
  CODE = "code",
  IMAGE = "image",
  DATA = "data",
  ARCHIVE = "archive",
  UNKNOWN = "unknown",
}

/**
 * * `document` - Document
 * * `code` - Code
 * * `image` - Image
 * * `data` - Data
 * * `archive` - Archive
 * * `unknown` - Unknown
 */
export enum ArchiveSearchRequestRequestContentTypesItems {
  DOCUMENT = "document",
  CODE = "code",
  IMAGE = "image",
  DATA = "data",
  ARCHIVE = "archive",
  UNKNOWN = "unknown",
}

/**
 * * `text` - Text
 * * `code` - Code
 * * `heading` - Heading
 * * `metadata` - Metadata
 * * `table` - Table
 * * `list` - List
 */
export enum ArchiveSearchRequestRequestChunkTypesItems {
  TEXT = "text",
  CODE = "code",
  HEADING = "heading",
  METADATA = "metadata",
  TABLE = "table",
  LIST = "list",
}

/**
 * Message sender role
 * * `user` - User
 * * `assistant` - Assistant
 * * `system` - System
 */
export enum ChatMessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
}

/**
 * Archive format
 * * `zip` - ZIP
 * * `tar` - TAR
 * * `tar.gz` - TAR GZ
 * * `tar.bz2` - TAR BZ2
 */
export enum DocumentArchiveArchiveType {
  ZIP = "zip",
  TAR = "tar",
  TAR_DOT_GZ = "tar.gz",
  TAR_DOT_BZ2 = "tar.bz2",
}

/**
 * * `pending` - Pending
 * * `processing` - Processing
 * * `completed` - Completed
 * * `failed` - Failed
 * * `cancelled` - Cancelled
 */
export enum DocumentArchiveProcessingStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

/**
 * Archive format
 * * `zip` - ZIP
 * * `tar` - TAR
 * * `tar.gz` - TAR GZ
 * * `tar.bz2` - TAR BZ2
 */
export enum DocumentArchiveDetailArchiveType {
  ZIP = "zip",
  TAR = "tar",
  TAR_DOT_GZ = "tar.gz",
  TAR_DOT_BZ2 = "tar.bz2",
}

/**
 * * `pending` - Pending
 * * `processing` - Processing
 * * `completed` - Completed
 * * `failed` - Failed
 * * `cancelled` - Cancelled
 */
export enum DocumentArchiveDetailProcessingStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

/**
 * Archive format
 * * `zip` - ZIP
 * * `tar` - TAR
 * * `tar.gz` - TAR GZ
 * * `tar.bz2` - TAR BZ2
 */
export enum DocumentArchiveListArchiveType {
  ZIP = "zip",
  TAR = "tar",
  TAR_DOT_GZ = "tar.gz",
  TAR_DOT_BZ2 = "tar.bz2",
}

/**
 * * `pending` - Pending
 * * `processing` - Processing
 * * `completed` - Completed
 * * `failed` - Failed
 * * `cancelled` - Cancelled
 */
export enum DocumentArchiveListProcessingStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
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
 * Type of content in chunk
 * * `text` - Text
 * * `code` - Code
 * * `heading` - Heading
 * * `metadata` - Metadata
 * * `table` - Table
 * * `list` - List
 */
export enum PatchedArchiveItemChunkRequestChunkType {
  TEXT = "text",
  CODE = "code",
  HEADING = "heading",
  METADATA = "metadata",
  TABLE = "table",
  LIST = "list",
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
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `partially_paid` - Partially Paid
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 */
export enum PaymentDetailStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  PARTIALLY_PAID = "partially_paid",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
}

/**
 * Current payment status
 * * `pending` - Pending
 * * `confirming` - Confirming
 * * `confirmed` - Confirmed
 * * `completed` - Completed
 * * `partially_paid` - Partially Paid
 * * `failed` - Failed
 * * `expired` - Expired
 * * `cancelled` - Cancelled
 */
export enum PaymentListStatus {
  PENDING = "pending",
  CONFIRMING = "confirming",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  PARTIALLY_PAID = "partially_paid",
  FAILED = "failed",
  EXPIRED = "expired",
  CANCELLED = "cancelled",
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

