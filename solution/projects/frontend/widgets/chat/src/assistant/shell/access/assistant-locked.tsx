'use client';

import type { ReactNode } from 'react';

import { useAssistantCopy } from '../../../i18n/assistant';
import { AssistantMark } from '../launcher/assistant-mark';

interface Props {
  /** Absent: the bundled "sign in to chat" words for the active language. */
  title?: string;
  body?: string;
  /** The way out ("Sign in"); absent when there is none (the assistant is switched off). */
  action?: ReactNode;
  /** @deprecated No composer is drawn any more (the block is centred in the whole column); ignored. */
  composerLabel?: string;
  /** Replaces the lock. */
  icon?: ReactNode;
  /** @deprecated Ignored: the action button is the only way out. */
  onComposerClick?: () => void;
}

/**
 * The chat as it looks when the viewer cannot write: a centred icon, one short reason and the action, centred in the full height of the column (no inert composer: it only looked like a field that does not work).
 * The root fills its parent two ways: `flex-1` when the parent is a flex column (the docked column) and `min-h-full` when it is a plain scrolling block (the tablet panel and the phone sheet); with only one of them the block sat against the header.
 */
export function AssistantLocked({ title, body, action, icon }: Props) {
  const copy = useAssistantCopy();
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-4 px-8 py-12 text-center">
        <span className="grid size-16 place-items-center rounded-full bg-muted text-foreground ring-1 ring-border">{icon ?? <AssistantMark className="size-9" />}</span>
        <div className="space-y-2">
          <p className="font-display text-lg font-semibold">{title ?? copy.lockedTitle}</p>
          <p className="mx-auto max-w-[32ch] text-sm leading-relaxed text-muted-foreground">{body ?? copy.lockedBody}</p>
        </div>
        {action ? <div className="mt-2">{action}</div> : null}
      </div>
    </div>
  );
}
