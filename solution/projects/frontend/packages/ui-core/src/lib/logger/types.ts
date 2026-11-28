/**
 * Logger Types
 *
 * Type definitions for the universal logging system.
 * Compatible with Console panel in FileWorkspace IDE layout.
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'success';

export interface LogEntry {
  /** Unique log ID */
  id: string;
  /** Timestamp when log was created */
  timestamp: Date;
  /** Log level */
  level: LogLevel;
  /** Component/module name that created the log */
  component: string;
  /** Log message */
  message: string;
  /** Additional data (objects, errors, etc.) */
  data?: Record<string, unknown>;
  /** Error stack trace (for error level) */
  stack?: string;
}

export interface LogFilter {
  /** Filter by log levels */
  levels: LogLevel[];
  /** Filter by component name (partial match) */
  component?: string;
  /** Filter by message text (partial match) */
  search?: string;
  /** Filter by time range */
  since?: Date;
}

export interface LogStore {
  /** All accumulated logs */
  logs: LogEntry[];
  /** Current filter settings */
  filter: LogFilter;
  /** Maximum logs to keep */
  maxLogs: number;

  /** Add new log entry */
  addLog: (entry: Omit<LogEntry, 'id' | 'timestamp'>) => void;
  /** Clear all logs */
  clearLogs: () => void;
  /** Update filter settings */
  setFilter: (filter: Partial<LogFilter>) => void;
  /** Reset filter to defaults */
  resetFilter: () => void;
  /** Get filtered logs */
  getFilteredLogs: () => LogEntry[];
  /** Export logs as JSON string */
  exportLogs: () => string;
}

export interface Logger {
  debug: (message: string, data?: Record<string, unknown>) => void;
  info: (message: string, data?: Record<string, unknown>) => void;
  warn: (message: string, data?: Record<string, unknown>) => void;
  error: (message: string, data?: Record<string, unknown>) => void;
  success: (message: string, data?: Record<string, unknown>) => void;
}

/**
 * Media-specific log helper methods
 */
export interface MediaLogger extends Logger {
  /** Log source load event */
  load: (src: string, type?: string) => void;
  /** Log state change */
  state: (state: string, details?: Record<string, unknown>) => void;
  /** Log seek event */
  seek: (from: number, to: number, duration: number) => void;
  /** Log buffer ranges */
  buffer: (buffered: TimeRanges, duration: number) => void;
  /** Log generic event */
  event: (name: string, data?: unknown) => void;
}
