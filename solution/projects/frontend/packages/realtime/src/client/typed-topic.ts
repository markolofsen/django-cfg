import type { EventMeta, TopicHandler } from './subscriptions';

/** The part of a zod schema the client uses; zod's own `ZodType<E>` satisfies it. */
export interface EventSchema<E> {
  safeParse(data: unknown): { success: true; data: E } | { success: false; error: unknown };
}

/**
 * A topic as the generated `realtime.ts` builds it (`ordersTopic({ orderId })`).
 * Structural on purpose: the package never imports generated code, and the
 * generator's `RealtimeTopic<E>` fits this shape. `__event` only carries `E`
 * for inference.
 */
export interface RealtimeTopic<E> {
  readonly name: string;
  readonly pattern?: string;
  readonly anonymous?: boolean;
  readonly schema: EventSchema<E> | null;
  readonly __event?: E;
}

/** A topic name, or a typed topic whose `E` types the events. */
export type TopicRef<E = unknown> = string | RealtimeTopic<E>;

export interface TypedTopicHandler<E> {
  onEvent(data: E, meta: EventMeta): void;
  onGap?: TopicHandler['onGap'];
  onRefused?: TopicHandler['onRefused'];
  onLive?: TopicHandler['onLive'];
}

export function topicName(topic: TopicRef<unknown>): string {
  return typeof topic === 'string' ? topic : topic.name;
}

/** Called with an event that does not match its topic's schema; the event is not delivered. */
export type InvalidEventHandler = (topic: string, error: unknown, data: unknown) => void;

/**
 * Wrap a typed handler for the untyped registry. With `validate` (development)
 * every payload goes through the schema and a mismatch is reported instead of
 * delivered. Without it the payload is trusted: the server validates every
 * publish against the same schema before it reaches the wire.
 */
export function toWireHandler<E>(
  topic: TopicRef<E>,
  handler: TypedTopicHandler<E>,
  validate: boolean,
  onInvalid: InvalidEventHandler,
): TopicHandler {
  const schema = typeof topic === 'string' ? null : topic.schema;
  const deliver = (data: unknown, meta: EventMeta) => {
    if (schema === null) {
      // An untyped topic: `E` defaults to `unknown`, so this states nothing new.
      handler.onEvent(data as E, meta);
      return;
    }
    if (!validate) {
      handler.onEvent(data as E, meta);
      return;
    }
    const parsed = schema.safeParse(data);
    if (parsed.success) handler.onEvent(parsed.data, meta);
    else onInvalid(meta.topic, parsed.error, data);
  };
  return { onEvent: deliver, onGap: handler.onGap, onRefused: handler.onRefused, onLive: handler.onLive };
}
