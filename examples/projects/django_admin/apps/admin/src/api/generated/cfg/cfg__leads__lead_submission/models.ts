import * as Enums from "../enums";

/**
 * Serializer for lead form submission from frontend.
 * 
 * Request model (no read-only fields).
 */
export interface LeadSubmissionRequest {
  name: string;
  email: string;
  company?: string | null;
  company_site?: string | null;
  /** * `email` - Email
  * `whatsapp` - WhatsApp
  * `telegram` - Telegram
  * `phone` - Phone
  * `other` - Other */
  contact_type?: Enums.LeadSubmissionRequestContactType;
  contact_value?: string | null;
  subject?: string | null;
  message: string;
  extra?: string | null;
  /** Frontend URL where form was submitted */
  site_url: string;
}

/**
 * Response serializer for successful lead submission.
 * 
 * Response model (includes read-only fields).
 */
export interface LeadSubmissionResponse {
  success: boolean;
  message: string;
  lead_id: number;
}

/**
 * Response serializer for lead submission errors.
 * 
 * Response model (includes read-only fields).
 */
export interface LeadSubmissionError {
  success: boolean;
  error: string;
  details?: Record<string, string>;
}

