/**
 * Serializer for health check response.
 * 
 * Response model (includes read-only fields).
 */
export interface HealthCheck {
  /** Overall health status: healthy, degraded, or unhealthy */
  status: string;
  /** Timestamp of the health check */
  timestamp: string;
  /** Service name */
  service: string;
  /** Django-CFG version */
  version: string;
  /** Detailed health checks for databases, cache, and system */
  checks: Record<string, any>;
  /** Environment information */
  environment: Record<string, any>;
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

