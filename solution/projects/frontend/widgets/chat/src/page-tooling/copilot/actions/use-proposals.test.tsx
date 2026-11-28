// @vitest-environment jsdom
import { act } from "react";
import { createElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useProposals, type ProposalQueue } from "./use-proposals";
import { VISIBLE_TIMEOUT_MS } from "../../browser-bridge/perform";
import type { ActionResult } from "../adapter";
import type { RefResolver } from "../../browser-bridge/overlay/resolve-ref";

(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let queue: ProposalQueue | null = null;
let reported: ActionResult[] = [];
let resolver: RefResolver | null = null;

function Probe() {
  queue = useProposals(resolver, (result) => reported.push(result));
  return null;
}

beforeEach(() => {
  document.body.innerHTML = "";
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  page = document.createElement("div");
  document.body.appendChild(page);
  reported = [];
  resolver = null;
  (globalThis as Record<string, unknown>).IntersectionObserver = class {
    constructor(private readonly cb: IntersectionObserverCallback) {}
    observe(el: Element) {
      this.cb([{ isIntersecting: true, intersectionRatio: 1, target: el } as never], this as never);
    }
    disconnect() {}
    unobserve() {}
    takeRecords() {
      return [];
    }
    root = null;
    rootMargin = "";
    thresholds = [];
  } as never;
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  page.remove();
  queue = null;
});

async function mount() {
  await act(async () => {
    root.render(createElement(Probe));
  });
}

/**
 * A button in the document, reachable as `@e1`.
 *
 * Deliberately OUTSIDE the React container: React owns that subtree and
 * replaces its contents on render, which detaches anything written there and
 * makes every action resolve `stale`. The real page is never inside the chat's
 * own root either.
 */
let page: HTMLDivElement;

function targetButton() {
  page.innerHTML = "<button>Save</button>";
  const button = page.querySelector("button")!;
  resolver = { resolve: (ref) => (ref === "@e1" ? button : null) };
  return button;
}

const CLICK = { kind: "click", ref: "@e1" } as const;

describe("useProposals — the confirmation gate", () => {
  /**
   * The property the whole gate exists for. A proposal is a card, not an
   * instruction: nothing reaches the page until the user says so.
   */
  it("does NOT touch the page when a proposal arrives", async () => {
    const button = targetButton();
    const clicked = vi.fn();
    button.addEventListener("click", clicked);

    await mount();
    await act(async () => {
      queue!.add("p1", CLICK, "Save");
      // Awaited, and long enough to outlast `executeAction`'s visibility wait.
      // Asserting synchronously here passes even with the gate removed —
      // acting is async, so "nothing happened yet" is not "nothing will".
      await new Promise((resolve) => setTimeout(resolve, VISIBLE_TIMEOUT_MS + 20));
    });

    expect(queue!.proposals).toHaveLength(1);
    expect(clicked).not.toHaveBeenCalled();
    expect(reported).toEqual([]);
  });

  it("acts on the page only after approval, and reports it", async () => {
    const button = targetButton();
    const clicked = vi.fn();
    button.addEventListener("click", clicked);

    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    await act(async () => queue!.approve("p1", CLICK));

    expect(clicked).toHaveBeenCalledTimes(1);
    expect(reported).toEqual([{ actionId: "p1", outcome: "approved" }]);
  });

  /**
   * A refusal is an answer. Without it the agent cannot tell "no" from a
   * delivery failure, and re-proposes the same action.
   */
  it("tells the agent about a refusal, and leaves the page alone", async () => {
    const button = targetButton();
    const clicked = vi.fn();
    button.addEventListener("click", clicked);

    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    act(() => queue!.reject("p1"));

    expect(clicked).not.toHaveBeenCalled();
    expect(reported).toEqual([{ actionId: "p1", outcome: "rejected" }]);
  });

  it("runs an approved action once, however many times Approve is pressed", async () => {
    const button = targetButton();
    const clicked = vi.fn();
    button.addEventListener("click", clicked);

    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    await act(async () => {
      await Promise.all([queue!.approve("p1", CLICK), queue!.approve("p1", CLICK)]);
    });

    expect(clicked).toHaveBeenCalledTimes(1);
    expect(reported).toHaveLength(1);
  });

  it("ignores an approval after a refusal", async () => {
    const button = targetButton();
    const clicked = vi.fn();
    button.addEventListener("click", clicked);

    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    act(() => queue!.reject("p1"));
    await act(async () => queue!.approve("p1", CLICK));

    expect(clicked).not.toHaveBeenCalled();
    expect(reported).toEqual([{ actionId: "p1", outcome: "rejected" }]);
  });

  /**
   * The page moves between the agent proposing and the user reading. The ref
   * is re-resolved at approval time, so a vanished target is reported as
   * `stale` rather than acted on by position.
   */
  it("reports stale when the target went away before approval", async () => {
    targetButton();
    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));

    page.innerHTML = "";

    await act(async () => queue!.approve("p1", CLICK));
    expect(reported).toEqual([{ actionId: "p1", outcome: "stale" }]);
  });

  it("expires what is still open when the turn moves on", async () => {
    targetButton();
    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    act(() => queue!.add("p2", CLICK, "Save again"));
    act(() => queue!.reject("p1"));

    act(() => queue!.expire());

    expect(reported).toEqual([
      { actionId: "p1", outcome: "rejected" },
      { actionId: "p2", outcome: "expired" },
    ]);
  });

  /**
   * A card rendered from a transcript block was never `add`ed — the block IS
   * the proposal. Settling it must still leave a record, or the card it came
   * from stays pending and offers Approve again after the action already ran.
   */
  it("records an outcome for a proposal it was never told about", async () => {
    targetButton();
    await mount();

    await act(async () => queue!.approve("from-transcript", CLICK));

    expect(reported).toEqual([{ actionId: "from-transcript", outcome: "approved" }]);
    expect(queue!.proposals).toEqual([
      expect.objectContaining({
        id: "from-transcript",
        state: { status: "settled", outcome: "approved" },
      }),
    ]);
  });

  it("records a refusal for a proposal it was never told about", async () => {
    targetButton();
    await mount();

    act(() => queue!.reject("from-transcript", CLICK));

    expect(reported).toEqual([{ actionId: "from-transcript", outcome: "rejected" }]);
    expect(queue!.proposals).toHaveLength(1);
  });

  /**
   * The settled record must keep the label the card was showing.
   *
   * `approve` knows the action but not the words, so a record built from the
   * action alone renders "Type ... into " with the target missing — the card
   * loses the name of the thing it just changed, at the exact moment the user
   * looks to confirm what happened.
   */
  it("keeps the label when settling a proposal it was never told about", async () => {
    targetButton();
    await mount();

    await act(async () => queue!.approve("from-transcript", CLICK, "the Save button"));

    expect(queue!.proposals[0]).toMatchObject({
      id: "from-transcript",
      label: "the Save button",
    });
  });

  it("ignores a duplicate proposal id", async () => {
    targetButton();
    await mount();
    act(() => queue!.add("p1", CLICK, "Save"));
    act(() => queue!.add("p1", CLICK, "Save"));

    expect(queue!.proposals).toHaveLength(1);
  });
});
