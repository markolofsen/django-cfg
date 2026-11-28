// @vitest-environment jsdom
import { act, createElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createActionRenderer } from "./renderer";
import type { Proposal } from "./proposal";
import type { ProposalQueue } from "./use-proposals";

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
});

function stubQueue(proposals: readonly Proposal[] = []): ProposalQueue {
  return {
    proposals,
    add: vi.fn(),
    approve: vi.fn(async () => {}),
    reject: vi.fn(),
    expire: vi.fn(),
  };
}

const BLOCK = {
  type: "data",
  kind: "ui-action",
  data: { id: "a1", label: "the Save button", action: { kind: "click", ref: "@e1" } },
};

async function render(node: React.ReactNode) {
  await act(async () => root.render(node));
}

describe("createActionRenderer", () => {
  it("renders a ui-action block as a card with both answers", async () => {
    const Renderer = createActionRenderer({ queue: stubQueue() });
    await render(createElement(Renderer, { part: BLOCK }));

    const labels = [...container.querySelectorAll("button")].map((b) => b.textContent);
    expect(labels).toEqual(["Approve", "Skip"]);
    expect(container.textContent).toContain("the Save button");
  });

  it("approves with the action carried by the block", async () => {
    const queue = stubQueue();
    const Renderer = createActionRenderer({ queue });
    await render(createElement(Renderer, { part: BLOCK }));

    await act(async () => {
      container.querySelector("button")!.click();
    });

    // The LABEL travels with the approval: the settled record is what the card
    // draws next, and without it the sentence loses its target.
    expect(queue.approve).toHaveBeenCalledWith(
      "a1",
      { kind: "click", ref: "@e1" },
      "the Save button"
    );
  });

  /**
   * The queue is the only source of the ANSWER. A settled id must render as
   * settled even though the block that produced it is unchanged — the
   * transcript never rewrites itself.
   */
  it("shows the outcome once the queue has settled that id", async () => {
    const queue = stubQueue([
      {
        id: "a1",
        action: { kind: "click", ref: "@e1" },
        label: "the Save button",
        state: { status: "settled", outcome: "approved" },
      },
    ]);
    const Renderer = createActionRenderer({ queue });
    await render(createElement(Renderer, { part: BLOCK }));

    expect(container.querySelector("button")).toBeNull();
    expect(container.textContent).toContain("Done");
  });

  /**
   * The registry dispatches on `part.type`, so this renderer owns EVERY data
   * part. Not delegating would blank every media block the chat draws.
   */
  it("delegates a data part of another kind to the chat renderer", async () => {
    const fallback = vi.fn(() => createElement("p", null, "chart"));
    const Renderer = createActionRenderer({ queue: stubQueue(), fallback });
    await render(createElement(Renderer, { part: { type: "data", kind: "chart", data: {} } }));

    expect(fallback).toHaveBeenCalled();
    expect(container.textContent).toBe("chart");
  });

  /**
   * The card is ONE sentence: a verb from the action and a noun phrase from
   * the agent's label. `Click` + `the Save button` composes by luck; a fill
   * without a connector reads "Type “ada@example.com” the email field".
   */
  it("reads as a sentence for a fill", async () => {
    const Renderer = createActionRenderer({ queue: stubQueue() });
    await render(
      createElement(Renderer, {
        part: {
          type: "data",
          kind: "ui-action",
          data: {
            id: "a2",
            label: "the email field",
            action: { kind: "fill", ref: "@e2", value: "ada@example.com" },
          },
        },
      })
    );

    // The sentence only — `textContent` on the card would sweep in the buttons.
    expect(container.querySelector("[data-sentence]")!.textContent).toBe(
      "Type “ada@example.com” into the email field"
    );
  });

  it("reads as a sentence for a click", async () => {
    const Renderer = createActionRenderer({ queue: stubQueue() });
    await render(createElement(Renderer, { part: BLOCK }));

    expect(container.textContent).toContain("Click the Save button");
  });

  it("renders nothing for a malformed ui-action block", async () => {
    const Renderer = createActionRenderer({ queue: stubQueue() });
    await render(
      createElement(Renderer, { part: { type: "data", kind: "ui-action", data: { id: "x" } } })
    );

    expect(container.innerHTML).toBe("");
  });
});
