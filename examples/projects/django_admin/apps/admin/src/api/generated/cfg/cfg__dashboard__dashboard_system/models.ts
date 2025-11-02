import * as Enums from "../enums";

/**
 * Serializer for overall system health status.
 * 
 * Response model (includes read-only fields).
 */
export interface SystemHealth {
  /** Overall system health status

  * `healthy` - healthy
  * `warning` - warning
  * `error` - error
  * `unknown` - unknown */
  overall_status: Enums.SystemHealthOverallStatus;
  /** Overall health percentage */
  overall_health_percentage: number;
  /** Health status of individual components */
  components: Array<SystemHealthItem>;
  /** Check timestamp (ISO format) */
  timestamp: string;
}

/**
 * Serializer for system performance metrics.
 * 
 * Response model (includes read-only fields).
 */
export interface SystemMetrics {
  /** CPU usage percentage */
  cpu_usage: number;
  /** Memory usage percentage */
  memory_usage: number;
  /** Disk usage percentage */
  disk_usage: number;
  /** Network incoming bandwidth */
  network_in: string;
  /** Network outgoing bandwidth */
  network_out: string;
  /** Average response time */
  response_time: string;
  /** System uptime */
  uptime: string;
}

/**
 * Serializer for system health status items. Maps to SystemHealthItem Pydantic
 * model.
 * 
 * Response model (includes read-only fields).
 */
export interface SystemHealthItem {
  /** Component name */
  component: string;
  /** Health status

  * `healthy` - healthy
  * `warning` - warning
  * `error` - error
  * `unknown` - unknown */
  status: Enums.SystemHealthItemStatus;
  /** Status description */
  description: string;
  /** Last check time (ISO format) */
  last_check: string;
  /** Health percentage (0-100) */
  health_percentage?: number | null;
}

