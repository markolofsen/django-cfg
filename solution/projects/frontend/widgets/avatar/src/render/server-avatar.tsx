import type { CSSProperties } from "react";

import { type AvatarKind, styleForSeed } from "../registry/corpora";
import { drawAvatar } from "./draw";

/**
 * The same face, drawn on the SERVER.
 *
 * A React Server Component, and the reason it exists rather than reusing
 * `SeededAvatar`: that one resolves its style through a hook, which forces
 * `'use client'` on every consumer and ships the style packages to the browser.
 * On a static, indexable catalogue page that is the wrong trade — the markup is
 * identical for a given seed, so it can be produced once at build time and sent
 * as bytes, with no JavaScript and no loading frame.
 *
 * The seed rule is unchanged and deliberately so: the SAME package, the SAME
 * corpora, the SAME hash. A visitor who sees a persona in the catalogue and then
 * installs it must meet the identical face in the product — a second generator
 * would be worse than no portrait at all.
 *
 * Awaits the style rather than lazy-loading it. There is no frame to fill on the
 * server; the import simply resolves before the markup is emitted.
 */
export interface ServerAvatarProps {
  /** A stable ADDRESS — for a catalogue listing, the role slug. Never a display
   *  name: a name-derived face changes on rename. */
  readonly seed: string;
  readonly kind?: AvatarKind;
  readonly size?: number;
  readonly className?: string;
}

export async function ServerAvatar({
  seed,
  kind = "person",
  size = 40,
  className,
}: ServerAvatarProps) {
  const style = await styleForSeed(kind, seed).load();
  const svg = drawAvatar(style, seed, size);
  const boxStyle: CSSProperties = { display: "block", width: size, height: size };

  // Generated here from a seed — never user content, never fetched — so there is
  // nothing to sanitise, and React cannot mount an SVG string any other way.
  return (
    <span
      className={className}
      style={boxStyle}
      aria-hidden
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
