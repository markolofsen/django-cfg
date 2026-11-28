// The streamdown `DiagramPlugin` over our synchronous renderer.
//
// May import: streamdown (types only), ./render.

import type { DiagramPlugin } from 'streamdown';

/**
 * Thrown when the source is not a diagram yet.
 *
 * A distinct type because the two rejections mean opposite things to a reader:
 * an unsupported diagram is final and its source is the answer, while a partial
 * one is simply not finished. Both fall back to the source, so nothing branches
 * on this today — it exists so the error surface can tell them apart without
 * matching on message text.
 */
export class DiagramIncompleteError extends Error {
  constructor() {
    super('diagram source is incomplete');
    this.name = 'DiagramIncompleteError';
  }
}

/**
 * A mermaid renderer for `Streamdown`'s plugin slot.
 *
 * WHY THE GUARD IS HERE AND NOT IN STREAMDOWN. Streamdown computes whether a
 * fence is still open and forwards it to the code-block branch as
 * `isIncomplete` — but the mermaid branch drops it, and its render effect is
 * keyed on the chart alone. So every streamed token reaches this function, and
 * the guard has to be ours or there is none.
 *
 * That matters because `renderDiagram` does NOT fail on a half-arrived source;
 * it draws a plausible wrong picture. Rejecting is what keeps the source
 * showing until the shape closes.
 *
 * `initialize` is a no-op: the plugin contract mirrors the mermaid runtime,
 * which needs configuring before use. Ours reads the theme from CSS variables
 * baked into the SVG, so there is no state to configure.
 */
export const diagramPlugin: DiagramPlugin = {
  language: 'mermaid',
  name: 'mermaid',
  type: 'diagram',
  getMermaid: () => ({
    initialize: () => undefined,
    // The `id` is streamdown's element handle. Ours goes unused: the SVG
    // carries no ids to collide, which is what lets one diagram be rendered
    // twice — inline and fullscreen — with no rewriting.
    render: async (_id: string, source: string) => {
      // Imported here rather than at the top so the parser is fetched by the
      // first diagram, not by the transcript that might never contain one. The
      // contract is already async, so this costs no extra round trip — and it
      // is what keeps the plugin registrable at the package root without
      // dragging 2.5 MB along with it.
      const { isDiagramComplete, renderDiagram } = await import('./render');
      if (!isDiagramComplete(source)) throw new DiagramIncompleteError();
      const result = renderDiagram(source);
      if (!result.ok) throw new Error(result.error);
      return { svg: result.svg };
    },
  }),
};
