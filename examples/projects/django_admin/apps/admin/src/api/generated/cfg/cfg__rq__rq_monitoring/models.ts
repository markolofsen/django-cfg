/**
 * RQ configuration serializer. Returns current RQ configuration from
 * django-cfg.
 * 
 * Response model (includes read-only fields).
 */
export interface RQConfig {
  /** RQ enabled status */
  enabled: boolean;
  /** Configured queues */
  queues: Record<string, any>;
  /** Async mode enabled */
  async_mode?: boolean;
  /** Show admin link */
  show_admin_link?: boolean;
  /** Prometheus metrics enabled */
  prometheus_enabled?: boolean;
  /** API token is configured */
  api_token_configured?: boolean;
  /** Scheduled tasks from django-cfg config */
  schedules?: Array<ScheduleInfo>;
}

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
 * Schedule information in config response.
 * 
 * Response model (includes read-only fields).
 */
export interface ScheduleInfo {
  func: string;
  queue: string;
  cron?: string | null;
  interval?: number | null;
  scheduled_time?: string | null;
  description?: string | null;
  timeout?: number | null;
  result_ttl?: number | null;
  repeat?: number | null;
}

