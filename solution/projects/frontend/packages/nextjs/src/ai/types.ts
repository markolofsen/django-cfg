/**
 * AI Documentation Types
 */

export interface SearchResult {
  title: string;
  content: string;
  url: string;
  score: number;
  category: string;
}

export interface SearchOptions {
  limit?: number;
  category?: string;
}

export interface McpConfig {
  mcpServers: {
    'djangocfg-docs': {
      url: string;
    };
  };
}

export interface ApiSearchResponse {
  results: Array<{
    title: string;
    content?: string;
    snippet?: string;
    url: string;
    score?: number;
    category?: string;
  }>;
}
