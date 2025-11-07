/**
 * Request to list active channels.
 * 
 * Request model (no read-only fields).
 */
export interface CentrifugoChannelsRequestRequest {
  /** Pattern to filter channels (e.g., 'user:*') */
  pattern?: string | null;
}

/**
 * List of active channels response.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoChannelsResponse {
  error?: CentrifugoError;
  result?: CentrifugoChannelsResult;
}

/**
 * Request to get channel history.
 * 
 * Request model (no read-only fields).
 */
export interface CentrifugoHistoryRequestRequest {
  /** Channel name */
  channel: string;
  /** Maximum number of messages to return */
  limit?: number | null;
  since?: CentrifugoStreamPosition;
  /** Reverse message order (newest first) */
  reverse?: boolean | null;
}

/**
 * Channel history response.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoHistoryResponse {
  error?: CentrifugoError;
  result?: CentrifugoHistoryResult;
}

/**
 * Server info response.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoInfoResponse {
  error?: CentrifugoError;
  result?: CentrifugoInfoResult;
}

/**
 * Request to get channel presence.
 * 
 * Request model (no read-only fields).
 */
export interface CentrifugoPresenceRequestRequest {
  /** Channel name */
  channel: string;
}

/**
 * Channel presence response.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoPresenceResponse {
  error?: CentrifugoError;
  result?: CentrifugoPresenceResult;
}

/**
 * Request to get channel presence statistics.
 * 
 * Request model (no read-only fields).
 */
export interface CentrifugoPresenceStatsRequestRequest {
  /** Channel name */
  channel: string;
}

/**
 * Channel presence stats response.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoPresenceStatsResponse {
  error?: CentrifugoError;
  result?: CentrifugoPresenceStatsResult;
}

/**
 * Centrifugo API error structure.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoError {
  /** Error code (0 = no error) */
  code?: number;
  /** Error message */
  message?: string;
}

/**
 * Channels result wrapper.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoChannelsResult {
  /** Map of channel names to channel info */
  channels: Record<string, CentrifugoChannelInfo>;
}

/**
 * Stream position for pagination.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoStreamPosition {
  /** Stream offset */
  offset: number;
  /** Stream epoch */
  epoch: string;
}

/**
 * History result wrapper.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoHistoryResult {
  /** List of publications */
  publications: Array<CentrifugoPublication>;
  /** Current stream epoch */
  epoch: string;
  /** Latest stream offset */
  offset: number;
}

/**
 * Info result wrapper.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoInfoResult {
  /** List of Centrifugo nodes */
  nodes: Array<CentrifugoNodeInfo>;
}

/**
 * Presence result wrapper.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoPresenceResult {
  /** Map of client IDs to client info */
  presence: Record<string, CentrifugoClientInfo>;
}

/**
 * Presence stats result.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoPresenceStatsResult {
  /** Number of connected clients */
  num_clients: number;
  /** Number of unique users */
  num_users: number;
}

/**
 * Information about a single channel.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoChannelInfo {
  /** Number of connected clients in channel */
  num_clients: number;
}

/**
 * Single publication (message) in channel history.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoPublication {
  /** Message payload */
  data: Record<string, any>;
  info?: CentrifugoClientInfo;
  /** Message offset in channel stream */
  offset: number;
  /** Optional message tags */
  tags?: Record<string, any> | null;
}

/**
 * Information about a single Centrifugo node.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoNodeInfo {
  /** Unique node identifier */
  uid: string;
  /** Node name */
  name: string;
  /** Centrifugo version */
  version: string;
  /** Number of connected clients */
  num_clients: number;
  /** Number of unique users */
  num_users: number;
  /** Number of active channels */
  num_channels: number;
  /** Node uptime in seconds */
  uptime: number;
  /** Total number of subscriptions */
  num_subs: number;
  metrics?: CentrifugoMetrics;
  process?: CentrifugoProcess;
}

/**
 * Information about connected client.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoClientInfo {
  /** User ID */
  user: string;
  /** Client UUID */
  client: string;
  /** Connection metadata */
  conn_info?: Record<string, any> | null;
  /** Channel-specific metadata */
  chan_info?: Record<string, any> | null;
}

/**
 * Server metrics.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoMetrics {
  /** Metrics collection interval */
  interval: number;
  /** Metric name to value mapping */
  items: Record<string, number>;
}

/**
 * Process information.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoProcess {
  /** CPU usage percentage */
  cpu: number;
  /** Resident set size in bytes */
  rss: number;
}

