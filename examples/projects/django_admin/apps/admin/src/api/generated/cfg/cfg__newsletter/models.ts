import * as Enums from "../enums";

/**
 * Serializer for NewsletterCampaign model.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedNewsletterCampaignRequest {
  newsletter?: number;
  subject?: string;
  email_title?: string;
  main_text?: string;
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
  sent_at?: string | null;
  recipient_count: number;
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
 * Simple serializer for unsubscribe.
 * 
 * Response model (includes read-only fields).
 */
export interface Unsubscribe {
  subscription_id: number;
}

/**
 * Simple serializer for unsubscribe.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedUnsubscribeRequest {
  subscription_id?: number;
}

