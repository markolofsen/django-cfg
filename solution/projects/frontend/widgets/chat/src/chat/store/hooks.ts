/**
 * React bindings for the store.
 *
 * The split is deliberate and is the whole performance story: the transcript
 * subscribes to `useMessageIds()` and each row to `useMessage(id)`, so a token
 * arriving in the last message re-renders one row rather than the list. MUI X
 * settled on the same pair, and a single `useMessages()` returning the array
 * cannot be optimised into it afterwards — every consumer would have to change.
 */

import { useCallback, useContext, useMemo, useSyncExternalStore } from "react";

import type { ChatCapabilities } from "../core/capabilities";
import type { ChatEvents } from "../core/conversation/events";
import type { ChatMessage } from "../core/conversation/parts";
import { ChatContext, type ChatContextValue } from "./context";
import type { ChatState, ChatStore } from "./store";

/**
 * Has the in-flight reply produced anything a reader can SEE yet?
 *
 * Two thresholds were tried and both were too early, each by one step:
 *
 *   - `streamingId !== null` flips on `message-start`, which opens an EMPTY
 *     message;
 *   - a non-empty `parts` array flips on `text-start`, which appends a part
 *     whose text is `""`.
 *
 * Both leave a measurable silent gap where the indicator is gone and the reply
 * has not appeared — the exact state it exists to prevent. So the question is
 * asked of the CONTENT: a text or reasoning part counts once it has characters,
 * and any other part counts as soon as it exists, because a tool call renders
 * its own header immediately.
 *
 * Returns a boolean rather than the message: `useSyncExternalStore` compares by
 * reference, and a selector minting an object per call re-renders forever.
 */
function hasRenderedPart(state: ChatState): boolean {
  const id = state.transcript.streamingId;
  if (id === null) return false;
  const parts = state.transcript.byId[id]?.parts ?? [];
  return parts.some((part) =>
    part.type === "text" || part.type === "reasoning" ? part.text !== "" : true,
  );
}

function useChatContext(): ChatContextValue {
  const value = useContext(ChatContext);
  if (value === null) {
    throw new Error("chat hooks must be used inside <ChatProvider>");
  }
  return value;
}

export function useChatStore(): ChatStore {
  return useChatContext().store;
}

/**
 * What this chat can do.
 *
 * A component asks for the capability it needs and renders nothing when it is
 * absent — that check IS the feature flag. There is no second boolean that can
 * disagree with it.
 */
export function useCapabilities(): ChatCapabilities {
  return useChatContext().capabilities;
}

/**
 * The chat's event bus.
 *
 * Announcements, not state: subscribe in an effect, never read during render.
 * What is TRUE comes from the store — a component that mirrors an event into
 * its own state has made a second owner of a fact the store already holds.
 *
 * The identity is stable for the life of the provider, so an effect may depend
 * on it without re-subscribing.
 */
export function useChatEvents(): ChatEvents {
  return useChatContext().events;
}

/**
 * Message ids in order.
 *
 * The identity of the array matters: `useSyncExternalStore` compares by
 * reference, so returning a fresh array per call would re-render the transcript
 * on every token. The reducer keeps `ids` stable unless a message is added, so
 * reading it directly is both correct and cheap.
 */
export function useMessageIds(): readonly string[] {
  const store = useChatStore();
  return useSyncExternalStore(
    store.subscribe,
    useCallback(() => store.getState().transcript.ids, [store]),
  );
}

/**
 * Whether the host's history fetch has answered.
 *
 * `false` with an empty transcript is LOADING, not empty — the distinction the
 * empty state needs and cannot make from the message list alone.
 */
export function useHistoryLoaded(): boolean {
  const store = useChatStore();
  return useSyncExternalStore(
    store.subscribe,
    useCallback(() => store.getState().historyLoaded, [store]),
  );
}

/** One message, re-rendering only when that message changes. */
export function useMessage(id: string): ChatMessage | undefined {
  const store = useChatStore();
  const subscribe = useCallback(
    (listener: () => void) => store.subscribeMessage(id, listener),
    [store, id],
  );
  return useSyncExternalStore(
    subscribe,
    useCallback(() => store.getState().transcript.byId[id], [store, id]),
  );
}

/**
 * When the row BEFORE `id` was created, or `undefined` when it is the first.
 *
 * A number, not the message: a row needs its neighbour only to tell whether the
 * calendar day changed, and subscribing to the whole message would re-render it
 * on every token arriving in the row above.
 *
 * Read from the list rather than passed down, so the day heading survives the
 * memo boundary that keeps a streaming transcript cheap.
 */
export function usePreviousMessageTime(id: string): number | undefined {
  const store = useChatStore();
  return useSyncExternalStore(
    store.subscribe,
    useCallback(() => {
      const { ids, byId } = store.getState().transcript;
      const index = ids.indexOf(id);
      if (index <= 0) return undefined;
      return byId[ids[index - 1] as string]?.createdAt;
    }, [store, id]),
  );
}

/**
 * Whether the row BEFORE `id` was spoken by the same author.
 *
 * A BOOLEAN, not the message, for the reason `usePreviousMessageTime` returns a
 * number: a row needs its neighbour only to decide whether to repeat the name,
 * and subscribing to the whole message would re-render it on every token
 * arriving in the row above — the one cost the id/message split exists to avoid.
 *
 * False for the first row, and false whenever either side has no author: a
 * system-authored line and a turn of yours both BREAK a run, so the next speaker
 * is named again rather than reading as the previous one still talking.
 */
export function usePreviousAuthorMatches(id: string): boolean {
  const store = useChatStore();
  return useSyncExternalStore(
    store.subscribe,
    useCallback(() => {
      const { ids, byId } = store.getState().transcript;
      const index = ids.indexOf(id);
      if (index <= 0) return false;
      const mine = byId[id]?.authorId;
      const before = byId[ids[index - 1] as string]?.authorId;
      return mine !== undefined && mine === before;
    }, [store, id]),
  );
}

export interface TurnState {
  readonly isStreaming: boolean;
  /**
   * A turn is in flight and has produced NOTHING yet.
   *
   * Derived, never stored: a turn is in flight and the reply holds no part yet.
   * A stored flag would be a second source of truth that can disagree with the
   * transcript about whether the answer has started.
   *
   * The threshold is the first PART, not the opening of the message — see
   * `hasRenderedPart`.
   *
   * The gap it names is the common case here, not an edge one — an agent may
   * read files or start a subagent for many seconds before its first token, and
   * during that time the transcript is otherwise silent.
   */
  readonly isPending: boolean;
  readonly stop: () => void;
}

export function useTurn(): TurnState {
  const store = useChatStore();
  const inFlight = useSyncExternalStore(
    store.subscribe,
    useCallback(() => store.getState().inFlight, [store]),
  );
  const rendered = useSyncExternalStore(
    store.subscribe,
    useCallback(() => hasRenderedPart(store.getState()), [store]),
  );
  return useMemo(
    () => ({
      isStreaming: inFlight !== null,
      isPending: inFlight !== null && !rendered,
      stop: store.stop,
    }),
    [inFlight, rendered, store.stop],
  );
}
