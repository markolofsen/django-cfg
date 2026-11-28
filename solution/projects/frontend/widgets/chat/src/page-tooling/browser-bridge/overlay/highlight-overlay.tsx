'use client';

import { useEffect } from 'react';
import { createPortal } from 'react-dom';

import { log } from '../logger';
import { SpotlightCanvas } from './spotlight-canvas';
import type { PointDirective, SpotlightRect } from './types';
import { useHighlightTargets } from './use-highlight-targets';
import { type RefResolver } from './resolve-ref';

/** Padding (px) drawn around each highlighted element. */
const HIGHLIGHT_PADDING = 6;
/** Corner radius (px) of the spotlight cut-out. */
const HIGHLIGHT_RADIUS = 6;

/** Props for `HighlightOverlay`. */
export interface HighlightOverlayProps {
  /** `point` directives from the AI's reply. Empty hides the overlay. */
  directives: PointDirective[];
  /** Resolves a CST ref to a live element (the snapshot's registry). */
  resolver: RefResolver | null;
  /** Auto-dismiss after N ms; 0 keeps it until directives clear. */
  ttlMs?: number;
  /** Called when the overlay dismisses (scrim click, Esc, or TTL). */
  onDismiss?: () => void;
}

/**
 * Draws an AI-driven spotlight over elements the assistant pointed at.
 *
 * Read-only: it highlights and optionally focuses elements — it never
 * changes the user's data. The page stays interactive underneath; the
 * scrim is purely visual and dismissable.
 */
export function HighlightOverlay({
  directives,
  resolver,
  ttlMs = 6000,
  onDismiss,
}: HighlightOverlayProps) {
  const targets = useHighlightTargets(directives, resolver);

  // Trace why the overlay does or does not show — the common failure is
  // directives arriving with no resolver, or refs that resolve to nothing.
  useEffect(() => {
    log.info('HighlightOverlay render', {
      directives: directives.length,
      hasResolver: resolver !== null,
      resolvedTargets: targets.length,
    });
  }, [directives, resolver, targets.length]);

  // Auto-dismiss after the TTL once something is showing.
  useEffect(() => {
    if (targets.length === 0 || ttlMs <= 0) return;
    const timer = window.setTimeout(() => onDismiss?.(), ttlMs);
    return () => window.clearTimeout(timer);
  }, [targets.length, ttlMs, onDismiss]);

  // Dismiss on Escape.
  useEffect(() => {
    if (targets.length === 0) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onDismiss?.();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [targets.length, onDismiss]);

  if (targets.length === 0 || typeof document === 'undefined') return null;

  const rects: SpotlightRect[] = targets.map((t) => ({
    rect: t.rect,
    padding: HIGHLIGHT_PADDING,
    radius: HIGHLIGHT_RADIUS,
  }));

  return createPortal(
    <div
      // Above page content (sticky headers ~z-40) but below the chat
      // companion/dock tiers (99/100) — it points at page elements, so it
      // must not cover the chat or any ui-core overlay.
      className="pointer-events-none fixed inset-0 z-[60]"
      data-chat-highlight-overlay=""
    >
      {/* The scrim is click-dismissable; it does not block the page. */}
      <div className="pointer-events-auto absolute inset-0">
        <SpotlightCanvas
          rects={rects}
          pulseRing
          onClick={() => onDismiss?.()}
        />
      </div>

      {/* Captions beside each highlighted element. */}
      {targets.map((t, i) =>
        t.label ? (
          <div
            key={i}
            className="bg-primary text-primary-foreground absolute rounded-md px-2 py-1 text-xs shadow-md"
            style={{
              left: t.rect.x,
              top: t.rect.y + t.rect.height + HIGHLIGHT_PADDING + 6,
              maxWidth: 240,
            }}
          >
            {t.label}
          </div>
        ) : null,
      )}
    </div>,
    document.body,
  );
}
