"use client";

import { useState } from "react";

import { LazyImageLightbox } from "@djangocfg/widget-media/image-viewer";

import { useChatCopy } from "../../i18n";

/** http(s), blob:, data:image and same-origin paths only: a `javascript:` URL in a stored or model-written message must not reach an `<img>` or the viewer. */
export function safeImageUrl(url: string): string | null {
  if (url.startsWith("/") && !url.startsWith("//")) return url;
  if (/^data:image\/(png|jpe?g|gif|webp|avif|svg\+xml)[;,]/i.test(url)) return url;
  try {
    return ["http:", "https:", "blob:"].includes(new URL(url).protocol) ? url : null;
  } catch {
    return null;
  }
}

export interface ZoomableImageProps {
  readonly src: string;
  readonly name?: string;
  /** The picture's own classes (size and fit); the button around it adds none. */
  readonly className?: string;
  /** The grid or list this picture is part of: the viewer opens on `index` and swipes through the rest. */
  readonly group?: readonly { readonly src: string; readonly name?: string }[];
  readonly index?: number;
  /** The src drawn in the page (a thumbnail); the viewer always gets `src`. */
  readonly thumbnail?: string;
  /** Replaces the button's own sizing (`block w-fit max-w-full`): a grid tile fills its cell. */
  readonly buttonClassName?: string;
}

/**
 * The one picture every message surface uses: a user's attachment, an image block or gallery an agent sent, and a markdown `![](…)`. It is a button; a click opens it large in the shared
 * lightbox (zoom, swipe, save) instead of a new tab, so a picture behaves the same wherever it came from. A host that owns a viewer passes `media.renderImage` and that wins for media blocks.
 */
export function ZoomableImage({ src, name = "", className = "max-h-64 max-w-full rounded-md object-contain", group, index = 0, thumbnail, buttonClassName }: ZoomableImageProps) {
  const copy = useChatCopy().blocks;
  const [open, setOpen] = useState(false);
  const images = group ?? [{ src, name }];
  return (
    <>
      <button type="button" data-media onClick={() => setOpen(true)} aria-label={`${copy.openImage}${name ? `: ${name}` : ""}`} className={buttonClassName ?? "block w-fit max-w-full cursor-zoom-in rounded-md focus-visible:outline-2 focus-visible:outline-offset-2"}>
        {/* referrerPolicy: a model-authored URL must not receive the transcript's address. */}
        <img src={thumbnail ?? src} alt={name} loading="lazy" referrerPolicy="no-referrer" className={className} data-slot="media-image" />
      </button>
      {open ? <LazyImageLightbox open images={images.map((image) => ({ src: image.src, name: image.name ?? "" }))} index={group ? index : 0} onClose={() => setOpen(false)} /> : null}
    </>
  );
}
