// Public root: <Chat>, the primitives, the composer, and the core contracts.
//
// `./content` is NOT re-exported here, and that is the one deliberate
// exclusion. It pulls `streamdown` plus Prism and katex — a host rendering a
// read-only transcript, or supplying its own markdown renderer, must not pay
// for a syntax highlighter. Everything else in this package is behaviour and
// types, which cost nothing to re-export.
//
// A host that renders model markdown imports `@djangocfg/widget-chat/content` and
// registers `Response` as its own text renderer. That is one line in the part
// registry, and it keeps the choice — and the weight — with the host.

export * from "./chat/core";
export * from "./i18n";
export * from "./chat/store";
export * from "./chat/primitives";
export * from "./chat/composer";
export * from "./chat/ui";
export * from "./chat/blocks";
