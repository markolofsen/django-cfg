// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// HTTP semantic-token helpers shared between RequestViewer, OpenapiViewer,
// LogViewer, and any other tool that visualizes HTTP traffic.
//
// IMPORTANT: these helpers return semantic token *names*, not Tailwind
// classes or hex colors. Consumers map the token to their own surface
// (e.g. `bg-success/15 text-success` vs `border-success-border`). This
// keeps the mapping consistent across tools and theme presets.
//
// Source pattern: request-viewer.tsx:70-92.

export type HttpStatusTone =
  | 'success'      // 2xx
  | 'info'         // 3xx
  | 'warning'      // 4xx
  | 'destructive'  // 5xx
  | 'muted';       // unknown / 1xx

export type HttpMethodTone =
  | 'success'      // GET
  | 'info'         // POST
  | 'warning'      // PUT / PATCH
  | 'destructive'  // DELETE
  | 'muted';       // OPTIONS / HEAD / unknown

/**
 * Map an HTTP status code to a semantic token name.
 *
 * @example
 *   statusColor(204) // 'success'
 *   statusColor(404) // 'warning'
 *   statusColor(503) // 'destructive'
 */
export function statusColor(status: number): HttpStatusTone {
  if (status >= 200 && status < 300) return 'success';
  if (status >= 300 && status < 400) return 'info';
  if (status >= 400 && status < 500) return 'warning';
  if (status >= 500) return 'destructive';
  return 'muted';
}

/**
 * Map an HTTP method to a semantic token name. Case-insensitive.
 *
 * @example
 *   methodColor('GET')    // 'success'
 *   methodColor('delete') // 'destructive'
 */
export function methodColor(method: string): HttpMethodTone {
  switch (method.toUpperCase()) {
    case 'GET':
      return 'success';
    case 'POST':
      return 'info';
    case 'PUT':
    case 'PATCH':
      return 'warning';
    case 'DELETE':
      return 'destructive';
    default:
      return 'muted';
  }
}
