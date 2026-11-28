// Block renderers. A widget is a PURE FUNCTION of its `data`: no store, no
// transcript, no streaming knowledge beyond an explicit prop. That is what
// makes one testable without mounting a provider — and why a dependency with a
// hidden context requirement (ui-core's Spinner needs i18n) cannot be used here.
//
// Each widget ships with a `read*` parser kept SEPARATE from the component, so
// a malformed payload degrades to "render nothing" instead of throwing inside a
// transcript row, and so the parsing is testable without a renderer.
//
// May import: core, utils, content.
// May NOT import: store, primitives, composer, ui.

export { MediaWidget } from "./media";
export type { MediaRendererProps } from "./media";
