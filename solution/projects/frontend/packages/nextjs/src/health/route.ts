/**
 * Health Route Handler for Next.js App Router
 *
 * Usage:
 * ```tsx
 * // app/healthz/route.ts
 * import { createHealthHandler } from '@djangocfg/nextjs/health';
 *
 * export const GET = createHealthHandler({
 *   version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
 *   checks: [
 *     {
 *       name: 'database',
 *       check: async () => {
 *         // Check database connection
 *         return await checkDatabase();
 *       },
 *     },
 *   ],
 * });
 * ```
 */

import { NextResponse } from 'next/server';

import type { HealthConfig, HealthResponse } from './types';

export function createHealthHandler(config: HealthConfig = {}) {
  const { version, checks = [], customData = {} } = config;

  return async function GET() {
    const startTime = Date.now();
    let status: 'ok' | 'error' = 'ok';
    const checkResults: Record<string, boolean> = {};

    // Run health checks
    if (checks.length > 0) {
      for (const check of checks) {
        try {
          const result = await check.check();
          checkResults[check.name] = result;
          if (!result) {
            status = 'error';
          }
        } catch {
          checkResults[check.name] = false;
          status = 'error';
        }
      }
    }

    const response: HealthResponse = {
      status,
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      ...(version && { version }),
      ...(checks.length > 0 && {
        checks: checkResults,
        durationMs: Date.now() - startTime,
      }),
      ...customData,
    };

    const statusCode = status === 'ok' ? 200 : 503;

    return NextResponse.json(response, { status: statusCode });
  };
}
