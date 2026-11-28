import { describe, expect, it, vi } from "vitest";

import { createChatEvents } from "./events";
import { emptyDraft } from "../compose/outbound";

const draft = { ...emptyDraft, text: "restart the agent" };

describe("delivery", () => {
  it("calls a handler with the payload", () => {
    const events = createChatEvents();
    const seen = vi.fn();
    events.on("queue:taken", seen);
    events.emit("queue:taken", { id: "q1", draft });
    expect(seen).toHaveBeenCalledWith({ id: "q1", draft });
  });

  it("calls every handler for one event", () => {
    const events = createChatEvents();
    const a = vi.fn();
    const b = vi.fn();
    events.on("turn:sent", a);
    events.on("turn:sent", b);
    events.emit("turn:sent", { draft });
    expect(a).toHaveBeenCalledOnce();
    expect(b).toHaveBeenCalledOnce();
  });

  it("does not cross events", () => {
    const events = createChatEvents();
    const other = vi.fn();
    events.on("turn:sent", other);
    events.emit("queue:promoted", { id: "q1" });
    expect(other).not.toHaveBeenCalled();
  });

  it("is silent for an event nobody listens to", () => {
    const events = createChatEvents();
    expect(() => events.emit("queue:taken", { id: "q1", draft })).not.toThrow();
  });
});

describe("unsubscribing", () => {
  it("stops delivery", () => {
    const events = createChatEvents();
    const seen = vi.fn();
    const off = events.on("turn:sent", seen);
    off();
    events.emit("turn:sent", { draft });
    expect(seen).not.toHaveBeenCalled();
  });

  it("still delivers to a handler that ANOTHER handler unsubscribed mid-dispatch", () => {
    // MUTANT: iterate the live set instead of a copy → this dies.
    //
    // A `Set` tolerates deleting the entry it is currently on, so a one-shot
    // removing itself is safe with or without the copy — that case proves
    // nothing. This is the case that does: everyone listening WHEN the event
    // happened must hear it, or a listener is skipped for this emit only and
    // reports nothing, which is indistinguishable from an event that never
    // fired.
    const events = createChatEvents();
    const victim = vi.fn();
    let off = () => {};
    // The remover is registered FIRST so it runs first and can still reach the
    // victim, which is only then added — iteration order is insertion order.
    events.on("turn:sent", () => off());
    off = events.on("turn:sent", victim);
    events.emit("turn:sent", { draft });
    expect(victim).toHaveBeenCalledOnce();
  });

  it("unsubscribes only the handler it was given", () => {
    const events = createChatEvents();
    const kept = vi.fn();
    const dropped = vi.fn();
    const off = events.on("turn:sent", dropped);
    events.on("turn:sent", kept);
    off();
    events.emit("turn:sent", { draft });
    expect(dropped).not.toHaveBeenCalled();
    expect(kept).toHaveBeenCalledOnce();
  });
});

describe("one bus per chat", () => {
  it("does not deliver across instances", () => {
    // Two conversations open side by side must not hear each other — the reason
    // this is a factory rather than a module-scoped singleton.
    const a = createChatEvents();
    const b = createChatEvents();
    const seen = vi.fn();
    a.on("turn:sent", seen);
    b.emit("turn:sent", { draft });
    expect(seen).not.toHaveBeenCalled();
  });
});
