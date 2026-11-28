'use client';

import { useState } from 'react';

import { useTopic } from '@djangocfg/realtime/react';

import type { DemoPingEventOutput } from '@/api/generated/models/demoPingEvent.zod';
import type { RealtimeTopic } from '@/api/generated/realtime';
import type { EventMeta, TopicState } from '@djangocfg/realtime';

const LIMIT = 20;

export interface LoggedPing {
  offset: string;
  at: string;
  note: string;
  /** The socket whose request published it; null for the CLI, a job, or exclude_sender=False. */
  originCid: string | null;
}

/** The last pings received on a topic while mounted, newest first. `null` subscribes to nothing. */
export function useTopicLog(topic: RealtimeTopic<DemoPingEventOutput> | null): {
  entries: LoggedPing[];
  state: TopicState | undefined;
} {
  const [entries, setEntries] = useState<LoggedPing[]>([]);
  const state = useTopic(topic, (event: DemoPingEventOutput, meta: EventMeta) => {
    const entry: LoggedPing = {
      offset: meta.offset,
      at: event.at ?? '',
      note: event.note ?? '',
      originCid: meta.originCid,
    };
    setEntries((prev) => [entry, ...prev].slice(0, LIMIT));
  });
  return { entries, state };
}
