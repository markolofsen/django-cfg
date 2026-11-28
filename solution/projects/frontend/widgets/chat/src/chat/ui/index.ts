// The styled layer — what a host actually mounts.
//
// This is the ONLY folder that knows ui-core and semantic tokens. Keeping it
// separate is what makes the copy-in strategy possible at all: components
// arrive from @sources as FORM, get re-tokened here, and never reach the
// layers below.
//
// May import: everything below it.
// May NOT be imported by: anything in this package.
//
// shadcn components are substituted with ui-core equivalents; four of those
// substitutions are not mechanical.

export { Chat } from "./chat/chat";
export type { ChatProps, ChatBody, ChatConversation, ChatSlots } from "./chat/chat";
export { ChatRecipientChip } from "./chips/recipient-chip";
export { MessageAuthor } from "./message/author";
export { ChatComposer } from "./chat/composer";
export type { ChatComposerProps } from "./chat/composer";
export { ChatTranscript } from "./transcript/transcript";
export type { ChatTranscriptProps } from "./transcript/transcript";
export { ChatSuggestions } from "./chat/suggestions";
export type { ChatSuggestionsProps } from "./chat/suggestions";
export { ChatMessageView, ChatMessageFrame, MessageProse } from "./message/message";
export { CollapsibleBody } from "./message/collapsible-body";
export { JumpToLatest } from "./transcript/jump-to-latest";
export type { JumpToLatestProps } from "./transcript/jump-to-latest";
export { MessageTime } from "./message/time";
export { MessageActions, messageCopyText, useCopyAction } from "./message/actions";
export type {
  MessageAction,
  MessageActionsProps,
  UseCopyActionOptions,
} from "./message/actions";
// Part renderers a host registers by name. Not a default registry: a host still
// names them, because which part types it draws — and what it substitutes for
// one — is its decision. There is no text renderer here on purpose; drawing
// text needs a markdown component, and `./content` is a separate subpath so a
// read-only host pays nothing for the code highlighter and katex.
//
// `*Renderer`, never `*Part`: `core` already exports `DataPart`, `ToolPart` and
// `ReasoningPart` as the part TYPES, and the root barrel re-exports both layers,
// so matching names would make every one of them ambiguous.
export { DataRenderer } from "./renderers/data";
export { AttachmentRenderer } from "./renderers/attachment";
export { ReasoningRenderer } from "./renderers/reasoning";
export { ToolRenderer } from "./renderers/tool";
export { PendingIndicator } from "./transcript/pending";
export type { PendingIndicatorProps } from "./transcript/pending";
export { DayDivider } from "./message/day-divider";
export type { DayDividerProps } from "./message/day-divider";
export { TurnMark } from "./transcript/turn-mark";
export type { TurnMarkProps, TurnMarkState } from "./transcript/turn-mark";
export type { ChatMessageViewProps, ChatMessageFrameProps } from "./message/message";
export { CollapseTrigger, useCollapse } from "./message/collapsible-body";
export type { Collapse, CollapseState } from "./message/collapsible-body";
export { LinkChip } from "./chips/link-chip";
export { LinkifiedText, type LinkifiedTextProps } from "./chips/linkified-text";
export { ChatLink, type ChatLinkProps } from "../content/chat-link";
export type { LinkChipProps } from "./chips/link-chip";
export { ChatSheet } from "./chat/sheet";
export type { ChatSheetProps } from "./chat/sheet";
export { ChatPanelHeader, PanelCloseButton, PanelIconButton, PANEL_TITLE_CLASS } from "./chat/panel-header";
export type { ChatPanelHeaderProps, PanelIconButtonProps } from "./chat/panel-header";
export { RunBlock, createRunRenderer, runSummary } from "./run";
export type { RunBlockProps, RunOptions, SummaryTone } from "./run";
