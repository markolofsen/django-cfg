import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedLeadSubmissionList {
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
  results: Array<LeadSubmission>;
}

/**
 * Serializer for lead form submission from frontend.
 * 
 * Request model (no read-only fields).
 */
export interface LeadSubmissionRequest {
  name: string;
  email: string;
  company?: string;
  company_site?: string;
  /** * `email` - Email
  * `whatsapp` - WhatsApp
  * `telegram` - Telegram
  * `phone` - Phone
  * `other` - Other */
  contact_type?: Enums.LeadSubmissionRequestContactType;
  contact_value?: string;
  subject?: string;
  message: string;
  extra?: string;
  /** Frontend URL where form was submitted */
  site_url: string;
}

/**
 * Serializer for lead form submission from frontend.
 * 
 * Response model (includes read-only fields).
 */
export interface LeadSubmission {
  name: string;
  email: string;
  company?: string;
  company_site?: string;
  /** * `email` - Email
  * `whatsapp` - WhatsApp
  * `telegram` - Telegram
  * `phone` - Phone
  * `other` - Other */
  contact_type?: Enums.LeadSubmissionContactType;
  contact_value?: string;
  subject?: string;
  message: string;
  extra?: string;
  /** Frontend URL where form was submitted */
  site_url: string;
}

/**
 * Serializer for lead form submission from frontend.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedLeadSubmissionRequest {
  name?: string;
  email?: string;
  company?: string;
  company_site?: string;
  /** * `email` - Email
  * `whatsapp` - WhatsApp
  * `telegram` - Telegram
  * `phone` - Phone
  * `other` - Other */
  contact_type?: Enums.PatchedLeadSubmissionRequestContactType;
  contact_value?: string;
  subject?: string;
  message?: string;
  extra?: string;
  /** Frontend URL where form was submitted */
  site_url?: string;
}

