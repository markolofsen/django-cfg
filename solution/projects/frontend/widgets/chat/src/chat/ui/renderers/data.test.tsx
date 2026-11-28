import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatCapabilities } from "../../core";
import type { ChatMessage, MessagePart } from "../../core";
import { ChatContext, type ChatContextValue } from "../../store/context";
import { DataRenderer } from "./data";

/**
 * Media reaches the transcript, and an unsafe src does not.
 *
 * The gate is the point of these tests. A media `src` is a URL the MODEL chose,
 * so rendering one is an outbound request made on the user's behalf — and unlike
 * the enrichment cards, a wrong answer here is not a missing widget but a
 * request to whoever the model named.
 *
 * Only `capabilities` is provided: this renderer reads nothing else off the
 * context, and standing up a store would test the harness rather than the rule.
 */

const PREFIXES = ["/api/admin/attachments/"] as const;

const context = (capabilities: ChatCapabilities): ChatContextValue =>
  ({ capabilities }) as ChatContextValue;

const message = { id: "m1", role: "assistant", parts: [] } as unknown as ChatMessage;

const render = (part: MessagePart, capabilities: ChatCapabilities) =>
  renderToStaticMarkup(
    <ChatContext.Provider value={context(capabilities)}>
      <DataRenderer part={part} message={message} />
    </ChatContext.Provider>,
  );

const imagePart = (src: string): MessagePart =>
  ({ type: "data", id: "b1", kind: "image", data: { kind: "image", src } }) as MessagePart;

describe("media blocks reach the transcript", () => {
  it("renders an https image", () => {
    expect(render(imagePart("https://example.com/a.png"), { media: { sameOriginPrefixes: [] } }))
      .toContain("https://example.com/a.png");
  });

  it("renders an allowlisted same-origin image", () => {
    const html = render(imagePart("/api/admin/attachments/abc"), {
      media: { sameOriginPrefixes: PREFIXES },
    });
    expect(html).toContain("/api/admin/attachments/abc");
  });

  it("renders a textual kind through the plain-text fallback", () => {
    const part = {
      type: "data",
      id: "b2",
      kind: "markdown",
      data: { kind: "markdown", content: "# hello" },
    } as MessagePart;
    expect(render(part, { media: { sameOriginPrefixes: [] } })).toContain("# hello");
  });
});

describe("the src gate", () => {
  // The whole reason the allowlist exists. Each of these is a scheme the server
  // rejects, and each would be an outbound request or worse if it rendered.
  it.each([
    ["javascript:", "javascript:alert(1)"],
    ["plain http", "http://evil.example/a.png"],
    ["non-image data:", "data:text/html;base64,PHNjcmlwdD4="],
    ["file:", "file:///etc/passwd"],
    ["protocol-relative", "//evil.example/a.png"],
    ["a path outside every prefix", "/api/other/a.png"],
    ["a traversal out of an allowed prefix", "/api/admin/attachments/../../etc/passwd"],
  ])("drops %s", (_label, src) => {
    const html = render(imagePart(src), { media: { sameOriginPrefixes: PREFIXES } });
    expect(html).toBe("");
  });

  // Absent capability is not "render everything anyway": a host that cannot say
  // which same-origin paths are its own cannot gate the request at all.
  it("renders nothing at all when the host declares no media capability", () => {
    expect(render(imagePart("https://example.com/a.png"), {})).toBe("");
  });

  it("still gates when the capability declares no prefixes", () => {
    const html = render(imagePart("/api/admin/attachments/abc"), {
      media: { sameOriginPrefixes: [] },
    });
    expect(html).toBe("");
  });
});

describe("a picture opens in the host's viewer", () => {
  /** Stands in for a host's lightbox, which lives above this package. */
  const renderImage = ({ src, title }: { readonly src: string; readonly title: string }) => (
    <button type="button" data-viewer={src}>
      {title}
    </button>
  );

  it("hands an agent-generated image to the host, not to a bare img", () => {
    // The asymmetry this closes: `renderImage` reached an ATTACHED image through
    // `file.tsx` while a GENERATED one never did, so a picture the agent sent
    // opened and a picture it produced was the only inert thing in the app.
    const html = render(imagePart("https://example.com/a.png"), {
      media: { sameOriginPrefixes: [], renderImage },
    });
    expect(html).toContain('data-viewer="https://example.com/a.png"');
    expect(html).not.toContain("<img");
  });

  it("titles the overlay with the name the agent gave the picture", () => {
    const part = {
      type: "data",
      id: "b2",
      kind: "image",
      data: { kind: "image", src: "https://example.com/a.png", title: "a stone bridge" },
    } as MessagePart;
    expect(render(part, { media: { sameOriginPrefixes: [], renderImage } })).toContain(
      "a stone bridge",
    );
  });

  it("still gates the src before the host ever sees it", () => {
    // The viewer is not a way around the allowlist: a rejected block never
    // reaches a renderer, so the capability cannot be used to fetch a URL the
    // gate refused.
    const html = render(imagePart("/api/admin/attachments/abc"), {
      media: { sameOriginPrefixes: [], renderImage },
    });
    expect(html).toBe("");
  });

  it("falls back to a plain img when the host supplies no viewer", () => {
    // Absent, not stubbed: a bare consumer still SEES the picture.
    const html = render(imagePart("https://example.com/a.png"), {
      media: { sameOriginPrefixes: [] },
    });
    expect(html).toContain("<img");
  });
});

describe("kinds this renderer does not own", () => {
  // The enrichment cards keep their own branch, and an unknown kind stays silent
  // rather than drawing a placeholder for content this build cannot read.
  it("renders nothing for a kind in neither set", () => {
    const part = { type: "data", id: "b3", kind: "not-a-kind", data: {} } as MessagePart;
    expect(render(part, { media: { sameOriginPrefixes: PREFIXES } })).toBe("");
  });
});
