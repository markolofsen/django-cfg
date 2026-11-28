// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';

/**
 * Copy a string to the clipboard and flash a `copied` flag for
 * `resetMs` (default 1500ms). Safe to call on browsers without
 * `navigator.clipboard` — returns silently.
 */
export function useCopyToClipboard(resetMs = 1500): {
  copied: boolean;
  copy: (text: string) => Promise<void>;
} {
  const [copied, setCopied] = React.useState(false);
  const timerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  React.useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const copy = React.useCallback(
    async (text: string) => {
      try {
        if (typeof navigator === 'undefined' || !navigator.clipboard) return;
        await navigator.clipboard.writeText(text);
        setCopied(true);
        if (timerRef.current) clearTimeout(timerRef.current);
        timerRef.current = setTimeout(() => setCopied(false), resetMs);
      } catch {
        // Clipboard API not available / permission denied — ignore.
      }
    },
    [resetMs],
  );

  return { copied, copy };
}
