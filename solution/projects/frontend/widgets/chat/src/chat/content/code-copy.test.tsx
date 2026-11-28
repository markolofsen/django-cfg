// @vitest-environment jsdom
import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Response } from "./response";

/**
 * Copy is the one behaviour of a fence that needs a document: a click on the
 * header's button must put the CODE on the clipboard. Mounted through
 * `Response`, so it pins the whole path (fence -> `ChatCode` -> kit
 * `PrettyCode` -> clipboard) and not the kit in isolation.
 */
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

// jsdom has no matchMedia; the theme hook asks it which palette to draw.
window.matchMedia ??= ((query: string) => ({ matches: false, media: query, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, onchange: null, dispatchEvent: () => false })) as typeof window.matchMedia;

const mounted: Array<() => void> = [];
afterEach(() => {
  while (mounted.length) mounted.pop()?.();
  vi.restoreAllMocks();
});

function mount(markdown: string): HTMLElement {
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  act(() => root.render(<Response>{markdown}</Response>));
  mounted.push(() => {
    act(() => root.unmount());
    host.remove();
  });
  return host;
}

describe("a fence's copy button", () => {
  it("copies the code, without the fence's closing newline", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    const host = mount("```ts\nconst x = 1;\nconst y = 2;\n```");

    const button = host.querySelector<HTMLButtonElement>('[data-slot="pretty-code"] button');
    expect(button).not.toBeNull();
    await act(async () => button?.click());

    expect(writeText).toHaveBeenCalledWith("const x = 1;\nconst y = 2;");
  });

  it("leaves the icon alone when the browser refuses the write", async () => {
    const writeText = vi.fn().mockRejectedValue(new Error("denied"));
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    const host = mount("```sh\nls\n```");

    const button = host.querySelector<HTMLButtonElement>('[data-slot="pretty-code"] button');
    await act(async () => button?.click());

    expect(writeText).toHaveBeenCalled();
    expect(button?.querySelector(".lucide-check")).toBeNull();
  });
});
