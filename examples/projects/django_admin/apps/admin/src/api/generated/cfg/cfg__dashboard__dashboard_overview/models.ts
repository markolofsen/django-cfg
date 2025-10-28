/**
 * Main serializer for dashboard overview endpoint. Uses DictField to avoid
 * allOf generation in OpenAPI.
 * 
 * Response model (includes read-only fields).
 */
export interface DashboardOverview {
  /** Dashboard statistics cards */
  stat_cards: Array<Record<string, any>>;
  /** System health status */
  system_health: Array<Record<string, any>>;
  /** Quick action buttons */
  quick_actions: Array<Record<string, any>>;
  /** Recent activity entries */
  recent_activity: Array<Record<string, any>>;
  /** System performance metrics */
  system_metrics: Record<string, any>;
  /** User statistics */
  user_statistics: Record<string, any>;
  /** Data timestamp (ISO format) */
  timestamp: string;
}

