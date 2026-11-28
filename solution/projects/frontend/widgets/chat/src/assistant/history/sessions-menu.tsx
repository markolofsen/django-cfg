'use client';

import { History, MessageSquare, Plus } from 'lucide-react';
import type { ReactNode } from 'react';

import { PanelIconButton } from '../../chat/ui';

import { useAssistantHistory } from '../shell';
import { useAssistantCopy } from '../shell';
import type { Session } from '../session';

interface Props {
  session: Pick<Session, 'busy' | 'startNew'>;
  /** The language of the words. Absent: the assistant's active language. */
  locale?: string;
  /** Hide the history button and keep only "New chat" (a host with no list endpoint, such as an anonymous one). */
  newOnly?: boolean;
  /** A free slot after everything else, for anything the host adds (its own `Button`s, a `MenuBuilder` dropdown, a switch). */
  children?: ReactNode;
}

/**
 * The chat's header controls (put them in the frame's or the dock's `actions`, next to Close; each is the chat's one `PanelIconButton`, so they match Help and Close on every surface): "New chat" (a new session; the old ones stay) and a History button
 * that swaps the conversation for the list of earlier chats (`AssistantHistory` draws it; the same button returns). "New chat" waits while an answer streams: Stop ends it first.
 * Outside `AssistantHostProvider` there is no screen to swap to, so only "New chat" shows.
 */
export function SessionsMenu({ session, locale, newOnly = false, children }: Props) {
  const copy = useAssistantCopy(locale);
  const history = useAssistantHistory();
  const open = history?.open === true;
  return (
    <div className="flex items-center gap-1" data-testid="sessions-menu">
      <PanelIconButton
        label={copy.newChat}
        disabled={session.busy}
        onClick={() => {
          history?.setOpen(false);
          void session.startNew();
        }}
      >
        <Plus className="size-4" aria-hidden="true" />
      </PanelIconButton>
      {newOnly || history === null ? null : (
        <PanelIconButton
          label={open ? copy.sessionsBack : copy.sessions}
          aria-pressed={open}
          onClick={() => history.setOpen(!open)}
        >
          {open ? <MessageSquare className="size-4" aria-hidden="true" /> : <History className="size-4" aria-hidden="true" />}
        </PanelIconButton>
      )}
      {children}
    </div>
  );
}
