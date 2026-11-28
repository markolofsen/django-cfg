import { describe, expect, it, vi } from "vitest";

import type { ChatAdapter, SendRequest } from "../core/conversation/adapter";
import type { StreamChunk } from "../core/conversation/chunks";
import { isTextPart, type ChatMessage } from "../core/conversation/parts";
import { selectMessages } from "../core/conversation/transcript";
import { createChatStore, type ChatStore } from "./store";

// --- harness -----------------------------------------------------------------

/** Deterministic ids: the store injects them, so nothing here reads a clock or RNG. */
function idGen(prefix: string): () => string {
  let n = 0;
  return () => `${prefix}${(n += 1)}`;
}

interface Recorded {
  readonly requests: SendRequest[];
  readonly adapter: ChatAdapter;
}

/** Adapter that replays a fixed script and closes. Records what it was asked to send. */
function scriptedAdapter(chunks: readonly StreamChunk[]): Recorded {
  const requests: SendRequest[] = [];
  return {
    requests,
    adapter: {
      sendMessage(request) {
        requests.push(request);
        return Promise.resolve(
          new ReadableStream<StreamChunk>({
            start(controller) {
              for (const chunk of chunks) controller.enqueue(chunk);
              controller.close();
            },
          }),
        );
      },
    },
  };
}

interface Controlled extends Recorded {
  /** Resolves once the store is reading, so a test can act mid-stream. */
  readonly started: Promise<void>;
  push(chunk: StreamChunk): void;
  close(): void;
  fail(error: unknown): void;
}

/**
 * Adapter driven chunk-by-chunk from the test body.
 *
 * The single-turn guard and `stop()` only exist WHILE a stream is open, so they
 * cannot be observed by a script that has already run to completion.
 */
function controlledAdapter(): Controlled {
  const requests: SendRequest[] = [];
  let controller: ReadableStreamDefaultController<StreamChunk> | null = null;
  let markStarted: () => void = () => {};
  const started = new Promise<void>((resolve) => {
    markStarted = resolve;
  });

  return {
    requests,
    started,
    push: (chunk) => controller?.enqueue(chunk),
    close: () => controller?.close(),
    fail: (error) => controller?.error(error),
    adapter: {
      sendMessage(request) {
        requests.push(request);
        return Promise.resolve(
          new ReadableStream<StreamChunk>({
            start(c) {
              controller = c;
              markStarted();
            },
          }),
        );
      },
    },
  };
}

function makeStore(adapter: ChatAdapter): ChatStore {
  return createChatStore({ adapter, makeId: idGen("u"), now: () => 1_700_000_000_000 });
}

/** Indexing is `T | undefined` under noUncheckedIndexedAccess; fail loudly instead of `!`. */
function at<T>(items: readonly T[], index: number): T {
  const item = items[index];
  if (item === undefined) throw new Error(`no item at ${index}`);
  return item;
}

function messages(store: ChatStore): readonly ChatMessage[] {
  return selectMessages(store.getState().transcript);
}

function firstRequest(recorded: Recorded): SendRequest {
  return at(recorded.requests, 0);
}

const reply: readonly StreamChunk[] = [
  { type: "message-start", messageId: "a1", createdAt: 1_700_000_000_001 },
  { type: "text-start", partId: "t1" },
  { type: "text-delta", partId: "t1", delta: "ok" },
  { type: "finish" },
];

// --- tests -------------------------------------------------------------------

