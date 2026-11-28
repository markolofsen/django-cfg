import { createAvatar } from "@dicebear/core";
import { describe, expect, it } from "vitest";

import { PERSON_STYLES, ROOM_STYLES } from "../registry/corpora";

/**
 * The size must survive a hostile stylesheet.
 *
 * Consumers wrap avatars in rows carrying `[&_svg]:size-4`, a descendant rule
 * meant for a chat row's icons. Any CSS rule outranks the `width`/`height`
 * ATTRIBUTES the generator emits, so a face sized only by attribute — or only by
 * its wrapper — collapses to 16px inside a correctly-sized tile. That shipped
 * once and had to be found from a screenshot, which is why it is pinned here.
 */
describe("generated svg", () => {
  it("carries an inline size on the root element, for every style", async () => {
    for (const entry of [...PERSON_STYLES, ...ROOM_STYLES]) {
      const style = await entry.load();
      const svg = createAvatar(style, { seed: "cid_probe", size: 36 }).toString();
      // The exact transform `useAvatarSvg` applies. Asserting the PRECONDITION
      // it relies on: a single root `<svg ` with attributes following it.
      expect(svg.startsWith("<svg ")).toBe(true);
      const patched = svg.replace("<svg ", '<svg style="width:36px;height:36px" ');
      expect(patched.startsWith('<svg style="width:36px;height:36px"')).toBe(true);
      // Exactly once — `replace` with a string pattern hits the first match, and
      // a style whose markup nested a second `<svg ` would leave the inner one
      // unsized while the assertion above still passed.
      expect(patched.match(/style="width:36px;height:36px"/g)).toHaveLength(1);
    }
  }, 20_000);

  /**
   * Element IDs are document-global, and every style declares the SAME ones.
   *
   * Each avatar emits `<mask id="viewboxMask">` and clips itself with
   * `url(#viewboxMask)`. Mounted inline, the second avatar on a page resolves the
   * FIRST one's mask — and because viewBoxes differ by style (16 units for pixel
   * art, 980 for notionists), the later drawings are clipped to a corner and
   * disappear. A mixed roster showed one face and five blanks.
   */
  it("namespaces every id, and leaves no dangling reference", async () => {
    for (const entry of [...PERSON_STYLES, ...ROOM_STYLES]) {
      const style = await entry.load();
      const raw = createAvatar(style, { seed: "cid_probe", size: 36 }).toString();
      const nonce = "zz";
      const out = raw
        .replace(/\bid="([^"]+)"/g, `id="$1-${nonce}"`)
        .replace(/url\(#([^)]+)\)/g, `url(#$1-${nonce})`);

      const ids = [...out.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1] ?? "");
      const refs = [...out.matchAll(/url\(#([^)]+)\)/g)].map((m) => m[1] ?? "");
      // THE CONTROL: renaming ids while missing a reference would "pass" a
      // uniqueness check and render nothing at all.
      expect(refs.every((ref) => ids.includes(ref))).toBe(true);
      expect(ids.every((id) => id.endsWith(`-${nonce}`))).toBe(true);
    }
  }, 20_000);

  it("is byte-identical for one seed, so React never replaces the node", async () => {
    const style = await PERSON_STYLES[0]!.load();
    const once = createAvatar(style, { seed: "cid_stable", size: 36 }).toString();
    const twice = createAvatar(style, { seed: "cid_stable", size: 36 }).toString();
    expect(once).toBe(twice);
  }, 20_000);
});
