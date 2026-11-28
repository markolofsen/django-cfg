import type { ReactNode } from "react";

import { LazyDiagram } from "@djangocfg/widget-media/diagram";
import type { MediaBlock } from "../core";

/**
 * The renderer for the media kinds whose payload is TEXT, not a URL.
 *
 * `MediaWidget` has always routed `json`/`code`/`markdown`/`text`/`mermaid`
 * through an optional `renderContent`, and nothing ever supplied one — so every
 * one of them fell through to a `<pre>`, including the diagrams the `show_media`
 * tool declares among its kinds. The callback was the seam; this is the thing
 * that was missing from the other side of it.
 *
 * Only `mermaid` is answered here. The other four ARE plain text until this
 * package has a reason to say otherwise, and the `<pre>` fallback is a correct
 * rendering of them rather than a placeholder — returning null for those is what
 * keeps the widget's own fallback in charge instead of duplicating it.
 *
 * Lives in `content/` because that is the layer that owns rendered content, and
 * `widgets/` may import it. The diagram reaches the transcript through the
 * layer whose job it is, not through a package a widget imported directly.
 */
export function renderMediaContent(block: MediaBlock): ReactNode {
  if (block.kind !== "mermaid") return null;
  // The wire calls this field `chart`; `readMediaBlock` normalises every
  // textual kind onto `content`, so there is one name here for all of them.
  const chart = block.content;
  if (chart === undefined || chart.trim() === "") return null;
  // Never streaming: a `show_media` block is dispatched once, whole. That is
  // the caller-side half of the guard the renderer cannot answer from the
  // source alone — the fenced rail, where the text really does arrive a token
  // at a time, is guarded inside the streamdown plugin instead.
  // Lazy: this file is reachable from the package ROOT through `data.tsx`, so
  // an eager import would put the parser in every transcript's first paint —
  // including the ones that never show a diagram.
  return <LazyDiagram chart={chart} />;
}
