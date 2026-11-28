import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { assertChatClient, chatClientProblems, ChatClientDriftError } from "./assert-chat-client";

const op = { responses: {} };
/** The shape the server's snapshot has, under another mount (`/apix/x/`): the check must not depend on the prefix or on operation ids. */
const current = () => ({
  paths: {
    "/apix/x/threads/": { get: op, post: op },
    "/apix/x/threads/{thread_id}/": { get: op },
    "/apix/x/threads/{thread_id}/messages/": { post: op },
    "/apix/x/threads/{thread_id}/messages/{message_id}/stream/": { get: op },
    "/apix/x/threads/{thread_id}/messages/{message_id}/cancel/": { post: op },
    "/apix/x/threads/{thread_id}/messages/{message_id}/parts/{index}/ack/": { post: op },
    "/apix/x/attachments/": { post: op },
  } as Record<string, Record<string, unknown>>,
  components: {
    schemas: {
      ChatMessage: { properties: { id: {}, parts: {}, trace: {} } } as { properties: Record<string, unknown> },
      ChatTraceStepFrame: { properties: {} },
    } as Record<string, { properties: Record<string, unknown> }>,
  },
});

describe("assertChatClient", () => {
  it("accepts a current document under any mount", () => {
    expect(() => assertChatClient(current())).not.toThrow();
  });

  it("accepts the framework's own snapshot of the server contract", () => {
    const path = new URL("../../../../../../../django-cfg/src/django_cfg/modules/django_llm/agent/chat/tests/snapshots/chat_api_openapi.json", import.meta.url);
    let raw: string;
    try {
      raw = readFileSync(path, "utf8");
    } catch {
      return; // the package checked out alone: the monorepo copy is not there
    }
    expect(chatClientProblems(JSON.parse(raw))).toEqual([]);
  });

  it("accepts a mount without trailing slashes, and a host with no attachments route when it says so", () => {
    const doc = current();
    doc.paths = Object.fromEntries(Object.entries(doc.paths).filter(([path]) => !path.endsWith("/attachments/")).map(([path, item]) => [path.replace(/\/$/, ""), item]));
    expect(chatClientProblems(doc, { attachments: false })).toEqual([]);
    expect(chatClientProblems(doc)).toEqual([expect.stringContaining("POST …/attachments/")]);
  });

  it("names a missing cancel and stream route", () => {
    const doc = current();
    delete doc.paths["/apix/x/threads/{thread_id}/messages/{message_id}/cancel/"];
    delete doc.paths["/apix/x/threads/{thread_id}/messages/{message_id}/stream/"];
    const problems = chatClientProblems(doc);
    expect(problems).toHaveLength(2);
    expect(problems.join("\n")).toMatch(/POST …\/threads\/\{\}\/messages\/\{\}\/cancel\//);
    expect(problems.join("\n")).toMatch(/GET …\/threads\/\{\}\/messages\/\{\}\/stream\//);
  });

  it("a method on the wrong path does not count", () => {
    const doc = current();
    doc.paths["/apix/x/threads/"] = { get: op }; // create is gone
    expect(chatClientProblems(doc)).toEqual([expect.stringContaining("POST …/threads/")]);
  });

  it("flags a schema that is `tool_calls` only, with no `trace`", () => {
    const doc = current();
    doc.components.schemas.ChatMessage = { properties: { id: {}, parts: {}, tool_calls: {} } };
    const problems = chatClientProblems(doc);
    expect(problems.some((p) => p.includes("no `trace`"))).toBe(true);
    expect(problems.some((p) => p.includes("still has `tool_calls`"))).toBe(true);
  });

  it("flags a missing trace_step frame schema and a missing message schema", () => {
    const doc = current();
    delete doc.components.schemas.ChatTraceStepFrame;
    delete doc.components.schemas.ChatMessage;
    expect(chatClientProblems(doc)).toHaveLength(2);
  });

  it("throws one error that lists every problem and says what to do", () => {
    const doc = current();
    doc.paths = {};
    let caught: unknown;
    try {
      assertChatClient(doc);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(ChatClientDriftError);
    expect((caught as ChatClientDriftError).problems).toHaveLength(8);
    expect((caught as Error).message).toMatch(/behind the server contract \(8 problems\)[\s\S]*make update/);
  });

  it("rejects something that is not an openapi document", () => {
    expect(() => assertChatClient({})).toThrow(/no `paths`/);
    expect(() => assertChatClient(null)).toThrow(ChatClientDriftError);
  });
});
