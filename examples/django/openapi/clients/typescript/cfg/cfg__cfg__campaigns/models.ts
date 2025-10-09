import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedNewsletterCampaignList {
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
  results: Array<NewsletterCampaign>;
}

/**
 * Serializer for NewsletterCampaign model.
 * 
 * Request model (no read-only fields).
 */
export interface NewsletterCampaignRequest {
  newsletter: number;
  subject: string;
  email_title: string;
  main_text: string;
  main_html_content?: string;
  button_text?: string;
  button_url?: string;
  secondary_text?: string;
}

/**
 * Serializer for NewsletterCampaign model.
 * 
 * Response model (includes read-only fields).
 */
export interface NewsletterCampaign {
  id: number;
  newsletter: number;
  newsletter_title: string;
  subject: string;
  email_title: string;
  main_text: string;
  main_html_content?: string;
  button_text?: string;
  button_url?: string;
  secondary_text?: string;
  /** * `draft` - Draft
  * `sending` - Sending
  * `sent` - Sent
  * `failed` - Failed */
  status: Enums.NewsletterCampaignStatus;
  created_at: string;
  sent_at?: string;
  recipient_count: number;
}

/**
 * Simple serializer for sending campaign.
 * 
 * Request model (no read-only fields).
 */
export interface SendCampaignRequest {
  campaign_id: number;
}

/**
 * Response for sending campaign.
 * 
 * Response model (includes read-only fields).
 */
export interface SendCampaignResponse {
  success: boolean;
  message?: string;
  sent_count?: number;
  error?: string;
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

