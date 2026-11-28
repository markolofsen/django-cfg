/**
 * Link-preview (URL unfurl) types — the data contract between the host's
 * metadata fetcher and the presentational card.
 *
 * The browser CANNOT fetch arbitrary URLs to scrape OpenGraph/meta tags
 * (CORS blocks cross-origin HTML reads), so resolution is ALWAYS a host
 * concern: a server route (Next.js) or a native backend (Wails/Go). The
 * UI never fetches — it receives already-resolved metadata, or a resolver
 * callback the host implements.
 */

/**
 * Resolved metadata for one URL — the unfurl result. All fields except
 * `url` are optional: a card renders from whatever subset is available
 * (favicon + title is enough; a bare `url` falls back to the hostname).
 * Plain JSON so it survives history persistence + SSE transport.
 */
export interface LinkPreviewData {
  /** The canonical/resolved URL the card links to. */
  url: string;
  /** og:title → twitter:title → <title>. */
  title?: string;
  /** og:description → twitter:description → <meta name=description>. */
  description?: string;
  /** og:image → twitter:image (absolute URL; host resolves relative ones). */
  image?: string;
  /** Favicon URL (host resolves <link rel=icon> / /favicon.ico). */
  favicon?: string;
  /** og:site_name → hostname. */
  siteName?: string;
}

/**
 * Host-provided resolver. Given a URL, returns its preview metadata, or
 * `null` when nothing useful could be fetched (so the card is skipped).
 * Implementations:
 *  - Wails/Go desktop → a bound `FetchLinkMetadata(url)` service method.
 *  - Next.js web → a `/api/unfurl?url=` route.
 * The host owns caching, SSRF protection, timeouts and bot User-Agents.
 */
export type ResolveLinkPreview = (
  url: string,
  signal?: AbortSignal,
) => Promise<LinkPreviewData | null>;
