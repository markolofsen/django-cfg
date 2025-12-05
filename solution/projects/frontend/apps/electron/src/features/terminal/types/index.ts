/**
 * Terminal feature types.
 */

export interface TerminalSession {
  id: string;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  title: string;
  workingDirectory: string;
}

export interface TerminalConfig {
  /** Django session ID (from REST API). If not provided, Electron generates one */
  sessionId?: string;
  shell: string;
  workingDirectory: string;
  cols: number;
  rows: number;
}

export interface TerminalTheme {
  background: string;
  foreground: string;
  cursor: string;
  cursorAccent: string;
  selection: string;
  black: string;
  red: string;
  green: string;
  yellow: string;
  blue: string;
  magenta: string;
  cyan: string;
  white: string;
  brightBlack: string;
  brightRed: string;
  brightGreen: string;
  brightYellow: string;
  brightBlue: string;
  brightMagenta: string;
  brightCyan: string;
  brightWhite: string;
}

// IPC Channel names
export const IPC_CHANNELS = {
  // Terminal -> Main
  TERMINAL_START: 'terminal:start',
  TERMINAL_STOP: 'terminal:stop',
  TERMINAL_INPUT: 'terminal:input',
  TERMINAL_RESIZE: 'terminal:resize',

  // Main -> Terminal
  TERMINAL_OUTPUT: 'terminal:output',
  TERMINAL_STATUS: 'terminal:status',
  TERMINAL_ERROR: 'terminal:error',
  TERMINAL_EXIT: 'terminal:exit',
} as const;

export type IPCChannel = typeof IPC_CHANNELS[keyof typeof IPC_CHANNELS];
