import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedCommandHistoryListList {
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
  results: Array<CommandHistoryList>;
}

/**
 * Full serializer for command details.
 * 
 * Response model (includes read-only fields).
 */
export interface CommandHistoryDetail {
  id: string;
  session_id: string;
  session_name: string;
  duration_ms: number;
  is_success: boolean;
  /** Executed command */
  command: string;
  /** Working directory when command was executed */
  working_directory?: string;
  /** Command execution status

  * `pending` - Pending
  * `running` - Running
  * `success` - Success
  * `failed` - Failed
  * `cancelled` - Cancelled
  * `timeout` - Timeout */
  status?: Enums.CommandHistoryDetailStatus;
  /** Standard output */
  stdout?: string;
  /** Standard error */
  stderr?: string;
  /** Process exit code */
  exit_code?: number | null;
  /** When command started executing */
  started_at?: string | null;
  /** When command finished */
  finished_at?: string | null;
  /** Bytes sent to process (stdin) */
  bytes_in?: number;
  /** Bytes received from process (stdout+stderr) */
  bytes_out?: number;
  created_at: string;
  updated_at: string;
  /** Terminal session */
  session: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedTerminalSessionListList {
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
  results: Array<TerminalSessionList>;
}

/**
 * Serializer for creating new session.
 * 
 * Request model (no read-only fields).
 */
export interface TerminalSessionCreateRequest {
  name?: string;
  shell?: string;
  working_directory?: string;
  environment?: Record<string, any>;
}

/**
 * Serializer for creating new session.
 * 
 * Response model (includes read-only fields).
 */
export interface TerminalSessionCreate {
  name?: string;
  shell?: string;
  working_directory?: string;
  environment?: Record<string, any>;
}

/**
 * Full serializer for session details.
 * 
 * Response model (includes read-only fields).
 */
export interface TerminalSessionDetail {
  id: string;
  is_alive: boolean;
  is_active: boolean;
  display_name: string;
  heartbeat_age_seconds: number;
  recent_commands: Array<CommandHistoryList>;
  /** Session display name */
  name?: string;
  /** Current session status

  * `pending` - Pending
  * `connected` - Connected
  * `disconnected` - Disconnected
  * `error` - Error */
  status: Enums.TerminalSessionDetailStatus;
  /** Connected Electron client hostname */
  electron_hostname: string;
  /** Electron client version */
  electron_version: string;
  /** Current working directory in terminal */
  working_directory?: string;
  /** Shell to use (e.g., /bin/bash, /bin/zsh) */
  shell?: string;
  /** Environment variables for the session */
  environment?: Record<string, any>;
  /** Total commands executed in this session */
  commands_count: number;
  /** Total bytes sent to terminal */
  bytes_sent: number;
  /** Total bytes received from terminal */
  bytes_received: number;
  /** When Electron client connected */
  connected_at?: string | null;
  /** Last heartbeat from Electron */
  last_heartbeat_at?: string | null;
  /** When session was disconnected */
  disconnected_at?: string | null;
  created_at: string;
  updated_at: string;
  /** Session owner (null for auto-created sessions) */
  user?: number | null;
}

/**
 * Serializer for sending input.
 * 
 * Request model (no read-only fields).
 */
export interface TerminalInputRequest {
  /** Input data as string */
  data?: string;
  /** Base64 encoded input data */
  data_base64?: string;
}

/**
 * Serializer for resize command.
 * 
 * Request model (no read-only fields).
 */
export interface TerminalResizeRequest {
  cols: number;
  rows: number;
  width?: number;
  height?: number;
}

/**
 * Serializer for signal command.
 * 
 * Request model (no read-only fields).
 */
export interface TerminalSignalRequest {
  /** * `2` - SIGINT
  * `9` - SIGKILL
  * `15` - SIGTERM */
  signal: Enums.TerminalSignalRequestSignal;
}

/**
 * Lightweight serializer for command lists.
 * 
 * Response model (includes read-only fields).
 */
export interface CommandHistoryList {
  id: string;
  session_id: string;
  /** Executed command */
  command: string;
  /** Command execution status

  * `pending` - Pending
  * `running` - Running
  * `success` - Success
  * `failed` - Failed
  * `cancelled` - Cancelled
  * `timeout` - Timeout */
  status?: Enums.CommandHistoryListStatus;
  /** Process exit code */
  exit_code?: number | null;
  output_preview: string;
  duration_ms: number;
  is_success: boolean;
  created_at: string;
}

/**
 * Lightweight serializer for session lists.
 * 
 * Response model (includes read-only fields).
 */
export interface TerminalSessionList {
  id: string;
  /** Session display name */
  name?: string;
  /** Current session status

  * `pending` - Pending
  * `connected` - Connected
  * `disconnected` - Disconnected
  * `error` - Error */
  status?: Enums.TerminalSessionListStatus;
  display_name: string;
  is_alive: boolean;
  /** Connected Electron client hostname */
  electron_hostname?: string;
  /** Current working directory in terminal */
  working_directory?: string;
  /** Shell to use (e.g., /bin/bash, /bin/zsh) */
  shell?: string;
  /** When Electron client connected */
  connected_at?: string | null;
  /** Last heartbeat from Electron */
  last_heartbeat_at?: string | null;
  created_at: string;
}

