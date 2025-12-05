import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

/**
 * Environment configuration for Electron app.
 *
 * In development: connects to local gRPC server (localhost:50051)
 * In production: connects to grpc.djangocfg.com via gRPC-Web (HTTPS)
 */
export const env = createEnv({
  server: {
    // App info
    NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),

    // gRPC configuration
    GRPC_HOST: z.string().default('localhost'),
    GRPC_PORT: z.coerce.number().default(50051),
    // Use TLS for production (grpc.djangocfg.com)
    GRPC_USE_TLS: z
      .string()
      .transform((val) => val === 'true')
      .default('false'),

    // Apple signing (optional for dev)
    APPLE_ID: z.email().optional(),
    APPLE_PASSWORD: z.string().optional(),
    APPLE_TEAM_ID: z.string().default('8GS9P4SZWC'),
    SIGN_IDENTITY: z.string().default('Developer ID Application: Igor Korotin (8GS9P4SZWC)'),
  },
  runtimeEnv: process.env,
  skipValidation: process.env.SKIP_ENV_VALIDATION === 'true',
});

/**
 * Get gRPC configuration based on environment.
 *
 * Development: localhost:50051 (no TLS)
 * Production: grpc.djangocfg.com:443 (TLS)
 */
export function getGrpcConfig() {
  const isDev = env.NODE_ENV === 'development';

  // Allow explicit override via env vars
  if (process.env.GRPC_HOST) {
    return {
      host: env.GRPC_HOST,
      port: env.GRPC_PORT,
      useTls: env.GRPC_USE_TLS,
    };
  }

  // Default configuration based on NODE_ENV
  if (isDev) {
    return {
      host: 'localhost',
      port: 50051,
      useTls: false,
    };
  }

  // Production defaults
  return {
    host: 'grpc.djangocfg.com',
    port: 443,
    useTls: true,
  };
}

export type Env = typeof env;
