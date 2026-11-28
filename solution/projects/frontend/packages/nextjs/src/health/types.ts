/**
 * Health check types
 */

import type { HealthResponse } from '../types';

export interface HealthCheck {
  name: string;
  check: () => Promise<boolean> | boolean;
}

export interface HealthConfig {
  version?: string;
  checks?: HealthCheck[];
  customData?: Record<string, unknown>;
}

export type { HealthResponse };

