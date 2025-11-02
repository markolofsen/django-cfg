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
 * List of gRPC methods with statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodList {
  /** Method statistics */
  methods: Array<MethodStatsSerializer>;
  /** Total number of methods */
  total_methods: number;
}

/**
 * Overview statistics for Centrifugo publishes.
 * 
 * Response model (includes read-only fields).
 */
export interface OverviewStats {
  /** Total publishes in period */
  total: number;
  /** Successful publishes */
  successful: number;
  /** Failed publishes */
  failed: number;
  /** Timeout publishes */
  timeout: number;
  /** Success rate percentage */
  success_rate: number;
  /** Average duration in milliseconds */
  avg_duration_ms: number;
  /** Average ACKs received */
  avg_acks_received: number;
  /** Statistics period in hours */
  period_hours: number;
}

/**
 * Recent gRPC requests list.
 * 
 * Response model (includes read-only fields).
 */
export interface RecentRequests {
  /** List of recent requests */
  requests: Array<Record<string, any>>;
  /** Number of requests returned */
  count: number;
  /** Total requests available */
  total_available: number;
  /** Current offset for pagination */
  offset?: number;
  /** Whether more results are available */
  has_more?: boolean;
}

/**
 * List of gRPC services with statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceList {
  /** Service statistics */
  services: Array<ServiceStatsSerializer>;
  /** Total number of services */
  total_services: number;
}

/**
 * Statistics for a single gRPC method.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodStatsSerializer {
  /** Method name */
  method_name: string;
  /** Service name */
  service_name: string;
  /** Total requests */
  total: number;
  /** Successful requests */
  successful: number;
  /** Error requests */
  errors: number;
  /** Average duration */
  avg_duration_ms: number;
  /** Last activity timestamp */
  last_activity_at: string | null;
}

/**
 * Statistics for a single gRPC service.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceStatsSerializer {
  /** Service name */
  service_name: string;
  /** Total requests */
  total: number;
  /** Successful requests */
  successful: number;
  /** Error requests */
  errors: number;
  /** Average duration */
  avg_duration_ms: number;
  /** Last activity timestamp */
  last_activity_at: string | null;
}

