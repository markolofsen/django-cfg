// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Pretext-powered balanced text. CSS `text-wrap: balance` only works up to
// ~6 lines and is inconsistent cross-browser; this is deterministic and
// scales to any length. On SSR / before measurement we fall back to the
// CSS rule so the first paint is never visibly off — once pretext has
// measured a width, the inline `maxWidth` style takes over.
//
// Powered by Pretext by Cheng Lou — github.com/chenglou/pretext

'use client';

import * as React from 'react';
import { cn } from '../../../lib/utils';
import {
  usePretextWithSegments,
  useBalancedWidth,
} from '../../../lib/pretext';
import {
  DEFAULT_BALANCED_FONT,
  DEFAULT_BALANCED_MAX_WIDTH,
  type BalancedTextProps,
} from './types';
import { useMeasuredFont } from './hooks/useMeasuredFont';
import { useMaxLinesWidth } from './hooks/useMaxLinesWidth';

function BalancedTextImpl({
  children,
  font,
  maxWidth = DEFAULT_BALANCED_MAX_WIDTH,
  maxLines,
  as,
  className,
  style,
  ...rest
}: BalancedTextProps) {
  // Typed as a concrete component shape rather than the bare `React.ElementType`
  // union: under React 19 types, rendering an `ElementType` union with `ref` +
  // `children` collapses those props to `never` (TS2745/TS2322). Pinning the
  // accepted props keeps the dynamic tag while staying type-safe.
  const Tag = (as ?? 'span') as React.ComponentType<
    React.HTMLAttributes<HTMLElement> & {
      ref?: React.Ref<HTMLElement>;
      'data-slot'?: string;
      'data-measured'?: string;
    }
  >;
  const ref = React.useRef<HTMLElement | null>(null);

  // Resolve the font: explicit prop wins; otherwise read computed style after mount.
  const measuredFont = useMeasuredFont(ref, font);
  const effectiveFont = font ?? measuredFont ?? DEFAULT_BALANCED_FONT;

  const prepared = usePretextWithSegments(children, effectiveFont);
  // Balanced width that preserves the natural line count at maxWidth.
  const balancedAtMax = useBalancedWidth(prepared, maxWidth);
  // If maxLines is set, search the narrower width that yields ≤ maxLines lines.
  const lineCappedWidth = useMaxLinesWidth(prepared, maxWidth, maxLines);

  const hasMeasured = balancedAtMax > 0 || lineCappedWidth > 0;
  const finalWidth = lineCappedWidth || balancedAtMax;

  // SSR / pre-measurement: rely on CSS `text-wrap: balance`. After measurement,
  // the inline `maxWidth` provides a deterministic balanced layout.
  const inlineStyle: React.CSSProperties = hasMeasured
    ? { maxWidth: finalWidth, ...style }
    : { textWrap: 'balance', ...style };

  return (
    <Tag
      ref={ref}
      data-slot="balanced-text"
      data-measured={hasMeasured ? 'true' : 'false'}
      className={cn(className)}
      style={inlineStyle}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export const BalancedText = React.memo(BalancedTextImpl);
BalancedText.displayName = 'BalancedText';
