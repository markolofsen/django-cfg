'use client';

import { useMemo } from 'react';

import { useAssistantHistory, usePublishHistoryPanel } from '../shell';

import { SessionsPanel } from './sessions-panel';

type SessionsPanelProps = React.ComponentProps<typeof SessionsPanel>;

/**
 * The chat history screen (`SessionsPanel`), published from wherever the session is. Render it beside `AssistantPortal`, with the same `session` as `SessionsMenu`;
 * the slot draws it over the conversation while the history is open. Without a provider it draws nothing.
 */
export function AssistantHistory({ session, locale }: { session: SessionsPanelProps['session']; locale?: string }) {
  const setOpen = useAssistantHistory()?.setOpen;
  const node = useMemo(() => (setOpen ? <SessionsPanel session={session} locale={locale} onDone={() => setOpen(false)} /> : null), [session, locale, setOpen]);
  usePublishHistoryPanel(node);
  return null;
}
