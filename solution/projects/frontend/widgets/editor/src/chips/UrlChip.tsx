'use client';

/**
 * `<UrlChip>` — a compact, clickable "URL chip" (Chrome-omnibox style):
 * a favicon + the domain with a middle-ellipsised path
 * (`github.com/wailsapp/…/README.md`), monospace, with the full href on
 * hover. Opens in a new tab.
 *
 * This is the SURFACE-AGNOSTIC, React counterpart of the TipTap composer's
 * `editorChip` (`kind: 'url'`, see `forms/MarkdownEditor/chip/ChipNode.ts`).
 * It matches that chip's look pixel-for-pixel using semantic tokens, so a
 * URL reads identically whether it sits in the composer (being typed) or in
 * a rendered chat bubble (`MarkdownMessage`'s `urlChipRule`).
 *
 * Presentational + self-contained: it imports only the pure URL detector
 * helpers (`url/detect`) — no TipTap / ProseMirror — so it can render a
 * known URL anywhere (chat messages, link lists, etc).
 *
 * Favicon degradation: the favicon `<img>` falls back to a lucide `Globe`
 * glyph on `onError` (offline / blocked / unknown host) so the chip never
 * shows a broken-image marker — mirroring the composer chip's behaviour.
 */

import { useState } from 'react';
import { Globe } from 'lucide-react';

import { cn } from '@djangocfg/ui-core/lib';
import {
  splitUrl,
  truncateUrlLabel,
  faviconUrl,
} from '../markdown/url/detect';

export interface UrlChipProps {
  /** The full, navigable href (`https://…`). */
  href: string;
  /**
   * Approximate max characters for the truncated label. The domain is
   * always preserved; only the path's middle collapses. Default 40.
   */
  maxChars?: number;
  className?: string;
}

/**
 * Render a URL as an inline, clickable chip. Favicon → globe glyph on
 * favicon load error.
 */
export function UrlChip({ href, maxChars = 40, className }: UrlChipProps) {
  const { host } = splitUrl(href);
  const favicon = faviconUrl(host);
  const label = truncateUrlLabel(href, { maxChars });

  // Favicon load failure → swap to the globe glyph. Also covers the empty-
  // favicon case (unparseable host → faviconUrl returns '').
  const [imgFailed, setImgFailed] = useState(false);
  const showGlobe = imgFailed || !favicon;

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      title={href}
      className={cn(
        // Inline pill matching the composer's `editor-chip--url`: muted
        // surface + border, monospace, semantic tokens only. `max-w` +
        // `truncate` (on the label) is the CSS safety net under the
        // precomputed middle-ellipsis label. No raw blue link styling —
        // the primary accent only lights up the border on hover + the
        // globe glyph.
        'inline-flex max-w-[22rem] items-center gap-1 rounded align-baseline',
        'border border-border bg-muted px-1.5 py-0.5',
        'font-mono text-[0.8125em] leading-tight text-foreground no-underline',
        'cursor-pointer transition-colors hover:border-primary',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        className,
      )}
    >
      <span
        className={cn(
          'flex size-3.5 shrink-0 items-center justify-center',
          showGlobe && 'text-primary',
        )}
        aria-hidden="true"
      >
        {showGlobe ? (
          <Globe className="size-3.5" />
        ) : (
          <img
            src={favicon}
            alt=""
            width={14}
            height={14}
            className="size-3.5 rounded-[2px]"
            onError={() => setImgFailed(true)}
          />
        )}
      </span>
      <span className="truncate">{label}</span>
    </a>
  );
}

export default UrlChip;
