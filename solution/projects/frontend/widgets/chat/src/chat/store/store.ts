/**
 * The store: transcript state plus the turn lifecycle.
 *
 * Hand-rolled on `useSyncExternalStore` rather than pulled from zustand — the
 * whole surface is five methods and a subscription, and the package's point is
 * to be dependency-light enough that a consumer can read it end to end. The
 * core reducer already owns every state transition; this only owns WHEN they
 * run and WHO is told.
 *
 * Per-message subscription is the load-bearing part. A transcript that
 * re-renders every row on every token is the difference between a chat that
 * feels instant and one that stutters at fifty messages, and it cannot be
 * retrofitted — it decides the shape of the selectors.
 */

import type { ChatAdapter } from "../core/conversation/adapter";
import type { StreamChunk } from "../core/conversation/chunks";
import type { ChatMessage, MessageStatus } from "../core/conversation/parts";
import { buildOutbound, isEmpty, type Draft } from "../core/compose/outbound";
import {
  dequeue,
  editQueued,
  emptyQueue,
  enqueue,
  promoteQueued,
  removeQueued,
  type QueueState,
} from "../core/compose/queue";
import {
  appendUserMessage,
  emptyTranscript,
  receiveMessage,
  reduce,
  selectMessages,
  type TranscriptState,
} from "../core/conversation/transcript";
import { messageOf } from "../utils";
import { ABORTED, aborted, sendRequest } from "./send-request";
import { createSubscribers, type Listener } from "./subscribers";

export interface ChatState {
  readonly transcript: TranscriptState;
  /** Prompts written while a turn was in flight, oldest first. */
  readonly queue: QueueState;
  /** Non-null while a turn is in flight; aborting it is the only way to stop. */
  readonly inFlight: AbortController | null;
  /**
   * Whether the host's history fetch has answered.
   *
   * Starts `false`: a store with no messages and no answer yet is LOADING, and
   * defaulting the other way is what let the empty state paint during a fetch.
   * A host that never seeds history calls `setHistoryLoaded(true)` once.
   */
  readonly historyLoaded: boolean;
}


export interface ChatStore {
  getState(): ChatState;
  subscribe(listener: Listener): () => void;
  /** Notified only when THIS message changes — the reason rows do not re-render. */
  subscribeMessage(id: string, listener: Listener): () => void;
  send(draft: Draft): Promise<void>;
  /** Queue explicitly. `send` already queues when a turn is in flight. */
  enqueue(draft: Draft): void;
  removeQueued(id: string): void;
  /** Replace a queued draft; editing it to empty removes the entry. */
  editQueued(id: string, draft: Draft): void;
  /**
   * Take a queued prompt back out for editing — the ArrowUp affordance.
   *
   * REMOVES it, unlike recalling a sent prompt, which copies. A sent turn
   * already happened and rewriting it is a different, explicit operation; a
   * queued prompt has not been seen by anyone, so leaving a copy behind would
   * send it twice — once as the entry still in the queue and once as the edit.
   *
   * Returns the draft so the caller can put it in the buffer, or `undefined` for
   * an unknown id.
   */
  takeQueued(id: string): Draft | undefined;
  /**
   * Cut the current turn short and release ONE queued prompt immediately.
   *
   * Named by row, because the button sits beside a row and the drain always
   * takes the head — so this promotes first. See `promoteQueued`.
   *
   * The prompt is not sent here. `stop()` aborts, and the turn's own `finally`
   * releases the head; one owner for "what goes next" is what stops a forced
   * release and a natural one from drifting. That block normally refuses to
   * drain after an abort — deliberately, so Stop cannot start something — and
   * this is the one intent that overrides it.
   */
  sendQueuedNow(id: string): void;
  stop(): void;
  /**
   * Abandon what belongs to the room being left: aborts the in-flight turn and
   * drops the queue. A turn and a queued prompt belong to the room they were
   * written in, so carrying either across a switch streams a reply into a
   * conversation that never asked for it. NOT the transcript — the caller
   * reseeds immediately. `stop()` is not a substitute: it leaves the queue,
   * which then drains into the wrong room.
   */
  leaveRoom(): void;
  /** Seed from history. Replaces the transcript wholesale; not a merge. */
  load(messages: readonly ChatMessage[]): void;
  /**
   * Add a message that arrived from elsewhere (another participant, the
   * assistant's answer fetched by the host). Never calls the adapter.
   *
   * Unlike `load` it merges: a known id is replaced in place, a new one is
   * appended, and a turn streaming right now is left alone, copy of it
   * included. See `receiveMessage`.
   */
  receive(message: ChatMessage): void;
  /**
   * Whether the host's history fetch has answered.
   *
   * An empty transcript means two different things — a room with no messages,
   * and a room whose messages are still in flight — and only the host knows
   * which. Without this the empty state showed for the duration of every cold
   * fetch: measured ~100ms on a room that then rendered 90 replies.
   */
  setHistoryLoaded(loaded: boolean): void;
}

