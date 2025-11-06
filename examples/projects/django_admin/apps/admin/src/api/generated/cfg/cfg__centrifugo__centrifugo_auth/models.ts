/**
 * Response model for Centrifugo connection token.
 * 
 * Response model (includes read-only fields).
 */
export interface ConnectionTokenResponse {
  /** JWT token for Centrifugo connection */
  token: string;
  /** Centrifugo WebSocket URL */
  centrifugo_url: string;
  /** Token expiration time (ISO 8601) */
  expires_at: string;
  /** List of allowed channels */
  channels: Array<string>;
}

