'use client';

import React, { memo, useCallback, useEffect, useRef, useState } from 'react';
import { useMediaQuery } from '@djangocfg/ui-core/hooks';

interface ChatMessageRowProps {
  /** Side of the conversation — drives flex alignment and `isUser`
   *  passed to `actions`. */
  isUser: boolean;
  /** The bubble (your own JSX). Anything goes — `<MarkdownMessage>`,
   *  custom card, multi-element composition. */
  children: React.ReactNode;
  /** Render-prop for the action row. Receives `visible` so the row
   *  knows when to fade in/out. Render `null` to opt out. */
  actions?: (visible: boolean, isUser: boolean) => React.ReactNode;
  /** Close delay in ms after the cursor leaves the row. Long enough
   *  to bridge cursor travel from bubble → action button without
   *  flicker. Default 250ms (Radix Tooltip-ish). */
  closeDelayMs?: number;
  /** Optional class on the column container. */
  className?: string;
}

// Owner of the bubble + action row layout.
//
// Why a state-based hover instead of `group-hover` CSS:
//   - CSS-only hover bridges break when the cursor crosses gaps
//     between the bubble and the (initially-invisible) row — the
//     row's `pointer-events-none` lets the cursor "fall through",
//     `group-hover` flips off, the row vanishes mid-travel.
//   - State + a small close timeout gives Radix-Tooltip-style
//     stability: enter shows immediately, leave waits N ms.
//   - On touch (`@media (hover:none)`) hover doesn't exist; we
//     always pass `visible={true}` so the affordance is reachable.
//
// The action row is rendered **absolutely** under the bubble so
// hidden rows don't allocate vertical space — no dead-air gap
// between consecutive messages.
//
// Memoised: re-renders only when `isUser`, `children`, `actions`,
// `closeDelayMs` or `className` change. `actions` render-prop is
// compared by reference — callers should stabilise it with useCallback.
function ChatMessageRowRaw({
  isUser,
  children,
  actions,
  closeDelayMs = 250,
  className = '',
}: ChatMessageRowProps) {
  const isTouch = useMediaQuery('(hover: none), (pointer: coarse)');
  const [hovered, setHovered] = useState(false);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const cancelClose = useCallback(() => {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  }, []);

  const open = useCallback(() => {
    cancelClose();
    setHovered(true);
  }, [cancelClose]);

  const scheduleClose = useCallback(() => {
    cancelClose();
    closeTimer.current = setTimeout(() => setHovered(false), closeDelayMs);
  }, [cancelClose, closeDelayMs]);

  useEffect(() => () => cancelClose(), [cancelClose]);

  // Touch: always-visible. Hover: state-driven.
  const visible = isTouch || hovered;

  // On touch, `static` positioning so the row claims real layout
  // space (otherwise an absolute always-visible row would still
  // overlap the next message). On hover devices, `absolute` so the
  // hidden row doesn't leave dead air between bubbles.
  const rowPositionClass = isTouch ? 'static mt-1' : 'absolute top-full';
  const rowSideClass = isUser ? 'right-0' : 'left-0';

  return (
    <div
      className={`relative flex flex-col ${isUser ? 'items-end' : 'items-start'} ${className}`}
      onPointerEnter={isTouch ? undefined : open}
      onPointerLeave={isTouch ? undefined : scheduleClose}
      onFocusCapture={open}
      onBlurCapture={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node | null)) scheduleClose();
      }}
    >
      {children}
      {actions && (
        <div className={`${rowPositionClass} ${rowSideClass}`}>
          {actions(visible, isUser)}
        </div>
      )}
    </div>
  );
}

export const ChatMessageRow = memo(ChatMessageRowRaw);
