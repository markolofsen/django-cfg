import { FileText, Film, Music } from "lucide-react";
import { formatBytes } from "../../core/compose/attachments";
import type { PartRenderProps } from "../../primitives";
import { safeImageUrl, ZoomableImage } from "../../content";

/** http(s), blob: and same-origin paths only — a `javascript:` URL in a stored message must not become a link. */
function safeUrl(url: string): string | null {
  if (url.startsWith("/") && !url.startsWith("//")) return url;
  try {
    const parsed = new URL(url);
    return ["http:", "https:", "blob:"].includes(parsed.protocol) ? url : null;
  } catch {
    return null;
  }
}

/**
 * A file the sender attached: a picture inline, audio and video with controls,
 * anything else as a named link. An unsafe URL renders the name alone.
 */
export function AttachmentRenderer({ part }: PartRenderProps) {
  if (part.type !== "attachment") return null;
  const { name, kind, size, url, mime } = part.attachment;
  const href = kind === "image" ? safeImageUrl(url) : safeUrl(url);
  if (href === null) {
    // No link: a file the server no longer stores (an empty `url`) or an unsafe one. The name stays; nothing is offered to open.
    return (
      <span className="flex w-fit max-w-full items-center gap-2 rounded-md border border-dashed border-border px-2.5 py-1.5 text-sm opacity-70">
        <FileText className="size-4 shrink-0" aria-hidden />
        <span className="truncate">{name}</span>
        {size > 0 ? <span className="shrink-0 text-xs">{formatBytes(size)}</span> : null}
      </span>
    );
  }

  if (kind === "image") return <ZoomableImage src={href} name={name} className="max-h-80 max-w-full rounded-xl object-cover" buttonClassName="block w-fit max-w-full cursor-zoom-in overflow-hidden rounded-xl focus-visible:outline-2 focus-visible:outline-offset-2" />;
  if (kind === "audio") {
    return (
      <figure className="flex max-w-full flex-col gap-1">
        <audio controls preload="none" src={href} className="max-w-full" />
        <figcaption className="truncate text-xs opacity-70">{name}</figcaption>
      </figure>
    );
  }
  if (kind === "video") {
    return (
      <figure className="flex max-w-full flex-col gap-1">
        <video controls preload="metadata" src={href} className="max-h-64 max-w-full rounded-md" />
        <figcaption className="truncate text-xs opacity-70">{name}</figcaption>
      </figure>
    );
  }
  const Icon = kind === "text" ? FileText : mime.startsWith("audio/") ? Music : mime.startsWith("video/") ? Film : FileText;
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      download={name}
      className="flex w-fit max-w-full items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-sm hover:bg-muted"
    >
      <Icon className="size-4 shrink-0" aria-hidden />
      <span className="truncate">{name}</span>
      <span className="shrink-0 text-xs opacity-70">{formatBytes(size)}</span>
    </a>
  );
}
