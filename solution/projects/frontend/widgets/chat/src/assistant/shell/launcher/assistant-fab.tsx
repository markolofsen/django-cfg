'use client';

import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';

import { Button } from '@djangocfg/ui-core/components';

import { ASSISTANT_TOGGLE } from '../composer/keys';
import { useAssistantCopy } from '../../../i18n/assistant';
import { AssistantMark } from './assistant-mark';

/** A short line that grows out of the button now and then, so people know what it is for (a live-chat teaser). It has no close control: it leaves by itself, and pressing it opens the chat. The host passes its own, translated, text. */
export interface FabHint {
  /** Absent: the bundled teaser for the active language. */
  text?: string;
  /** Wait after the button appears before the first showing. Default 2500. */
  delayMs?: number;
  /** How long one showing stays. Default 12000. */
  visibleMs?: number;
  /** Quiet rings around the button after the bubble has gone, one per interval. Default: every 25 s, three times. */
  reminders?: { everyMs: number; count: number };
  /** Classes for the bubble's colours (the package draws it with the popover tokens). */
  className?: string;
  /** The bubble appeared (the host may remember that it was shown). */
  onShown?: () => void;
}

interface Props {
  /** Accessible name and tooltip text; the button is icon-only. Absent: the bundled words for the active language. */
  label?: string;
  onClick: () => void;
  hint?: FabHint;
  /** Replaces `AssistantMark` (the "AI" tile), for example a message bubble for a live-chat feel. It is drawn at 28px whatever class it carries (`Button` pins its icons to 16px; the button overrides that). */
  icon?: ReactNode;
  /** The key the host binds to open the assistant (`AssistantFrame` `onOpenChange` binds ⌘J / Ctrl+J), drawn in the tooltip for the viewer's system. `false`: no key shown. */
  hotkey?: string | false;
}

const DEFAULT_REMINDERS = { everyMs: 25_000, count: 3 };

/**
 * The floating assistant button for screens without room for the column: bottom right, clear of the safe area. The host decides when it shows.
 * It pops in on load; with a `hint` a bubble follows after a moment, and ring pulses remind of the button later. Pressing the bubble opens the chat.
 */
export function AssistantFab({ label: given, onClick, hint, icon, hotkey = ASSISTANT_TOGGLE }: Props) {
  const copy = useAssistantCopy();
  const label = given ?? copy.fabLabel;
  const [bubble, setBubble] = useState<'off' | 'in' | 'leaving'>('off');
  const [ring, setRing] = useState(0);
  const dismissed = useRef(false);
  const hintRef = useRef(hint);
  hintRef.current = hint;
  const hasHint = hint !== undefined;
  const delayMs = hint?.delayMs ?? 2500;
  const visibleMs = hint?.visibleMs ?? 12_000;
  const reminders = hint?.reminders ?? DEFAULT_REMINDERS;

  const leave = useCallback(() => {
    setBubble((current) => (current === 'in' ? 'leaving' : current));
    window.setTimeout(() => setBubble('off'), 250);
  }, []);

  // The showing: after the delay, for a while, then away; reminders follow unless the bubble was closed or the button was pressed.
  useEffect(() => {
    if (!hasHint) return;
    const timers: number[] = [];
    timers.push(
      window.setTimeout(() => {
        if (dismissed.current) return;
        setBubble('in');
        hintRef.current?.onShown?.();
        timers.push(window.setTimeout(leave, visibleMs));
        for (let i = 1; i <= reminders.count; i += 1) {
          timers.push(
            window.setTimeout(() => {
              if (!dismissed.current) setRing((n) => n + 1);
            }, visibleMs + i * reminders.everyMs),
          );
        }
      }, delayMs),
    );
    return () => timers.forEach((id) => window.clearTimeout(id));
  }, [hasHint, delayMs, visibleMs, reminders.count, reminders.everyMs, leave]);

  const press = () => {
    dismissed.current = true;
    onClick();
  };

  return (
    <div
      style={{ right: 'max(1rem, env(safe-area-inset-right))', bottom: 'max(1rem, env(safe-area-inset-bottom))' }}
      className="pointer-events-none fixed z-40 flex flex-col items-end gap-2"
    >
      {hint && bubble !== 'off' ? (
        // Like a message bubble: one soft shape whose corner points at the button, text balanced on its lines, nothing to close.
        <button
          type="button"
          role="status"
          onClick={press}
          data-leaving={bubble === 'leaving' || undefined}
          className={`assistant-fab-hint pointer-events-auto -mb-1 max-w-[min(16rem,calc(100vw-2rem))] rounded-[1.25rem] rounded-br-[0.4rem] px-4 py-2.5 text-start text-[0.9375rem] font-medium leading-snug tracking-[-0.01em] text-balance shadow-lg outline-none focus-visible:ring-2 focus-visible:ring-ring ${hint.className ?? 'bg-popover text-popover-foreground'}`}
        >
          {hint.text ?? copy.hint}
        </button>
      ) : null}
      <span className="relative inline-flex">
        {ring > 0 ? <span key={ring} aria-hidden="true" className="assistant-fab-ring absolute inset-0 rounded-full bg-primary" /> : null}
        <Button
          type="button"
          aria-label={label}
          tooltip={hotkey ? { content: label, hotkey, side: 'left', sideOffset: 10 } : undefined}
          onClick={press}
          className="assistant-fab pointer-events-auto relative inline-flex size-14 [&_svg]:size-7 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg outline-none transition-transform hover:scale-105 hover:bg-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 active:scale-95"
        >
          {icon ?? <AssistantMark className="size-7" />}
        </Button>
      </span>
    </div>
  );
}
