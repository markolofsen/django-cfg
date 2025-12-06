/**
 * Command execution status
 * * `pending` - Pending
 * * `running` - Running
 * * `success` - Success
 * * `failed` - Failed
 * * `cancelled` - Cancelled
 * * `timeout` - Timeout
 */
export enum CommandHistoryDetailStatus {
  PENDING = "pending",
  RUNNING = "running",
  SUCCESS = "success",
  FAILED = "failed",
  CANCELLED = "cancelled",
  TIMEOUT = "timeout",
}

/**
 * Command execution status
 * * `pending` - Pending
 * * `running` - Running
 * * `success` - Success
 * * `failed` - Failed
 * * `cancelled` - Cancelled
 * * `timeout` - Timeout
 */
export enum CommandHistoryListStatus {
  PENDING = "pending",
  RUNNING = "running",
  SUCCESS = "success",
  FAILED = "failed",
  CANCELLED = "cancelled",
  TIMEOUT = "timeout",
}

/**
 * Current session status
 * * `pending` - Pending
 * * `connected` - Connected
 * * `disconnected` - Disconnected
 * * `error` - Error
 */
export enum TerminalSessionDetailStatus {
  PENDING = "pending",
  CONNECTED = "connected",
  DISCONNECTED = "disconnected",
  ERROR = "error",
}

/**
 * Current session status
 * * `pending` - Pending
 * * `connected` - Connected
 * * `disconnected` - Disconnected
 * * `error` - Error
 */
export enum TerminalSessionListStatus {
  PENDING = "pending",
  CONNECTED = "connected",
  DISCONNECTED = "disconnected",
  ERROR = "error",
}

/**
 * * `2` - SIGINT
 * * `9` - SIGKILL
 * * `15` - SIGTERM
 */
export enum TerminalSignalRequestSignal {
  VALUE_2 = 2,
  VALUE_9 = 9,
  VALUE_15 = 15,
}

