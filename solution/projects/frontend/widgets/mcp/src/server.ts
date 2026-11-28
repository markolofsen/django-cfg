import { normalizeMcpEndpoint, type McpServer } from './install';

/** Where django-cfg mounts MCP unless the project moves it (`endpoint_path`). */
export const DEFAULT_MCP_PATH = '/cfg/mcp/';

/** `api.example.com` → `example`: the product word a client registers the server under. */
function productWord(url: string): string {
  try {
    const host = new URL(url).hostname.replace(/^(www|api|mcp)\./, '');
    return host.split('.')[0] || 'mcp';
  } catch {
    return 'mcp';
  }
}

/** Resolve the host's API origin without coupling the widget to auth internals. */
function apiOrigin(): string {
  const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env;
  return env?.NEXT_PUBLIC_API_PROXY_URL || env?.NEXT_PUBLIC_API_URL ||
    (typeof window !== 'undefined' ? window.location.origin : '');
}

/**
 * Fill what a django-cfg host already implies: the MCP endpoint is the API
 * host plus the default path, and the alias and connector name come from the
 * host name. Anything passed wins, so a project that moved MCP or wants its own
 * brand name sets only that field.
 */
export function resolveMcpServer(server: Partial<McpServer> = {}): McpServer {
  const url = normalizeMcpEndpoint(server.url ?? `${apiOrigin().replace(/\/+$/, '')}${DEFAULT_MCP_PATH}`);
  const word = productWord(url);
  return {
    url,
    alias: server.alias ?? word.toLowerCase(),
    name: server.name ?? word.charAt(0).toUpperCase() + word.slice(1),
  };
}