describe("send", () => {
  it("shows the user message before the adapter answers", async () => {
    // Optimistic append: waiting for the backend makes the composer feel dead.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;

    expect(messages(store).map((m) => m.role)).toEqual(["user"]);

    controlled.close();
    await turn;
  });



  it("passes prior turns as history", async () => {
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);

    await store.send({ text: "first" });
    await store.send({ text: "second" });

    const history = at(recorded.requests, 1).history;
    // The first turn and its reply — but not "second", which rides as `text`.
    expect(history.map((m) => m.role)).toEqual(["user", "assistant"]);
    expect(at(history, 0).parts.filter(isTextPart).map((p) => p.text)).toEqual(["first"]);
  });

  it("excludes the turn being sent from its own history", async () => {
    // `history` means PRIOR turns. Including the message whose text rides
    // beside it makes an adapter that concatenates the two send it twice.
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);

    await store.send({ text: "only" });

    expect(firstRequest(recorded).history).toHaveLength(0);
  });

  it("refuses a blank draft", async () => {
    // Guarded in the store, not the composer, so every entry point obeys it —
    // keyboard, button, or a host calling `send` directly. Otherwise the
    // transcript grows a bubble with zero parts.
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);

    await store.send({ text: "   " });

    expect(recorded.requests).toHaveLength(0);
    expect(messages(store)).toHaveLength(0);
  });
});

describe("one turn at a time", () => {
  it("ignores a second send while streaming", async () => {
    // Two interleaved streams land in one message and no chunk carries enough
    // identity to untangle them afterwards.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "first" });
    await controlled.started;
    await store.send({ text: "second" });

    expect(controlled.requests).toHaveLength(1);
    expect(messages(store).map((m) => m.role)).toEqual(["user"]);

    controlled.close();
    await turn;
  });

  it("accepts the next send once the turn has ended", async () => {
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);

    await store.send({ text: "first" });
    await store.send({ text: "second" });

    expect(recorded.requests).toHaveLength(2);
    expect(store.getState().inFlight).toBeNull();
  });
});

/**
 * The two fields `useTurn().isPending` is derived from.
 *
 * The flag itself lives in a hook and needs a renderer; what it MEANS is a pure
 * function of the store, so the meaning is what is pinned here. Deriving rather
 * than storing is the whole decision — a stored flag could disagree with the
 * transcript about whether the answer had started.
 */
/**
 * Resolves on the store's next notification.
 *
 * The store reads the stream in an async loop, so a pushed chunk is applied
 * some indeterminate number of microtasks later. Awaiting the store's own
 * signal pins the wait to the event that matters rather than to a guessed
 * count, which would pass or fail on an unrelated change to the read loop.
 */
function nextChange(store: ChatStore): Promise<void> {
  return new Promise((resolve) => {
    const stop = store.subscribe(() => {
      stop();
      resolve();
    });
  });
}

function isPending(store: ChatStore): boolean {
  const state = store.getState();
  const id = state.transcript.streamingId;
  const parts = id === null ? [] : (state.transcript.byId[id]?.parts ?? []);
  const rendered = parts.some((part) =>
    part.type === "text" || part.type === "reasoning" ? part.text !== "" : true,
  );
  return state.inFlight !== null && !rendered;
}

