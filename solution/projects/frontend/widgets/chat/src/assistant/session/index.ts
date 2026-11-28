// The session layer: one conversation over the wire. A stream adapter that turns frames into chat chunks, `useSession` (load, send, reconnect, reconcile after a lost stream),
// the thread storage and the chat API kit, the stored-to-message mapping and the offline scripted transport.
// Layer: `session` imports `wire`, `store`, `core`, `utils` and `i18n`; it draws nothing, so a host with its own UI can use it alone.
export { scriptedTransport, type ScriptStep } from './stream/scripted-transport';
export { useSession, type Session, type SessionCopy, type SessionDeps, type SessionNotice, type ThreadState } from './stream/use-session';
export { createStreamAdapter, sendFeedbackTurn, type AdapterDeps } from './stream/adapter';
export { reconcile, type Reconciled } from './stream/reconcile';
export { fromStored, fromStoredThread } from './stream/from-stored';
export { relativeTime, restoreSession, type SessionStorage, type ThreadApi } from './threads/sessions';
export { groupSessions, filterSessions, type SessionGroup } from './threads/group-sessions';
export { createSessionStorage, useRememberedSession } from './threads/storage';
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
} from './threads/kit';
