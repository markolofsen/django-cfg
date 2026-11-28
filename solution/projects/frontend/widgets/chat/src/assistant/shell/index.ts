/**
 * The shell, session-free: the frame, the dock, the host trio and its history slot, the chat body, the composer behaviour, the copy and the panel state. A host with its own transport
 * (a call polls its lines) imports this and leaves the SSE wire, the session storage and the demo out of its graph. `../assistant` re-exports all of it and adds the session layer.
 * Layer: `shell` imports `ui`, `composer`, `primitives`, `widgets`, `content`, `store`, `core`, `utils` and `i18n`; never `session` or `wire`.
 */
export { AssistantChat, type DataPartRenderer } from './conversation/assistant-chat';
export { DEFAULT_MODEL, useModelAliases } from './conversation/models';
export { useAssistantCopy, useAssistantLocale, ASSISTANT_DICTIONARIES, type AssistantCopy } from '../../i18n/assistant';
export { askAssistant } from './composer/handoff';
export { SUGGESTION_ICON_KEYS, suggestionIcon, type SuggestionIconKey } from './composer/suggestion-icons';
export { ChatDock } from './panel/chat-dock';
export { AssistantFrame, DOCK_FROM, type FrameLabels } from './panel/assistant-frame';
export { AssistantFab, type FabHint } from './launcher/assistant-fab';
export { AssistantHelp, useHelpRows, type HelpRow } from './panel/assistant-help';
export { ASSISTANT_TOGGLE, DICTATION_TOGGLE } from './composer/keys';
export { AssistantGreeting, type AssistantGreetingProps } from './launcher/assistant-greeting';
export { AssistantMark } from './launcher/assistant-mark';
export { AssistantLocked } from './access/assistant-locked';
export { createAssistantUi, useMediaQuery, useViewportWidth, type UiOptions, type UiState, type UiStorage } from './panel/panel-state';
export { AssistantHostProvider, AssistantPortal, AssistantSlot, AssistantHeaderActions, useAssistantHistory, usePublishHistoryPanel } from './panel/host';
export { MessageFooter } from './conversation/message-footer';
export { AssistantAuthGate, useAssistantAccess, useSignIn, type AssistantLockOptions, type AssistantAccess } from './access/assistant-auth-gate';
