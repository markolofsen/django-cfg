/**
 * Simple serializer for bulk email.
 * 
 * Request model (no read-only fields).
 */
export interface BulkEmailRequest {
  recipients: Array<string>;
  subject: string;
  email_title: string;
  main_text: string;
  main_html_content?: string;
  button_text?: string;
  button_url?: string;
  secondary_text?: string;
}

/**
 * Response for bulk email sending.
 * 
 * Response model (includes read-only fields).
 */
export interface BulkEmailResponse {
  success: boolean;
  sent_count: number;
  failed_count: number;
  total_recipients: number;
  error?: string;
}

