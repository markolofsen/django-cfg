/**
 * Request to generate proto files.
 * 
 * Request model (no read-only fields).
 */
export interface ProtoGenerateRequestRequest {
  /** List of app labels to generate protos for (uses enabled_apps from config if not specified) */
  apps?: Array<string>;
  /** Force regeneration even if proto file exists */
  force?: boolean;
}

/**
 * Response from proto generation.
 * 
 * Response model (includes read-only fields).
 */
export interface ProtoGenerateResponse {
  status: string;
  generated: Array<string>;
  generated_count: number;
  errors: Array<ProtoGenerateError>;
  proto_dir: string;
}

/**
 * Proto generation error.
 * 
 * Response model (includes read-only fields).
 */
export interface ProtoGenerateError {
  app: string;
  error: string;
}

