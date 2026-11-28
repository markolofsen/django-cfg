import { describe, expect, it } from "vitest";

import { toolMarker } from "../tools/picks";
import { extractToolId } from "./tool-id";

describe("extractToolId", () => {
  it("reads the id back out of a canonical link", () => {
    expect(extractToolId("app://tool/read_file")).toBe("read_file");
  });

  it("returns null for a bare tool link that names nothing", () => {
    // Parses, but identifies no tool — the caller must treat this exactly like
    // "not a tool link", since neither can be drawn as a chip.
    expect(extractToolId("app://tool")).toBeNull();
  });

  it("returns null for other app hosts and for foreign hrefs", () => {
    for (const href of [
      "app://note/abc",
      "app://note/abc",
      "https://example.com/tool/read_file",
      "not a url",
      undefined,
    ]) {
      expect(extractToolId(href)).toBeNull();
    }
  });

  /** The composer's writer and this reader must agree, or no pick ever chips. */
  it("round-trips whatever the marker writer produced", () => {
    const marker = toolMarker("transcribe_audio", "Transcribe audio");
    const href = marker.slice(marker.indexOf("](") + 2, marker.lastIndexOf(")"));

    expect(extractToolId(href)).toBe("transcribe_audio");
  });
});
