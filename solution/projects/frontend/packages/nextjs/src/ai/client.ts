/**
 * DjangoCFG Documentation Client
 *
 * HTTP client for accessing DjangoCFG documentation via MCP server API.
 */

import { API_INFO_ENDPOINT, API_SEARCH_ENDPOINT, DEFAULT_TIMEOUT, MCP_BASE_URL } from './constants';

import type { SearchResult, SearchOptions, McpConfig, ApiSearchResponse } from './types';

/**
 * Client for DjangoCFG Documentation API.
 */
export class DjangoCfgDocsClient {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = MCP_BASE_URL, timeout: number = DEFAULT_TIMEOUT) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.timeout = timeout;
  }

  private async makeRequest<T>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
    let url = `${this.baseUrl}${endpoint}`;

    if (params) {
      const searchParams = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        searchParams.set(key, String(value));
      }
      url = `${url}?${searchParams.toString()}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'User-Agent': 'DjangoCFG-AI-Client/1.0',
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Search documentation.
   */
  async search(query: string, options: SearchOptions = {}): Promise<SearchResult[]> {
    const { limit = 5, category } = options;

    const params: Record<string, string | number> = { q: query, limit };
    if (category) {
      params.category = category;
    }

    const data = await this.makeRequest<ApiSearchResponse>(API_SEARCH_ENDPOINT, params);

    const results = data.results || (Array.isArray(data) ? data : []);

    return results.map((item) => ({
      title: item.title || '',
      content: item.content || item.snippet || '',
      url: item.url || '',
      score: item.score || 0,
      category: item.category || '',
    }));
  }

  /**
   * Get detailed info about a specific topic.
   */
  async getInfo(topic: string): Promise<Record<string, unknown>> {
    return this.makeRequest(API_INFO_ENDPOINT, { topic });
  }

  /**
   * Get MCP server configuration for AI assistants.
   */
  getMcpConfig(): McpConfig {
    return {
      mcpServers: {
        'djangocfg-docs': {
          url: `${this.baseUrl}/mcp`,
        },
      },
    };
  }
}

// Default client instance
let defaultClient: DjangoCfgDocsClient | null = null;

function getClient(): DjangoCfgDocsClient {
  if (!defaultClient) {
    defaultClient = new DjangoCfgDocsClient();
  }
  return defaultClient;
}

/**
 * Search DjangoCFG documentation.
 *
 * @example
 * ```ts
 * const results = await search('database configuration');
 * results.forEach(r => console.log(r.title, r.url));
 * ```
 */
export async function search(query: string, options: SearchOptions = {}): Promise<SearchResult[]> {
  return getClient().search(query, options);
}

/**
 * Get documentation as formatted text.
 *
 * @example
 * ```ts
 * const docs = await getDocs('How to configure PostgreSQL?');
 * console.log(docs);
 * ```
 */
export async function getDocs(query: string, limit: number = 3): Promise<string> {
  const results = await search(query, { limit });

  if (results.length === 0) {
    return `No documentation found for: ${query}`;
  }

  const output: string[] = [];

  results.forEach((r, i) => {
    output.push(`## ${i + 1}. ${r.title}`);
    output.push(r.content);
    if (r.url) {
      output.push(`📖 Read more: ${r.url}`);
    }
    output.push('');
  });

  return output.join('\n');
}

/**
 * Get detailed info about a topic.
 */
export async function getInfo(topic: string): Promise<Record<string, unknown>> {
  return getClient().getInfo(topic);
}

/**
 * Get MCP server configuration.
 */
export function getMcpConfig(): McpConfig {
  return getClient().getMcpConfig();
}
