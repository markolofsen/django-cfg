import { createAvatar } from "@dicebear/core";
import type { Style } from "@dicebear/core";

import { hashSeed } from "../seed/hash";

/**
 * Turn a resolved style and a seed into mountable SVG markup.
 *
 * Separate from both renderers because the two rewrites below are properties of
 * INLINE SVG in a shared document, not of React. The client hook and the server
 * function must apply them identically — two copies would drift, and the drift
 * is invisible until a page shows one face and blanks the rest.
 */
export function drawAvatar(style: Style<Record<string, unknown>>, seed: string, size: number): string {
  const raw = createAvatar(style, { seed, size }).toString();

  // Element IDs are DOCUMENT-global, and every style declares the same ones.
  // Each avatar emits `<mask id="viewboxMask">` and clips itself with
  // `url(#viewboxMask)`, so a second avatar on the page resolves the FIRST
  // one's mask. With viewBoxes differing by style — 16 units for pixel art,
  // 980 for notionists — the later drawings clip to a corner and vanish.
  //
  // Derived from the seed, never random: identical markup on every render, so
  // React does not replace the node and a server render matches its hydration.
  const nonce = hashSeed(`${size}:${seed}`).toString(36);
  const namespaced = raw
    .replace(/\bid="([^"]+)"/g, `id="$1-${nonce}"`)
    .replace(/url\(#([^)]+)\)/g, `url(#$1-${nonce})`);

  // The generator emits `width`/`height` ATTRIBUTES, and any CSS rule outranks
  // an attribute. Consumers wrap avatars in rows carrying `[&_svg]:size-4` — a
  // descendant rule meant for a chat row's icons — which collapsed every face
  // to 16px inside its own correctly-sized tile. An INLINE style is the one
  // thing that rule cannot outrank.
  return namespaced.replace("<svg ", `<svg style="width:${size}px;height:${size}px" `);
}
