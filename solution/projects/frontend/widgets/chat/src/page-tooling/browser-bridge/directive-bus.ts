'use client';

/**
 * AI directive bus — receives `point` directives off the chat SSE
 * stream and exposes them to the highlight overlay.
 *
 * The backend emits a `directive` SSE event carrying highlight/focus
 * instructions keyed by CST ref ids. A host transport observes the raw
 * frame and calls `pushDirectives`; the chat UI subscribes through
 * `useChatDirectives` and feeds the result to `<HighlightOverlay>`.
 *
 * A singleton bus keeps the transport (which has no React context)
 * decoupled from the consuming component.
 */

import { useSyncExternalStore } from 'react';

import { log } from './logger';
import type { PointDirective } from './overlay/types';

// ─── Wire parsing ───────────────────────────────────────────────────

/** A CST ref looks like "@e4". */
const REF_RE = /^@e\d+$/;

/**
 * Validate the raw `directives` array from a `directive` SSE frame.
 *
 * The backend already validates refs against the snapshot, but the wire
 * is untyped at this boundary — drop anything malformed so a bad frame
 * can never crash the overlay.
 */
export function parseDirectives(raw: unknown): PointDirective[] {
  if (!Array.isArray(raw)) {
    log.warn('parseDirectives: payload is not an array', { raw });
    return [];
  }
  const out: PointDirective[] = [];
  let dropped = 0;
  for (const item of raw) {
    if (!item || typeof item !== 'object') {
      dropped++;
      continue;
    }
    const d = item as Record<string, unknown>;
    if (d.type !== 'point') {
      dropped++;
      continue;
    }
    if (typeof d.ref !== 'string' || !REF_RE.test(d.ref)) {
      log.warn('parseDirectives: dropped directive with bad ref', { ref: d.ref });
      dropped++;
      continue;
    }
    const directive: PointDirective = {
      type: 'point',
      ref: d.ref as PointDirective['ref'],
    };
    if (d.highlight === false) directive.highlight = false;
    if (d.focus === true) directive.focus = true;
    if (typeof d.label === 'string' && d.label.trim()) {
      directive.label = d.label.trim();
    }
    out.push(directive);
  }
  log.info('parseDirectives', { in: raw.length, out: out.length, dropped });
  return out;
}

// ─── Singleton bus ──────────────────────────────────────────────────

let current: PointDirective[] = [];
const subscribers = new Set<() => void>();

function notify(): void {
  for (const s of subscribers) s();
}

/**
 * Transport-side entry point. Replaces the active directive set — the
 * latest `directive` event for a turn wins; an empty array clears the
 * overlay. Called synchronously from a host transport's event handler.
 */
export function pushDirectives(directives: PointDirective[]): void {
  log.info('pushDirectives → bus', {
    count: directives.length,
    refs: directives.map((d) => d.ref),
    subscribers: subscribers.size,
  });
  current = directives;
  notify();
}

/** Clear the active directives (e.g. when the overlay is dismissed). */
export function clearDirectives(): void {
  if (current.length === 0) return;
  log.info('clearDirectives');
  current = [];
  notify();
}

function subscribe(cb: () => void): () => void {
  subscribers.add(cb);
  return () => subscribers.delete(cb);
}

function getSnapshot(): PointDirective[] {
  return current;
}

/** Stable empty reference for the SSR snapshot. */
const EMPTY: PointDirective[] = [];

/**
 * Subscribe to the active `point` directives. Re-renders the caller
 * whenever a new `directive` event arrives or the set is cleared.
 */
export function useChatDirectives(): PointDirective[] {
  return useSyncExternalStore(subscribe, getSnapshot, () => EMPTY);
}
