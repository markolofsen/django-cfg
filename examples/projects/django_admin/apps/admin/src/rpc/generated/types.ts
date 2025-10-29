/**
 * Generated TypeScript Types
 * Auto-generated - DO NOT EDIT
 */

export interface UserPresenceParams {
  /** User ID */
  user_id: string;
  /** Status: online, away, busy, offline */
  status: string;
}

export interface HealthCheckResult {
  /** System status: healthy, degraded, unhealthy */
  status: string;
  /** System uptime in seconds */
  uptime_seconds: number;
  /** Database status */
  database: string;
  /** Cache status */
  cache: string;
}

export interface HealthCheckParams {
  /** Include detailed system info */
  include_details?: boolean;
}

export interface UserPresenceResult {
  /** User ID */
  user_id: string;
  /** Current status */
  status: string;
  /** Last seen timestamp (ISO 8601) */
  last_seen: string;
}

