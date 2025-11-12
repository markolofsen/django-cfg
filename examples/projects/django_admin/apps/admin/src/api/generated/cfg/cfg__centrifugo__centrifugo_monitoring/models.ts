/**
 * List of channel statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ChannelList {
  /** Channel statistics */
  channels: Array<ChannelStats>;
  /** Total number of channels */
  total_channels: number;
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
 * Overview statistics for Centrifugo publishes.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoOverviewStats {
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
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPublishList {
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
  results: Array<Publish>;
}

/**
 * Timeline response with hourly/daily breakdown for DRF.
 * 
 * Response model (includes read-only fields).
 */
export interface TimelineResponse {
  timeline: Array<TimelineItem>;
  period_hours: number;
  interval: string;
}

/**
 * Statistics per channel.
 * 
 * Response model (includes read-only fields).
 */
export interface ChannelStats {
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
  last_activity_at: string | null;
}

/**
 * Single publish item for DRF pagination.
 * 
 * Response model (includes read-only fields).
 */
export interface Publish {
  message_id: string;
  channel: string;
  status: string;
  wait_for_ack: boolean;
  acks_received: number;
  acks_expected: number | null;
  duration_ms: number | null;
  created_at: string;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
}

/**
 * Single timeline data point for DRF.
 * 
 * Response model (includes read-only fields).
 */
export interface TimelineItem {
  timestamp: string;
  count: number;
  successful: number;
  failed: number;
  timeout: number;
}

