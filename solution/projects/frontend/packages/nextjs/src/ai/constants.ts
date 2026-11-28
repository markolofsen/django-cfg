/**
 * AI Documentation Constants
 */

// MCP Server URLs
export const MCP_BASE_URL = 'https://mcp.djangocfg.com';
export const MCP_SERVER_URL = `${MCP_BASE_URL}/mcp`;
export const MCP_API_URL = `${MCP_BASE_URL}/api/search`;

// API Endpoints
export const API_SEARCH_ENDPOINT = '/api/search';
export const API_INFO_ENDPOINT = '/api/info';
export const DEFAULT_TIMEOUT = 10000; // ms

// AI Hint for console output
export const AI_DOCS_HINT = `🤖 AI Docs: ${MCP_SERVER_URL} | pnpm ai-docs search "query"`;

// Full AI Hint description
export const AI_HINT = `
DjangoCFG Documentation is available via MCP server.

To get help with DjangoCFG configuration:
1. Use the MCP server: ${MCP_SERVER_URL}
2. Or search directly: ${MCP_API_URL}?q=YOUR_QUERY&limit=5

Example queries:
- "How to configure PostgreSQL database?"
- "What is DatabaseConfig?"
- "How to setup Redis cache?"
- "Email configuration with SMTP"
`;
