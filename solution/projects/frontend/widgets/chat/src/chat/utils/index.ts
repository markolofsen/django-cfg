// Leaf mechanics: byte formatting, ids, clipboard, class merging, dates.
//
// May import: nothing local. This folder is a sink.
//
// Membership test, stated because this is where codebases dump everything: if
// the helper's signature mentions a message, a part, a tool or a block, it is
// NOT a util — it belongs in core.

export { messageOf } from "./error-message";
export { dayHeadingFor, type DayHeading } from "./day-heading";
export { markdownToText, markdownToLine } from "./markdown-text";
export type { MarkdownTextOptions, OpaqueBlock } from "./markdown-text";