describe("the pending gap", () => {
  it("is open between send and the first part", async () => {
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    // The control: before anything is sent the gap must be CLOSED, or an
    // assertion that it opens would pass on a function stuck at `true`.
    expect(isPending(store)).toBe(false);

    const turn = store.send({ text: "hi" });
    await controlled.started;

    expect(isPending(store)).toBe(true);

    controlled.close();
    await turn;
  });

  it("stays open while the reply message is open but empty", async () => {
    // `message-start` opens an EMPTY message. Measured in the browser, the gap
    // between it and the first text delta is its own silent second — an
    // indicator that ended here would leave the reader looking at nothing
    // again, which is the defect it exists to prevent.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    const opened = nextChange(store);
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    await opened;

    expect(store.getState().transcript.streamingId).toBe("a1");
    expect(isPending(store)).toBe(true);

    controlled.close();
    await turn;
  });

  it("closes on the first part, not at turn-end", async () => {
    // The distinction the whole indicator rests on: a streaming answer must not
    // render under a "waiting" label, so the gap closes on content arriving
    // while the turn is still in flight.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    const opened = nextChange(store);
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    await opened;
    const opened2 = nextChange(store);
    controlled.push({ type: "text-start", partId: "t1" });
    await opened2;

    // `text-start` appends a part whose text is `""`. Still nothing to read, so
    // the gap must not close here either — this is the second too-early
    // threshold, caught in the browser as a run of silent frames.
    expect(store.getState().transcript.byId.a1?.parts).toHaveLength(1);
    expect(isPending(store)).toBe(true);

    const filled = nextChange(store);
    controlled.push({ type: "text-delta", partId: "t1", delta: "Here" });
    await filled;

    expect(isPending(store)).toBe(false);
    expect(store.getState().inFlight).not.toBeNull();

    controlled.close();
    await turn;
  });

  it("closes on a tool call, which renders before it has any output", async () => {
    // The counterweight to the empty-text rule. A tool part draws its own header
    // the moment it exists, so requiring characters HERE would keep a waiting
    // label above a visible tool call — the mirror of the defect above.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    const opened = nextChange(store);
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    await opened;
    const tool = nextChange(store);
    controlled.push({ type: "tool-input-start", toolCallId: "c1", toolName: "read_file" });
    await tool;

    expect(isPending(store)).toBe(false);

    controlled.close();
    await turn;
  });

  it("closes when a turn fails before producing anything", async () => {
    // Otherwise the indicator spins forever on the one turn that most needs to
    // say what happened. The failure surface takes over instead.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.fail(new Error("server down"));
    await turn;

    expect(isPending(store)).toBe(false);
  });
});

describe("terminal states", () => {
  it("completes on finish", async () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    await store.send({ text: "hi" });

    expect(at(messages(store), 1).status).toEqual({ state: "complete" });
  });

  it("marks a stream that closed with no terminal chunk interrupted", async () => {
    // Leaving it `streaming` renders a spinner forever; calling it `complete`
    // claims a reply the server never finished. Interrupted is the honest state
    // and the one the host reconciles from.
    const store = makeStore(
      scriptedAdapter([
        { type: "message-start", messageId: "a1", createdAt: 1 },
        { type: "text-start", partId: "t1" },
        { type: "text-delta", partId: "t1", delta: "half" },
      ]).adapter,
    );

    await store.send({ text: "hi" });

    expect(at(messages(store), 1).status).toEqual({ state: "interrupted" });
    expect(store.getState().transcript.streamingId).toBeNull();
  });

  it("surfaces a failure that happens before the reply opens", async () => {
    // The nastiest case: `sendMessage` rejects before any `message-start`, so
    // there is no assistant message to mark. Routing it through the reducer
    // alone is a silent no-op — a refused connection or a bad token would
    // leave the transcript looking as if nothing had been sent. The user's own
    // turn carries the verdict instead.
    const store = makeStore({
      sendMessage: () => Promise.reject(new Error("connection refused")),
    });

    await store.send({ text: "hi" });

    expect(at(messages(store), 0).status).toEqual({
      state: "failed",
      message: "connection refused",
    });
    expect(store.getState().inFlight).toBeNull();
  });

  it("stops a stalled stream that never sends a chunk", async () => {
    // THE test for the read loop. This adapter parks in `read()` and ignores
    // the signal entirely — a hung server. A loop that checks the signal only
    // BETWEEN reads never gets another iteration, so the turn stays open
    // forever and Stop looks dead on exactly the turn it exists for. Only
    // racing the read against the signal ends this; if the race is removed,
    // this test hangs rather than failing.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    store.stop();
    await turn;

    expect(at(messages(store), 0).status).toEqual({ state: "interrupted" });
    expect(store.getState().inFlight).toBeNull();
  });

  it("fails the open message when the stream errors mid-turn", async () => {
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    controlled.fail(new Error("upstream 502"));
    await turn;

    expect(at(messages(store), 1).status).toEqual({ state: "failed", message: "upstream 502" });
  });

  it("treats stop() as interrupted, never failed", async () => {
    // Cancellation is a user decision, not a fault; a red error bubble for
    // pressing stop reads as the agent breaking.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);

    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    store.stop();
    controlled.fail(new Error("The operation was aborted"));
    await turn;

    expect(at(messages(store), 1).status).toEqual({ state: "interrupted" });
    expect(store.getState().inFlight).toBeNull();
  });
});

