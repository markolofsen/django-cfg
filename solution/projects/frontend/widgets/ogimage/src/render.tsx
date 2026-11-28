import { ImageResponse } from 'next/og';
import type { ReactNode } from 'react';

import { OG_FONT_FAMILY, type OgFonts } from './fonts';

/**
 * One Open Graph card renderer, every djangocfg app.
 *
 * A card is what a link BECOMES in WhatsApp, Telegram, Slack, iMessage and
 * Facebook — often the only part of a site a person sees before deciding
 * whether to open the page. This module draws it; `card.ts` decides what it
 * says. Brand identity (name, mark, accent, palette) is passed in by the app,
 * so a CMDOP card and an MLS card come from the same layout and still read as
 * two products.
 *
 * ── Constraints this layout is built around ───────────────────────────────
 *
 * Satori is not a browser. It implements a subset of flexbox and needs
 * `display: flex` stated on anything with children, computes no cascade, and
 * parses no `oklch()` — so colours arrive here as hex/rgba literals.
 *
 * The frame is fixed at 1200x630 and NOTHING CLIPS: a title long enough to
 * wrap past its allotted lines pushes into the footer instead of truncating.
 * Callers hand over text that fits — `fitDescription` in `card.ts` owns that
 * budget, and `titleSizeFor` below is the scale it reasons against.
 */

export const OG_SIZE = { width: 1200, height: 630 } as const;
export const OG_CONTENT_TYPE = 'image/png';

/** Colours a card is drawn in. Every field has a default; override the few that carry the brand. */
export interface OgTheme {
  /** Flat ground behind a text-only card, and the base a photograph sits on. */
  background: string;
  /** Darker corner of the background gradient. */
  backgroundDeep: string;
  /** Title and wordmark. */
  foreground: string;
  /** Description and domain. */
  muted: string;
  /** The inset hairline frame. */
  border: string;
  /** Eyebrow, mark, and the background wash. `accentColor` on the options overrides it per card. */
  accent: string;
  /** Footer line — the scannable facts. Defaults to `accent`. */
  footer?: string;
}

/** Dark, neutral, blue-accented — the palette every consumer started from. */
export const DEFAULT_OG_THEME: OgTheme = {
  background: '#07111D',
  backgroundDeep: '#02070C',
  foreground: '#F2F7FB',
  muted: '#A9B7C5',
  border: 'rgba(194, 216, 235, 0.22)',
  accent: '#61B8FF',
};

export interface OgImageOptions {
  /** The one line that must survive. Never empty — callers fall back first. */
  title: string;
  /** Small uppercase kicker: what KIND of thing this is. */
  eyebrow?: string;
  description?: string;
  /**
   * Bottom-left supporting line — price, category, author. Kept distinct from
   * `description` because it is scanned, not read.
   */
  footer?: string;
  /** Bottom-right origin, so a forwarded card still says where it came from. */
  domain?: string;
  /**
   * A photograph to render behind the copy, as an absolute URL or data URI.
   * When present a scrim darkens the left half so the copy survives whatever
   * the photograph happens to be.
   */
  image?: string;
  /** Per-card accent; falls back to `theme.accent`. */
  accentColor?: string;
  /**
   * Brand wordmark drawn top-left, next to `mark`. Omit for a card whose
   * `title` IS the brand (the site-wide brand card).
   */
  brand?: string;
  /**
   * Brand mark, top-left. Inline SVG only: Satori cannot load React icon
   * components with CSS, and an `<img>` to a remote logo makes every card
   * depend on a network fetch that can fail while a crawler waits.
   */
  mark?: ReactNode;
  theme?: Partial<OgTheme>;
}

/**
 * Type scale by length. These three steps are what `fitDescription` budgets
 * against — changing them changes how much description fits, so the two move
 * together.
 */
export function titleSizeFor(title: string): number {
  if (title.length > 58) return 52;
  if (title.length > 34) return 66;
  return 84;
}

