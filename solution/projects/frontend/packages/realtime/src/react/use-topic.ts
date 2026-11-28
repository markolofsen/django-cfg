'use client';

import { useEffect, useRef } from 'react';

import { topicName } from '../client';
import { useRealtimeContext } from './context';
import { useRealtimeState } from './use-realtime-state';

import type { EventMeta, TopicRef } from '../client';
import type { SubErrorCode } from '../protocol';
import type { TopicState } from '../store';

export interface UseTopicOptions {
  /** History no longer reaches the last offset: refetch. Defaults to the provider's `onGap`. */
  onGap?: (topic: string) => void;
  /** The server refused the topic (`sub_err`). */
  onRefused?: (code: SubErrorCode, topic: string) => void;
}

/**
 * Receive a topic while the component is mounted: a name, or a typed topic from
 * the generated `realtime.ts` (`ordersTopic({ orderId })`), whose event type
 * types `onEvent`. `null` subscribes to nothing. Only a new topic NAME
 * resubscribes: a builder called inline and new handlers each render are fine.
 * Returns the topic's status and offset (`undefined` before the first
 * subscription and outside a provider).
 */
export function useTopic<E = unknown>(
  topic: TopicRef<E> | null,
  onEvent: (data: E, meta: EventMeta) => void,
  options: UseTopicOptions = {},
): TopicState | undefined {
  const context = useRealtimeContext();
  const name = topic === null ? null : topicName(topic);
  const latest = useRef({ topic, onEvent, onGap: options.onGap, onRefused: options.onRefused });
  useEffect(() => {
    latest.current = { topic, onEvent, onGap: options.onGap, onRefused: options.onRefused };
  });

  useEffect(() => {
    const ref = latest.current.topic;
    if (context === null || name === null || ref === null) return;
    return context.client.subscribe<E>(ref, {
      onEvent: (data, meta) => latest.current.onEvent(data, meta),
      onGap: (t) => {
        const own = latest.current.onGap;
        if (own) own(t);
        else context.gap(t);
      },
      onRefused: (code, t) => latest.current.onRefused?.(code, t),
    });
  }, [context, name]);

  return useRealtimeState((s) => (name === null ? undefined : s.topics[name]));
}
