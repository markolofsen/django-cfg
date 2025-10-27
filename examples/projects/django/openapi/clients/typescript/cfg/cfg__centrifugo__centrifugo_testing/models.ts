/**
 * Request model for connection token generation.
 * 
 * Request model (no read-only fields).
 */
export interface ConnectionTokenRequestRequest {
  /** User ID for the connection */
  user_id: string;
  /** List of channels to authorize */
  channels?: Array<string>;
}

/**
 * Response model for connection token.
 * 
 * Response model (includes read-only fields).
 */
export interface ConnectionTokenResponse {
  /** JWT token for WebSocket connection */
  token: string;
  /** Centrifugo WebSocket URL */
  centrifugo_url: string;
  /** Token expiration time (ISO 8601) */
  expires_at: string;
}

/**
 * Request model for test message publishing.
 * 
 * Request model (no read-only fields).
 */
export interface PublishTestRequestRequest {
  /** Target channel name */
  channel: string;
  /** Message data (any JSON object) */
  data: Record<string, any>;
  /** Wait for client acknowledgment */
  wait_for_ack?: boolean;
  /** ACK timeout in seconds */
  ack_timeout?: number;
}

/**
 * Response model for test message publishing.
 * 
 * Response model (includes read-only fields).
 */
export interface PublishTestResponse {
  /** Whether publish succeeded */
  success: boolean;
  /** Unique message ID */
  message_id: string;
  /** Target channel */
  channel: string;
  /** Number of ACKs received */
  acks_received?: number;
  /** Whether message was delivered */
  delivered?: boolean;
  /** Error message if failed */
  error?: string | null;
}

/**
 * Request model for manual ACK sending.
 * 
 * Request model (no read-only fields).
 */
export interface ManualAckRequestRequest {
  /** Message ID to acknowledge */
  message_id: string;
  /** Client ID sending the ACK */
  client_id: string;
}

/**
 * Response model for manual ACK.
 * 
 * Response model (includes read-only fields).
 */
export interface ManualAckResponse {
  /** Whether ACK was sent successfully */
  success: boolean;
  /** Message ID that was acknowledged */
  message_id: string;
  /** Error message if failed */
  error?: string | null;
}

