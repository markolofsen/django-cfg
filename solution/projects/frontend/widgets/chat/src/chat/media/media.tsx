import type { ReactNode } from "react";
import type { MediaBlock, MediaGeneration } from "../core";
import { ZoomableImage } from "../content";

/**
 * The media registry: one event type, eleven kinds.
 *
 * WHY A REGISTRY AND NOT ELEVEN PROPS. Eleven kinds behind one wire event is
 * exactly the shape the O(1) rule exists for — a twelfth adds an entry here and
 * a renderer, never a prop on `<Chat>`.
 *
 * WHY THE RENDERERS ARE THIN. Measured against both references:
 * djangocfg's `VideoBlock` is 21 lines and `AudioBlock` 26, because each wraps
 * an existing player; Vercel's `audio-player.tsx` is 231 lines because it builds
 * one. Vercel's `image.tsx` could not be used at all — it is typed against
 * `Experimental_GeneratedImage` from the `ai` package and renders base64 only,
 * which is not our model.
 *
 * So: the chat owns the FRAME (aspect, fallback, click-to-zoom); the element or
 * the host's player owns playback. A renderer past ~60 lines is a signal it is
 * re-implementing something that already exists.
 *
 * The `src` gate is NOT here. It runs once at dispatch in
 * `core/media/readMediaBlock`, the split the archived chat states outright:
 * validated centrally "before this renderer runs, so we can trust it here".
 * Per-renderer checking is how one of eleven quietly ends up without one.
 */

export interface MediaRendererProps {
  readonly block: MediaBlock;
  /** Textual kinds hand their content to the host's markdown/code renderer. */
  readonly renderContent?: (block: MediaBlock) => ReactNode;
  /** Kinds needing a real player (audio, video, map) may be supplied by a host. */
  readonly renderPlayer?: (block: MediaBlock) => ReactNode;
  /**
   * A picture, drawn by the host's viewer so it opens like every other image in
   * the app. Absent ⇒ a plain `<img>`, which the frame comment above calls
   * out as the one thing in a transcript that looks openable and is not.
   *
   * `generation` rides along because the host owns the picture's chrome and is
   * therefore the only layer that can offer "what made this". It is passed
   * rather than fetched: the block already carries it, and this package cannot
   * import the feature that would render it.
   */
  readonly renderImage?: (image: {
    readonly src: string;
    readonly title: string;
    readonly generation?: MediaGeneration;
  }) => ReactNode;
}

export function MediaWidget(props: MediaRendererProps) {
  // Wrapped once at the entry rather than by a class on each of the eight
  // renderers below: the rhythm belongs to "a media block in a transcript", and
  // a per-renderer class is a rule the ninth kind joins by remembering to. Two
  // of the branches also delegate to a HOST element whose root this package does
  // not own, so there is no class list to put it on there at all.
  return <div className="chat-block">{mediaOf(props)}</div>;
}

function mediaOf({ block, renderContent, renderPlayer, renderImage }: MediaRendererProps) {
  switch (block.kind) {
    case "image":
      return <MediaImage block={block} renderImage={renderImage} />;
    case "gallery":
      return <MediaGallery block={block} renderImage={renderImage} />;
    case "audio":
    case "video":
    case "map":
      // A host-supplied player wins; the native element is the fallback so a
      // bare consumer still plays media instead of rendering nothing.
      return renderPlayer?.(block) ?? <MediaPlayable block={block} />;
    case "json":
    case "code":
    case "markdown":
    case "text":
    case "mermaid":
      // Routed to the CONTENT renderer rather than a second markdown path —
      // this is the seam where widgets/ and content/ meet on one vocabulary.
      return renderContent?.(block) ?? <MediaPlainText block={block} />;
    case "link":
      return <MediaLink block={block} />;
  }
}

function MediaImage({
  block,
  renderImage,
}: {
  readonly block: MediaBlock;
  readonly renderImage?: MediaRendererProps["renderImage"];
}) {
  if (block.src === undefined) return null;
  // `title` before `alt`: the title is what the agent chose to call the picture
  // and the viewer shows it as the overlay's name, while `alt` is often empty on
  // a decorative image, which would leave that overlay unlabelled.
  const viewed = renderImage?.({
    src: block.src,
    title: block.title ?? block.alt ?? "",
    generation: block.generation,
  });
  if (viewed !== undefined && viewed !== null) return viewed;
  return <ZoomableImage src={block.src} name={block.title ?? block.alt ?? ""} className="max-h-96 w-full rounded-md object-cover" />;
}