describe("subscriptions", () => {
  it("wakes the row whose message changed", async () => {
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);
    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });

    const listener = vi.fn();
    store.subscribeMessage("a1", listener);
    controlled.push({ type: "text-start", partId: "t1" });
    controlled.push({ type: "text-delta", partId: "t1", delta: "ok" });

    // The read loop is async, so a synchronous assertion right after `push`
    // races it. Settle the turn first and assert on the total.
    controlled.close();
    await turn;

    expect(listener.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it("leaves other rows alone while a neighbour streams", async () => {
    // If this fails, every row re-renders per token and the whole per-message
    // subscription — the reason this store is hand-rolled — buys nothing.
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);
    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });

    const neighbour = vi.fn();
    store.subscribeMessage(at(messages(store), 0).id, neighbour);
    controlled.push({ type: "text-start", partId: "t1" });
    controlled.push({ type: "text-delta", partId: "t1", delta: "ok" });
    controlled.push({ type: "text-delta", partId: "t1", delta: "!" });

    expect(neighbour).not.toHaveBeenCalled();

    controlled.close();
    await turn;
  });

  it("stops notifying after unsubscribe", async () => {
    const controlled = controlledAdapter();
    const store = makeStore(controlled.adapter);
    const turn = store.send({ text: "hi" });
    await controlled.started;
    controlled.push({ type: "message-start", messageId: "a1", createdAt: 1 });

    const listener = vi.fn();
    const unsubscribe = store.subscribeMessage("a1", listener);
    unsubscribe();
    controlled.push({ type: "text-start", partId: "t1" });

    expect(listener).not.toHaveBeenCalled();

    controlled.close();
    await turn;
  });

  it("notifies the global listener on any change", async () => {
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);
    const listener = vi.fn();
    store.subscribe(listener);

    await store.send({ text: "hi" });

    expect(listener.mock.calls.length).toBeGreaterThan(1);
  });

  it("stops notifying the global listener after unsubscribe", async () => {
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);
    const listener = vi.fn();
    store.subscribe(listener)();

    await store.send({ text: "hi" });

    expect(listener).not.toHaveBeenCalled();
  });
});

describe("load", () => {
  const seeded: readonly ChatMessage[] = [
    {
      id: "h1",
      role: "user",
      parts: [{ type: "text", id: "h1:text", text: "earlier" }],
      status: { state: "complete" },
      createdAt: 1,
    },
    {
      id: "h2",
      role: "assistant",
      parts: [{ type: "text", id: "h2:text", text: "reply" }],
      status: { state: "complete" },
      createdAt: 2,
    },
  ];

  it("replaces the transcript wholesale", async () => {
    const recorded = scriptedAdapter(reply);
    const store = makeStore(recorded.adapter);
    await store.send({ text: "stale" });

    store.load(seeded);

    expect(messages(store).map((m) => m.id)).toEqual(["h1", "h2"]);
  });

  it("wakes the rows it seeded", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    const row = vi.fn();
    const global = vi.fn();
    store.subscribeMessage("h2", row);
    store.subscribe(global);

    store.load(seeded);

    expect(row).toHaveBeenCalledTimes(1);
    expect(global).toHaveBeenCalledTimes(1);
  });
});

/**
 * The prompt queue.
 *
 * What it replaces was one line — `if (state.inFlight !== null) return;` — which
 * DISCARDED a second turn in silence. Our agents run for minutes, so that was
 * the moment a user was most likely to have something to add, and the text
 * simply vanished: no error, no toast, nothing to notice it by.
 */
