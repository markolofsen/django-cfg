import { describe, expect, it } from "vitest";
import { MEDIA_KINDS, SRC_KINDS, TEXTUAL_KINDS, URL_FIELDS, isMediaKind } from "./kinds";

describe("the media vocabulary", () => {
  it("holds the eleven kinds the server accepts", () => {
    // Locked against the server's supported-kinds set.
    // If the server grows a twelfth, this test fails and the
    // registry gets an entry — which is the intended way to find out, rather
    // than a block silently rendering nothing in production.
    expect([...MEDIA_KINDS].sort()).toEqual([
      "audio",
      "code",
      "gallery",
      "image",
      "json",
      "link",
      "map",
      "markdown",
      "mermaid",
      "text",
      "video",
    ]);
  });

  it("treats an unknown kind as unsupported rather than throwing", () => {
    // A transcript stored by a newer agent can reach an older client. The
    // degrade is "render nothing", never a crash inside a transcript row.
    expect(isMediaKind("hologram")).toBe(false);
    expect(isMediaKind(8)).toBe(false);
    expect(isMediaKind(undefined)).toBe(false);
  });

  it("classifies every kind as either textual or src-bearing, none as both", () => {
    // A kind in neither set has no renderer route at all; a kind in both has
    // two, and the second one wins by accident. Either is a silent gap, so the
    // partition is asserted rather than assumed.
    for (const kind of MEDIA_KINDS) {
      const textual = TEXTUAL_KINDS.has(kind);
      const src = SRC_KINDS.has(kind);
      // `map` is deliberately neither: its payload is a LatLng centre, not a
      // URL and not text.
      if (kind === "map") {
        expect(textual || src, "map should be neither").toBe(false);
        continue;
      }
      expect(textual !== src, `${kind} must be exactly one of textual/src`).toBe(true);
    }
  });
});

describe("URL_FIELDS", () => {
  it("lists a field for every src-bearing kind and none for the rest", () => {
    for (const kind of MEDIA_KINDS) {
      const fields = URL_FIELDS[kind];
      expect(fields.length > 0, `${kind}`).toBe(SRC_KINDS.has(kind));
    }
  });

  it("includes the SECONDARY urls, which are the ones a renderer forgets", () => {
    // Each of these is gated by the server's validation and each is an outbound request
    // the browser makes for a model-authored block. Validating `src` and then
    // dropping an unchecked `favicon` into an <img> leaves the exfil vector
    // open while looking careful.
    expect(URL_FIELDS.audio).toContain("cover");
    expect(URL_FIELDS.video).toContain("cover");
    expect(URL_FIELDS.gallery).toContain("items[].thumbnail");
    expect(URL_FIELDS.link).toContain("link.image");
    expect(URL_FIELDS.link).toContain("link.favicon");
  });
});