function MediaGallery({
  block,
  renderImage,
}: {
  readonly block: MediaBlock;
  readonly renderImage?: MediaRendererProps["renderImage"];
}) {
  const items = block.items ?? [];
  if (items.length === 0) return null;

  return (
    <ul className="grid grid-cols-3 gap-1" data-slot="media-gallery">
      {/* Index, not `item.src`: a gallery may legitimately carry the same URL
          twice — a before/after of one file, or a repeated placeholder — and a
          duplicate key makes React drop or duplicate rows. The list is
          append-only within a block and never reorders, so the index is stable
          for its lifetime. Caught by the Gallery story, which showed one pixel
          twice and turned the warning into a story-test failure. */}
      {items.map((item, index) => (
        <li key={index}>
          <GalleryTile item={item} renderImage={renderImage} group={items.map((one) => ({ src: one.src, name: one.alt }))} index={index} />
        </li>
      ))}
    </ul>
  );
}

/**
 * One picture in a gallery.
 *
 * Its own component because the tile makes a decision the grid does not: the
 * grid shows a THUMBNAIL, the viewer must open the full-size source, so the two
 * srcs are different values and choosing between them inside the `map` is the
 * render algorithm the JSX boundary keeps out of markup.
 */
function GalleryTile({
  item,
  renderImage,
  group,
  index,
}: {
  readonly item: NonNullable<MediaBlock["items"]>[number];
  readonly renderImage?: MediaRendererProps["renderImage"];
  readonly group: readonly { readonly src: string; readonly name?: string }[];
  readonly index: number;
}) {
  const viewed = renderImage?.({ src: item.src, title: item.alt ?? "" });
  if (viewed !== undefined && viewed !== null) return viewed;
  return <ZoomableImage src={item.src} thumbnail={item.thumbnail} name={item.alt ?? ""} group={group} index={index} className="aspect-square w-full rounded object-cover" />;
}

function MediaPlayable({ block }: { readonly block: MediaBlock }) {
  if (block.src === undefined) return null;

  if (block.kind === "audio") {
    return (
      // No caption track: agent-produced audio arrives without one.
      <audio src={block.src} controls preload="metadata" className="w-full" data-slot="media-audio" />
    );
  }

  return (
    // No caption track: agent-produced video arrives without one.
    <video
      src={block.src}
      poster={block.cover}
      controls
      preload="metadata"
      className="w-full rounded-md"
      style={{ aspectRatio: block.aspectRatio ?? 16 / 9 }}
      data-slot="media-video"
    />
  );
}

function MediaPlainText({ block }: { readonly block: MediaBlock }) {
  if (block.content === undefined) return null;
  return (
    <pre className="overflow-x-auto rounded-md p-3 text-xs" data-slot="media-text">
      {block.content}
    </pre>
  );
}

function MediaLink({ block }: { readonly block: MediaBlock }) {
  if (block.url === undefined) return null;
  const preview = block.link;

  return (
    <a
      href={block.url}
      target="_blank"
      // `noopener` is required with target=_blank; `noreferrer` keeps the
      // transcript URL from reaching a destination the model chose.
      rel="noopener noreferrer"
      className="flex gap-3 rounded-md border p-3 no-underline"
      data-slot="media-link"
    >
      {preview?.image === undefined ? null : (
        <img
          src={preview.image}
          alt=""
          loading="lazy"
          referrerPolicy="no-referrer"
          className="size-16 shrink-0 rounded object-cover"
        />
      )}
      <span className="min-w-0">
        {/* Falls back to the URL: the server's contract is that a preview with
            no title still renders as a bare URL card, not as nothing. */}
        <span className="block truncate text-sm font-medium">
          {preview?.title ?? block.url}
        </span>
        {preview?.description === undefined ? null : (
          <span className="line-clamp-2 text-xs opacity-70">{preview.description}</span>
        )}
      </span>
    </a>
  );
}
