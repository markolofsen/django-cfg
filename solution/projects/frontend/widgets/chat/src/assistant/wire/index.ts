// The browser half of the chat wire: the SSE frames the server speaks, the tolerant decoder, the transport that opens the stream, and the stored shapes a thread is replayed from.
// Layer: `wire` imports `core` and `utils` only; the session layer reads it. `fixtures/events.json` is the Python twin the server's contract test pins.
export {
  createTransport,
  ChatHttpError,
  ChatNetworkError,
  ThreadNotFoundError,
  type ChatTransport,
  type RejectCode,
  type SendInput,
  type TransportConfig,
} from './transport';
export { StreamLostError } from './parse-sse';
export { decodeFrame, WIRE_VERSION } from './frames';
export type { ChatContext, Frame, Phase, StreamErrorCode } from './frames';
export type { StoredAttachment, StoredConversation, StoredMessage, StoredPart, StoredStatus, StoredThread } from './stored';
export { decodeStep, stepPart, storedTraceParts, type StoredTrace, type TraceStep } from './trace';
