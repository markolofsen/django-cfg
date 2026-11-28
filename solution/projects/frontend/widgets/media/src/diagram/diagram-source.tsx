'use client';

import type { MermaidErrorComponentProps } from 'streamdown';

/**
 * What a fenced diagram shows when it cannot be drawn.
 *
 * Replaces streamdown's default, which paints red-on-red error text with the
 * source folded into a `<details>`. Two reasons that default is wrong here.
 *
 * The source IS the answer. An agent that drew a diagram type our parser does
 * not cover still said something; an error box says only that we failed, and
 * hides what was said behind a disclosure.
 *
 * And most rejections are not errors at all. A diagram mid-stream is rejected
 * on every token until its shape closes, so the default would flash a red box
 * through the whole of a streamed diagram and then replace it with a picture.
 *
 * `retry` is deliberately unused: nothing here is transient. Re-running the
 * same parser over the same source yields the same verdict, and when the source
 * GROWS streamdown re-renders on its own.
 */
export function DiagramSource({ chart }: MermaidErrorComponentProps) {
  return (
    <pre className="chat-diagram-source" data-slot="diagram-source">
      {chart.trim()}
    </pre>
  );
}
