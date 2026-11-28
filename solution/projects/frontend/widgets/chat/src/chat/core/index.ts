export * from "./conversation/parts";
export * from "./compose/attachments";
export * from "./conversation/group-parts";
export * from "./conversation/adapter";
export * from "./capabilities";
export * from "./compose/outbound";
export * from "./room/recipient";
export * from "./room/reply";
export * from "./room/mentions";
export * from "./tools/picks";
// What a pick still wants. A rule about the DRAFT, so it ships with the model
// rather than being re-derived at the surface that renders the hint.
export * from "./compose/tool-prompt";
export { addToolPick, addToolPicks, removeToolPick, toggleToolPick } from "./tools/picks-set";
export * from "./conversation/chunks";
// Every adapter that mints a tool part owes the reader the same name, so the
// rule ships with the model rather than being re-derived at each entry point.
export * from "./tools/name";
export * from "./conversation/transcript";
export * from "./media";
export * from "./tools";
export * from "./compose/recall";
export * from "./voice";
export * from "./compose/queue";
export * from "./screen";
export * from "./conversation/incomplete-math";
export * from "./compose/draft-storage";
export * from "./conversation/events";
export * from "./room/reload-decision";
// The host implements `AskReplace` and so must be able to name its return.
// `composer/index.ts` states this barrel already carries it and declines to
// re-export for that reason — the two must agree, or the type is reachable from
// nowhere and every host writes its own union.
export * from "./compose/text-replace";
// The mention URL scheme. Exported because `configureMentionScheme` is a host
// call — the scheme is the host's product name, and nothing else can supply it.
export * from "./links";
// Trace steps that are not a thought or a tool call travel as `data` parts of this kind.
export * from "./run/trace";
export * from "./run/view";
export * from "./run/privacy";
export * from "./run/paging";
export * from "./run/segment";
export * from "./run/export";
