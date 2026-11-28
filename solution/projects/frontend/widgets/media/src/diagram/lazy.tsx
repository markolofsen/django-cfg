'use client';

/**
 * Lazy-loaded Diagram.
 *
 * The renderer carries `beautiful-mermaid` (~2.5 MB), which no transcript needs
 * until a diagram actually appears — and most never carry one. Splitting it out
 * is what keeps the promise that a host rendering a read-only transcript pays
 * for a parser it does not reach.
 *
 * This is the form every CONSUMER should mount. The eager `Diagram` stays
 * exported for a host that has already decided it wants the chunk, and for the
 * stories, where a Suspense boundary would only add a frame to assert around.
 */

import { lazy, Suspense } from 'react';

import type { DiagramProps } from './diagram';

export type { DiagramProps };

const DiagramImpl = lazy(() => import('./diagram').then((mod) => ({ default: mod.Diagram })));

/**
 * The source, while the renderer arrives.
 *
 * The same thing every other fallback here shows, and for the same reason: it
 * is the answer the agent gave. A spinner would replace content that is already
 * in hand with a promise of content.
 */
function Fallback({ chart }: { readonly chart: string }) {
  return (
    <pre className="chat-diagram-source" data-slot="diagram-source">
      {chart.trim()}
    </pre>
  );
}

export function LazyDiagram(props: DiagramProps) {
  return (
    <Suspense fallback={<Fallback chart={props.chart} />}>
      <DiagramImpl {...props} />
    </Suspense>
  );
}
