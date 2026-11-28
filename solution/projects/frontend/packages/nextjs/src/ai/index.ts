/**
 * DjangoCFG AI Documentation Client
 *
 * Provides access to DjangoCFG documentation via MCP server API.
 *
 * @example
 * ```ts
 * import { search, getDocs, getMcpConfig } from '@djangocfg/nextjs/ai';
 *
 * // Search documentation
 * const results = await search('database configuration');
 *
 * // Get formatted docs
 * const docs = await getDocs('How to configure PostgreSQL?');
 *
 * // Get MCP config for AI assistants
 * const config = getMcpConfig();
 * ```
 */

export { DjangoCfgDocsClient, search, getDocs, getInfo, getMcpConfig } from './client';
export type { SearchResult, SearchOptions, McpConfig } from './types';
export {
  MCP_BASE_URL,
  MCP_SERVER_URL,
  MCP_API_URL,
  AI_DOCS_HINT,
  AI_HINT,
} from './constants';
