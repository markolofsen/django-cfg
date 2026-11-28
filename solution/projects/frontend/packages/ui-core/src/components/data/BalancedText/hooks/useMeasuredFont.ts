// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Read the host element's computed font shorthand after mount so the caller
// doesn't have to duplicate the design tokens that style the element.
// Returns `null` until the effect has run (SSR + first render), at which point
// the BalancedText component falls back to a literal default font string.

'use client';

import * as React from 'react';

export function useMeasuredFont(
  ref: React.RefObject<HTMLElement | null>,
  explicitFont: string | undefined,
): string | null {
  const [font, setFont] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (explicitFont) return; // caller wins; skip measurement
    const el = ref.current;
    if (!el) return;
    const cs = getComputedStyle(el);
    // `font` shorthand is the most compact; some browsers return '' when
    // individual properties were set separately — fall back to a manual build.
    const shorthand = cs.font;
    if (shorthand && shorthand.trim() !== '') {
      setFont(shorthand);
      return;
    }
    const composed = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} / ${cs.lineHeight} ${cs.fontFamily}`;
    setFont(composed);
  }, [ref, explicitFont]);

  return font;
}
