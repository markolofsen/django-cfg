import * as Enums from "../enums";

/**
 * User balance serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface Balance {
  /** Current balance in USD */
  balance_usd: string;
  balance_display: string;
  /** Total amount deposited (lifetime) */
  total_deposited: string;
  /** Total amount withdrawn (lifetime) */
  total_withdrawn: string;
  /** When the last transaction occurred */
  last_transaction_at?: string | null;
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
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<PaymentList>;
}

/**
 * Detailed payment information.
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentDetail {
  /** Unique identifier for this record */
  id: string;
  /** Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID) */
  internal_payment_id: string;
  /** Payment amount in USD */
  amount_usd: string;
  currency_code: string;
  currency_name: string;
  currency_token: string;
  currency_network: string;
  /** Amount to pay in cryptocurrency */
  pay_amount?: string | null;
  /** Actual amount received in cryptocurrency */
  actual_amount?: string | null;
  /** Actual amount received in USD */
  actual_amount_usd?: string | null;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `partially_paid` - Partially Paid
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled */
  status: Enums.PaymentDetailStatus;
  status_display: string;
  /** Cryptocurrency payment address */
  pay_address?: string | null;
  /** Get QR code URL. */
  qr_code_url?: string | null;
  /** Payment page URL (if provided by provider) */
  payment_url?: string | null;
  /** Blockchain transaction hash */
  transaction_hash?: string | null;
  /** Get blockchain explorer link. */
  explorer_link?: string | null;
  /** Number of blockchain confirmations */
  confirmations_count: number;
  /** When this payment expires (typically 30 minutes) */
  expires_at?: string | null;
  /** When this payment was completed */
  completed_at?: string | null;
  /** When this record was created */
  created_at: string;
  is_completed: boolean;
  is_failed: boolean;
  is_expired: boolean;
  /** Payment description */
  description: string;
}

/**
 * Payment list item (lighter than detail).
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentList {
  /** Unique identifier for this record */
  id: string;
  /** Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID) */
  internal_payment_id: string;
  /** Payment amount in USD */
  amount_usd: string;
  currency_code: string;
  currency_token: string;
  /** Current payment status

  * `pending` - Pending
  * `confirming` - Confirming
  * `confirmed` - Confirmed
  * `completed` - Completed
  * `partially_paid` - Partially Paid
  * `failed` - Failed
  * `expired` - Expired
  * `cancelled` - Cancelled */
  status: Enums.PaymentListStatus;
  status_display: string;
  /** When this record was created */
  created_at: string;
  /** When this payment was completed */
  completed_at?: string | null;
}

