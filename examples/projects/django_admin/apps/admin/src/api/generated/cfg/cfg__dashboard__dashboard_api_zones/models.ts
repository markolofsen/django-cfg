/**
 * API zones summary serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface APIZonesSummary {
  zones: Array<APIZone>;
  summary: Record<string, string>;
}

/**
 * OpenAPI zone/group serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface APIZone {
  name: string;
  title: string;
  description: string;
  app_count: number;
  endpoint_count: number;
  status: string;
  schema_url: string;
  api_url: string;
  apps: Array<string>;
}

