/**
 * What happens inside a chat, as data.
 *
 * The alternative this replaces is a prop threaded from the component that
 * KNOWS a thing happened to the component that must react — through every layer
 * between them, none of which cares. `ComposerQueue` needed the composer's
 * field; the ask card needs the composer's focus; a host wants to know a prompt
 * was taken back. Each on its own is one more prop on `<Chat>`, and the
 * predecessor reached 83 of them that way.
 *
 * Modelled on `a typed transport`'s `IEventBus` — one typed map, no untyped
 * escape hatch — but declared here rather than imported: the chat package must
 * not depend on the transport to talk to itself.
 */

import type { Draft } from "../compose/outbound";

/**
 * Every event, with its payload. `void` means the event carries nothing.
 *
 * Names are `subject:verb`, past tense: an event states what HAPPENED. A name
 * in the imperative ("focus:composer") is a command wearing an event's clothes,
 * and a bus that carries commands becomes a second, untyped API for the thing
 * it is commanding.
 */
export interface ChatEventMap {
  /** A queued prompt was taken back for editing; it has left the queue. */
  "queue:taken": { readonly id: string; readonly draft: Draft };
  /** A prompt was promoted past the running turn, which is now aborted. */
  "queue:promoted": { readonly id: string };
  /** A turn was sent. Carries what went out, not what comes back. */
  "turn:sent": { readonly draft: Draft };
}

export type ChatEventName = keyof ChatEventMap;

export type ChatEventHandler<E extends ChatEventName> = (payload: ChatEventMap[E]) => void;

export type Unsubscribe = () => void;

/** Names whose payload is `void`: emitted with no second argument. */
export type VoidChatEvent = {
  [E in ChatEventName]: ChatEventMap[E] extends void ? E : never;
}[ChatEventName];

export type DataChatEvent = Exclude<ChatEventName, VoidChatEvent>;

export interface ChatEvents {
  on<E extends DataChatEvent>(event: E, handler: ChatEventHandler<E>): Unsubscribe;
  on<E extends VoidChatEvent>(event: E, handler: () => void): Unsubscribe;
  emit<E extends DataChatEvent>(event: E, payload: ChatEventMap[E]): void;
  emit<E extends VoidChatEvent>(event: E): void;
}

/**
 * An in-memory bus, one per chat.
 *
 * Per chat and not module-scoped: two conversations open side by side must not
 * hear each other's events, which a singleton cannot express. Created beside
 * the store, handed down the same provider.
 *
 * Handlers are copied before dispatch, which fixes the listener list at the
 * moment of the emit. A `Set` tolerates deleting the CURRENT entry mid-loop, so
 * a one-shot unsubscribing itself is safe either way — the case that is not is
 * one handler unsubscribing ANOTHER. Without the copy that second handler is
 * silently skipped for this emit, which reads exactly like an event that never
 * fired. Everyone listening when the event happened hears it.
 */
export function createChatEvents(): ChatEvents {
  const handlers = new Map<ChatEventName, Set<(payload: never) => void>>();

  function on(event: ChatEventName, handler: (payload: never) => void): Unsubscribe {
    const set = handlers.get(event) ?? new Set();
    handlers.set(event, set);
    set.add(handler);
    return () => {
      set.delete(handler);
    };
  }

  function emit(event: ChatEventName, payload?: unknown): void {
    const set = handlers.get(event);
    if (set === undefined) return;
    for (const handler of [...set]) (handler as (p: unknown) => void)(payload);
  }

  return { on, emit } as ChatEvents;
}
