/**
 * withMonitor — Route Handler wrapper for @djangocfg/nextjs
 *
 * Catches unhandled errors from a Next.js Route Handler,
 * forwards them to serverMonitor, then re-throws so Next.js
 * still returns a 500 response normally.
 *
 * @example
 * // app/api/orders/route.ts
 * import { withMonitor } from '@djangocfg/nextjs/monitor'
 *
 * export const POST = withMonitor(async (req) => {
 *   // handler code
 *   return Response.json({ ok: true })
 * })
 */

import { serverDevtools } from '@djangocfg/devtools/server'

type RouteHandler = (req: Request, ctx?: unknown) => Promise<Response> | Response

export function withMonitor(handler: RouteHandler): RouteHandler {
  return async (req: Request, ctx?: unknown): Promise<Response> => {
    try {
      return await handler(req, ctx)
    } catch (err) {
      try {
        await serverDevtools.captureError(err, { url: req.url })
      } catch { /* never crash */ }
      throw err
    }
  }
}
