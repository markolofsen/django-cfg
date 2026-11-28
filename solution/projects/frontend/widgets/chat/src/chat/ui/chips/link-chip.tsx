import type { ComponentProps } from "react";
import { Globe } from "lucide-react";

import { linkChipLabel } from "../../core/links";

/**
 * The anchor's own props are accepted and forwarded so a wrapper that CLONES
 * this element — a hover card trigger, a tooltip — can attach its handlers.
 */
export interface LinkChipProps extends ComponentProps<"a"> {
  /** The href, already hardened by the renderer. */
  href: string;
}

/**
 * Inline chip rendered in place of a BARE url in a chat bubble.
 *
 * ## Why only a bare url
 *
 * `[the docs](https://…)` already has the label its author chose; boxing it
 * adds weight and removes nothing. A bare url has no label at all, so the
 * reader is left parsing the raw string — often longer than the sentence
 * around it, and wrapping mid-url across two lines. That is what a chip fixes.
 * The decision itself lives in `core/links/prose.ts`, so it is testable
 * without a DOM.
 *
 * ## An anchor, not a button
 *
 * A link is a LINK: the browser already knows how to open one in a new tab,
 * copy its address, or show it on hover, and every one of those is lost the
 * moment a button stands in for it.
 *
 * ## The label is the short form, the href is the tooltip
 *
 * Same trade the file chip makes with a path. `linkChipLabel` keeps the domain
 * whole and collapses the path's middle; the whole url stays one hover away.
 *
 * ## It does not take which side of the bubble it is on
 *
 * It used to, and nothing could supply the answer: the anchor is rendered from
 * the host's memoized `components` object, which is built once per screen and
 * cannot carry a per-message value without re-parsing every message. The
 * stylesheet reads `data-role` off the message wrapper instead.
 */
export function LinkChip({ href, ...rest }: LinkChipProps) {
  const label = linkChipLabel(href);

  return (
    <a
      // FIRST, so the hardened `target`/`rel` below cannot be overwritten by a
      // caller — but present at all so a cloning wrapper's handlers survive.
      {...rest}
      href={href}
      // Size, colour, ground and the width ceiling come from `.chat-chip` and
      // `.chat-link-chip` in markdown.css. This list carries STRUCTURE only.
      //
      // No `items-center`: the rule sets `align-items: baseline` so the LABEL
      // donates the chip's baseline, and a utility would win over it.
      className="chat-chip chat-link-chip inline-flex h-auto min-w-0 gap-1 align-baseline whitespace-nowrap"
      // The label collapses the url's middle, so the whole address is visible
      // NOWHERE else — this is both the tooltip and the accessible name. A
      // wrapper showing it more richly passes `title=""` to suppress it.
      title={rest.title ?? href}
      target="_blank"
      // `noreferrer` implies `noopener`; both are stated because the pair is
      // what keeps the opened page from reaching back through `window.opener`.
      rel="noreferrer noopener"
    >
      <Globe aria-hidden />
      <span className="truncate">{label}</span>
    </a>
  );
}
