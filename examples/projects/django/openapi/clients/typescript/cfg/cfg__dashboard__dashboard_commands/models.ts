/**
 * Response serializer for command help.
 * 
 * Response model (includes read-only fields).
 */
export interface CommandHelpResponse {
  status: string;
  command: string;
  app?: string;
  help_text?: string;
  is_allowed?: boolean;
  risk_level?: string;
  error?: string;
}

/**
 * Request serializer for command execution.
 * 
 * Request model (no read-only fields).
 */
export interface CommandExecuteRequestRequest {
  /** Name of the Django management command */
  command: string;
  /** Positional arguments for the command */
  args?: Array<string>;
  /** Named options for the command (e.g., {'verbosity': '2'}) */
  options?: Record<string, any>;
}

/**
 * Commands summary serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface CommandsSummary {
  total_commands: number;
  core_commands: number;
  custom_commands: number;
  categories: Array<string>;
  commands: Array<Command>;
  categorized: Record<string, any>;
}

/**
 * Django management command serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface Command {
  name: string;
  app: string;
  help: string;
  is_core: boolean;
  is_custom: boolean;
  is_allowed?: boolean;
  risk_level?: string;
}

