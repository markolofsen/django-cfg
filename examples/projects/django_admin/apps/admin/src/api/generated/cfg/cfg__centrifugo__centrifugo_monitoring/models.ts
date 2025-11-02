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
 * Recent publishes list.
 * 
 * Response model (includes read-only fields).
 */
export interface RecentPublishes {
  /** List of recent publishes */
  publishes: Array<Record<string, any>>;
  /** Number of publishes returned */
  count: number;
  /** Total publishes available */
  total_available: number;
  /** Current offset for pagination */
  offset?: number;
  /** Whether more results are available */
  has_more?: boolean;
}

/**
 * List of channel statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ChannelList {
  /** Channel statistics */
  channels: Array<ChannelStatsSerializer>;
  /** Total number of channels */
  total_channels: number;
}

/**
 * Statistics per channel.
 * 
 * Response model (includes read-only fields).
 */
export interface ChannelStatsSerializer {
  /** Channel name */
  channel: string;
  /** Total publishes to this channel */
  total: number;
  /** Successful publishes */
  successful: number;
  /** Failed publishes */
  failed: number;
  /** Average duration */
  avg_duration_ms: number;
  /** Average ACKs received */
  avg_acks: number;
  /** Last activity timestamp (ISO format) */
  last_activity_at?: string | null;
}

