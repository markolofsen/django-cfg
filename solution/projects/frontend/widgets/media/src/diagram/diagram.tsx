'use client';

import { useMemo } from 'react';

import { useMediaCopy, type MediaCopy } from '../i18n';
import { isDiagramComplete, renderDiagram } from './render';

export interface DiagramProps {
  /** Mermaid source, possibly still arriving. */
  readonly chart: string;
  /**
   * Whether the source is still being written.
   *
   * Supplied by the caller because only it knows: a fenced block knows its
   * fence is open, a `show_media` block is finished the moment it exists. The
   * shape of the source cannot answer this on its own — see `isDiagramComplete`,
   * which is the second, weaker check applied underneath.
   */
  readonly streaming?: boolean;
  readonly className?: string;
  /** Override the widget's English copy; omitted keys fall back to defaults. */
  readonly copy?: Partial<MediaCopy>;
}

/**
 * A mermaid diagram, or its source when that is the honest answer.
 *
 * Both fallbacks show the SOURCE rather than an error box, because the source
 * is what the agent actually said. A diagram that cannot be drawn is still an
 * answer; an error box is not.
 */
export function Diagram({ chart, streaming = false, className, copy }: DiagramProps) {
  const copyText = useMediaCopy(copy);

  // Rendering is the expensive step and `chart` changes on every streamed
  // token, so the guard is inside the memo: a diagram still being written must
  // not be parsed at all, not merely have its output discarded.
  const result = useMemo(() => {
    if (streaming || !isDiagramComplete(chart)) return null;
    return renderDiagram(chart);
  }, [chart, streaming]);

  if (result === null || !result.ok) {
    return (
      <pre className={`chat-diagram-source ${className ?? ''}`} data-slot="diagram-source">
        {chart.trim()}
      </pre>
    );
  }

  return (
    <div
      className={`chat-diagram ${className ?? ''}`}
      data-slot="diagram"
      // The parser escapes label text into `data-*` attributes, so a model
      // cannot get markup out of a label and into the document. That is a
      // security property of a dependency rather than of this file, so it is
      // pinned by `injection.test.ts` instead of trusted.
      dangerouslySetInnerHTML={{ __html: result.svg }}
      role="img"
      aria-label={copyText.diagram}
    />
  );
}
