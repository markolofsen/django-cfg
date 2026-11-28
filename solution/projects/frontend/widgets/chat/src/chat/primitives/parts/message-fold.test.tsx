import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatMessage, MessagePart, ToolState } from "../../core/conversation/parts";
import { MessageContent } from "./message";
import { PartRegistryProvider, type PartRegistry } from "./part-registry";

const tool = (id: string, toolState: ToolState = { state: "output-available", input: {}, output: "" }): MessagePart => ({
  type: "tool",
  id,
  toolName: "read",
  toolState,
});
const message = (parts: MessagePart[]): ChatMessage => ({ id: "m", role: "assistant", parts, status: { state: "complete" }, createdAt: 0 });

const renderers: PartRegistry = {
  tool: ({ part }) => <i data-tool={part.id} />,
  text: ({ part }) => <p>{part.type === "text" ? part.text : ""}</p>,
};

const html = (parts: MessagePart[]) =>
  renderToStaticMarkup(
    <PartRegistryProvider renderers={renderers}>
      <MessageContent message={message(parts)} />
    </PartRegistryProvider>,
  );

describe("a message's settled tool calls", () => {
  it("fold behind one counter, closed, with the calls inside", () => {
    const out = html([tool("a"), tool("b"), tool("c")]);
    expect(out).toContain('class="chat-fold"');
    expect(out).toContain("3 tools used");
    expect(out).not.toContain(" open");
    expect(out.match(/data-tool=/g)).toHaveLength(3);
  });

  it("do not fold while one runs", () => {
    // MUTANT: planFold without the activity guard -> a counter appears mid-run.
    const out = html([tool("a"), tool("b"), tool("c", { state: "input-available", input: {} })]);
    expect(out).not.toContain("chat-fold");
    expect(out.match(/data-tool=/g)).toHaveLength(3);
  });

  it("leave a failed call outside the counter", () => {
    const out = html([tool("a"), tool("b"), tool("e", { state: "output-error", input: {}, error: "x" })]);
    expect(out).toContain("2 tools used");
    const outside = out.slice(out.indexOf("</details>"));
    expect(outside).toContain('data-tool="e"');
  });

  it("keep the prose between two runs in place", () => {
    const out = html([tool("a"), tool("b"), { type: "text", id: "t", text: "between" }, tool("c"), tool("d")]);
    expect(out.indexOf("between")).toBeGreaterThan(out.indexOf("2 tools used"));
    expect(out.match(/chat-fold"/g)).toHaveLength(2);
  });
});
