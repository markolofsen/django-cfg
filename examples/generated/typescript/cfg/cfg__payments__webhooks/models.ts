/**
 * Serializer for webhook processing response. Standard response format for all
 * webhook endpoints.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookResponse {
  /** Whether webhook was processed successfully */
  success: boolean;
  /** Processing result message */
  message: string;
  /** Internal payment ID */
  payment_id?: string;
  /** Provider payment ID */
  provider_payment_id?: string;
  /** Processing timestamp */
  processed_at?: string;
}

/**
 * Serializer for webhook processing response. Standard response format for all
 * webhook endpoints.
 * 
 * Request model (no read-only fields).
 */
export interface WebhookResponseRequest {
  /** Whether webhook was processed successfully */
  success: boolean;
  /** Processing result message */
  message: string;
  /** Internal payment ID */
  payment_id?: string;
  /** Provider payment ID */
  provider_payment_id?: string;
  /** Processing timestamp */
  processed_at?: string;
}

/**
 * Serializer for webhook health check response.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookHealth {
  /** Health status */
  status: string;
  /** Check timestamp */
  timestamp: string;
  /** Provider health status */
  providers: string;
}

/**
 * Serializer for supported providers response.
 * 
 * Response model (includes read-only fields).
 */
export interface SupportedProviders {
  /** Request success status */
  success: boolean;
  /** List of supported providers */
  providers: string;
  /** Total number of providers */
  total_count: number;
  /** Response timestamp */
  timestamp: string;
}

/**
 * Serializer for webhook statistics response.
 * 
 * Response model (includes read-only fields).
 */
export interface WebhookStats {
  /** Total webhooks processed */
  total_webhooks: number;
  /** Successfully processed webhooks */
  successful_webhooks: number;
  /** Failed webhook processing attempts */
  failed_webhooks: number;
  /** Success rate percentage */
  success_rate: number;
  /** Per-provider statistics */
  providers: string;
}

