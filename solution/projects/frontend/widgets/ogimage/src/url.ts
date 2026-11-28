import type { Metadata } from 'next';

/**
 * Site-origin helpers for OG routes — where a card says it came from, and the
 * one metadata trap that silently disables every card.
 */

export interface SiteUrlOptions {
  /** App-owned canonical URL, used when the env var is not set (build-time page-data collection). */
  fallback?: string;
  /** Defaults to `process.env`; injectable for tests. */
  env?: Record<string, string | undefined>;
}

export function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

/**
 * Resolve any public URL (`NEXT_PUBLIC_*`) against an app-owned fallback.
 * Throws only when neither is given — a misconfiguration worth failing on.
 */
export function resolvePublicUrl(value: string | undefined, fallback?: string): string {
  const resolved = value || fallback;
  if (!resolved) {
    throw new Error('A public URL (NEXT_PUBLIC_*) or a fallback is required.');
  }
  return trimTrailingSlash(new URL(resolved).toString());
}

/** The canonical site origin, from `NEXT_PUBLIC_SITE_URL` or the fallback. */
export function siteUrlFromEnv(options: SiteUrlOptions = {}): string {
  const env = options.env ?? process.env;
  return resolvePublicUrl(env.NEXT_PUBLIC_SITE_URL, options.fallback);
}

export function metadataBaseFromEnv(options: SiteUrlOptions = {}): URL {
  return new URL(siteUrlFromEnv(options));
}

/** The host to print bottom-right on a card, e.g. `djangocfg.com`. */
export function domainFromEnv(options: SiteUrlOptions = {}): string {
  return metadataBaseFromEnv(options).host;
}

/**
 * Lets a segment's `opengraph-image.tsx` control both OG and Twitter images.
 *
 * Next's file convention only applies where no explicit `images` is set in
 * metadata — and an explicit entry WINS. So an `openGraph.images` array in a
 * layout does not complement the cards below it, it silently disables them.
 * Run generated metadata through this before returning it from a segment that
 * owns a card.
 */
export function withoutOgImages(metadata: Metadata): Metadata {
  const openGraph = metadata.openGraph ? { ...metadata.openGraph } : undefined;
  if (openGraph && 'images' in openGraph) {
    delete (openGraph as { images?: unknown }).images;
  }

  const twitter = metadata.twitter ? { ...metadata.twitter } : undefined;
  if (twitter && 'images' in twitter) {
    delete (twitter as { images?: unknown }).images;
  }

  return { ...metadata, openGraph, twitter };
}
