/**
 * MarkdownMessage — chat-tuned markdown renderer.
 *
 * Public API:
 *   - `MarkdownMessage` (default + named) — the React component.
 *   - `MarkdownMessageProps` — its full prop shape.
 *   - `LinkRule` — the declarative link-handling primitive.
 *   - `extractTextFromChildren` — utility for callers that build their
 *     own custom `a` renderers and need a string label.
 *   - `urlChipRule` — opt-in built-in `LinkRule` that renders a bare
 *     web URL as a compact `<UrlChip>` (favicon + middle-ellipsis).
 *   - `ActionRow` — dumb action row (copy button), takes `visible`
 *     from its owner.
 *   - `ChatMessageRow` — opinionated bubble + action-row wrapper
 *     with state-driven hover, close-delay and touch handling.
 */
export { MarkdownMessage, default } from './MarkdownMessage';
export type { MarkdownMessageProps, LinkRule } from './types';
export { extractTextFromChildren } from './plainText';
export { urlChipRule } from './builtinRules';
export { ActionRow } from './ActionRow';
export { ChatMessageRow } from './ChatMessageRow';
