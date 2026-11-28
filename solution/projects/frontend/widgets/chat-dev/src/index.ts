/**
 * Developer data on screen: an OpenAPI schema, a request, a log, an
 * environment and an API reference table.
 *
 * The root barrel is the HTTP tone helpers only (no React, no dependencies).
 * Every viewer is a subpath on purpose: `./openapi` carries a sampler, an HTTP
 * client and a store, and a host mounting an env table must not pay for it.
 */
export type { HttpMethodTone, HttpStatusTone } from './request-viewer/http';
export { methodColor, statusColor } from './request-viewer/http';
