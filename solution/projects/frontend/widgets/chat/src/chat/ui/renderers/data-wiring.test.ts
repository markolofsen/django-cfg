import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The renderers `DataRenderer` hands to `MediaWidget`.
 *
 * `MediaWidget` takes three optional render callbacks and falls back silently
 * when one is missing — which is exactly how `renderContent` stayed unsupplied
 * while looking wired: the seam existed, the widget called it, and every
 * textual block quietly rendered as a `<pre>`. Nothing failed, because an
 * absent capability and an absent WIRE look identical from inside the widget.
 *
 * So the gate belongs on the mount site rather than on any renderer. Read as
 * source rather than rendered: mounting this component needs a store, a
 * capability and a message, and none of that is what could regress here — the
 * question is whether the prop is passed at all.
 */

const DATA_RENDERER = readFileSync(join(import.meta.dirname, "data.tsx"), "utf8");

describe("the media renderers are wired", () => {
  it("reads the file it is asserting about", () => {
    // The control. Every assertion below is a substring match, and all of them
    // pass against an empty string — a read that silently returned nothing
    // would report a green gate over a file it never saw.
    expect(DATA_RENDERER).toContain("MediaWidget");
  });

  it.each(["renderContent", "renderPlayer", "renderImage"])(
    "passes %s to MediaWidget",
    (prop) => {
      expect(DATA_RENDERER).toContain(`${prop}={`);
    },
  );
});
