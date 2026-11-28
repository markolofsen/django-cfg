'use client';

import { createContext, useContext } from 'react';

import type { CaptureResult } from '../engine';

/**
 * The page-snapshot context value.
 *
 * Exposes the opt-in state, capture, staleness, and a `getChatMetadata`
 * contributor the host passes to `ChatProvider.getDynamicMetadata`.
 */
export interface PageSnapshotContextValue {
  /** Whether the user has opted in to sharing page context. */
  isLinked: boolean;
  /** Toggle the opt-in. */
  setIsLinked: (linked: boolean) => void;

  /**
   * Capture a snapshot for sending. Returns null when not linked, when
   * not in a browser, or when capture fails. Updates `lastSnapshot` and
   * clears the stale flag.
   */
  capture: () => CaptureResult | null;

  /**
   * Capture a snapshot for preview only — ignores the opt-in gate and
   * does not update staleness state. Drives the preview drawer.
   */
  generatePreview: () => CaptureResult | null;

  /**
   * The chat metadata contributor. Returns `{ pageContext }` when linked,
   * `undefined` otherwise. Read by `copilot` at send time, so it captures
   * a fresh snapshot per message (capture-on-submit).
   *
   * It named `ChatProvider.getDynamicMetadata` until 2026-09-10. That prop
   * belonged to the archived chat; the rebuilt one has no metadata seam, which
   * is why the copilot wraps the adapter instead.
   */
  getChatMetadata: () => Record<string, unknown> | undefined;

  /** The most recent captured snapshot, if any. */
  lastSnapshot: CaptureResult | null;

  /**
   * The snapshot that rode the most recent chat message — the one the
   * assistant was given. CST ref ids are positional, so a `point`
   * directive in the reply must be resolved against *this* snapshot's
   * ref registry, never `lastSnapshot` (which the route-change
   * auto-capture overwrites) and never a fresh capture (which re-numbers
   * refs). Null until the first message is sent.
   */
  sentSnapshot: CaptureResult | null;

  /** Whether the captured context is stale vs the current page. */
  isStale: boolean;

  /** Force a fresh capture and clear staleness (e.g. chip "refresh"). */
  refresh: () => void;
}

/** Internal context — consumed via `usePageSnapshot`. */
export const PageSnapshotContext =
  createContext<PageSnapshotContextValue | null>(null);

/**
 * Access the page-snapshot context.
 *
 * Must be used within a `PageSnapshotProvider`.
 */
export function usePageSnapshot(): PageSnapshotContextValue {
  const ctx = useContext(PageSnapshotContext);
  if (!ctx) {
    throw new Error(
      'usePageSnapshot must be used within a PageSnapshotProvider.',
    );
  }
  return ctx;
}
