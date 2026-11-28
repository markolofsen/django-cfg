import { MCP_KEY_HEADER, mcpInfoUrl, parseServerInfo, type McpServer, type McpServerInfo } from '../install';

/**
 * GET `<server url>/info/` with the user's key. Every failure (network, CORS, 401, an older server, a bad body) is null: the
 * panel works without the summary.
 */
export async function fetchServerInfo(server: Pick<McpServer, 'url'>, key: string, signal?: AbortSignal): Promise<McpServerInfo | null> {
  try {
    const response = await fetch(mcpInfoUrl(server), { headers: { [MCP_KEY_HEADER]: key, Accept: 'application/json' }, credentials: 'omit', signal });
    return response.ok ? parseServerInfo(await response.json()) : null;
  } catch {
    return null;
  }
}
