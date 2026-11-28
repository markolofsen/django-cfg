// @vitest-environment jsdom
import { act } from "react";
import { createElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { PageSnapshotProvider } from "../page-snapshot";
import { usePageCopilot, type PageCopilot } from "./use-page-copilot";
import type { PageAwareAdapter, PageTurn } from "./adapter";

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let copilot: PageCopilot | null = null;
let turns: PageTurn[] = [];

const host: PageAwareAdapter = {
  sendMessage: (_request, turn) => {
    turns.push(turn);
    return Promise.resolve(new ReadableStream());
  },
};

function Probe() {
  copilot = usePageCopilot(host);
  return null;
}

beforeEach(() => {
  document.body.innerHTML = "";
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  turns = [];
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  copilot = null;
});

async function mount(linked: boolean) {
  await act(async () => {
    root.render(
      // eslint-disable-next-line react/no-children-prop
      createElement(PageSnapshotProvider, {
        defaultLinked: linked,
        children: createElement(Probe),
      })
    );
  });
}

const send = async () => {
  await act(async () => {
    await copilot!.adapter.sendMessage({
      text: "hi",
      history: [],
      recipient: "all",
      mentions: [],
      messageId: "m1",
      attachments: [],
      signal: new AbortController().signal,
    });
  });
};

describe("usePageCopilot", () => {
  it("sends no page when the user has not opted in", async () => {
    document.body.innerHTML += "<main><h1>Private</h1></main>";
    await mount(false);
    await send();
    expect(turns[0]).toEqual({});
  });

  it("sends the page on the first turn", async () => {
    document.body.innerHTML += "<main><h1>Shared</h1></main>";
    await mount(true);
    await send();
    expect(turns[0]?.page?.kind).toBe("snapshot");
  });

  /**
   * The whole reason the capture carries a content hash. Re-sending an
   * unchanged tree costs thousands of tokens per turn and tells the agent
   * nothing it does not already have.
   */
  it("sends a reference, not the tree, while the page is unchanged", async () => {
    document.body.innerHTML += "<main><h1>Steady</h1></main>";
    await mount(true);
    await send();
    await send();

    expect(turns[0]?.page?.kind).toBe("snapshot");
    expect(turns[1]?.page).toEqual({
      kind: "unchanged",
      hash: expect.stringMatching(/^[0-9a-f]{8}$/),
    });
  });

  it("sends the tree again once the page changes", async () => {
    document.body.innerHTML += '<main id="s"><h1>Before</h1></main>';
    await mount(true);
    await send();
    document.querySelector("#s")!.innerHTML = "<h1>After</h1><p>More</p>";
    await send();

    expect(turns[1]?.page?.kind).toBe("snapshot");
  });

  it("carries a reported result on the next turn, once", async () => {
    await mount(false);
    act(() => {
      copilot!.reportResult({ actionId: "a1", outcome: "rejected" });
    });

    await send();
    expect(turns[0]?.results).toEqual([{ actionId: "a1", outcome: "rejected" }]);

    // Drained by the send: a result repeated every turn would have the agent
    // answer the same refusal again.
    await send();
    expect("results" in turns[1]!).toBe(false);
  });
});
