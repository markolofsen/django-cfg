import type { Metadata } from 'next'
import type { OgSpec } from './types'

const OG_WIDTH = 1200
const OG_HEIGHT = 630

/** A Next.js OG image entry. */
function imageEntry(url: string, alt: string) {
  return { url, width: OG_WIDTH, height: OG_HEIGHT, alt }
}

/**
 * Builds the og/twitter image fragment for a given image URL — the one place
 * that knows the shape Next.js expects.
 */
function ogImageFragment(url: string, alt: string): Pick<Metadata, 'openGraph' | 'twitter'> {
  return {
    openGraph: { images: [imageEntry(url, alt)] },
    twitter: { card: 'summary_large_image', images: [url] },
  }
}

/** Extract a plain title string from Next.js's title shapes. */
export function extractTitle(metadata: Metadata): string {
  const t = metadata.title
  if (!t) return ''
  if (typeof t === 'string') return t
  if (typeof t === 'object' && 'absolute' in t) return (t as { absolute: string }).absolute
  if (typeof t === 'object' && 'default' in t) return (t as { default: string }).default
  return ''
}

/**
 * Resolves an `OgSpec` into a concrete og/twitter image fragment. `staticUrl`
 * is the site's brand image, used for the `'static'` case.
 *
 * This is the single decision point for "what is the OG image" — no other code
 * branches on the spec.
 *
 * An `opengraph-image` route does NOT override this. Next.js applies that file
 * convention only when metadata leaves `openGraph.images` unset, and this
 * function always sets it — so while `createMetadata` runs for a page, its
 * `opengraph-image.tsx` is silently never rendered. To use a per-page card, the
 * page must keep `openGraph.images` out of its metadata entirely (build it
 * without this function, or delete the key afterwards).
 */
export function resolveOgImage(
  spec: OgSpec,
  staticUrl: string,
  fallbackTitle: string
): Pick<Metadata, 'openGraph' | 'twitter'> {
  if (spec === 'static') {
    return ogImageFragment(staticUrl, fallbackTitle)
  }
  return ogImageFragment(spec.image, spec.alt ?? fallbackTitle)
}
