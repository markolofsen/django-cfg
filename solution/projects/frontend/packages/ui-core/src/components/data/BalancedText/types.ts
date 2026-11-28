// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type { ComponentPropsWithoutRef, ElementType, ReactNode } from 'react';

/**
 * CSS font shorthand for Pretext measurement.
 *
 * Must match the actually rendered font, otherwise the balanced width will be
 * off. When `font` is omitted, the component reads `getComputedStyle()` on the
 * element after mount and falls back to {@link DEFAULT_BALANCED_FONT} on the
 * server.
 */
export type BalancedFont = string;

export interface BalancedTextOwnProps {
  /** Text to balance. Required as a string — pretext measures runs of glyphs, not React trees. */
  children: string;
  /** CSS font shorthand (`'16px Inter, sans-serif'`). When omitted, reads `getComputedStyle`. */
  font?: BalancedFont;
  /**
   * Hard cap on width in px. Balanced width never exceeds this. When omitted,
   * the parent container's measured `clientWidth` is used. `maxLines` cannot
   * make the text wider than this.
   * @default 600
   */
  maxWidth?: number;
  /**
   * Cap on number of lines. When set, the balanced width is the *narrowest*
   * width that still keeps ≤ `maxLines` lines (instead of preserving the
   * natural line count at `maxWidth`). Useful for headings.
   */
  maxLines?: number;
  /** Element to render as. @default 'span' */
  as?: ElementType;
}

/** Props for {@link BalancedText}. */
export type BalancedTextProps = BalancedTextOwnProps &
  Omit<ComponentPropsWithoutRef<'span'>, keyof BalancedTextOwnProps | 'children'> & {
    children: string;
  };

/** Fallback used on SSR and when `font` is not provided + measurement hasn't run. */
export const DEFAULT_BALANCED_FONT: BalancedFont =
  '16px ui-sans-serif, system-ui, -apple-system, sans-serif';

export const DEFAULT_BALANCED_MAX_WIDTH = 600;

/** Internal: BalancedText render shape (used by subcomponents). */
export interface InternalRenderProps {
  Tag: ElementType;
  balancedWidth: number;
  hasMeasured: boolean;
  text: string;
  className?: string;
  style?: React.CSSProperties;
  rest: Record<string, unknown>;
  textNode: ReactNode;
}
