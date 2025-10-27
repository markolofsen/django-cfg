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
}

