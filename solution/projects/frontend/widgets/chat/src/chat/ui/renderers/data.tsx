import type { ReactNode } from "react";

import { BlockRenderer, isBlockKind } from "../../blocks";
import { isMediaKind, readMediaBlock } from "../../core";
import { renderMediaContent } from "../../content";
import type { PartRenderProps } from "../../primitives";
import { useCapabilities } from "../../store";
import { MediaWidget, type MediaRendererProps } from "../../media";

/**
 * Typed blocks the agent authored.
 *
 * ONE renderer for every `data` part, switching on `kind`, rather than one
 * registry entry per kind. The registry is keyed on `part.type`, and `kind` is
 * an open set a host grows. An unknown kind renders nothing, which is the
 * honest outcome: a client one build behind its backend stays silent instead
 * of drawing a placeholder for content it cannot read.
 *
 * The parsers own the degradation. Each takes `unknown` and returns null on a
 * malformed payload, so nothing here guards a shape twice.
 */
export function DataRenderer({ part, message }: PartRenderProps) {
  const capabilities = useCapabilities();
  const media = capabilities.media;
  if (part.type !== "data") return null;

  // Questions, approvals and change cards are the package's own blocks; they need no capability.
  if (isBlockKind(part.kind)) return <BlockRenderer part={part} message={message} />;

  // The eleven media kinds arrive under their OWN kind name, not a `media`
  // wrapper — a host passes a built-in block through whole.
  if (isMediaKind(part.kind)) {
    // Absent capability ⇒ nothing renders. A media src is a URL the model chose,
    // and a host that cannot say which same-origin paths are its own has no way
    // to gate the request the browser would make.
    if (media === undefined) return null;
    const block = readMediaBlock(part.data, media.sameOriginPrefixes);
    // Gated centrally, once: a rejected src leaves `readMediaBlock` as null
    // rather than reaching a renderer that would draw a broken element.
    if (block === null) return null;
    // The capability types these `unknown` because core imports no React; this
    // is the React file that narrows them.
    const renderPlayer = media.renderPlayer as
      | ((b: typeof block) => ReactNode)
      | undefined;
    // Forwarded for the same reason as the player: a picture the agent produced
    // must open in the host's viewer like every other image in the app.
    const renderImage = media.renderImage as MediaRendererProps["renderImage"];
    // Supplied by the package, NOT by the capability beside it. The player and
    // the viewer are the host's because only the host owns them; a diagram is
    // drawn from the block's own text by a renderer this package depends on, so
    // routing it through the capability would ask every host to opt in to a
    // decision none of them can make differently. That asymmetry is deliberate:
    // a capability answers "does this host have one", and here the answer
    // cannot vary.
    return (
      <MediaWidget
        block={block}
        renderContent={renderMediaContent}
        renderPlayer={renderPlayer}
        renderImage={renderImage}
      />
    );
  }

  return null;
}
