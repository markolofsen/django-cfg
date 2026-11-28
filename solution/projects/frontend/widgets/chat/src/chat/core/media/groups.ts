/**
 * Which parts of a turn form one picture grid.
 *
 * A messenger shows pictures sent together as ONE block (2, 3, 4 and "+N"), not as a stack of
 * full-width tiles. Pure and DOM-free so the rule is tested as data.
 */
import type { AttachmentPart, MessagePart } from "../conversation/parts";

export type PartItem =
  | { readonly kind: "part"; readonly part: MessagePart }
  | { readonly kind: "images"; readonly id: string; readonly parts: readonly AttachmentPart[] };

/** A picture the grid can draw: an image attachment that still has a link. An expired or unlinked one stays an ordinary part (a muted chip). */
export const isGridImage = (part: MessagePart): part is AttachmentPart =>
  part.type === "attachment" && part.attachment.kind === "image" && part.attachment.url !== "";

/** Runs of two or more consecutive grid images become one item; a lone picture and every other part pass through unchanged. */
export function groupMedia(parts: readonly MessagePart[]): PartItem[] {
  const items: PartItem[] = [];
  let run: AttachmentPart[] = [];
  const flush = () => {
    if (run.length >= 2) items.push({ kind: "images", id: `grid:${run[0]!.id}`, parts: run });
    else for (const part of run) items.push({ kind: "part", part });
    run = [];
  };
  for (const part of parts) {
    if (isGridImage(part)) run.push(part);
    else {
      flush();
      items.push({ kind: "part", part });
    }
  }
  flush();
  return items;
}

/** Tiles drawn (the rest fold into "+N" on the last). */
export const GRID_MAX = 4;
