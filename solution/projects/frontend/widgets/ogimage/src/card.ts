import type { ReactNode } from 'react';

import { loadOgFonts, type OgFonts } from './fonts';
import { OG_CONTENT_TYPE, OG_SIZE, renderOgImage, type OgTheme } from './render';

/**
 * The card fabric — what an Open Graph card SAYS, as opposed to how
 * `render.tsx` draws it.
 *
 * An app binds its identity once with `createOgCards` and every
 * `opengraph-image.tsx` calls one of the two fabrics, so a product link, a
 * category link and an article link preview as three recognisably different
 * cards while staying obviously one product.
 *
 * Two rules hold everywhere in this file:
 *
 *   Never throw. A card is rendered while a crawler waits, and a route that
 *   500s leaves a bare grey rectangle in the chat thread — strictly worse than
 *   a generic brand card. Callers pass what they managed to load, including
 *   nothing, and `brandCard` is the floor.
 *
 *   Never invent. A missing field is absent, not a placeholder — a placeholder
 *   is a claim about the entity that the page itself does not make. This file
 *   trims; it never writes.
 */

/**
 * A title long enough to wrap eats the description's space, and Satori does
 * not clip — it overflows into the footer. So the description budget is a
 * function of the title's length, derived from `titleSizeFor`'s three steps
 * and the 800px copy column.
 *
 * Trimming happens at a word boundary with an ellipsis, so the reader can see
 * the text is a preview. Nothing is rewritten; only cut.
 */
export function fitDescription(title: string, description: string | null | undefined): string | undefined {
  const text = description?.trim();
  if (!text) return undefined;

  // Past ~44 characters the title is already two or three lines and owns the
  // space between the mark and the footer, so it gets the card to itself.
  const budget = title.length > 44 ? 0 : title.length > 34 ? 92 : 150;
  if (budget === 0) return undefined;
  if (text.length <= budget) return text;

  const cut = text.slice(0, budget);
  const lastSpace = cut.lastIndexOf(' ');
  return `${(lastSpace > 24 ? cut.slice(0, lastSpace) : cut).replace(/[\s.,;:—-]+$/u, '')}…`;
}

/**
 * Joins the footer's facts, dropping the ones that are absent rather than
 * leaving a stray separator: "· Bahamas" reads as a rendering fault.
 */
export function ogFooter(...parts: Array<string | number | null | undefined>): string | undefined {
  const kept = parts
    .map((part) => (typeof part === 'number' ? String(part) : part?.trim()))
    .filter((part): part is string => Boolean(part));
  return kept.length ? kept.join('  ·  ') : undefined;
}

/**
 * An absolute URL for a photograph Satori is to draw.
 *
 * Satori fetches this itself, so a relative path resolves against nothing and
 * the card renders without its image — hence `siteUrl`, which a root-relative
 * path is resolved against. Anything that is not a usable absolute URL comes
 * back `undefined`, which degrades to the text-only card: the one failure mode
 * here that a reader would never notice.
 */
export function ogImageUrl(path: string | null | undefined, siteUrl: string): string | undefined {
  const raw = path?.trim();
  if (!raw) return undefined;
  if (raw.startsWith('data:')) return raw;
  try {
    const url = new URL(raw, siteUrl);
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.toString() : undefined;
  } catch {
    return undefined;
  }
}

/** The identity every card from one app shares. Bound once with `createOgCards`. */
export interface OgCardsConfig {
  /** Brand name — the brand card's title, and the wordmark on content cards. */
  name: string;
  /** Brand card description, unless the route passes its own. */
  description?: string;
  /** Brand card footer — the tagline. */
  tagline?: string;
  /** Host printed bottom-right, e.g. `djangocfg.com`. See `domainFromEnv`. */
  domain?: string;
  /** Site origin, so `contentCard({ image: '/media/x.jpg' })` resolves. */
  siteUrl?: string;
  accentColor?: string;
  /** Brand mark, inline SVG. See `OgImageOptions.mark`. */
  mark?: ReactNode;
  theme?: Partial<OgTheme>;
  /** Swap the typeface. Defaults to the vendored Plus Jakarta Sans. */
  loadFonts?: () => Promise<OgFonts>;
}

export interface ContentCardOptions {
  /**
   * Nullable on purpose: a caller whose fetch failed passes nothing and gets
   * the brand card, which is the honest fallback rather than a card headed
   * "undefined".
   */
  title: string | null | undefined;
  /** Small uppercase kicker: what KIND of thing this is ("Skill", "For sale"). */
  eyebrow?: string;
  description?: string | null;
  /** Scannable facts. Defaults to the brand name. See `ogFooter`. */
  footer?: string;
  /** Absolute URL, root-relative path (needs `siteUrl`), or data URI. */
  image?: string | null;
  accentColor?: string;
}

export interface OgCards {
  /** Re-export from every `opengraph-image.tsx`: `export { size, contentType }`. */
  size: typeof OG_SIZE;
  contentType: typeof OG_CONTENT_TYPE;
  /** The site-wide fallback: home, section landings, and any detail route whose record failed to load. */
  brandCard(eyebrow?: string, description?: string): Promise<Response>;
  /** One catalogue entity. Falls back to `brandCard` when `title` is empty. */
  contentCard(options: ContentCardOptions): Promise<Response>;
}

/** Binds an app's identity to the two fabrics. Call once, in an `_lib/og.ts`. */
export function createOgCards(config: OgCardsConfig): OgCards {
  const loadFonts = config.loadFonts ?? loadOgFonts;
  const shared = {
    domain: config.domain,
    accentColor: config.accentColor,
    mark: config.mark,
    theme: config.theme,
  };

  async function brandCard(eyebrow?: string, description?: string): Promise<Response> {
    return renderOgImage(
      {
        ...shared,
        title: config.name,
        eyebrow,
        description: fitDescription(config.name, description ?? config.description),
        footer: config.tagline,
      },
      await loadFonts(),
    );
  }

  async function contentCard(options: ContentCardOptions): Promise<Response> {
    const title = options.title?.trim();
    if (!title) return brandCard();

    return renderOgImage(
      {
        ...shared,
        accentColor: options.accentColor ?? config.accentColor,
        brand: config.name,
        title,
        eyebrow: options.eyebrow,
        description: fitDescription(title, options.description),
        footer: options.footer ?? config.name,
        image: ogImageUrl(options.image, config.siteUrl ?? 'http://invalid.invalid'),
      },
      await loadFonts(),
    );
  }

  return { size: OG_SIZE, contentType: OG_CONTENT_TYPE, brandCard, contentCard };
}