export interface StoreOptions {
  readonly adapter: ChatAdapter;
  /** Injected so tests stay deterministic and history replay keeps real stamps. */
  readonly makeId: () => string;
  readonly now: () => number;
}

export function createChatStore(options: StoreOptions): ChatStore {
  let state: ChatState = {
    transcript: emptyTranscript,
    queue: emptyQueue,
    inFlight: null,
    historyLoaded: false,
  };
  /**
   * Set by `sendQueuedNow` so the abort it triggers still drains.
   *
   * NOT part of `ChatState`: it lives only between an abort and the `finally`
   * that reads it, nothing renders from it, and putting it in the state would
   * wake every subscriber for a flag none of them can see.
   *
   * Cleared where it is read, so an ordinary Stop that follows can never inherit
   * a release the user did not ask for.
   */
  let releaseAfterAbort = false;
  const { notify, subscribe, subscribeMessage } = createSubscribers();

  function apply(next: ChatState, changed: Iterable<string>): void {
    state = next;
    notify(changed);
  }

  function applyChunk(chunk: StreamChunk): void {
    const before = state.transcript;
    const transcript = reduce(before, chunk);
    if (transcript === before) return;

    // Only the streaming message can change, so that is the only row to wake.
    // Waking all of them here is precisely the stutter this store exists to
    // avoid, and it would go unnoticed until the transcript got long.
    const touched = transcript.streamingId ?? before.streamingId;
    apply({ ...state, transcript }, touched === null ? [] : [touched]);
  }

  /**
   * End a turn that failed, whether or not the assistant ever opened a message.
   *
   * The subtle case this exists for: `sendMessage()` rejecting BEFORE any
   * `message-start`. Routing that through the reducer would be a no-op — there
   * is no message to mark — so a connection refused, a 500, or a bad auth token
   * left the transcript looking as if nothing had been sent. Silent failure is
   * the worst outcome of the three; a visible failed turn is the point.
   */
  function fail(status: MessageStatus, userMessageId: string): void {
    const streaming = state.transcript.streamingId;
    if (streaming !== null) {
      const message = state.transcript.byId[streaming];
      if (message !== undefined) {
        apply(
          {
            ...state,
            transcript: {
              ...state.transcript,
              byId: { ...state.transcript.byId, [streaming]: { ...message, status } },
              streamingId: null,
            },
          },
          [streaming],
        );
        return;
      }
    }

    // No assistant message exists, so the user's own turn carries the verdict.
    const user = state.transcript.byId[userMessageId];
    if (user === undefined) return;
    apply(
      {
        ...state,
        transcript: {
          ...state.transcript,
          byId: { ...state.transcript.byId, [userMessageId]: { ...user, status } },
        },
      },
      [userMessageId],
    );
  }

  const store: ChatStore = {
    getState: () => state,

    subscribe,
    subscribeMessage,

    setHistoryLoaded(loaded) {
      if (state.historyLoaded === loaded) return;
      apply({ ...state, historyLoaded: loaded }, []);
    },

    load(messages) {
      const byId: Record<string, ChatMessage> = {};
      for (const message of messages) byId[message.id] = message;
      apply(
        {
          ...state,
          transcript: { ids: messages.map((m) => m.id), byId, streamingId: null },
        },
        messages.map((m) => m.id),
      );
    },

    receive(message) {
      const transcript = receiveMessage(state.transcript, message);
      if (transcript === state.transcript) return;
      apply({ ...state, transcript }, [message.id]);
    },

    stop() {
      state.inFlight?.abort();
    },

    leaveRoom() {
      // Both effects are synchronous and independent: `abort()` only signals,
      // and the turn's `finally` runs a microtask later, by which time the queue
      // is already empty. The drain is refused there anyway — `releaseAfterAbort`
      // stays false, so leaving a room can never SEND one of its queued prompts.
      if (state.queue !== emptyQueue) apply({ ...state, queue: emptyQueue }, []);
      state.inFlight?.abort();
    },

    async send(draft) {
      // Guarded here rather than in the composer so that every entry point —
      // keyboard, button, a host calling `send` directly — obeys it.
      if (isEmpty(draft)) return;

      // One turn at a time: two streams into one message cannot be untangled,
      // because no chunk carries enough identity to say which it belongs to.
      //
      // But a turn already in flight now QUEUES rather than returning. The bare
      // `return` here discarded the prompt in silence — no error, no toast, the
      // text simply gone — at exactly the moment our minutes-long agents make a
      // user most likely to add something. The queue drains itself in `finally`.
      if (state.inFlight !== null) {
        apply({ ...state, queue: enqueue(state.queue, draft, options.makeId()) }, []);
        return;
      }

      const outbound = buildOutbound(draft, options.makeId(), options.now());
      const controller = new AbortController();

      // Captured BEFORE the user's message is appended. `history` means prior
      // turns; including the turn whose text rides beside it makes an adapter
      // that concatenates the two send the message twice.
      const history = selectMessages(state.transcript);

      // The user's turn is authored, not streamed — it goes in whole. The
      // assistant's message is opened later by the adapter's `message-start`,
      // because only the adapter knows its id.
      apply(
        {
          ...state,
          transcript: appendUserMessage(state.transcript, outbound.message),
          inFlight: controller,
        },
        [outbound.message.id],
      );

      try {
        const stream = await options.adapter.sendMessage(sendRequest(draft, outbound.message.id, outbound.text, history, controller.signal));
        const reader = stream.getReader();
        // The loop races each read against the abort signal rather than
        // checking it between reads. A transport that ignores the signal parks
        // in `read()` forever, and a between-reads check never runs again — so
        // Stop would look dead precisely on the stalled turn it exists for.
        for (;;) {
          const next = await Promise.race([reader.read(), aborted(controller.signal)]);
          if (next === ABORTED) {
            void reader.cancel().catch(() => undefined);
            break;
          }
          if (next.done) break;
          applyChunk(next.value);
        }
        // A stream that ends without a terminal frame is an interruption, not a
        // completion: the reply may still have been persisted server-side, so
        // the host reconciles rather than showing a permanent error. Routed
        // through `fail` so a stream that closed before `message-start` is
        // still visible rather than silently doing nothing.
        if (state.transcript.streamingId !== null || controller.signal.aborted) {
          fail({ state: "interrupted" }, outbound.message.id);
        }
      } catch (error) {
        fail(
          controller.signal.aborted
            ? { state: "interrupted" }
            : { state: "failed", message: messageOf(error) },
          outbound.message.id,
        );
      } finally {
        apply({ ...state, inFlight: null }, []);

        // Drain the next queued prompt — unattended, because a queue that
        // needed a "go" button would be a to-do list, not a queue.
        //
        // NOT after an abort. The user pressed Stop; sending the next prompt
        // would make Stop start something, which is the opposite of what the
        // control says. Their queue survives for when they choose to continue.
        // Read and cleared together: a forced release is spent by the abort it
        // was set for, so a later plain Stop cannot inherit it.
        const forced = releaseAfterAbort;
        releaseAfterAbort = false;

        if (!controller.signal.aborted || forced) {
          const { next, rest } = dequeue(state.queue);
          if (next !== null) {
            apply({ ...state, queue: rest }, []);
            // `store.send`, never `this.send`: every consumer destructures
            // (`const { send } = useChatStore()`), and a `this` that arrives
            // undefined would throw here — inside a `finally`, where it would
            // mask whatever the turn was actually doing.
            //
            // `void`: this send owns its own errors, and awaiting it would chain
            // every queued turn onto the first one's promise, so an abort deep in
            // the chain would settle a caller that is long gone.
            void store.send(next.draft);
          }
        }
      }
    },

    enqueue(draft) {
      if (isEmpty(draft)) return;
      apply({ ...state, queue: enqueue(state.queue, draft, options.makeId()) }, []);
    },

    removeQueued(id) {
      apply({ ...state, queue: removeQueued(state.queue, id) }, []);
    },

    editQueued(id, draft) {
      apply({ ...state, queue: editQueued(state.queue, id, draft) }, []);
    },

    takeQueued(id) {
      const chosen = state.queue.items.find((item) => item.id === id);
      if (chosen === undefined) return undefined;
      apply({ ...state, queue: removeQueued(state.queue, id) }, []);
      return chosen.draft;
    },

    sendQueuedNow(id) {
      // Nothing in flight: the queue is not waiting on anything, so there is no
      // turn to cut short and the abort path would do nothing at all. Release it
      // directly instead of leaving the button dead.
      if (state.inFlight === null) {
        const taken = store.takeQueued(id);
        if (taken !== undefined) void store.send(taken);
        return;
      }
      // Promote BEFORE aborting: the drain takes the head, and the abort's
      // `finally` can run as soon as the signal fires.
      const promoted = promoteQueued(state.queue, id);
      if (promoted === state.queue) return;
      apply({ ...state, queue: promoted }, []);
      releaseAfterAbort = true;
      state.inFlight.abort();
    },
  };

  return store;
}
