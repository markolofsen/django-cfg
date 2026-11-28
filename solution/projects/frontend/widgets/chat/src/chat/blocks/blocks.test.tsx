import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatMessage, MessagePart } from "../core";
import { ChatContext, type ChatContextValue } from "../store/context";
import { createChatStore } from "../store";
import { withModel } from "../store/send-request";
import { BlockRenderer, isBlockKind, readApproval, readAsk, readChanges } from "./index";

describe("payload parsers", () => {
  it("reads an ask with string and object options, drops blanks", () => {
    const ask = readAsk({ question: "Which?", options: ["A", { label: "B", description: "bee" }, "", 3] });
    expect(ask?.options).toEqual([{ label: "A" }, { label: "B", description: "bee" }]);
    expect(ask?.other).toBe(false);
  });
  it("an ask with no options always allows a typed answer", () => {
    expect(readAsk({ question: "Name?" })?.other).toBe(true);
    expect(readAsk({ options: [], other: "Type here" })?.other).toBe("Type here");
  });
  it("rejects what is not a block", () => {
    expect(readAsk(null)).toBeNull();
    expect(readAsk({ options: [] })).toBeNull();
    expect(readApproval({ changes: [] })).toBeNull();
    expect(readChanges({ items: ["x"] })).toBeNull();
  });
  it("keeps only well-formed approval changes", () => {
    const approval = readApproval({ summary: "S", changes: [{ path: "a", to: "b", from: "c" }, { path: "x" }, "no"] });
    expect(approval?.changes).toEqual([{ path: "a", to: "b", from: "c" }]);
  });
  it("drops an unsafe item link but keeps the item", () => {
    const changes = readChanges({ title: "T", items: [{ label: "ok", href: "/p/1" }, { label: "bad", href: "javascript:alert(1)" }, "plain"] });
    expect(changes?.items).toEqual([{ label: "ok", href: "/p/1" }, { label: "bad" }, { label: "plain" }]);
    expect(changes?.undoable).toBe(false);
  });
  it("knows its kinds", () => {
    expect(["ask", "approval", "changes"].every(isBlockKind)).toBe(true);
    expect(isBlockKind("table")).toBe(false);
  });
});

const message = (id: string, role: "user" | "assistant", parts: readonly MessagePart[] = []): ChatMessage =>
  ({ id, role, parts, status: { state: "complete" }, createdAt: 0 }) as ChatMessage;

function render(part: MessagePart, rows: readonly ChatMessage[]) {
  const store = createChatStore({ adapter: { sendMessage: async () => new ReadableStream() }, makeId: () => "x", now: () => 0 });
  store.load(rows);
  const context = { store, capabilities: {}, events: {} } as unknown as ChatContextValue;
  return renderToStaticMarkup(
    <ChatContext.Provider value={context}>
      <BlockRenderer part={part} message={rows[0]!} />
    </ChatContext.Provider>,
  );
}

describe("BlockRenderer", () => {
  const ask: MessagePart = { id: "p", type: "data", kind: "ask", data: { question: "Which?", options: ["A", "B"] } };
  it("offers the options on the latest message", () => {
    const html = render(ask, [message("a1", "assistant", [ask])]);
    expect(html).toContain('data-block="ask"');
    expect(html).toContain('data-locked="false"');
    expect(html).not.toContain('disabled=""');
  });
  it("shows the block settled once a user message follows it", () => {
    const html = render(ask, [message("a1", "assistant", [ask]), message("u1", "user")]);
    expect(html).toContain('data-locked="true"');
    expect(html).toContain('disabled=""');
  });
  it("draws nothing for a malformed payload", () => {
    const bad: MessagePart = { id: "p", type: "data", kind: "approval", data: { nope: 1 } };
    expect(render(bad, [message("a1", "assistant", [bad])])).toBe("");
  });
});

describe("withModel", () => {
  const request = { text: "hi" } as Parameters<typeof withModel>[0];
  it("adds the chosen model", () => expect(withModel(request, "fast").model).toBe("fast"));
  it("leaves the request alone without a choice", () => expect(withModel(request, undefined)).toBe(request));
});
