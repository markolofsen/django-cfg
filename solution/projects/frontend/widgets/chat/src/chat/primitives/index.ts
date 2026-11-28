// Headless compound components: behaviour and accessibility, NO styling.
// Transcript, message, tool calls, the part registry, focus and scroll.
//
// May import: store, core, utils.
// May NOT import: composer, ui, Tailwind classes.
//
// Unstyled on purpose — this is the escape hatch. Beside a ready-made <Chat>
// there is always <ChatProvider> plus your own UI. Without one, prop explosion
// returns: that is exactly how the predecessor reached 83 props.

export { Transcript } from "./transcript/transcript";
export type { TranscriptProps } from "./transcript/transcript";
export { Message, MessageContent } from "./parts/message";
export type { MessageProps, MessageContentProps } from "./parts/message";
export { PartRegistryProvider, usePartRenderer } from "./parts/part-registry";
export type { PartRegistry, PartRenderer, PartRenderProps, PartRegistryProviderProps } from "./parts/part-registry";
export { ToolCall, ToolCallHeader, ToolCallInput, ToolCallOutput, SubagentThread } from "./parts/tool-call";
export type {
  ToolCallProps,
  ToolCallHeaderProps,
  ToolCallInputProps,
  ToolCallOutputProps,
  SubagentThreadProps,
} from "./parts/tool-call";
export { Suggestions, useHasSuggestions } from "./suggestions";
export type { SuggestionsProps, SuggestionRenderProps } from "./suggestions";
export { useDismiss } from "./layer/use-dismiss";
export type { UseDismissOptions } from "./layer/use-dismiss";
export {
  useSelectAllTranscript,
  selectTranscript,
  claimsSelectAll,
  isEditableTarget,
} from "./transcript/use-select-all-transcript";
export { useRovingFocus } from "./transcript/use-roving-focus";
export type { RovingFocus } from "./transcript/use-roving-focus";
export { useStickToBottom } from "./transcript/use-stick-to-bottom";
export type { StickToBottom } from "./transcript/use-stick-to-bottom";
export { useOverflows } from "./use-overflows";
export { useTurnActivity } from "./transcript/use-turn-activity";
export type { TurnActivity } from "./transcript/use-turn-activity";
export { useHoldBottom } from "./transcript/use-hold-bottom";
export type { HoldBottomOptions } from "./transcript/use-hold-bottom";
export { useViewportBox, trackViewport } from "./layer/use-viewport-box";
export { useLayer } from "./layer/use-layer";
export type { UseLayerOptions } from "./layer/use-layer";
