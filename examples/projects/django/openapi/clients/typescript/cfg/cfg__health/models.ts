/**
 * Health check response.
 * 
 * Response model (includes read-only fields).
 */
export interface HealthCheck {
  /** Health status: healthy or unhealthy */
  status: string;
  /** Configured wrapper URL */
  wrapper_url: string;
  /** Whether API key is configured */
  has_api_key: boolean;
  /** Current timestamp */
  timestamp: string;
}

/**
 * Serializer for quick health check response.
 * 
 * Response model (includes read-only fields).
 */
export interface QuickHealth {
  /** Quick health status: ok or error */
  status: string;
  /** Timestamp of the health check */
  timestamp: string;
  /** Error message if health check failed */
  error?: string;
}

