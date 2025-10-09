/**
 * Simple serializer for newsletter subscription.
 * 
 * Request model (no read-only fields).
 */
export interface SubscribeRequest {
  newsletter_id: number;
  email: string;
}

/**
 * Response for subscription.
 * 
 * Response model (includes read-only fields).
 */
export interface SubscribeResponse {
  success: boolean;
  message: string;
  subscription_id?: number;
}

/**
 * Generic error response.
 * 
 * Response model (includes read-only fields).
 */
export interface ErrorResponse {
  success?: boolean;
  message: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedNewsletterSubscriptionList {
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
  results: Array<NewsletterSubscription>;
}

/**
 * Simple serializer for unsubscribe.
 * 
 * Request model (no read-only fields).
 */
export interface UnsubscribeRequest {
  subscription_id: number;
}

/**
 * Generic success response.
 * 
 * Response model (includes read-only fields).
 */
export interface SuccessResponse {
  success: boolean;
  message: string;
}

/**
 * Serializer for NewsletterSubscription model.
 * 
 * Response model (includes read-only fields).
 */
export interface NewsletterSubscription {
  id: number;
  newsletter: number;
  newsletter_title: string;
  user?: number;
  user_email: string;
  email: string;
  is_active?: boolean;
  subscribed_at: string;
  unsubscribed_at?: string;
}

