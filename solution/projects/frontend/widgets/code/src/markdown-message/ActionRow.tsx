'use client';

import React, { memo } from 'react';
import { CopyButton } from '@djangocfg/ui-core/components';

interface ActionRowProps {
  /** Raw text to copy — pass the same source string used for render. */
  value: string;
  /** Bubble side. Just controls flex alignment; nothing is mirrored. */
  isUser: boolean;
  /**
   * Whether the row is currently shown. Owner-controlled (typically
   * `<ChatMessageRow>` toggles this on hover with a small close delay).
   * The component is intentionally dumb about visibility — owners
   * have full control over reveal logic (hover, focus, always-on,
   * touch behaviour, etc.).
   */
  visible: boolean;
}

// Action row that lives directly under a chat bubble.
// Visibility is fully owner-controlled via `visible`.
//
// We render at `opacity-0` (not `display:none`) so the fade in/out
// stays smooth across re-renders. While invisible we drop pointer
// events so a hidden row can't intercept clicks meant for the page
// underneath.
//
// Memoised: re-renders only when `value`, `isUser` or `visible` change.
// All props are primitives, so default shallow comparison is sufficient.
function ActionRowRaw({ value, isUser, visible }: ActionRowProps) {
  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}
        transition-opacity duration-150
        ${visible ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
    >
      <CopyButton
        value={value}
        size="icon"
        variant="ghost"
        iconClassName="h-3.5 w-3.5"
        className="h-7 w-7 text-muted-foreground hover:text-foreground"
        // Hidden rows must not be reachable via Tab — otherwise
        // keyboard users land on an invisible button.
        tabIndex={visible ? 0 : -1}
        aria-hidden={!visible}
      />
    </div>
  );
}

export const ActionRow = memo(ActionRowRaw);
