'use client';

import { Plus, Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { Input } from '@djangocfg/ui-core/components';

import { useAssistantCopy, useAssistantLocale } from '../shell';
import type { Session } from '../session';
import { relativeTime } from '../session';
import { filterSessions, groupSessions } from '../session';

interface Props {
  session: Pick<Session, 'thread' | 'sessions' | 'busy' | 'startNew' | 'switchTo' | 'refreshSessions'>;
  /** Called after a chat is opened or a new one is started: the host returns to the conversation. */
  onDone: () => void;
  locale?: string;
}

/** The search field appears from this many chats on: below it the whole list fits and a field is noise. */
const SEARCH_FROM = 7;

/**
 * The chat history as a screen of its own, drawn in place of the conversation (Messages, Notes): a "New chat" row, the chats grouped by Today / Yesterday / month,
 * a search field once the list is long. Rows are plain buttons, so the keyboard and a screen reader work with no extra code; the open chat is marked.
 * It reads the list when it appears and never fetches more than the session already holds.
 */
export function SessionsPanel({ session, onDone, locale }: Props) {
  const copy = useAssistantCopy(locale);
  const active = useAssistantLocale(locale);
  const current = session.thread.kind === 'ready' ? session.thread.session : null;
  const { refreshSessions, startNew, switchTo, busy, sessions } = session;
  const [query, setQuery] = useState('');

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  const shown = useMemo(() => (sessions === null ? [] : filterSessions(sessions, query)), [sessions, query]);
  const groups = useMemo(() => groupSessions(shown, active), [shown, active]);
  const searchable = (sessions?.length ?? 0) >= SEARCH_FROM;

  const open = async (id: string) => {
    if (id === current || (await switchTo(id))) onDone();
  };
  const fresh = async () => {
    await startNew();
    onDone();
  };

  return (
    <div className="flex h-full min-h-0 flex-col" data-testid="sessions-panel">
      <div className="flex flex-col gap-2 px-3 pt-3 pb-2">
        <button
          type="button"
          disabled={busy}
          onClick={() => void fresh()}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-primary hover:bg-primary/10 focus-visible:outline-2 focus-visible:outline-ring disabled:opacity-50"
        >
          <Plus className="size-4" aria-hidden="true" />
          {copy.newChat}
        </button>
        {searchable ? (
          <div className="relative">
            <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
            <Input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={copy.sessionsSearch} aria-label={copy.sessionsSearch} className="pl-8" />
          </div>
        ) : null}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-3">
        {sessions === null ? null : sessions.length === 0 ? (
          <p className="px-3 py-6 text-center text-sm text-muted-foreground">{copy.sessionsEmpty}</p>
        ) : groups.length === 0 ? (
          <p className="px-3 py-6 text-center text-sm text-muted-foreground">{copy.sessionsNoMatch}</p>
        ) : (
          groups.map((group) => (
            <section key={group.key} aria-label={group.label} className="pb-2">
              <h3 className="px-3 pt-3 pb-1 text-xs font-medium text-muted-foreground">{group.label}</h3>
              <ul className="flex flex-col">
                {group.items.map((item) => {
                  const isCurrent = item.id === current;
                  return (
                    <li key={item.id}>
                      <button
                        type="button"
                        disabled={busy}
                        aria-current={isCurrent ? 'true' : undefined}
                        onClick={() => void open(item.id)}
                        className={`flex w-full items-baseline justify-between gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-muted focus-visible:outline-2 focus-visible:outline-ring disabled:opacity-50 ${isCurrent ? 'bg-muted font-medium' : ''}`}
                      >
                        <span className="min-w-0 flex-1 truncate">{item.title || copy.newChat}</span>
                        <span className="shrink-0 text-xs text-muted-foreground">{relativeTime(item.last_message_at, active)}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
