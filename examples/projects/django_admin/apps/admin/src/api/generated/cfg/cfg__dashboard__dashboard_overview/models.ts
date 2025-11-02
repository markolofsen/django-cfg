import * as Enums from "../enums";

/**
 * Main serializer for dashboard overview endpoint. Uses typed serializers for
 * proper OpenAPI schema generation.
 * 
 * Response model (includes read-only fields).
 */
export interface DashboardOverview {
  /** Dashboard statistics cards */
  stat_cards: Array<StatCard>;
  system_health: Record<string, any>;
  /** Quick action buttons */
  quick_actions: Array<QuickAction>;
  /** Recent activity entries */
  recent_activity: Array<ActivityEntry>;
  system_metrics: Record<string, any>;
  user_statistics: Record<string, any>;
  /** Application statistics */
  app_statistics?: Array<AppStatistics>;
  /** Data timestamp (ISO format) */
  timestamp: string;
}

/**
 * Serializer for dashboard statistics cards. Maps to StatCard Pydantic model.
 * 
 * Response model (includes read-only fields).
 */
export interface StatCard {
  /** Card title */
  title: string;
  /** Main value to display */
  value: string;
  /** Material icon name */
  icon: string;
  /** Change indicator (e.g., '+12%') */
  change?: string | null;
  /** Change type

  * `positive` - positive
  * `negative` - negative
  * `neutral` - neutral */
  change_type?: Enums.StatCardChangeType;
  /** Additional description */
  description?: string | null;
  /** Card color theme */
  color?: string;
}

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
 * Serializer for quick action buttons. Maps to QuickAction Pydantic model.
 * 
 * Response model (includes read-only fields).
 */
export interface QuickAction {
  /** Action title */
  title: string;
  /** Action description */
  description: string;
  /** Material icon name */
  icon: string;
  /** Action URL */
  link: string;
  /** Button color theme

  * `primary` - primary
  * `success` - success
  * `warning` - warning
  * `danger` - danger
  * `secondary` - secondary
  * `info` - info
  * `default` - default */
  color?: Enums.QuickActionColor;
  /** Action category */
  category?: string;
}

/**
 * Serializer for recent activity entries.
 * 
 * Response model (includes read-only fields).
 */
export interface ActivityEntry {
  /** Activity ID */
  id: number;
  /** User who performed the action */
  user: string;
  /** Action type (created, updated, deleted, etc.) */
  action: string;
  /** Resource affected */
  resource: string;
  /** Activity timestamp (ISO format) */
  timestamp: string;
  /** Material icon name */
  icon: string;
  /** Icon color */
  color: string;
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
 * Serializer for user statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface UserStatistics {
  /** Total number of users */
  total_users: number;
  /** Active users (last 30 days) */
  active_users: number;
  /** New users (last 7 days) */
  new_users: number;
  /** Number of superusers */
  superusers: number;
}

/**
 * Serializer for application-specific statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface AppStatistics {
  /** Application name */
  app_name: string;
  /** Application statistics */
  statistics: Record<string, any>;
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