describe("prompts written while a turn is in flight", () => {
  it("queues instead of discarding", async () => {
    // MUTANT: restore the bare `return` → this dies.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    void store.send({ text: "second" });

    expect(live.requests, "the second turn was sent concurrently").toHaveLength(1);
    expect(store.getState().queue.items.map((i) => i.draft.text)).toEqual(["second"]);
  });

  it("drains itself when the turn ends — no button to press", async () => {
    // A queue that needed a "go" is a to-do list, not a queue.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    void store.send({ text: "second" });
    live.close();
    await vi.waitFor(() => {
      expect(live.requests).toHaveLength(2);
    });

    expect(at(live.requests, 1).text).toBe("second");
    expect(store.getState().queue.items).toHaveLength(0);
  });

  it("drains in ORDER, one at a time", async () => {
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    void store.send({ text: "second" });
    void store.send({ text: "third" });
    expect(store.getState().queue.items).toHaveLength(2);

    live.close();
    await vi.waitFor(() => {
      expect(live.requests.length).toBeGreaterThanOrEqual(2);
    });
    expect(at(live.requests, 1).text).toBe("second");
  });

  it("does NOT drain after a stop", async () => {
    // MUTANT: drain regardless of `aborted` → this dies. The user pressed Stop;
    // starting the next prompt would make Stop start something, which is the
    // opposite of what the control says. Their queue survives for later.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    void store.send({ text: "second" });
    store.stop();

    await vi.waitFor(() => {
      expect(store.getState().inFlight).toBeNull();
    });
    expect(live.requests, "Stop started the queued turn").toHaveLength(1);
    expect(store.getState().queue.items.map((i) => i.draft.text)).toEqual(["second"]);
  });


  it("keeps the queue across a send, rather than clearing it", async () => {
    // MUTANT: drop the `...state` spread from the send's apply() → this dies.
    // That apply rebuilds the state from two fields, so it silently resets the
    // queue at the START of every turn.
    //
    // The order below is what makes the mutant visible, and the first version of
    // this test had it wrong: it queued AFTER the turn had started, so the
    // clearing apply() had already run and there was nothing to lose. The queue
    // must be non-empty BEFORE a send begins — which is the real scenario too,
    // since a drained prompt starts its own turn while later prompts still wait.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "second" });
    store.enqueue({ text: "third" });
    expect(store.getState().queue.items).toHaveLength(2);

    // "second" drains and starts a turn; "third" must survive that turn's start.
    live.close();
    await vi.waitFor(() => {
      expect(live.requests).toHaveLength(2);
    });
    expect(
      store.getState().queue.items.map((i) => i.draft.text),
      "the queue was cleared when the drained turn began",
    ).toEqual(["third"]);
  });

  it("edits and removes a queued prompt", async () => {
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "typo" });
    const id = at(store.getState().queue.items, 0).id;

    store.editQueued(id, { text: "fixed" });
    expect(at(store.getState().queue.items, 0).draft.text).toBe("fixed");

    store.removeQueued(id);
    expect(store.getState().queue.items).toHaveLength(0);
  });

  it("TAKES a queued prompt for editing, rather than copying it", async () => {
    // MUTANT: return the draft without removing the entry → this dies. A queued
    // prompt has not been seen by anyone, so leaving a copy behind sends it
    // twice: once from the queue and once as the edit the user is about to make.
    // A SENT prompt is the opposite case and is deliberately copied.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "draft to edit" });
    const id = at(store.getState().queue.items, 0).id;

    expect(store.takeQueued(id)?.text).toBe("draft to edit");
    expect(store.getState().queue.items, "the taken prompt is still queued").toHaveLength(0);
  });

  it("returns undefined for an id the queue no longer holds", async () => {
    // A row can be removed by another click between render and dispatch, and
    // recall must not throw for a race the user cannot see.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);
    void store.send({ text: "first" });
    await live.started;
    expect(store.takeQueued("gone")).toBeUndefined();
  });

  it("releases the CHOSEN row, not the head, when told to send now", async () => {
    // The control sits on every row, so it must name the row it is beside.
    // MUTANT: drop the `promoteQueued` call → "second" is released instead.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "second" });
    store.enqueue({ text: "third" });
    const third = at(store.getState().queue.items, 1).id;

    store.sendQueuedNow(third);

    await vi.waitFor(() => {
      expect(live.requests).toHaveLength(2);
    });
    expect(at(live.requests, 1).text).toBe("third");
    // The one it jumped stays queued, in its own order.
    expect(store.getState().queue.items.map((i) => i.draft.text)).toEqual(["second"]);
  });

  it("interrupts the running turn rather than waiting for it", async () => {
    // The whole point of the control: anything softer is just the queue, which
    // already works. The cut turn ends `interrupted`, never `failed` — it was
    // stopped on purpose.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    live.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    store.enqueue({ text: "urgent" });
    const id = at(store.getState().queue.items, 0).id;

    store.sendQueuedNow(id);

    await vi.waitFor(() => {
      expect(live.requests).toHaveLength(2);
    });
    expect(at(live.requests, 1).text).toBe("urgent");
  });

  it("spends the forced release on ONE abort, so a later Stop still refuses", async () => {
    // MUTANT: set `releaseAfterAbort` without clearing it where it is read →
    // this dies. The flag is one-shot: an ordinary Stop that follows must not
    // inherit a release the user never asked for, which is the invariant the
    // "does NOT drain after a stop" test above protects.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "urgent" });
    store.sendQueuedNow(at(store.getState().queue.items, 0).id);

    await vi.waitFor(() => {
      expect(live.requests).toHaveLength(2);
    });

    // A second turn is now live. Queue behind it and press Stop the ordinary way.
    store.enqueue({ text: "later" });
    store.stop();

    await vi.waitFor(() => {
      expect(store.getState().inFlight).toBeNull();
    });
    expect(live.requests, "a plain Stop inherited the forced release").toHaveLength(2);
    expect(store.getState().queue.items.map((i) => i.draft.text)).toEqual(["later"]);
  });

  it("sends now with nothing in flight, instead of leaving the button dead", async () => {
    // No turn to cut short means the abort path would do nothing at all.
    const scripted = scriptedAdapter([{ type: "finish" }]);
    const store = makeStore(scripted.adapter);

    store.enqueue({ text: "queued with no turn" });
    store.sendQueuedNow(at(store.getState().queue.items, 0).id);

    await vi.waitFor(() => {
      expect(scripted.requests).toHaveLength(1);
    });
    expect(firstRequest(scripted).text).toBe("queued with no turn");
    expect(store.getState().queue.items).toHaveLength(0);
  });

  it("sends immediately when nothing is in flight", async () => {
    // The queue must not become the only path: with no turn open, a send sends.
    const scripted = scriptedAdapter([{ type: "finish" }]);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "alone" });
    expect(scripted.requests).toHaveLength(1);
    expect(store.getState().queue.items).toHaveLength(0);
  });
});

