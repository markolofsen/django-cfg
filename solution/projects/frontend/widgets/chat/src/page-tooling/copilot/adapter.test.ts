import { describe, expect, it, vi } from "vitest";

import { withPageContext, type PageAwareAdapter, type PageTurn } from "./adapter";
import type { SendRequest } from "../../chat/core";
import type { PageContext } from "./context";

const PAGE: PageContext = { kind: "unchanged", hash: "abcd1234" };

function spyAdapter(): PageAwareAdapter & { turns: PageTurn[] } {
  const turns: PageTurn[] = [];
  return {
    turns,
    sendMessage: (_request, turn) => {
      turns.push(turn);
      return Promise.resolve(new ReadableStream());
    },
  };
}

const request: SendRequest = {
  text: "hi",
  history: [],
  recipient: "all",
  mentions: [],
  messageId: "m1",
  attachments: [],
  signal: new AbortController().signal,
};

describe("withPageContext", () => {
  it("hands the page to the host adapter", async () => {
    const host = spyAdapter();
    const wrapped = withPageContext(host, {
      readPage: () => PAGE,
      drainResults: () => [],
    });

    await wrapped.sendMessage(request);

    expect(host.turns[0]?.page).toEqual(PAGE);
  });

  /**
   * Absent means absent. A host reading `'page' in turn` must not see a key
   * whose value is undefined — that reads as "the page was shared and is
   * empty", which is a different fact from "not shared".
   */
  it("omits the page entirely when nothing is shared", async () => {
    const host = spyAdapter();
    const wrapped = withPageContext(host, {
      readPage: () => undefined,
      drainResults: () => [],
    });

    await wrapped.sendMessage(request);

    expect(host.turns[0]).toEqual({});
    expect("page" in host.turns[0]!).toBe(false);
  });

  it("carries pending action results, and omits the key when there are none", async () => {
    const host = spyAdapter();
    const results = [{ actionId: "a1", outcome: "rejected" as const }];
    const wrapped = withPageContext(host, {
      readPage: () => undefined,
      drainResults: () => results,
    });

    await wrapped.sendMessage(request);
    expect(host.turns[0]?.results).toEqual(results);

    const empty = spyAdapter();
    const second = withPageContext(empty, {
      readPage: () => undefined,
      drainResults: () => [],
    });
    await second.sendMessage(request);
    expect("results" in empty.turns[0]!).toBe(false);
  });

  /**
   * Capture-on-send. Reading at wrap time would send the page as it was when
   * the chat mounted, which is the page the user has since navigated away from.
   */
  it("reads the page at send time, not at wrap time", async () => {
    const host = spyAdapter();
    const readPage = vi.fn(() => PAGE);
    const wrapped = withPageContext(host, { readPage, drainResults: () => [] });

    expect(readPage).not.toHaveBeenCalled();
    await wrapped.sendMessage(request);
    expect(readPage).toHaveBeenCalledTimes(1);
  });

  it("passes the chat's own request through untouched", async () => {
    const seen: unknown[] = [];
    const host: PageAwareAdapter = {
      sendMessage: (req) => {
        seen.push(req);
        return Promise.resolve(new ReadableStream());
      },
    };
    const wrapped = withPageContext(host, {
      readPage: () => undefined,
      drainResults: () => [],
    });

    await wrapped.sendMessage(request);
    expect(seen[0]).toBe(request);
  });
});
