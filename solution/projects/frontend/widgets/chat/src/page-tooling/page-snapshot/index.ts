/**
 * @djangocfg/widget-chat/page-snapshot
 *
 * Client-side capture engine: walks a live React/Next.js DOM into a
 * compact, token-efficient, redacted CST snapshot for an AI chat that
 * understands the page the user is looking at.
 *
 * A sink: it imports nothing else in this package. Kept inside the chat
 * widget while its only consumer is `copilot`; split it out only when a
 * non-chat LLM surface needs it.
 */

// Engine.
export {
  PageSnapshotEngine,
  DEFAULT_TOKEN_BUDGET,
  type CaptureEngineOptions,
  type CaptureResult,
  type CaptureTelemetry,
} from './engine';

// CST types.
export type {
  CSTNode,
  CSTRootNode,
  CSTInteractiveNode,
  CSTContainerNode,
  CSTTextNode,
  CSTRefId,
  CSTInteractiveRole,
  CSTContainerRole,
} from './cst/types';
export {
  isInteractiveNode,
  isContainerNode,
  isTextNode,
  hasChildren,
} from './cst/types';

// Payload.
export {
  CST_SCHEMA_VERSION,
  type PageContextPayload,
  type SnapshotMetadata,
  type SnapshotRepresentation,
} from './cst/payload';

// Directives — shared with the chat for AI-driven highlight/focus.
export {
  isPointDirective,
  type UIDirective,
  type PointDirective,
  type ChatResponseMeta,
} from './cst/directives';

// Redaction (audit surface).
export {
  RedactionAuditor,
  type RedactionAuditReport,
  type RedactionReason,
  type RedactionEntry,
} from './redaction/audit';

// Refs.
export { RefRegistry } from './refs/registry';
export {
  computeLocator,
  resolveLocator,
  type RefLocator,
} from './refs/locator';

// Utilities.
export { estimateTokens } from './tokens';
export { serializeCST } from './cst/serialize';
export { hashSnapshot } from './hash';
export { type ScopeStrategy } from './capture/scope';

// React surface.
export {
  PageSnapshotProvider,
  type PageSnapshotProviderProps,
} from './react/provider';
export {
  usePageSnapshot,
  type PageSnapshotContextValue,
} from './react/use-page-snapshot';
export {
  usePageSnapshotToggle,
  type PageSnapshotToggle,
} from './react/use-page-snapshot-toggle';
export {
  PageSnapshotChip,
  type PageSnapshotChipProps,
} from './react/page-snapshot-chip';
export {
  PageSnapshotPreview,
  type PageSnapshotPreviewProps,
} from './react/page-snapshot-preview';
