import { describe, expect, it } from "vitest";

import type { Draft } from "./outbound";
import {
  dequeue,
  editQueued,
  emptyQueue,
  enqueue,
  promoteQueued,
  removeQueued,
} from "./queue";

/**
 * The queue, as pure state.
 *
 * The behaviour it replaces was one line — `if (state.inFlight !== null) return;`
 * — which discarded a second turn in silence. These tests are cheap because the
 * queue holds no React and no clock; the ordering and the empty rules are all
 * there is to get wrong, and both are invisible once wrapped in a hook.
 */

const draft = (text: string): Draft => ({ text });
const withTool = (): Draft => ({
  text: "",
  pickedTools: [{ id: "read_file", label: "Read a file" }],
});

describe("enqueue", () => {
  it("appends in order", () => {
    const q = enqueue(enqueue(emptyQueue, draft("one"), "a"), draft("two"), "b");
    expect(q.items.map((i) => i.draft.text)).toEqual(["one", "two"]);
  });

  it("refuses an empty draft", () => {
    // MUTANT: drop the isEmpty guard → this dies. A queued nothing puts a row in
    // the strip that sends nothing when it drains.
    expect(enqueue(emptyQueue, draft("   "), "a").items).toHaveLength(0);
    expect(enqueue(emptyQueue, draft(""), "a").items).toHaveLength(0);
  });

  it("accepts a draft that is ONLY a picked tool", () => {
    // Choosing a tool from the menu is a request in itself. `isEmpty` already
    // knows this; the queue must not re-decide it.
    expect(enqueue(emptyQueue, withTool(), "a").items).toHaveLength(1);
  });

  it("never mutates the state it was given", () => {
    const before = enqueue(emptyQueue, draft("one"), "a");
    enqueue(before, draft("two"), "b");
    expect(before.items).toHaveLength(1);
  });
});

describe("dequeue", () => {
  it("takes the OLDEST first", () => {
    // MUTANT: pop from the end → this dies. A queue that drains newest-first
    // answers the user's afterthought before the thing they actually asked.
    const q = enqueue(enqueue(emptyQueue, draft("one"), "a"), draft("two"), "b");
    const { next, rest } = dequeue(q);
    expect(next?.draft.text).toBe("one");
    expect(rest.items.map((i) => i.draft.text)).toEqual(["two"]);
  });

  it("answers null on an empty queue without throwing", () => {
    const { next, rest } = dequeue(emptyQueue);
    expect(next).toBeNull();
    expect(rest.items).toHaveLength(0);
  });

  it("returns the remainder instead of mutating", () => {
    // The caller sends, THEN stores the rest. A mutating dequeue would leave a
    // prompt both gone and unsent if the send threw.
    const q = enqueue(emptyQueue, draft("one"), "a");
    dequeue(q);
    expect(q.items).toHaveLength(1);
  });
});

describe("edit and remove", () => {
  it("replaces one draft, leaving the others and the ORDER alone", () => {
    const q = enqueue(enqueue(emptyQueue, draft("one"), "a"), draft("two"), "b");
    const edited = editQueued(q, "a", draft("ONE"));
    expect(edited.items.map((i) => i.draft.text)).toEqual(["ONE", "two"]);
  });

  it("removes an entry edited to empty", () => {
    // MUTANT: keep the entry → this dies. A row the user emptied on purpose
    // would sit in the strip and send nothing.
    const q = enqueue(emptyQueue, draft("one"), "a");
    expect(editQueued(q, "a", draft("")).items).toHaveLength(0);
  });

  it("ignores an unknown id rather than throwing", () => {
    const q = enqueue(emptyQueue, draft("one"), "a");
    expect(editQueued(q, "nope", draft("x")).items).toHaveLength(1);
    expect(removeQueued(q, "nope").items).toHaveLength(1);
  });

  it("removes by id", () => {
    const q = enqueue(enqueue(emptyQueue, draft("one"), "a"), draft("two"), "b");
    expect(removeQueued(q, "a").items.map((i) => i.draft.text)).toEqual(["two"]);
  });
});

describe("promoteQueued", () => {
  const three = () =>
    enqueue(
      enqueue(enqueue(emptyQueue, draft("one"), "a"), draft("two"), "b"),
      draft("three"),
      "c",
    );

  it("moves the chosen prompt to the head", () => {
    // The drain always takes the head, so "send now" on the third row can only
    // mean anything if the row moves there first. MUTANT: return `state`
    // unchanged → the button beside "three" releases "one".
    expect(promoteQueued(three(), "c").items.map((i) => i.draft.text)).toEqual([
      "three",
      "one",
      "two",
    ]);
  });

  it("keeps the others in their original order", () => {
    // Promotion is not a reshuffle: the user chose ONE prompt to jump, and the
    // rest keep the order they were written in.
    expect(promoteQueued(three(), "b").items.map((i) => i.draft.text)).toEqual([
      "two",
      "one",
      "three",
    ]);
  });

  it("returns the SAME state for an unknown id", () => {
    // Identity, not just equality: `sendQueuedNow` reads `promoted === state`
    // to decide there is nothing to release, so a fresh-but-equal object would
    // abort a running turn for a row that no longer exists.
    const q = three();
    expect(promoteQueued(q, "gone")).toBe(q);
  });

  it("leaves a head prompt where it is", () => {
    const q = three();
    expect(promoteQueued(q, "a").items.map((i) => i.draft.text)).toEqual([
      "one",
      "two",
      "three",
    ]);
  });
});
