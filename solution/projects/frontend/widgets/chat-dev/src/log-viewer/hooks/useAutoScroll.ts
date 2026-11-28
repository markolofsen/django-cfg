// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import type { VirtuosoHandle } from 'react-virtuoso';

/**
 * Sticky-bottom controller for the virtualized log list. Tracks whether
 * the viewport is pinned to the latest entry; when it is and a new entry
 * arrives, jumps to the end via Virtuoso's `scrollToIndex`. When the
 * user has scrolled up, the controller stays out of the way and exposes
 * `scrollToBottom` so the UI can offer a "Jump to latest" pill.
 *
 * The previous (DOM-scroll) implementation set `scrollTop = scrollHeight`
 * inside an effect. That works for a non-virtualized list but fights
 * Virtuoso, which owns the scroller. We instead use Virtuoso's
 * `atBottomStateChange` callback (fired with hysteresis) and call
 * `scrollToIndex` when new entries land while we're pinned.
 */
export interface UseAutoScrollResult {
  virtuosoRef: React.RefObject<VirtuosoHandle | null>;
  isAtBottom: boolean;
  /** Wire to Virtuoso's `atBottomStateChange`. */
  onAtBottomChange: (atBottom: boolean) => void;
  /** Jump to the end of the list. Used by the "New logs below" pill. */
  scrollToBottom: () => void;
}

export function useAutoScroll(
  entryCount: number,
  enabled: boolean,
): UseAutoScrollResult {
  const virtuosoRef = React.useRef<VirtuosoHandle | null>(null);
  const [isAtBottom, setIsAtBottom] = React.useState(true);
  const isAtBottomRef = React.useRef(true);
  const lastCountRef = React.useRef(entryCount);

  const onAtBottomChange = React.useCallback((atBottom: boolean) => {
    isAtBottomRef.current = atBottom;
    setIsAtBottom(atBottom);
  }, []);

  const scrollToBottom = React.useCallback(() => {
    const handle = virtuosoRef.current;
    if (!handle) return;
    // `LAST` is Virtuoso's sentinel for "bottom".
    handle.scrollToIndex({ index: 'LAST', behavior: 'auto' });
    isAtBottomRef.current = true;
    setIsAtBottom(true);
  }, []);

  React.useEffect(() => {
    const prev = lastCountRef.current;
    lastCountRef.current = entryCount;
    if (!enabled) return;
    if (entryCount <= prev) return; // shrink / no-op
    if (!isAtBottomRef.current) return;
    // Defer one frame so Virtuoso settles the new row's height first;
    // otherwise the jump lands one row short on the very first append.
    const id = requestAnimationFrame(() => {
      virtuosoRef.current?.scrollToIndex({ index: 'LAST', behavior: 'auto' });
    });
    return () => cancelAnimationFrame(id);
  }, [entryCount, enabled]);

  return { virtuosoRef, isAtBottom, onAtBottomChange, scrollToBottom };
}
