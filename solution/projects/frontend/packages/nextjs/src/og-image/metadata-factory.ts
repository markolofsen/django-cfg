import type { Metadata } from 'next'
import type { OgSpec } from './types'
import { resolveOgImage } from './metadata'

/**
 * Site-wide identity the metadata factory needs. Config-agnostic on purpose —
 * the package doesn't know about any app's `settings` object, so the consumer
 * passes these once (typically derived from their own settings module).
 */
export interface SiteMetaConfig {
  /** Brand / app name, e.g. "CMDOP". Used in titles, siteName, alt text. */
  name: string
  /** Default description used when a page doesn't supply its own. */
  description: string
  /** Absolute site origin, e.g. "https://cmdop.com". Used for canonical/og url. */
  siteUrl: string
  /** Ready-made static brand OG image URL (absolute or root-relative). */
  ogImage: string
  /** Optional favicon / apple-touch icons forwarded to Metadata.icons. */
  icons?: Metadata['icons']
  /** Locales for hreflang alternates. Omit for single-locale sites. */
  locales?: readonly string[]
  /** Locale used for x-default hreflang (defaults to "en" or first locale). */
  defaultLocale?: string
}

/**
 * Per-page inputs. Only `title` is really worth setting per page; everything
 * else falls back to the site config.
 */
export interface PageMeta {
  /** Page title (without the brand suffix). Falls back to the site name. */
  title?: string
  /** Page description; falls back to the site description. */
  description?: string
  keywords?: string[]
  /** Current locale, used for canonical + openGraph.locale + alternates. */
  locale?: string
  /**
   * Path without locale prefix, e.g. "/skills" or "/skills/foo". Home is ''
   * (or '/'). Leading/trailing slashes are normalized, so both canonical and
   * og:url come out well-formed whichever you pass.
   */
  path?: string
  /**
   * What the OG image should be. Defaults to `'static'` (the brand image).
   * - `'static'`          brand image from config (default)
   * - `{ image, alt? }`   an exact image URL (e.g. a content screenshot)
   *
   * Every case here writes `openGraph.images`, which SUPPRESSES an
   * `opengraph-image.tsx` route for the page — Next.js honours that file
   * convention only when metadata sets no images. A per-page rendered card
   * therefore needs metadata that omits the key, not just the route file.
   */
  og?: OgSpec
  /** Escape hatch: extra Metadata fields merged last (robots, authors, etc.). */
  extra?: Metadata
}

/**
 * Joins the site origin, an optional locale segment, and a page path into one
 * absolute URL.
 *
 * This is the SINGLE place the URL shape is decided. `canonical` and
 * `openGraph.url` describe the same page, so they must be built by the same
 * function — when they were two hand-rolled template literals they drifted
 * apart (one inserted a slash the other didn't), and a page shipped a canonical
 * and an og:url pointing at two different URLs.
 *
 * Contract (see `PageMeta.path`): `path` carries its own leading slash —
 * "/skills", "/skills/foo" — and home is '' (we also tolerate '/'). Segments
 * are normalized rather than trusted, so a stray or missing slash at a call
 * site cannot produce "site.com//skills" or "site.comskills".
 */
function buildUrl(siteUrl: string, locale: string | undefined, path: string): string {
  const origin = siteUrl.replace(/\/+$/, '')
  const segments = [locale, path]
    .map((segment) => segment?.replace(/^\/+|\/+$/g, '') ?? '')
    .filter(Boolean)
  return segments.length ? `${origin}/${segments.join('/')}` : origin
}

function buildAlternates(
  config: SiteMetaConfig,
  path: string,
  locale: string
): Metadata['alternates'] {
  if (!config.locales?.length) {
    return { canonical: buildUrl(config.siteUrl, undefined, path) }
  }
  const languages: Record<string, string> = {}
  for (const loc of config.locales) {
    languages[loc] = buildUrl(config.siteUrl, loc, path)
  }
  const xDefault =
    config.defaultLocale ?? (config.locales.includes('en') ? 'en' : config.locales[0])
  languages['x-default'] = buildUrl(config.siteUrl, xDefault, path)
  return { canonical: buildUrl(config.siteUrl, locale, path), languages }
}

/**
 * Builds a complete Next.js `Metadata` from a one-time site config plus per-page
 * inputs — title-template, description, openGraph, twitter, canonical + hreflang,
 * icons, and the OG image — so pages only declare what's unique.
 *
 * The OG image is chosen by the single `og` field (defaults to the static brand
 * image). There is exactly one way to do each thing.
 *
 *   // app/_core/metadata.ts
 *   export const createMetadata = makeMetadataFactory({
 *     name: settings.app.name,
 *     description: settings.app.description,
 *     siteUrl: settings.app.siteUrl,
 *     ogImage: settings.app.media.ogimage,
 *     icons: { icon: settings.app.media.favicon },
 *     locales: LOCALES,
 *   })
 *
 *   // landing page — static brand image (default)
 *   export const metadata = createMetadata({ title: 'Pricing', path: '/pricing' })
 *   // content page with its own image
 *   export const metadata = createMetadata({ title: p.name, og: { image: p.image } })
 */
export function createMetadata(config: SiteMetaConfig, page: PageMeta = {}): Metadata {
  const title = page.title ?? config.name
  const description = page.description ?? config.description
  const locale = page.locale ?? config.defaultLocale ?? 'en'
  const path = page.path ?? ''
  // Same builder as the canonical below — og:url and canonical name the same
  // page, so they are never allowed to be assembled by two different rules.
  const ogUrl = buildUrl(config.siteUrl, config.locales?.length ? locale : undefined, path)

  const ogImage = resolveOgImage(page.og ?? 'static', config.ogImage, title)

  const metadata: Metadata = {
    title,
    description,
    keywords: page.keywords,
    alternates: buildAlternates(config, path, locale),
    openGraph: {
      type: 'website',
      locale,
      url: ogUrl,
      siteName: config.name,
      title,
      description,
      ...ogImage.openGraph,
    },
    twitter: {
      title,
      description,
      ...ogImage.twitter,
    },
    icons: config.icons,
  }

  if (!page.extra) return metadata
  // Shallow-merge the escape hatch, but deep-merge the nested og/twitter so the
  // image we just set isn't clobbered by a partial `extra.openGraph`.
  return {
    ...metadata,
    ...page.extra,
    openGraph: { ...metadata.openGraph, ...page.extra.openGraph },
    twitter: { ...metadata.twitter, ...page.extra.twitter },
  }
}

/**
 * Curries `createMetadata` with a fixed site config so pages call a zero-config
 * factory. This is the single recommended entry point for app metadata.
 */
export function makeMetadataFactory(config: SiteMetaConfig) {
  return (page: PageMeta = {}): Metadata => createMetadata(config, page)
}
