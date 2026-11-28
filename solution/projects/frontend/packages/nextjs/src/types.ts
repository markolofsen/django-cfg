/**
 * Common types for @djangocfg/nextjs package
 */

export type ChangeFreq = 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';

export interface SitemapUrl {
  loc: string;
  lastmod?: string;
  changefreq?: ChangeFreq;
  priority?: number;
}

export interface SitemapConfig {
  siteUrl: string;
  urls: SitemapUrl[];
  cacheControl?: string;
}

export interface HealthResponse {
  status: 'ok' | 'error';
  timestamp: string;
  uptime: number;
  version?: string;
  checks?: Record<string, boolean>;
  /** Wall-clock time spent running the configured checks, in milliseconds. */
  durationMs?: number;
}


export interface ErrorPageConfig {
  code?: string | number;
  title?: string;
  description?: string;
  supportEmail?: string;
}