describe("leaving a room", () => {
  it("aborts the turn that was in flight", async () => {
    // The turn belongs to the room it was sent to. Carried across a switch it
    // streams a reply into a conversation that never asked for it, under a
    // "thinking" indicator the new room cannot stop.
    //
    // MUTANT: drop the `abort()` → this dies.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    expect(store.getState().inFlight).not.toBeNull();

    store.leaveRoom();

    await vi.waitFor(() => {
      expect(store.getState().inFlight).toBeNull();
    });
  });

  it("drops queued prompts, which were written for the room being left", async () => {
    // MUTANT: remove the queue reset → this dies, and the previous room's
    // unsent text shows up in the next conversation.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "written for the old room" });
    expect(store.getState().queue.items).toHaveLength(1);

    store.leaveRoom();

    expect(store.getState().queue.items).toHaveLength(0);
  });

  it("never SENDS a queued prompt on the way out", async () => {
    // The worst version of this bug, because it reaches the server rather than
    // just the screen. TWO independent things prevent it — the queue is emptied
    // before the `finally` looks at it, and the drain is refused after an abort
    // regardless — so this test survives either one being removed alone. That
    // redundancy is deliberate and is why the mutant note names both.
    //
    // MUTANT: drop the queue reset AND set `releaseAfterAbort = true` → this
    // dies. Either alone leaves the other guard holding.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);

    void store.send({ text: "first" });
    await live.started;
    store.enqueue({ text: "must not be sent" });

    store.leaveRoom();

    // Give the abort's `finally` a chance to run before asserting the absence.
    await vi.waitFor(() => {
      expect(store.getState().inFlight).toBeNull();
    });
    expect(live.requests, "a queued prompt was sent while leaving").toHaveLength(1);
  });

  it("leaves the transcript alone — the caller reseeds it", async () => {
    // Clearing here too blanks the surface for a frame between the leave and
    // the seed. `load` is what replaces the transcript, and it runs next.
    //
    // MUTANT: clear the transcript in `leaveRoom` → this dies.
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "hi" });
    expect(messages(store).length).toBeGreaterThan(0);

    const before = messages(store).length;
    store.leaveRoom();

    expect(messages(store)).toHaveLength(before);
  });

  it("is safe with nothing in flight and nothing queued", () => {
    // The ordinary case: most room switches happen on an idle room, and this
    // must not throw or wake subscribers for a change that did not happen.
    const store = makeStore(scriptedAdapter(reply).adapter);
    const before = store.getState();

    store.leaveRoom();

    expect(store.getState()).toBe(before);
  });
});

