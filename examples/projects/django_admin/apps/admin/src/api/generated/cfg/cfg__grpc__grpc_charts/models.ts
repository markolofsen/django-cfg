/**
 * Combined dashboard charts data.
 * 
 * Response model (includes read-only fields).
 */
export interface DashboardCharts {
  server_uptime: ServerUptimeChart;
  request_volume: RequestVolumeChart;
  response_time: ResponseTimeChart;
  service_activity: ServiceActivityChart;
  error_distribution: ErrorDistributionChart;
  /** Period in hours for all charts */
  period_hours: number;
  /** When data was generated */
  generated_at: string;
}

/**
 * Error distribution chart data.
 * 
 * Response model (includes read-only fields).
 */
export interface ErrorDistributionChart {
  /** Chart title */
  title?: string;
  /** Error distribution data */
  error_types?: Array<ErrorDistributionDataPoint>;
  /** Period in hours */
  period_hours: number;
  /** Total number of errors */
  total_errors: number;
  /** Most common error code */
  most_common_error?: string | null;
}

/**
 * Request volume over time chart data.
 * 
 * Response model (includes read-only fields).
 */
export interface RequestVolumeChart {
  /** Chart title */
  title?: string;
  /** Volume data points */
  data_points?: Array<RequestVolumeDataPoint>;
  /** Period in hours */
  period_hours: number;
  /** Data granularity */
  granularity: string;
  /** Total requests in period */
  total_requests: number;
  /** Average success rate */
  avg_success_rate: number;
}

/**
 * Response time over time chart data.
 * 
 * Response model (includes read-only fields).
 */
export interface ResponseTimeChart {
  /** Chart title */
  title?: string;
  /** Response time data points */
  data_points?: Array<ResponseTimeDataPoint>;
  /** Period in hours */
  period_hours: number;
  /** Data granularity */
  granularity: string;
  /** Overall average duration */
  overall_avg_ms: number;
  /** Overall P95 duration */
  overall_p95_ms: number;
}

/**
 * Server lifecycle events timeline.
 * 
 * Response model (includes read-only fields).
 */
export interface ServerLifecycleChart {
  /** Chart title */
  title?: string;
  /** Lifecycle events */
  events?: Array<ServerLifecycleEvent>;
  /** Period in hours */
  period_hours: number;
  /** Total number of events */
  total_events: number;
  /** Number of server restarts */
  restart_count: number;
  /** Number of error events */
  error_count: number;
}

/**
 * Server uptime over time chart data.
 * 
 * Response model (includes read-only fields).
 */
export interface ServerUptimeChart {
  /** Chart title */
  title?: string;
  /** Uptime data points */
  data_points?: Array<ServerUptimeDataPoint>;
  /** Period in hours */
  period_hours: number;
  /** Data granularity */
  granularity: string;
  /** Total unique servers in period */
  total_servers: number;
  /** Currently running servers */
  currently_running: number;
}

/**
 * Service activity comparison chart data.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceActivityChart {
  /** Chart title */
  title?: string;
  /** Service activity data */
  services?: Array<ServiceActivityDataPoint>;
  /** Period in hours */
  period_hours: number;
  /** Total number of services */
  total_services: number;
  /** Most active service name */
  most_active_service?: string | null;
}

/**
 * Error distribution data point.
 * 
 * Response model (includes read-only fields).
 */
export interface ErrorDistributionDataPoint {
  /** gRPC status code */
  error_code: string;
  /** Number of occurrences */
  count: number;
  /** Percentage of total errors */
  percentage: number;
  /** Service name if filtered */
  service_name?: string | null;
}

/**
 * Request volume data point.
 * 
 * Response model (includes read-only fields).
 */
export interface RequestVolumeDataPoint {
  /** ISO timestamp */
  timestamp: string;
  /** Total requests in period */
  total_requests: number;
  /** Successful requests */
  successful_requests: number;
  /** Failed requests */
  failed_requests: number;
  /** Success rate percentage */
  success_rate: number;
}

/**
 * Response time statistics data point.
 * 
 * Response model (includes read-only fields).
 */
export interface ResponseTimeDataPoint {
  /** ISO timestamp */
  timestamp: string;
  /** Average duration */
  avg_duration_ms: number;
  /** P50 percentile */
  p50_duration_ms: number;
  /** P95 percentile */
  p95_duration_ms: number;
  /** P99 percentile */
  p99_duration_ms: number;
  /** Minimum duration */
  min_duration_ms: number;
  /** Maximum duration */
  max_duration_ms: number;
}

/**
 * Server lifecycle event.
 * 
 * Response model (includes read-only fields).
 */
export interface ServerLifecycleEvent {
  /** Event timestamp */
  timestamp: string;
  /** Event type (started, stopped, error) */
  event_type: string;
  /** Server address */
  server_address: string;
  /** Server process ID */
  server_pid: number;
  /** Uptime at event time (for stop events) */
  uptime_seconds?: number | null;
  /** Error message if applicable */
  error_message?: string | null;
}

/**
 * Server uptime data point.
 * 
 * Response model (includes read-only fields).
 */
export interface ServerUptimeDataPoint {
  /** ISO timestamp */
  timestamp: string;
  /** Number of running servers */
  server_count: number;
  /** List of server addresses */
  servers?: Array<string>;
}

/**
 * Service activity data point.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceActivityDataPoint {
  /** Service name */
  service_name: string;
  /** Number of requests */
  request_count: number;
  /** Success rate percentage */
  success_rate: number;
  /** Average duration */
  avg_duration_ms: number;
}

