/**
 * @djangocfg/api/auth/server
 *
 * Server-side authentication utilities.
 * Use this entry point in server components, API routes, and middleware.
 *
 * @example
 * ```typescript
 * // middleware.ts
 * import { proxyMiddleware } from '@djangocfg/api/auth/server';
 *
 * export function middleware(request: NextRequest) {
 *   return proxyMiddleware(request);
 * }
 * ```
 */

// Middlewares
export * from './middlewares';
