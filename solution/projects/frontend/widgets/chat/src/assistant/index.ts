export { AssistantChat, type DataPartRenderer } from './shell';
export { DEFAULT_MODEL, useModelAliases } from './shell';
// The interactive blocks are chat's and need no registration (`kind`: ask, approval, changes); re-exported for a host that draws one itself.
export { ApprovalBlock, AskBlock, ChangesBlock, type ApprovalPayload, type AskPayload, type ChangesPayload } from '../chat/blocks';
export { type ModelOption, type ModelsCapability } from '../chat/core';
// The attachment vocabulary is chat's; re-exported so an embedder configures the assistant from one import.
export {
  DEFAULT_ATTACHMENT_KINDS,
  DEFAULT_MAX_FILES,
  DEFAULT_MAX_FILE_BYTES,
  type Attachment,
  type AttachmentKind,
  type AttachmentUploadContext,
  type AttachmentsCapability,
  type UploadedAttachment,
} from '../chat/core';
export { scriptedTransport, type ScriptStep } from './session';
export { useAssistantCopy, useAssistantLocale, ASSISTANT_DICTIONARIES, type AssistantCopy } from './shell';
export { askAssistant } from './shell';
export { ChatDock } from './shell';
export { AssistantFrame, DOCK_FROM, type FrameLabels } from './shell';
export { AssistantHelp, useHelpRows, type HelpRow } from './shell';
export { MessageFooter } from './shell';
export { AssistantFab, type FabHint } from './shell';
export { ASSISTANT_TOGGLE, DICTATION_TOGGLE } from './shell';
export { AssistantGreeting, type AssistantGreetingProps } from './shell';
export { AssistantMark } from './shell';
export { AssistantLocked } from './shell';
export { createAssistantUi, useMediaQuery, useViewportWidth, type UiOptions, type UiState, type UiStorage } from './shell';
export { AssistantHostProvider, AssistantPortal, AssistantSlot, AssistantHeaderActions, useAssistantHistory } from './shell';
export { AssistantHistory } from './history/assistant-history';
export { SessionsPanel } from './history/sessions-panel';
export { groupSessions, filterSessions, type SessionGroup } from './session';
export { useSession, type Session, type SessionCopy, type SessionDeps, type SessionNotice, type ThreadState } from './session';
export { relativeTime, restoreSession, type SessionStorage, type ThreadApi } from './session';
export { SessionsMenu } from './history/sessions-menu';
export { createSessionStorage, useRememberedSession } from './session';
export {
  createChatTransport,
  loadChatAttachments,
  ChatUploadError,
  type ChatAttachmentCalls,
  type ChatAttachmentLimitsShape,
  type ChatAttachmentShape,
  type ChatAttachmentsConfig,
  storedMessageOf,
  storedThreadOf,
  type ChatCallResult,
  type ChatConnection,
  type ChatMessageShape,
  type ChatThreadCalls,
  type ChatThreadDetailShape,
  type ChatThreadListItemShape,
  type ChatThreadShape,
  type ChatTransportConfig,
} from './session';
export type { StoredAttachment } from './wire';
export { createStreamAdapter, sendFeedbackTurn, type AdapterDeps } from './session';
export { reconcile, type Reconciled } from './session';
export { fromStored, fromStoredThread } from './session';
export { createTransport, ChatHttpError, ChatNetworkError, ThreadNotFoundError, type ChatTransport, type RejectCode, type SendInput, type TransportConfig } from './wire';
export { StreamLostError } from './wire';
export { decodeFrame, WIRE_VERSION } from './wire';
export type { ChatContext, Frame, Phase, StreamErrorCode } from './wire';
export type { StoredConversation, StoredMessage, StoredPart, StoredStatus, StoredThread } from './wire';
export { citationsRenderer, KB_RENDERERS, KB_PAYLOAD_KINDS, type Citation } from './examples/kb-assistant';
export { DemoAssistant, DEMO_SUGGESTIONS, useDemoAssistant } from './examples/demo/demo-assistant';
export { DEMO_RENDERERS, DEMO_PAYLOAD_KINDS } from './examples/demo/widgets';
export { DEMO_THREAD, demoReply, demoScript } from './examples/demo/thread';
export { SUGGESTION_ICON_KEYS, suggestionIcon, type SuggestionIconKey } from './shell';
export { AssistantAuthGate, useAssistantAccess, useSignIn, type AssistantLockOptions, type AssistantAccess } from './shell';
