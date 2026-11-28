import type { CSSProperties } from "react";

import { type AvatarKind } from "../registry/corpora";
import { placeholderColour } from "../seed/placeholder";
import { useAvatarSvg } from "./use-avatar-svg";

/**
 * A face derived from a seed — the same seed always draws the same face, on
 * every device and every reload, with nothing persisted anywhere.
 *
 * That determinism is why this package exists rather than an avatar column: a
 * stored face would be a second source of truth for a value this function
 * already returns, and the two would disagree the day one was written and the
 * other was not.
 *
 * Domain-neutral by construction. It takes a string and a kind, never a contact
 * — WHICH identity seeds a face is a product decision that belongs beside the
 * surfaces making it, not inside the thing that draws.
 */
export interface SeededAvatarProps {
  /**
   * The stable identity to derive from. Must be an ADDRESS, never a display
   * name: a name-derived face changes on rename, which reads as the agent having
   * been replaced.
   */
  readonly seed: string;
  /**
   * What KIND of thing wears it, which selects the corpus.
   *
   * `person` draws a character, `room` an abstract mark. A room drawn with a
   * face would claim to be a person; the difference is carried in the silhouette
   * so a mixed list separates before any glyph is read.
   */
  readonly kind?: AvatarKind;
  /** Rendered size in px. The SVG is square and scales to it. */
  readonly size?: number;
  readonly className?: string;
}

export function SeededAvatar({ seed, kind = "person", size = 40, className }: SeededAvatarProps) {
  const svg = useAvatarSvg(kind, seed, size);
  // `block`, because a bare <span> is inline: an empty one collapses to a
  // zero-height sliver however much width and height it is given, which is what
  // an unloaded row looked like — a dot instead of a tile.
  const style: CSSProperties = { display: "block", width: size, height: size };

  if (!svg) {
    // The style package has not landed yet. A seeded colour, so the column is
    // varied from the first frame rather than flashing uniform grey and then
    // becoming varied.
    return (
      <span
        className={className}
        style={{ ...style, backgroundColor: placeholderColour(seed) }}
        aria-hidden
      />
    );
  }

  // The markup is GENERATED HERE from a seed — it is never user content and
  // never crosses the network, so there is nothing to sanitise. React cannot
  // mount an SVG string any other way.
  //
  // Sizing the wrapper is not enough and `useAvatarSvg` says why: consumers
  // carry `[&_svg]:size-4`, which collapses the drawing inside a correctly-sized
  // box. The size travels inline on the SVG itself.
  return (
    <span
      className={className}
      style={style}
      aria-hidden
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
