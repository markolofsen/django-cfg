'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

import { useIsMobile, usePathnameChange } from '@djangocfg/ui-core/hooks';
import { ChatPanelHeader, ChatSheet, PanelCloseButton } from '../../../chat/ui';

import { useHeaderActions } from './host';
import { GatedBody, type AssistantLockOptions } from '../access/assistant-auth-gate';
import { useAssistantCopy } from '../../../i18n/assistant';
import { headerActions, headingNode } from './header-slots';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** The chat, or the slot that shows it. */
  children: ReactNode;
  title: string;
  /** What the thread is about ("The Quiet Harbour"), shown under the title; absent outside a title or browse scope. */
  contextLine?: string;
  /** Accessible name of the close button on phones. Absent: the bundled word. */
  closeLabel?: string;
  /** Header controls before the close button (for example `SessionsMenu`). */
  actions?: ReactNode;
  /** Show the signed-out view instead of the chat to a reader who is not signed in (see `AssistantFrame`). */
  requireAuth?: boolean;
  lock?: AssistantLockOptions;
  /** Replaces the title in the header (see `AssistantFrame`). The dialog keeps the title as its accessible name. */
  heading?: ReactNode;
  /** The Help `?` (see `AssistantFrame`): absent, the bundled one; `false`, none. The sheet never draws it (no keyboard on a phone). */
  help?: ReactNode | false;
  /** From 768 px up: the floating `window` (default) or the full-screen `sheet`. */
  tablet?: 'window' | 'sheet';
  /** The floating window's distance from the bottom edge (a CSS length, default `1rem`). */
  windowBottom?: string;
  /** On a phone, close the sheet when the page moves to another path (not for a query or hash change). Default true; `false` keeps it open across pages. */
  closeOnNavigate?: boolean;
}

/** The chat when the page has no room for a column: a floating window bottom right on tablets (no backdrop, the page stays usable), the package's full-screen `ChatSheet` on phones (it owns the keyboard, layer and pinning problems). */
export function ChatDock({ open, onOpenChange, children, title, contextLine, closeLabel, actions, requireAuth, lock, heading, help, tablet = 'window', windowBottom, closeOnNavigate = true }: Props) {
  const isMobile = useIsMobile();
  // The sheet covers the whole page: a navigation (a link in the chat, the sign-in button) leaves it over the new page, so it closes. The router is whatever ui-core's adapter bridges.
  usePathnameChange(() => onOpenChange(false), { enabled: open && isMobile && closeOnNavigate });
  const copy = useAssistantCopy();
  const published = useHeaderActions();
  const shown = actions ?? published;
  const chat = <GatedBody requireAuth={requireAuth} lock={lock}>{children}</GatedBody>;

  if (isMobile || tablet === 'sheet') {
    return (
      <ChatSheet open={open} onOpenChange={onOpenChange} title={title} heading={heading} description={contextLine} closeLabel={closeLabel ?? copy.close} actions={shown}>
        {chat}
      </ChatSheet>
    );
  }

  return (
    <FloatingWindow open={open} title={title} contextLine={contextLine} bottom={windowBottom}>
      <ChatPanelHeader
        heading={headingNode(heading, title)}
        description={contextLine ? <p className="truncate text-xs text-muted-foreground">{contextLine}</p> : undefined}
        actions={headerActions(help, shown)}
        close={<PanelCloseButton label={closeLabel ?? copy.close} onClick={() => onOpenChange(false)} />}
      />
      <div className="min-h-0 flex-1 overflow-y-auto">{chat}</div>
    </FloatingWindow>
  );
}

/** How long the window stays mounted after `open` turns false, so it can slide out. A little over the transition. */
const EXIT_MS = 220;

/**
 * The chat as a window over the page, bottom right, for a window too narrow for a column and too wide for a phone sheet: the usual support-chat
 * shape. **Not modal**: no backdrop, no focus trap, no scroll lock, and no dismissal by a press elsewhere or by Esc (those belong to the page); the
 * header's Close, or the floating button the host shows while it is closed, is the way out. It stays mounted for the exit transition.
 * Portalled to `<body>` so a transformed ancestor cannot move a `fixed` box.
 */
function FloatingWindow({ open, title, contextLine, bottom, children }: { open: boolean; title: string; contextLine?: string; bottom?: string; children: ReactNode }) {
  const [present, setPresent] = useState(open);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (open) {
      setPresent(true);
      // Two frames on, so the browser has laid out the hidden start before it moves to the shown one.
      let frame = requestAnimationFrame(() => {
        frame = requestAnimationFrame(() => setVisible(true));
      });
      return () => cancelAnimationFrame(frame);
    }
    setVisible(false);
    const timer = window.setTimeout(() => setPresent(false), EXIT_MS);
    return () => window.clearTimeout(timer);
  }, [open]);

  if (!present || typeof document === 'undefined') return null;
  return createPortal(
    <div
      role="dialog"
      aria-modal="false"
      aria-label={title}
      aria-description={contextLine}
      data-slot="assistant-floating-window"
      data-state={visible ? 'open' : 'closed'}
      style={bottom ? { bottom: `max(${bottom}, env(safe-area-inset-bottom))`, height: `min(680px, calc(100dvh - ${bottom} - 1rem))` } : undefined}
      className={[
        'fixed z-500 flex flex-col overflow-hidden rounded-xl border bg-background shadow-2xl shadow-black/20',
        // A host with a bar along the bottom (a call's controls) states how far up the window starts; the height then shrinks to fit above it.
        bottom ? 'right-4 w-[min(420px,calc(100vw-2rem))]' : 'right-4 bottom-[max(1rem,env(safe-area-inset-bottom))] w-[min(420px,calc(100vw-2rem))] h-[min(680px,calc(100dvh-2rem))]',
        'origin-bottom-right transition-[opacity,transform] duration-200 ease-out motion-reduce:transition-none',
        visible ? 'translate-y-0 scale-100 opacity-100' : 'pointer-events-none translate-y-3 scale-95 opacity-0',
      ].join(' ')}
    >
      {children}
    </div>,
    document.body,
  );
}
