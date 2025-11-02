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

