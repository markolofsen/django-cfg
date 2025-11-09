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
  acks_expected: number;
  duration_ms: number | null;
  created_at: string;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
}

