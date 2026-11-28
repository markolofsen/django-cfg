import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatLink } from "./chat-link";
import { LinkPreviewProvider, loadLinkPreview, resetLinkPreviews } from "./link-preview";

const URL_ = "https://example.com/some/long/path";
const ICON = "data:image/png;base64,iVBORw0KGgo=";

beforeEach(resetLinkPreviews);

describe("ChatLink preview", () => {
  it("is the short address with no provider", () => {
    const html = renderToStaticMarkup(<ChatLink href={URL_} />);
    expect(html).toContain("chat-link-chip");
    expect(html).not.toContain("chat-link-title");
  });

  it("asks for nothing while rendering on the server, and keeps the short address", () => {
    const resolve = vi.fn(async () => ({ title: "x" }));
    const html = renderToStaticMarkup(
      <LinkPreviewProvider resolve={resolve}>
        <ChatLink href={URL_} />
      </LinkPreviewProvider>,
    );
    expect(resolve).not.toHaveBeenCalled();
    expect(html).not.toContain("chat-link-title");
  });

  it("shows icon, title and host for an address already looked up", async () => {
    const resolve = vi.fn(async () => ({ title: "Example page", favicon: ICON }));
    await loadLinkPreview(URL_, resolve);
    const html = renderToStaticMarkup(
      <LinkPreviewProvider resolve={resolve}>
        <ChatLink href={URL_} />
      </LinkPreviewProvider>,
    );
    expect(html).toContain('class="chat-link-title truncate">Example page<');
    expect(html).toContain('class="chat-link-host truncate">example.com<');
    expect(html).toContain(`src="${ICON}"`);
    expect(html).toContain("Example page\nhttps://example.com");
  });

  it("never draws an icon that is not a plain inline image", async () => {
    await loadLinkPreview(URL_, async () => ({ title: "T", favicon: "https://evil.example/i.png" }));
    const html = renderToStaticMarkup(
      <LinkPreviewProvider resolve={async () => undefined}>
        <ChatLink href={URL_} />
      </LinkPreviewProvider>,
    );
    expect(html).not.toContain("<img");
    expect(html).toContain("chat-link-title");
  });

  it("does not use a preview for the author's own label or for http", async () => {
    await loadLinkPreview(URL_, async () => ({ title: "T" }));
    await loadLinkPreview("http://example.com/p", async () => ({ title: "T" }));
    const labelled = renderToStaticMarkup(
      <LinkPreviewProvider resolve={async () => undefined}>
        <ChatLink href={URL_}>the docs</ChatLink>
      </LinkPreviewProvider>,
    );
    expect(labelled).toContain("the docs");
    expect(labelled).not.toContain("chat-link-title");
    const plain = renderToStaticMarkup(
      <LinkPreviewProvider resolve={async () => undefined}>
        <ChatLink href="http://example.com/p" />
      </LinkPreviewProvider>,
    );
    expect(plain).not.toContain("chat-link-title");
  });
});

describe("loadLinkPreview", () => {
  it("asks once per address, however many ask", async () => {
    const resolve = vi.fn(async () => ({ title: "T" }));
    await Promise.all([loadLinkPreview(URL_, resolve), loadLinkPreview(URL_, resolve)]);
    await loadLinkPreview(URL_, resolve);
    expect(resolve).toHaveBeenCalledTimes(1);
  });

  it("treats a rejection as nothing to show", async () => {
    const resolve = vi.fn(async () => {
      throw new Error("boom");
    });
    await expect(loadLinkPreview(URL_, resolve)).resolves.toBeUndefined();
  });

  it("runs at most three lookups at once", async () => {
    let live = 0;
    let peak = 0;
    const releases: Array<() => void> = [];
    const resolve = (): Promise<undefined> =>
      new Promise((done) => {
        live += 1;
        peak = Math.max(peak, live);
        releases.push(() => {
          live -= 1;
          done(undefined);
        });
      });
    const all = Array.from({ length: 6 }, (_, i) => loadLinkPreview(`https://e${i}.example.com/`, resolve));
    await Promise.resolve();
    expect(peak).toBe(3);
    while (releases.length) {
      releases.shift()?.();
      await Promise.resolve();
      await Promise.resolve();
    }
    await Promise.all(all);
    expect(peak).toBe(3);
  });
});