/** Renders one Open Graph card as a PNG response. */
export function renderOgImage(options: OgImageOptions, fonts: OgFonts): Response {
  const theme: OgTheme = { ...DEFAULT_OG_THEME, ...options.theme };
  const accent = options.accentColor ?? theme.accent;
  const footerColor = theme.footer ?? accent;
  const withImage = Boolean(options.image);

  // Two passes, tuned by rendering them. The photograph is the POINT of an
  // image card, so the scrim protects the copy column and then gets out of the
  // way: near-opaque under the copy, clearing past it so the right half stays
  // a photograph; a light touch top and bottom for the mark and footer.
  const imageScrim = withImage
    ? `linear-gradient(90deg, rgba(2,8,14,0.92) 0%, rgba(2,8,14,0.86) 34%, rgba(2,8,14,0.48) 60%, rgba(2,8,14,0.12) 82%, rgba(2,8,14,0.04) 100%), linear-gradient(180deg, rgba(2,8,14,0.42) 0%, rgba(2,8,14,0.06) 34%, rgba(2,8,14,0.10) 62%, rgba(2,8,14,0.52) 100%)`
    : undefined;

  // Satori stringifies every style value, so an unwanted shadow must be ABSENT
  // rather than `none`.
  const shadow = (value: string) => (withImage ? { textShadow: value } : {});

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'relative',
          overflow: 'hidden',
          padding: '70px 86px',
          color: theme.foreground,
          backgroundColor: theme.background,
          // Without a photograph the card carries an accent wash off the top
          // left, so a text-only card still reads as a brand rather than as a
          // dark rectangle.
          ...(withImage
            ? {}
            : {
                backgroundImage: `radial-gradient(880px 520px at 2% -10%, ${accent}30, transparent 60%), linear-gradient(150deg, ${theme.backgroundDeep} 0%, ${theme.background} 76%)`,
              }),
          fontFamily: OG_FONT_FAMILY,
        }}
      >
        {options.image ? (
          <img
            src={options.image}
            width={OG_SIZE.width}
            height={OG_SIZE.height}
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : null}
        {/* `width`/`height`, NOT `inset: 0`. An absolutely positioned element
            with no children and no explicit size collapses to a zero box in
            Satori, and `inset` does not give it one — an overlay written that
            way draws nothing at all. Same trap applies to the frame below. */}
        {imageScrim ? (
          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundImage: imageScrim }} />
        ) : null}

        {/* An inset hairline frame: a mount around a photograph, and a visible
            edge on the white background of a chat thread. */}
        <div
          style={{
            position: 'absolute',
            top: 22,
            left: 22,
            width: OG_SIZE.width - 44,
            height: OG_SIZE.height - 44,
            border: `1px solid ${theme.border}`,
            borderRadius: 26,
          }}
        />

        <div style={{ display: 'flex', position: 'relative', alignItems: 'center', gap: 16, minHeight: 52 }}>
          {options.mark ? <div style={{ display: 'flex', color: accent }}>{options.mark}</div> : null}
          {options.brand ? (
            <div style={{ display: 'flex', fontSize: 30, fontWeight: 800, letterSpacing: -0.6, ...shadow('0 1px 12px rgba(0,0,0,0.8)') }}>
              {options.brand}
            </div>
          ) : null}
        </div>

        {/* Narrower over a photograph: the scrim's dark half is the left half,
            and 720px keeps every wrapped line on ground the scrim covers. */}
        <div style={{ display: 'flex', flexDirection: 'column', position: 'relative', maxWidth: withImage ? 720 : 800 }}>
          {options.eyebrow ? (
            <div
              style={{
                display: 'flex',
                marginBottom: 16,
                // The accent is tuned for the flat dark ground. Over a
                // photograph even a scrimmed sky can rise under it, so the
                // eyebrow goes to foreground there.
                color: withImage ? theme.foreground : accent,
                fontSize: 22,
                fontWeight: 600,
                letterSpacing: 2.2,
                textTransform: 'uppercase',
                ...shadow('0 1px 12px rgba(0,0,0,0.8)'),
              }}
            >
              {options.eyebrow}
            </div>
          ) : null}
          <div
            style={{
              display: 'flex',
              fontSize: titleSizeFor(options.title),
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: -1.5,
              ...shadow('0 2px 22px rgba(0,0,0,0.55)'),
            }}
          >
            {options.title}
          </div>
          {options.description ? (
            <div
              style={{
                display: 'flex',
                marginTop: 20,
                // Muted grey is a deliberate step down on the flat card; over
                // a photograph it lands too close to the scrimmed image, so
                // the description keeps foreground and separates by size.
                color: withImage ? theme.foreground : theme.muted,
                fontSize: 24,
                fontWeight: 500,
                lineHeight: 1.32,
                maxWidth: withImage ? 660 : 730,
                ...shadow('0 1px 12px rgba(0,0,0,0.75)'),
              }}
            >
              {options.description}
            </div>
          ) : null}
        </div>

        <div style={{ display: 'flex', position: 'relative', alignItems: 'flex-end', justifyContent: 'space-between' }}>
          {options.footer ? (
            <div style={{ display: 'flex', color: footerColor, fontSize: 23, fontWeight: 600, letterSpacing: 0.2, ...shadow('0 1px 12px rgba(0,0,0,0.85)') }}>
              {options.footer}
            </div>
          ) : (
            <div style={{ display: 'flex' }} />
          )}
          {options.domain ? (
            <div style={{ display: 'flex', color: theme.muted, fontSize: 21, fontWeight: 500, ...shadow('0 1px 12px rgba(0,0,0,0.85)') }}>
              {options.domain}
            </div>
          ) : null}
        </div>
      </div>
    ),
    { ...OG_SIZE, fonts },
  );
}