// --- room: receive() and the recipient -----------------------------------------

function remote(id: string, text: string, extra: Partial<ChatMessage> = {}): ChatMessage {
  return {
    id,
    role: "user",
    parts: [{ type: "text", id: `${id}:text`, text }],
    status: { state: "complete" },
    createdAt: 1_700_000_000_500,
    authorId: "seat-2",
    from: "other",
    ...extra,
  };
}

describe("receive()", () => {
  it("appends a remote message without calling the adapter", () => {
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);

    store.receive(remote("r1", "hello"));

    expect(messages(store).map((m) => m.id)).toEqual(["r1"]);
    expect(at(messages(store), 0).from).toBe("other");
    expect(scripted.requests, "receive must never reach the model").toHaveLength(0);
    expect(store.getState().inFlight).toBeNull();
  });

  it("keeps the order messages arrived in", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    store.receive(remote("r1", "one"));
    store.receive(remote("r2", "two"));
    expect(messages(store).map((m) => m.id)).toEqual(["r1", "r2"]);
  });

  it("replaces a known id in place, so a re-delivered message does not move or double", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    store.receive(remote("r1", "draft"));
    store.receive(remote("r2", "next"));

    store.receive(remote("r1", "confirmed"));

    expect(messages(store).map((m) => m.id)).toEqual(["r1", "r2"]);
    const first = at(messages(store), 0);
    expect(first.parts.filter(isTextPart).map((p) => p.text)).toEqual(["confirmed"]);
  });

  it("wakes the whole-store listeners and only the touched row", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    store.receive(remote("r1", "one"));
    const whole = vi.fn();
    const row1 = vi.fn();
    const row2 = vi.fn();
    store.subscribe(whole);
    store.subscribeMessage("r1", row1);
    store.subscribeMessage("r2", row2);

    store.receive(remote("r2", "two"));

    expect(whole).toHaveBeenCalledTimes(1);
    expect(row2).toHaveBeenCalledTimes(1);
    expect(row1).not.toHaveBeenCalled();
  });

  it("does nothing when handed the very message it already holds", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    const message = remote("r1", "one");
    store.receive(message);
    const before = store.getState();

    store.receive(message);

    expect(store.getState()).toBe(before);
  });

  it("does not drop the message that is streaming", async () => {
    // MUTANT: make receive() go through `load` or clear `streamingId` → this
    // dies. A remote message landing mid-answer must not cut the answer short.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);
    void store.send({ text: "ask" });
    await live.started;
    live.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    live.push({ type: "text-start", partId: "t1" });
    live.push({ type: "text-delta", partId: "t1", delta: "par" });
    await vi.waitFor(() => expect(store.getState().transcript.streamingId).toBe("a1"));

    store.receive(remote("r1", "meanwhile"));
    live.push({ type: "text-delta", partId: "t1", delta: "tial" });
    live.push({ type: "finish" });
    live.close();

    await vi.waitFor(() => expect(store.getState().inFlight).toBeNull());
    const answer = messages(store).find((m) => m.id === "a1");
    expect(answer?.parts.filter(isTextPart).map((p) => p.text)).toEqual(["partial"]);
    expect(answer?.status).toEqual({ state: "complete" });
    expect(messages(store).map((m) => m.id)).toContain("r1");
  });

  it("ignores a polled copy of the message still streaming", async () => {
    // The stream owns its id until it finishes; a snapshot of the half-written
    // reply would overwrite parts the reducer is still extending.
    const live = controlledAdapter();
    const store = makeStore(live.adapter);
    void store.send({ text: "ask" });
    await live.started;
    live.push({ type: "message-start", messageId: "a1", createdAt: 1 });
    live.push({ type: "text-start", partId: "t1" });
    live.push({ type: "text-delta", partId: "t1", delta: "live" });
    await vi.waitFor(() => expect(store.getState().transcript.streamingId).toBe("a1"));

    store.receive({
      id: "a1",
      role: "assistant",
      parts: [{ type: "text", id: "t1", text: "stale" }],
      status: { state: "complete" },
      createdAt: 1,
    });

    expect(store.getState().transcript.streamingId).toBe("a1");
    const answer = messages(store).find((m) => m.id === "a1");
    expect(answer?.parts.filter(isTextPart).map((p) => p.text)).toEqual(["live"]);
    live.push({ type: "finish" });
    live.close();
    await vi.waitFor(() => expect(store.getState().inFlight).toBeNull());
  });

  it("appends after a load, which it does not replace", () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    store.load([remote("h1", "history")]);
    store.receive(remote("r1", "new"));
    expect(messages(store).map((m) => m.id)).toEqual(["h1", "r1"]);
  });
});

