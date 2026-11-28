// Mermaid rendering, reached from both rails a diagram arrives on: a fenced
// block in prose (the streamdown plugin) and a `show_media` block (the
// component).
//
// EVERYTHING HERE IS DEFERRED. The parser is ~2.5 MB and most transcripts carry
// no diagram, so a consumer importing this barrel must not pay for one until a
// diagram appears — `LazyDiagram` splits it behind Suspense and the plugin
// behind its own async `render`. Pinned by `cost.test.ts`, which walks this
// file's static graph.
//
// The eager `Diagram` and the pure `render` are deliberately NOT re-exported.
// A barrel re-export is a static edge, so naming them here would pull the
// parser into every consumer and quietly undo the split — which is exactly what
// this file did on its first version. Reach for them by their own paths.
//
// Deliberately NOT re-exported from the package root — see `@dev/decisions.md`
// D4. A host rendering a read-only transcript pays for neither.

export type { DiagramProps } from './diagram';
export { LazyDiagram } from './lazy';
export { DiagramSource } from './diagram-source';
export { diagramPlugin, DiagramIncompleteError } from './plugin';
