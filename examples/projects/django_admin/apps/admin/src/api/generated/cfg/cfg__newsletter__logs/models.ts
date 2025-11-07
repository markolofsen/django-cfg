import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedEmailLogList {
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
  results: Array<EmailLog>;
}

/**
 * Serializer for EmailLog model.
 * 
 * Response model (includes read-only fields).
 */
export interface EmailLog {
  id: string;
  user?: number | null;
  user_email: string;
  newsletter?: number | null;
  newsletter_title: string;
  /** Comma-separated email addresses */
  recipient: string;
  subject: string;
  body: string;
  /** * `pending` - Pending
  * `sent` - Sent
  * `failed` - Failed */
  status: Enums.EmailLogStatus;
  created_at: string;
  sent_at?: string | null;
  error_message?: string | null;
}