describe("the recipient of a send", () => {
  it("reaches the adapter, and is `all` with no mentions for a draft that chose no one", async () => {
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "hello" });
    expect(firstRequest(scripted).recipient).toBe("all");
    expect(firstRequest(scripted).mentions).toEqual([]);
  });

  it("carries Draft.to to the adapter and marks the sender's own message private", async () => {
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "hello", to: { id: "g3", label: "Anna" } });
    expect(firstRequest(scripted).recipient).toEqual({ id: "g3", label: "Anna" });
    expect(at(messages(store), 0).private).toEqual({ with: "Anna" });
    expect(at(messages(store), 0).highlight).toBe("private");
  });

  it("carries the mentioned seats to the adapter", async () => {
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "@Anna hello", mentions: ["g3"] });
    expect(firstRequest(scripted).mentions).toEqual(["g3"]);
  });

  it("names the optimistic message to the adapter, so a host can reuse its id as a client id", async () => {
    const scripted = scriptedAdapter(reply);
    const store = makeStore(scripted.adapter);
    await store.send({ text: "hello" });
    expect(firstRequest(scripted).messageId).toBe(at(messages(store), 0).id);
  });

  it("leaves the private mark off a line for the room", async () => {
    const store = makeStore(scriptedAdapter(reply).adapter);
    await store.send({ text: "hello" });
    expect(at(messages(store), 0)).not.toHaveProperty("private");
  });
});
