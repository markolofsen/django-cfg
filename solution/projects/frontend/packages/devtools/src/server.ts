/**
 * @djangocfg/devtools/server
 *
 * Server-side error reporting for Next.js route handlers, Server Components,
 * and middleware. No browser APIs — safe in Node.js / Edge Runtime.
 *
 * @example
 * import { serverDevtools } from '@djangocfg/devtools/server'
 * serverDevtools.configure({ project: 'my-app', baseUrl: 'https://api.myapp.com' })
 *
 * export async function POST(req: Request) {
 *   try { ... } catch (err) {
 *     await serverDevtools.captureError(err, { url: req.url })
 *     return new Response('Internal Server Error', { status: 500 })
 *   }
 * }
 */

import { sendBatch } from './ingest'
import { EventLevel, EventType } from './types'
import type { DevtoolsEvent, ServerDevtoolsConfig } from './types'

export { EventLevel, EventType } from './types'
export type { DevtoolsEvent, ServerDevtoolsConfig } from './types'

let _config: ServerDevtoolsConfig = {}

async function send(events: DevtoolsEvent[]): Promise<void> {
  try {
    // `??`, not a spread of the config underneath: an event carrying an
    // explicit `project_name: undefined` would otherwise blank the configured
    // one. Same precedence as the browser store.
    await sendBatch(_config.baseUrl ?? '', events.map((e) => ({
      ...e,
      project_name: e.project_name ?? _config.project,
      environment: e.environment ?? _config.environment,
    })))
  } catch {
    // Never throw from error reporting
  }
}

export const serverDevtools = {
  configure(config: ServerDevtoolsConfig): void {
    _config = config
  },

  async captureError(
    err: unknown,
    ctx?: { url?: string; extra?: Record<string, unknown> },
  ): Promise<void> {
    await send([
      {
        event_type: EventType.JS_ERROR,
        level: EventLevel.ERROR,
        message: err instanceof Error ? err.message : String(err),
        stack_trace: err instanceof Error ? (err.stack ?? '') : '',
        url: ctx?.url ?? '',
        extra: ctx?.extra,
      },
    ])
  },

  async captureNetworkError(
    status: number,
    method: string,
    apiUrl: string,
    ctx?: { pageUrl?: string; extra?: Record<string, unknown> },
  ): Promise<void> {
    await send([
      {
        event_type: EventType.NETWORK_ERROR,
        level: status >= 500 ? EventLevel.ERROR : EventLevel.WARNING,
        message: `HTTP ${status} — ${method} ${apiUrl}`,
        url: ctx?.pageUrl ?? '',
        http_status: status,
        http_method: method,
        http_url: apiUrl,
        extra: ctx?.extra,
      },
    ])
  },

  async capture(event: DevtoolsEvent): Promise<void> {
    await send([event])
  },
}

export type ServerDevtools = typeof serverDevtools
