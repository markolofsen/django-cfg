/**
 * @djangocfg/nextjs/monitor
 *
 * Server-side error reporting for Next.js Route Handlers and Server
 * Components, backed by `@djangocfg/devtools/server`.
 *
 * Configure once in lib/monitor.ts, then use withMonitor() or serverDevtools.
 *
 * @example
 * // lib/monitor.ts
 * import { serverDevtools } from '@djangocfg/nextjs/monitor'
 * serverDevtools.configure({
 *   project: process.env.PROJECT_NAME ?? 'my-app',
 *   environment: process.env.NODE_ENV,
 *   baseUrl: process.env.NEXT_PUBLIC_API_URL,
 * })
 *
 * // app/api/orders/route.ts
 * import { withMonitor } from '@djangocfg/nextjs/monitor'
 * export const POST = withMonitor(async (req) => {
 *   // ...
 * })
 */

export { serverDevtools } from '@djangocfg/devtools/server'
export type { ServerDevtoolsConfig } from '@djangocfg/devtools/server'

/** @deprecated Renamed — use `serverDevtools`. */
export { serverDevtools as serverMonitor } from '@djangocfg/devtools/server'
/** @deprecated Renamed — use `ServerDevtoolsConfig`. */
export type { ServerDevtoolsConfig as ServerMonitorConfig } from '@djangocfg/devtools/server'

export { withMonitor } from './withMonitor'
