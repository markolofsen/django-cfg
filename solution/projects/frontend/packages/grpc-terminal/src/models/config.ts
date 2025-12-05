/**
 * Configuration models for gRPC Terminal client.
 */

export interface GRPCConfig {
  /** gRPC server host */
  host: string;
  /** gRPC server port */
  port: number;
  /** Use TLS/SSL */
  useTls: boolean;
  /** Connection timeout in seconds */
  timeoutSeconds: number;
  /** Reconnect interval in seconds */
  reconnectInterval: number;
  /** Heartbeat interval in seconds */
  heartbeatInterval: number;
}

export interface TerminalConfig {
  /** Default shell to use */
  shell: string;
  /** Initial working directory */
  workingDirectory: string;
  /** Environment variables */
  env: Record<string, string>;
  /** Terminal columns */
  cols: number;
  /** Terminal rows */
  rows: number;
}

export interface ClientConfig {
  /** Session ID (UUID) */
  sessionId: string;
  /** Electron hostname for identification */
  hostname: string;
  /** gRPC configuration */
  grpc: GRPCConfig;
  /** Terminal configuration */
  terminal: TerminalConfig;
}

/**
 * Default gRPC configuration for development.
 */
export const DEFAULT_GRPC_CONFIG: GRPCConfig = {
  host: 'localhost',
  port: 50051,
  useTls: false,
  timeoutSeconds: 30,
  reconnectInterval: 5,
  heartbeatInterval: 30,
};

/**
 * Default terminal configuration.
 */
export const DEFAULT_TERMINAL_CONFIG: TerminalConfig = {
  shell: process.platform === 'win32' ? 'powershell.exe' : '/bin/zsh',
  workingDirectory: process.env.HOME || '~',
  env: {
    TERM: 'xterm-256color',
    COLORTERM: 'truecolor',
  },
  cols: 80,
  rows: 24,
};

/**
 * Options for creating client configuration.
 */
export interface ClientConfigOptions {
  hostname?: string;
  grpc?: Partial<GRPCConfig>;
  terminal?: Partial<TerminalConfig>;
}

/**
 * Create client configuration with defaults.
 */
export function createClientConfig(
  sessionId: string,
  options: ClientConfigOptions = {}
): ClientConfig {
  return {
    sessionId,
    hostname: options.hostname || require('os').hostname(),
    grpc: { ...DEFAULT_GRPC_CONFIG, ...options.grpc },
    terminal: { ...DEFAULT_TERMINAL_CONFIG, ...options.terminal },
  };
}
