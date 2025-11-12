/**
 * gRPC health check response.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCHealthCheck {
  /** Health status: healthy or unhealthy */
  status: string;
  /** Configured gRPC server host */
  server_host: string;
  /** Configured gRPC server port */
  server_port: number;
  /** Whether gRPC is enabled */
  enabled: boolean;
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
  methods: Array<MethodStats>;
  /** Total number of methods */
  total_methods: number;
}

/**
 * Overview statistics for gRPC requests.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCOverviewStats {
  /** Total requests in period */
  total: number;
  /** Successful requests */
  successful: number;
  /** Error requests */
  errors: number;
  /** Cancelled requests */
  cancelled: number;
  /** Timeout requests */
  timeout: number;
  /** Success rate percentage */
  success_rate: number;
  /** Average duration in milliseconds */
  avg_duration_ms: number;
  /** 95th percentile duration in milliseconds */
  p95_duration_ms: number | null;
  /** Statistics period in hours */
  period_hours: number;
  server: GRPCServerStatus;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedRecentRequestList {
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
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<RecentRequest>;
}

/**
 * Statistics for a single gRPC method.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodStats {
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
 * gRPC server status and information for overview stats.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCServerStatus {
  /** Server status (running, stopped, error, etc.) */
  status: string;
  /** Whether server is currently running */
  is_running: boolean;
  /** Server host address */
  host: string;
  /** Server port */
  port: number;
  /** Full server address (host:port) */
  address: string;
  /** Process ID */
  pid: number | null;
  /** Server start time */
  started_at: string | null;
  /** Server uptime in seconds */
  uptime_seconds: number;
  /** Human-readable uptime */
  uptime_display: string;
  /** Number of registered services */
  registered_services_count: number;
  /** Whether reflection is enabled */
  enable_reflection: boolean;
  /** Whether health check is enabled */
  enable_health_check: boolean;
  /** Last heartbeat timestamp */
  last_heartbeat: string | null;
  /** List of registered services with stats */
  services: Array<GRPCRegisteredService>;
  /** Whether all services are healthy (no recent errors) */
  services_healthy: boolean;
}

/**
 * Recent request information.
 * 
 * Request model (no read-only fields).
 */
export interface RecentRequest {
  /** Database ID */
  id: number;
  /** Request ID */
  request_id: string;
  /** Service name */
  service_name: string;
  /** Method name */
  method_name: string;
  /** Request status */
  status: string;
  /** Duration in milliseconds */
  duration_ms?: number;
  /** gRPC status code */
  grpc_status_code?: string;
  /** Error message if failed */
  error_message?: string;
  /** Request timestamp */
  created_at: string;
  /** Client IP address */
  client_ip?: string;
  /** User ID (if authenticated) */
  user_id?: number | null;
  /** Username (if authenticated) */
  username?: string | null;
  /** Whether request was authenticated */
  is_authenticated?: boolean;
  /** API Key ID (if used) */
  api_key_id?: number | null;
  /** API Key name (if used) */
  api_key_name?: string | null;
}

/**
 * Information about a registered gRPC service.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCRegisteredService {
  /** Service name */
  name: string;
  /** Full service name with package */
  full_name: string;
  /** Number of methods in service */
  methods_count: number;
  /** Total requests to this service in period */
  request_count: number;
  /** Error requests to this service in period */
  error_count: number;
  /** Success rate percentage for this service */
  success_rate: number;
}

