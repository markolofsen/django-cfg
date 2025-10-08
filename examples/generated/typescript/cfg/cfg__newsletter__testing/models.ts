/**
 * Simple serializer for test email.
 * 
 * Request model (no read-only fields).
 */
export interface TestEmailRequest {
  email: string;
  subject?: string;
  message?: string;
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

