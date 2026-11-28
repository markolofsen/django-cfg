import { describe, expect, it } from "vitest";
import { readMediaBlock } from "./block";

const PREFIXES = ["/api/admin/"] as const;
const read = (data: unknown) => readMediaBlock(data, PREFIXES);

/**
 * The gate runs ONCE, at dispatch — so this is where the allowlist has to be
 * proven applied, not inside eleven separate renderers.
 */

describe("gating", () => {
  it("keeps a block whose src is allowed", () => {
    const block = read({ kind: "image", src: "https://example.com/a.png", alt: "a" });

    expect(block).toMatchObject({ kind: "image", src: "https://example.com/a.png" });
  });

  it("returns null when a src-bearing kind loses its only source", () => {
    // Rendering an empty frame would claim media exists that the gate refused.
    expect(read({ kind: "image", src: "javascript:alert(1)" })).toBeNull();
    expect(read({ kind: "video", src: "http://example.com/v.mp4" })).toBeNull();
  });

  it("drops an unsafe COVER but keeps the playable audio", () => {
    // The degrade is per-field: a rejected decoration must not take the content
    // with it. This is the case that separates "gated" from "blocked".
    const block = read({
      kind: "audio",
      src: "https://example.com/a.mp3",
      cover: "javascript:alert(1)",
    });

    expect(block?.src).toBe("https://example.com/a.mp3");
    expect(block?.cover).toBeUndefined();
  });

  it("drops an unsafe favicon and image from a link preview, keeping the text", () => {
    const block = read({
      kind: "link",
      url: "https://example.com",
      link: {
        title: "Title",
        image: "http://evil.example/x.png",
        favicon: "javascript:alert(1)",
      },
    });

    expect(block?.link?.title).toBe("Title");
    expect(block?.link?.image).toBeUndefined();
    expect(block?.link?.favicon).toBeUndefined();
  });

  it("drops only the rejected gallery items", () => {
    const block = read({
      kind: "gallery",
      items: [
        { src: "https://example.com/1.png" },
        { src: "javascript:alert(1)" },
        { src: "https://example.com/2.png", thumbnail: "http://evil/x.png" },
      ],
    });

    expect(block?.items).toHaveLength(2);
    expect(block?.items?.[1]?.thumbnail).toBeUndefined();
  });

  it("returns null for a gallery whose every item was rejected", () => {
    expect(read({ kind: "gallery", items: [{ src: "javascript:x" }] })).toBeNull();
  });
});

describe("kinds", () => {
  it("rejects an unknown kind rather than guessing a renderer", () => {
    expect(read({ kind: "hologram", src: "https://example.com/x" })).toBeNull();
    expect(read({ src: "https://example.com/x" })).toBeNull();
  });

  it("keeps a textual kind with content and no src", () => {
    const block = read({ kind: "code", content: "const x = 1;", language: "ts" });

    expect(block).toMatchObject({ kind: "code", content: "const x = 1;", language: "ts" });
  });

  it("returns null for a textual kind with no content", () => {
    expect(read({ kind: "markdown" })).toBeNull();
  });

  it("reads each textual kind from the field the SERVER actually sends", () => {
    // The defect this file could not see. Every other case here hands the
    // reader a generic `content`, which the server never sends — it names each
    // kind's payload separately, so all four of these arrived with `content`
    // undefined and were dropped by the check below. A dropped block is
    // indistinguishable from one the agent never sent, so nothing reported it.
    expect(read({ kind: "mermaid", chart: "graph TD; A-->B" })?.content).toBe("graph TD; A-->B");
    expect(read({ kind: "markdown", markdown: "# title" })?.content).toBe("# title");
    expect(read({ kind: "text", text: "plain" })?.content).toBe("plain");
    expect(read({ kind: "code", code: "const x = 1;", language: "ts" })?.content).toBe(
      "const x = 1;",
    );
  });

  it("serialises a json block, whose payload is a VALUE and not text", () => {
    // The one textual kind that is not a string on the wire.
    expect(read({ kind: "json", data: { a: 1 } })?.content).toBe('{\n  "a": 1\n}');
  });

  it("still accepts the generic field, so a hand-built block keeps working", () => {
    // Stories and tests speak the model's vocabulary rather than the server's.
    expect(read({ kind: "mermaid", content: "graph TD; A-->B" })?.content).toBe("graph TD; A-->B");
  });

  it("keeps an empty string as content, since a blank code block is legitimate", () => {
    // `str()` treats "" as absent for titles; content must NOT, or an
    // intentionally empty block becomes an unrenderable one.
    expect(read({ kind: "text", content: "" })?.content).toBe("");
  });

  it("survives junk without throwing", () => {
    for (const junk of [null, undefined, 7, "image", [], { kind: 8 }]) {
      expect(() => read(junk)).not.toThrow();
    }
  });
});

/**
 * The reader picks keys explicitly, so a field the server sends and this list
 * omits is dropped silently — no type error, no failing render, just a card
 * that has nothing to show. Both halves are pinned for that reason.
 */
describe("provenance and facts", () => {
  const src = "https://example.com/a.png";

  it("carries a generation through", () => {
    const block = read({
      kind: "image",
      src,
      generation: {
        prompt: "a red bicycle",
        size: "1024x1024",
        quality: "best",
        model: "google/gemini-2.5-flash-image",
        publicUrl: "https://cdn.example/img/abc/1.jpg",
      },
    });
    expect(block?.generation).toEqual({
      prompt: "a red bicycle",
      size: "1024x1024",
      quality: "best",
      // Describes the RESULT, not the request.
      model: "google/gemini-2.5-flash-image",
      // Survives the server rewriting `src` to its own path.
      publicUrl: "https://cdn.example/img/abc/1.jpg",
    });
  });

  it("refuses a public url the media allowlist rejects", () => {
    // A provenance field is written by a tool, so an ungated one would be an
    // address a model chose — the same hazard the block's own src is gated for.
    const block = read({
      kind: "image",
      src,
      generation: { prompt: "a red bicycle", publicUrl: "javascript:alert(1)" },
    });
    expect(block?.generation?.publicUrl).toBeUndefined();
  });

  it("drops a generation with no prompt, rather than keeping an empty shell", () => {
    expect(read({ kind: "image", src, generation: { size: "1024x1024" } })?.generation)
      .toBeUndefined();
  });

  const HASH = "a".repeat(64);

  it("names the blob a hosted src IS", () => {
    // The address and the identity are one string, so the block states its own
    // key and nothing has to look it up.
    const block = read({ kind: "image", src: `/api/admin/${HASH}` });
    expect(block?.attachmentId).toBe(HASH);
  });

  it("claims no blob for a picture hosted elsewhere", () => {
    // Those bytes never reached this server, so nothing here has measured them.
    expect(read({ kind: "image", src })?.attachmentId).toBeUndefined();
  });

  it("refuses a path segment that is not a full content address", () => {
    // Another same-origin route — an uploaded file — whose last segment is not a
    // hash. Reading it as an id would name a blob that does not exist.
    expect(read({ kind: "image", src: "/api/admin/notes/x.png" })?.attachmentId)
      .toBeUndefined();
  });
});

describe("the control", () => {
  it("can return a block at all, so the null assertions are not vacuous", () => {
    expect(read({ kind: "image", src: "https://example.com/a.png" })).not.toBeNull();
  });
});
