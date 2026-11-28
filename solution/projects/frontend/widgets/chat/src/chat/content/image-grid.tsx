"use client";

import { cn } from "@djangocfg/ui-core/lib";

import type { AttachmentPart } from "../core/conversation/parts";
import { GRID_MAX } from "../core/media/groups";
import { safeImageUrl, ZoomableImage } from "./zoomable-image";

/**
 * Pictures sent together, laid out like a messenger: 2 side by side, 3 as one large and two stacked, 4 as 2x2, more as 2x2 with "+N" on the last tile.
 * Every tile opens the shared lightbox on its own picture and swipes through the rest. Tiles crop to fill (`object-cover`); the full picture is one click away.
 */
export function ImageGrid({ parts }: { readonly parts: readonly AttachmentPart[] }) {
  const shown = parts.slice(0, GRID_MAX);
  const extra = parts.length - shown.length;
  const group = parts.map((part) => ({ src: safeImageUrl(part.attachment.url) ?? "", name: part.attachment.name })).filter((image) => image.src !== "");
  const three = shown.length === 3;
  return (
    <div
      role="group"
      data-slot="image-grid"
      data-media
      data-count={shown.length}
      className={cn(
        "grid w-[22rem] max-w-full gap-0.5 overflow-hidden rounded-xl",
        shown.length === 2 ? "aspect-[2/1] grid-cols-2" : "aspect-square grid-cols-2 grid-rows-2",
      )}
    >
      {shown.map((part, index) => {
        const src = safeImageUrl(part.attachment.url);
        if (src === null) return null;
        const last = index === shown.length - 1 && extra > 0;
        return (
          <div key={part.id} className={cn("relative min-h-0 min-w-0", three && index === 0 && "row-span-2")}>
            <ZoomableImage
              src={src}
              name={part.attachment.name}
              group={group}
              index={index}
              className="size-full object-cover"
              buttonClassName="block size-full cursor-zoom-in focus-visible:outline-2 focus-visible:-outline-offset-2"
            />
            {last ? (
              <span className="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/50 text-2xl font-medium text-white" aria-hidden>
                +{extra}
              </span>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
