// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// When `maxLines` is set we want the narrowest width that produces ≤ maxLines.
// `useBalancedWidth` only preserves the *natural* line count at maxWidth — it
// won't push the text into fewer lines than the user typed by accident.
// This hook complements it: it walks line counts and binary-searches for a
// width ≤ maxWidth that yields exactly `min(natural, maxLines)` lines.

'use client';

import { walkLineRanges } from '@chenglou/pretext';
import * as React from 'react';
import type { PreparedTextWithSegments } from '../../../../lib/pretext';

// Imported statically: `@chenglou/pretext` is ESM-only, so the previous lazy
// `require` resolved in no runtime — under Vite/ESM `require` is not defined
// and the first render threw `require is not defined`.

export function useMaxLinesWidth(
  prepared: PreparedTextWithSegments | null,
  maxWidth: number,
  maxLines: number | undefined,
): number {
  return React.useMemo(() => {
    if (!prepared || !maxLines || maxLines <= 0 || maxWidth <= 0) return 0;

    // Natural line count at maxWidth. If it's already within the cap, defer
    // to `useBalancedWidth` (returning 0 means "don't use my value").
    let naturalCount = 0;
    walkLineRanges(prepared, maxWidth, () => {
      naturalCount++;
    });
    if (naturalCount <= maxLines) return 0;

    // Binary search: find the narrowest width that produces ≤ maxLines lines.
    // Wider width → fewer lines, narrower width → more lines.
    let lo = 1;
    let hi = Math.ceil(maxWidth);
    let best = hi;

    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      let count = 0;
      walkLineRanges(prepared, mid, () => {
        count++;
      });

      if (count <= maxLines) {
        best = mid;
        hi = mid - 1; // try narrower
      } else {
        lo = mid + 1;
      }
    }

    return best;
  }, [prepared, maxWidth, maxLines]);
}
