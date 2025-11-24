/**
 * Virtual serializer for Crypto Client Command interface. Clients are not
 * stored in database - they exist as gRPC connections. This serializer
 * represents a connected crypto client with its metadata.
 * 
 * Response model (includes read-only fields).
 */
export interface ClientCommand {
  /** Client UUID */
  client_id: string;
  /** Client name (e.g., crypto-bot-001) */
  client_name: string;
  /** Is client currently connected */
  connected: boolean;
  /** Last heartbeat timestamp */
  last_heartbeat?: string | null;
  /** Client metadata */
  metadata: Record<string, any>;
  wallets_synced: number;
  sync_requests: number;
  /** Last wallet sync timestamp */
  last_sync?: string | null;
}

