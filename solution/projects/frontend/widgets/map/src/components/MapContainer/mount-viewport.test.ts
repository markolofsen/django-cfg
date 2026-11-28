import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

/**
 * The camera opens AT `initialViewport`; it never travels there.
 *
 * A consumer addressing the map by URL depends on this: easing in from the
 * default view on a shared link tells the visitor they arrived somewhere else
 * first, and on a link that names a specific place it is simply wrong.
 *
 * The property holds because `viewport` reaches `<Map>` as controlled props and
 * nothing in this component animates the camera on mount. That is a fact about
 * the source, so it is asserted against the source — a rendered assertion would
 * need a WebGL context this suite has no reason to carry.
 */

const source = (name: string): string =>
  readFileSync(fileURLToPath(new URL(name, import.meta.url)), "utf8");

describe("the initial camera", () => {
  it("reaches the map as controlled props, not as a flight", () => {
    const inner = source("./MapInner.tsx");

    // The handoff: whatever the provider seeded is what the map opens with.
    expect(inner).toMatch(/<Map[\s\S]{0,200}\{\.\.\.viewport\}/);

    // And no animation on the way in. `MapCluster` and the consumers may fly the
    // camera later; this component must not do it at all, or the addressed
    // position becomes a destination.
    for (const move of ["flyTo", "easeTo", "jumpTo"]) {
      expect(inner).not.toContain(move);
    }
  });

  it("is captured once, so a later value cannot fight a gesture", () => {
    const context = source("../../context/MapContext.tsx");

    // A ref, not state: re-reading the prop would make every parent render pull
    // the camera back to where the URL said it was when the page loaded.
    expect(context).toMatch(/initialViewportRef\s*=\s*useRef/);
    expect(context).toMatch(/useState<MapViewport>\(initialViewportRef\.current\)/);
  });
});
